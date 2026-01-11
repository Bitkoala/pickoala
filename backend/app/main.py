from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from app.config import get_settings
from app.database import init_db, AsyncSessionLocal
from app.redis import init_redis, close_redis
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, StreamingResponse, Response
from app.models.image import Image
from app.models.file import File
from app.api import auth, upload, images, albums, user, files, chunk # Added 'files' and 'chunk' here
from app.api.admin import router as admin_router
from app.utils.rate_limit import get_real_ip, is_blacklisted

# Import all models to ensure they are registered with SQLAlchemy
from app.models import user as user_model
from app.models import image as image_model
from app.models import album as album_model
from app.models import settings as settings_model
from app.models import audit_log as audit_log_model
from app.models import backup as backup_model
from app.models import payment as payment_model
from app.models import activation_code as activation_code_model

settings = get_settings()

# Ensure uploads directory exists
os.makedirs(settings.upload_path, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    await init_redis()
    await init_db()
    # Load IP header settings
    from app.utils.rate_limit import refresh_ip_header_settings
    try:
        await refresh_ip_header_settings()
        logger.info("IP header settings loaded")
    except Exception as e:
        logger.warning(f"Failed to load IP header settings, using defaults: {e}")
    
    # Initialize backup scheduler
    try:
        from app.services.backup.scheduler import init_scheduler
        await init_scheduler()
        logger.info("Backup scheduler initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize backup scheduler: {e}")
    
    logger.info("Application started successfully")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    
    # Shutdown backup scheduler
    try:
        from app.services.backup.scheduler import shutdown_scheduler
        await shutdown_scheduler()
    except Exception as e:
        logger.warning(f"Error shutting down backup scheduler: {e}")
    
    await close_redis()
    logger.info("Application shut down")


app = FastAPI(
    title=settings.app_name,
    description="A secure image hosting service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_debug else [settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Check IP blacklist
    ip = get_real_ip(request)
    if await is_blacklisted(ip):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Your IP has been temporarily blocked"}
        )
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "error.validationError",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "error.internalError"}
    )


