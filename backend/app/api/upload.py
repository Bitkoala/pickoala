"""
Image Upload API
图片上传接口 - 支持异步审核模式
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, BackgroundTasks, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
from app.database import get_db
from app.models.user import User
from app.models.image import Image, ImageStatus
from app.schemas.image import ImageUploadResponse, ImageResponse
from app.api.deps import get_current_user_optional
from app.utils.validators import validate_image_file, validate_image_content
from app.utils.rate_limit import get_real_ip
from app.utils.security import generate_random_string
from app.utils.date_path import get_date_path
from app.services.image import process_image
from app.services.storage import get_storage_backend_async
from app.services.audit import get_audit_service, run_audit_in_background

from app.services.watermark import apply_watermark
from app.services.ai_service import gemini_service
from app.services import settings as settings_service
from app.services import security as security_service
from app.config import get_settings
from app.api.admin.audit import create_audit_log
import logging
from datetime import datetime
import os
from sqlalchemy import select

router = APIRouter(prefix="/upload", tags=["Upload"])
config = get_settings()
logger = logging.getLogger(__name__)


@router.post("", response_model=ImageUploadResponse)
async def upload_image(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    album_id: Optional[int] = None,
    with_watermark: bool = Form(False),
    watermark_config: Optional[str] = Form(None),
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    上传图片
    
    流程：
    1. 验证文件和权限
    2. 处理图片（压缩、获取尺寸）
    3. 保存到存储
    4. 创建数据库记录（状态为 pending 如果启用审核）
    5. 后台异步执行审核
    6. 立即返回响应给用户
    """
    ip = get_real_ip(request)
    user_id = user.id if user else None
    
    # ========== 权限检查 ==========
    is_banned, ban_reason = await security_service.is_banned(ip, user_id, db)
    if is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"上传功能已被暂时禁用。原因: {ban_reason}"
        )
    
    if not user and not await settings_service.is_guest_upload_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="游客上传已禁用"
        )
    
    # Determine VIP status
    is_vip = False
    if user and user.vip_expire_at:
        if user.vip_expire_at > datetime.utcnow():
            is_vip = True
    
    # ========== 速率限制 ==========
    is_allowed, limit_type, _ = await security_service.check_rate_limit_multi(
        ip, user_id, is_user=bool(user), is_vip=is_vip
    )
    if not is_allowed:
        await security_service.log_violation(
            ip=ip, violation_type="rate_limit_exceeded",
            user_id=user_id, details={"limit_type": limit_type}, db=db
        )
        messages = {
            "minute": "上传过于频繁，请稍后再试",
            "hour": "已达到每小时上传限制",
            "day": "已达到每日上传限制"
        }
        raise HTTPException(status_code=429, detail=messages.get(limit_type, "请求过于频繁"))
    
    # ========== 文件验证 ==========
    if is_vip:
        max_size = await settings_service.get_max_upload_size_vip()
    elif user:
        max_size = await settings_service.get_max_upload_size_user()
    else:
        max_size = await settings_service.get_max_upload_size_guest()
    allowed_extensions = await settings_service.get_allowed_extensions()
    logger.info(f"[Upload] File: {file.filename}, max_size: {max_size}, allowed_ext: {allowed_extensions}")
    
    try:
        extension = validate_image_file(file, max_size, allowed_extensions)
    except HTTPException as e:
        logger.warning(f"[Upload] File validation failed: {e.detail}")
        raise
    
    content = await file.read()
    logger.info(f"[Upload] File size: {len(content)} bytes, extension: {extension}")
    
    try:
        mime_type, corrected_extension = await validate_image_content(content, extension, max_size)
    except HTTPException as e:
        logger.warning(f"[Upload] Content validation failed: {e.detail}")
        raise
    
    # 如果扩展名被修正，使用修正后的扩展名
    if corrected_extension != extension:
        logger.info(f"[Upload] Extension auto-corrected: {extension} -> {corrected_extension}")
        extension = corrected_extension

    logger.info(f"[Upload] Validated: mime_type={mime_type}, extension={extension}")
    
    # ========== 图片处理 ==========
    compression_quality = await settings_service.get_compression_quality()
    processed_content, width, height, final_extension = process_image(
        content, extension, quality=compression_quality
    )

    # Update mime_type if converted to webp
    if final_extension == 'webp' and extension != 'webp':
        mime_type = 'image/webp'
        logger.info(f"[Upload] Converted to WebP, mime_type updated to {mime_type}")
    
    # Apply watermark if requested and user has permission
    if with_watermark and user:
        # Check VIP status
        is_vip_for_wm = False
        if user.vip_expire_at and user.vip_expire_at > datetime.utcnow():
            is_vip_for_wm = True
            
        if is_vip_for_wm:
             # Parse watermark config
             wm_config_dict = {}
             if watermark_config:
                 try:
                     wm_config_dict = json.loads(watermark_config)
                 except Exception as e:
                     logger.warning(f"Failed to parse watermark config: {e}")
             
             # Pass config to apply_watermark (overrides user settings)
             processed_content = apply_watermark(processed_content, user, config=wm_config_dict)
    
    # ========== 生成文件名 ==========
    while True:
        filename = generate_random_string(8)
        result = await db.execute(select(Image).where(Image.filename == filename))
        if not result.scalar_one_or_none():
            break
    
    full_filename = f"{filename}.{final_extension}"
    
    # ========== 生成日期路径 ==========
    date_path = await get_date_path()
    logger.info(f"[Upload] Date path: {date_path}")
    
    # ========== 保存到存储 ==========
    storage = await get_storage_backend_async()
    try:
        # 传递日期路径给存储后端，返回完整的相对路径
        file_path = await storage.save(processed_content, full_filename, date_path)
        logger.info(f"[Upload] File saved to: {file_path}")
    except Exception as e:
        logger.error(f"Storage error: {e}")
        raise HTTPException(status_code=500, detail="图片保存失败")
    
    # ========== 确定初始状态 ==========
    audit_enabled = await settings_service.is_audit_enabled()
    initial_status = ImageStatus.PENDING if audit_enabled else ImageStatus.APPROVED
    
    # ========== 创建数据库记录 ==========
    # 获取图片URL - 对于本地存储，如果配置了CDN域名，也会返回完整URL
    image_url = storage.get_url(file_path)
    # 只有当URL是完整URL（以http开头）时才存储到storage_url
    # 相对路径（/uploads/...）不需要存储，由Image.url属性动态生成
    storage_url_value = image_url if image_url.startswith('http') else None
    
    image = Image(
        filename=filename,
        original_filename=file.filename,
        extension=final_extension,
        mime_type=mime_type,
        file_size=len(processed_content),
        file_path=file_path,  # 存储完整相对路径，如 "2025/12/14/abc123.png"
        width=width,
        height=height,
        storage_type=storage.storage_type,
        storage_url=storage_url_value,
        user_id=user.id if user else None,
        album_id=album_id if user and album_id else None,
        guest_ip=ip if not user else None,  # Legacy field
        upload_ip=ip,  # 记录所有上传者的IP（无论游客还是用户）
        status=initial_status,
    )
    
    db.add(image)
    await db.commit()
    await db.refresh(image)
    
    # ========== 后台异步审核 ==========
    if audit_enabled:
        audit_service = await get_audit_service()
        if audit_service.enabled:
            # 获取图片公网URL（腾讯云审核需要完整的公网URL）
            # 如果是云存储，storage_url 已经是完整URL
            # 如果是本地存储，需要拼接站点URL
            if image.storage_url:
                image_public_url = image.storage_url
            else:
                # Generic fallback using site_url + image.url
                site_url = await settings_service.get_site_url()
                site_url = site_url.rstrip('/') if site_url else ''
                
                if not site_url:
                    logger.warning(f"[Upload] site_url not configured, skipping audit for image {image.id}")
                    image_public_url = None
                else:
                    # image.url is the relative path (e.g. /uploads/... or /img/images/...)
                    image_public_url = f"{site_url}{image.url}"
            
            # 添加后台任务 - 不阻塞响应（仅当有有效URL时）
            if image_public_url:
                background_tasks.add_task(
                    run_audit_in_background,
                    image.id,
                    processed_content,
                    audit_service,
                    image_public_url  # 传递完整公网URL给审核服务
                )
                logger.info(f"Scheduled background audit for image {image.id}, url={image_public_url}")
            else:
                # 无法审核时，直接设置为 approved（避免图片永远处于 pending 状态）
                image.status = ImageStatus.APPROVED
                await db.commit()
                logger.warning(f"[Upload] Image {image.id} auto-approved due to missing audit URL")
    
    # ========== 记录审计日志 ==========
    await create_audit_log(
        db=db,
        action="upload",
        ip_address=ip,
        user_id=user.id if user else None,
        resource_type="image",
        resource_id=image.id,
        user_agent=request.headers.get("User-Agent"),
        details=f"Uploaded image: {file.filename} -> {filename}.{final_extension}",
        log_status="success"
    )
    
    # ========== 触发实时备份 ==========
    try:
        from app.services.backup.scheduler import trigger_realtime_backup
        background_tasks.add_task(
            trigger_realtime_backup,
            image.id,
            file_path,
            len(processed_content)
        )
        logger.debug(f"Scheduled realtime backup for image {image.id}")
    except Exception as e:
        logger.warning(f"Failed to schedule realtime backup: {e}")
    
    # ========== 返回响应 ==========
    image_url = image.url    # 6. Return response
    
    # Trigger AI Analysis in Background
    if image and image.id:
        # Check if Gemini is configured before setting status and adding task
        gemini_keys = await settings_service.get_gemini_api_keys()
        if gemini_keys:
            image.ai_analysis_status = "pending"
            await db.commit()
            
            # Define the background task wrapper
            async def run_ai_analysis(img_id: int, file_path: str, db_session_maker):
                # Create a new session for the background task
                async with db_session_maker() as session:
                    try:
                        logger.info(f"Starting AI analysis for image {img_id}")
                        # Update status to processing
                        stmt_update = select(Image).where(Image.id == img_id)
                        res_update = await session.execute(stmt_update)
                        db_img_update = res_update.scalar_one_or_none()
                        if db_img_update:
                            db_img_update.ai_analysis_status = "processing"
                            await session.commit()

                        full_path = os.path.join(config.upload_path, file_path)
                        result = await gemini_service.analyze_image(full_path)
                        
                        if "error" not in result:
                            # Update DB
                            stmt = select(Image).where(Image.id == img_id)
                            result_db = await session.execute(stmt)
                            db_img = result_db.scalar_one_or_none()
                            
                            if db_img:
                                db_img.ai_tags = json.dumps(result.get("tags", []))
                                db_img.ai_description = result.get("description", "")
                                db_img.ai_analysis_status = "completed"
                                await session.commit()
                                logger.info(f"AI analysis completed for image {img_id}")
                        else:
                            logger.error(f"AI analysis failed for image {img_id}: {result['error']}")
                            # Update status to failed
                            stmt = select(Image).where(Image.id == img_id)
                            result_db = await session.execute(stmt)
                            db_img = result_db.scalar_one_or_none()
                            if db_img:
                                db_img.ai_analysis_status = "failed"
                                await session.commit()

                    except Exception as e:
                        logger.error(f"Background AI task error: {str(e)}")

            # Trigger AI analysis if enabled
            if await settings_service.is_ai_analysis_enabled():
                # We need a session maker to pass to the background task
                from app.database import AsyncSessionLocal
                background_tasks.add_task(run_ai_analysis, image.id, image.file_path, AsyncSessionLocal)

    return ImageUploadResponse(
        success=True,
        image=ImageResponse.model_validate(image),
        url=image_url,
        markdown=f"![{image.original_filename}]({image_url})",
        html=f'<img src="{image_url}" alt="{image.original_filename}">',
        bbcode=f"[img]{image_url}[/img]",
    )


@router.post("/paste", response_model=ImageUploadResponse)
async def upload_from_paste(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """从剪贴板粘贴上传"""
    return await upload_image(request, background_tasks, file, None, False, None, user, db)