# Include routers
from app.api import appeal, gallery, download, payments, activation, file_collections
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(chunk.router, prefix="/api")
app.include_router(file_collections.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(albums.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(appeal.router, prefix="/api")
app.include_router(gallery.router, prefix="/api")  # 公开画廊API
app.include_router(download.router, prefix="/api")  # 批量下载API
app.include_router(activation.router, prefix="/api") # 激活码API
app.include_router(payments.router, prefix="/api/payments")  # Stripe支付API
app.include_router(admin_router, prefix="/api")

# Dynamic image serving with status check (replaces static mount)
# This ensures rejected images cannot be accessed
from sqlalchemy.orm import selectinload
from datetime import datetime

@app.get("/uploads/{file_path:path}")
@app.get("/img/{file_path:path}")
async def serve_image(file_path: str):
    """
    动态图片/文件访问端点 - 检查文件状态后再返回
    被拒绝的图片返回替换图或 403
    """
    from app.services.settings import get_audit_violation_image

    # 安全检查：防止路径遍历攻击
    if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
        logger.warning(f"Path traversal attempt blocked: {file_path}")
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # 构建完整路径并验证它在 upload_path 内
    full_file_path = os.path.normpath(os.path.join(settings.upload_path, file_path))
    upload_path_normalized = os.path.normpath(settings.upload_path)
    
    if not full_file_path.startswith(upload_path_normalized):
        logger.warning(f"Path escape attempt blocked: {file_path} -> {full_file_path}")
        raise HTTPException(status_code=400, detail="Invalid path")

    async with AsyncSessionLocal() as db:
        # 1. First, check if it's an Image (common case)
        filename = file_path.split('/')[-1] if '/' in file_path else file_path
        if '.' in filename:
            name_part = filename.rsplit('.', 1)[0]
            result = await db.execute(
                select(Image).options(selectinload(Image.user)).where(Image.filename == name_part)
            )
            image = result.scalar_one_or_none()
            
            if image:
                # Handle Image Logic (Status check)
                status_str = str(image.status.value).lower() if hasattr(image.status, 'value') else str(image.status).lower()
                
                # Check rejection first
                if status_str == "rejected":
                    from app.services.settings import get_audit_violation_image
                    replacement_url = await get_audit_violation_image()
                    if replacement_url and replacement_url.strip():
                        return RedirectResponse(url=replacement_url.strip(), status_code=302)
                    raise HTTPException(status_code=403, detail="Image removed due to policy violation")
                
                cache_control = "public, max-age=31536000" if status_str == "approved" else "no-store, no-cache, must-revalidate, max-age=0"
                headers = {
                    "Cache-Control": cache_control,
                    "CDN-Cache-Control": cache_control,
                }

                # VIP Watermark Check
                if image.user and image.user.vip_expire_at and image.user.vip_expire_at > datetime.now() and image.user.watermark_enabled:
                    try:
                        from app.services.watermark import apply_watermark
                        from fastapi.responses import Response
                        import aiofiles
                        
                        # Apply watermark for cloud or local
                        content = None
                        if image.storage_type != "local":
                            # Download from cloud
                            import httpx
                            from app.services.storage import get_storage_backend_async
                            storage = await get_storage_backend_async()
                            cloud_url = storage.get_url(image.file_path, is_internal=True)
                            async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=15.0) as client:
                                resp = await client.get(cloud_url)
                                if resp.status_code == 200:
                                    content = resp.content
                        else:
                            # Read from local
                            if os.path.isfile(full_file_path):
                                async with aiofiles.open(full_file_path, 'rb') as f:
                                    content = await f.read()
                        
                        if content:
                            watermarked_content = apply_watermark(content, image.user)
                            return Response(
                                content=watermarked_content,
                                media_type=image.mime_type,
                                headers=headers
                            )
                    except Exception as e:
                        logger.error(f"Failed to apply VIP watermark for image {image.id}: {e}")

                # Default serving (Cloud or Local)
                if image.storage_type != "local":
                    try:
                        import httpx
                        from fastapi.responses import StreamingResponse
                        from app.services.storage import get_storage_backend_async
                        
                        storage = await get_storage_backend_async()
                        cloud_url = storage.get_url(image.file_path, is_internal=True)
                        
                        async def stream_cloud_image():
                            async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=15.0) as client:
                                try:
                                    async with client.stream("GET", cloud_url) as resp:
                                        if resp.status_code >= 400: return
                                        async for chunk in resp.aiter_bytes(): yield chunk
                                except Exception: return

                        return StreamingResponse(stream_cloud_image(), media_type=image.mime_type, headers=headers)
                    except Exception:
                        if image.storage_url: return RedirectResponse(url=image.storage_url, status_code=302)
                        raise HTTPException(status_code=502, detail="Failed to fetch image")

                # Local Fallback
                if not os.path.isfile(full_file_path):
                    raise HTTPException(status_code=404, detail="Image file not found")
                
                return FileResponse(full_file_path, media_type=image.mime_type, headers=headers)
        
        # 2. If not Image, check if it's a File (Video/File or its thumbnail)
        result = await db.execute(
            select(File).where(or_(File.file_path == file_path, File.thumbnail_path == file_path))
        )
        file_record = result.scalar_one_or_none()
        
        if file_record:
            # Files also support storage_url (though currently mostly local)
            # Add dynamic redirection here if needed later
            if not os.path.isfile(full_file_path):
                 raise HTTPException(status_code=404, detail="File not found")
            
            media_type = file_record.mime_type
            if file_path == file_record.thumbnail_path:
                media_type = "image/jpeg"
            
            return FileResponse(full_file_path, media_type=media_type, headers={
                "Cache-Control": "public, max-age=31536000",
            })

        # 3. If neither, deny access
        raise HTTPException(status_code=404, detail="Resource not found")


# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Public site settings (no auth required)
@app.get("/api/site/settings")
async def get_public_site_settings():
    """Get public site settings for frontend."""
    from app.services.settings import get_public_settings
    return await get_public_settings()


# Root redirect
@app.get("/api")
async def api_root():
    from app.services.settings import get_site_name
    site_name = await get_site_name()
    return {
        "name": site_name,
        "version": "1.0.0",
        "docs": "/api/docs",
    }


# Serve frontend static files (for Docker deployment)
# This should be mounted last to avoid conflicts with API routes
import os
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    from fastapi.responses import FileResponse
    
    # Serve static assets
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    # Serve index.html for SPA routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve frontend SPA for all non-API routes."""
        # Skip API routes
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        
        # Try to serve static file first
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fallback to index.html for SPA routing
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return JSONResponse(status_code=404, content={"detail": "Not found"})
