"""
System Settings Service
Provides centralized access to system settings from database.
Settings are cached and refreshed periodically.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from app.models.settings import SystemSettings
from app.database import AsyncSessionLocal
import logging
import asyncio

logger = logging.getLogger(__name__)

# In-memory cache for settings
_settings_cache: Dict[str, str] = {}
_cache_loaded = False
_cache_lock = asyncio.Lock()


# Default values (fallback if not in database)
DEFAULTS = {
    # General
    "general_site_name": "PicKoala",
    "general_site_title": "考拉云图 - 简洁优雅的图床服务",
    "general_site_description": "免费稳定的图片托管服务，支持多格式上传，全球CDN加速",
    "general_site_slogan": "简洁优雅的图床服务",
    "general_site_footer": "考拉云图 - 让图片分享更简单",
    "general_site_url": "http://localhost:3000",
    "general_site_logo": "",  # Logo URL, empty for text logo
    "general_site_logo_dark": "",  # Dark mode Logo URL
    "general_site_favicon": "",  # Favicon URL
    "general_timezone": "Asia/Shanghai",  # System timezone
    "general_enable_registration": "true",
    "general_enable_guest_upload": "true",
    
    # Customer Service
    "cs_mode": "off",  # off, crisp, custom
    "cs_crisp_id": "",
    "cs_custom_title": "联系客服",
    "cs_custom_qr": "",  # URL to QR image
    "cs_custom_desc": "扫描二维码或点击下方按钮联系我们",
    "cs_custom_link": "",
    "cs_custom_link_text": "联系我们",
    
    "cs_custom_link": "",
    "cs_custom_link_text": "联系我们",
    
    # Announcement
    "announcement_popup_enabled": "false",
    "announcement_popup_content": "",
    "announcement_navbar_enabled": "false",
    "announcement_navbar_content": "",
    
    # Upload
    "upload_max_size_guest": "5242880",  # 5MB
    "upload_max_size_user": "10485760",  # 10MB
    "upload_allowed_extensions": "png,jpg,jpeg,gif,webp",
    "upload_compression_quality": "85",
    "upload_max_dimension": "",
    
    # Upload - File
    "upload_file_max_size_guest": "52428800",  # 50MB
    "upload_file_max_size_user": "104857600",  # 100MB
    "upload_file_max_size_vip": "524288000",   # 500MB
    "upload_file_allowed_extensions": "zip,rar,7z,tar,gz,pdf,doc,docx,xls,xlsx,ppt,pptx,txt,md",

    # Upload - Video
    "upload_video_max_size_guest": "52428800",  # 50MB
    "upload_video_max_size_user": "524288000",  # 500MB
    "upload_video_max_size_vip": "2147483648",   # 2GB
    "upload_video_allowed_extensions": "mp4,webm,ogg,mov,avi,mkv",
    
    # Storage
    "storage_type": "local",
    # Local storage
    "storage_local_public_url": "",  # Custom CDN URL for local storage
    # S3-Compatible Storage (unified)
    "storage_s3c_provider": "custom",
    "storage_s3c_access_key_id": "",
    "storage_s3c_secret_access_key": "",
    "storage_s3c_bucket_name": "",
    "storage_s3c_endpoint_url": "",
    "storage_s3c_region": "",
    "storage_s3c_public_url": "",
    # Aliyun OSS (native SDK)
    "storage_oss_access_key_id": "",
    "storage_oss_access_key_secret": "",
    "storage_oss_bucket_name": "",
    "storage_oss_endpoint": "",
    # Tencent COS (native SDK)
    "storage_cos_secret_id": "",
    "storage_cos_secret_key": "",
    "storage_cos_bucket_name": "",
    "storage_cos_region": "",
    "storage_cos_public_url": "",
    # Legacy (for backward compatibility)
    "storage_r2_access_key_id": "",
    "storage_r2_secret_access_key": "",
    "storage_r2_bucket_name": "",
    "storage_r2_endpoint": "",
    "storage_r2_public_url": "",
    "storage_s3_access_key_id": "",
    "storage_s3_secret_access_key": "",
    "storage_s3_bucket_name": "",
    "storage_s3_region": "",
    
    # Security - Rate Limits
    "security_rate_limit_guest_per_minute": "3",
    "security_rate_limit_user_per_minute": "10",
    "security_rate_limit_guest_per_hour": "10",
    "security_rate_limit_user_per_hour": "100",
    "security_rate_limit_guest_per_day": "30",
    "security_rate_limit_user_per_day": "500",
    "security_rate_limit_vip_per_minute": "30",
    "security_rate_limit_vip_per_hour": "300",
    "security_rate_limit_vip_per_day": "2000",
    
    # Security - File Rate Limits
    "security_rate_limit_guest_file_per_minute": "1",
    "security_rate_limit_user_file_per_minute": "5",
    "security_rate_limit_vip_file_per_minute": "10",
    "security_rate_limit_guest_file_per_hour": "3",
    "security_rate_limit_user_file_per_hour": "20",
    "security_rate_limit_vip_file_per_hour": "50",
    "security_rate_limit_guest_file_per_day": "10",
    "security_rate_limit_user_file_per_day": "50",
    "security_rate_limit_vip_file_per_day": "200",
    
    # Security - Video Rate Limits
    "security_rate_limit_guest_video_per_minute": "1",
    "security_rate_limit_user_video_per_minute": "3",
    "security_rate_limit_vip_video_per_minute": "10",
    "security_rate_limit_guest_video_per_hour": "5",
    "security_rate_limit_user_video_per_hour": "20",
    "security_rate_limit_vip_video_per_hour": "50",
    "security_rate_limit_guest_video_per_day": "10",
    "security_rate_limit_user_video_per_day": "50",
    "security_rate_limit_vip_video_per_day": "200",
    
    # Security - Auto Ban
    "security_auto_ban_enabled": "true",
    "security_audit_fail_threshold": "3",
    "security_rate_exceed_threshold": "3",
    "security_temp_ban_duration": "1440",  # 24 hours in minutes
    "security_rate_limit_login_attempts": "5",
    # Security - IP Detection
    "security_real_ip_header": "X-Forwarded-For",  # X-Forwarded-For, X-Real-IP, CF-Connecting-IP
    "security_trust_proxy": "true",
    
    # Audit
    "audit_enabled": "false",
    "audit_provider": "",
    "audit_api_key": "",
    "audit_api_secret": "",
    "audit_auto_reject": "false",
    "audit_violation_image": "",  # URL of replacement image for rejected images
    
    # Email
    "email_enabled": "false",
    "email_smtp_host": "",
    "email_smtp_port": "587",
    "email_smtp_user": "",
    "email_smtp_password": "",
    "email_smtp_ssl": "false",
    "email_from_address": "",
    "email_from_name": "PicKoala",
    "email_template_verify_subject": "[{{site_name}}] 验证您的邮箱",
    "email_template_verify_body": """<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;"><div style="max-width: 600px; margin: 0 auto; padding: 20px;"><h2 style="color: #2c3e50;">欢迎加入 {{site_name}}！</h2><p>您好，{{username}}！</p><p>感谢您的注册。请点击下方按钮验证您的邮箱地址：</p><div style="text-align: center; margin: 30px 0;"><a href="{{verify_url}}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">验证邮箱</a></div><p>或者复制以下链接到浏览器：</p><p style="background: #f5f5f5; padding: 10px; word-break: break-all;">{{verify_url}}</p><p style="color: #7f8c8d; font-size: 12px;">此链接将在24小时后失效。如果您没有注册账号，请忽略此邮件。</p><hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;"><p style="color: #95a5a6; font-size: 12px;">此邮件由系统自动发送，请勿回复。</p></div></body></html>""",
    "email_template_reset_subject": "[{{site_name}}] 重置密码",
    "email_template_reset_body": """<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;"><div style="max-width: 600px; margin: 0 auto; padding: 20px;"><h2 style="color: #2c3e50;">重置密码</h2><p>您好，{{username}}！</p><p>我们收到了重置您账号密码的请求。请点击下方按钮重置密码：</p><div style="text-align: center; margin: 30px 0;"><a href="{{reset_url}}" style="background-color: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">重置密码</a></div><p>或者复制以下链接到浏览器：</p><p style="background: #f5f5f5; padding: 10px; word-break: break-all;">{{reset_url}}</p><p style="color: #7f8c8d; font-size: 12px;">此链接将在1小时后失效。如果您没有请求重置密码，请忽略此邮件。</p><hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;"><p style="color: #95a5a6; font-size: 12px;">此邮件由系统自动发送，请勿回复。</p></div></body></html>""",
    
    # Payment Settings (Stripe)
    "payment_stripe_enabled": "false",
    "payment_stripe_secret_key": "",
    "payment_stripe_webhook_secret": "",
    "payment_stripe_price_id": "",
    "payment_stripe_currency": "HKD",
    
    # Payment Settings (Alipay)
    "payment_alipay_enabled": "false",
    "payment_alipay_app_id": "",
    "payment_alipay_private_key": "",
    "payment_alipay_public_key": "",

    # Payment Settings (Epay)
    "payment_epay_enabled": "false",
    "payment_epay_api_url": "",
    "payment_epay_partner_id": "",
    "payment_epay_partner_key": "",
    "payment_epay_name": "易支付",
    "payment_epay_logo_url": "",

    # OAuth - Google
    "oauth_google_enabled": "false",
    "oauth_google_client_id": "",
    "oauth_google_client_secret": "",
    
    # OAuth - Linux.do
    "oauth_linuxdo_enabled": "false",
    "oauth_linuxdo_client_id": "",
    "oauth_linuxdo_client_secret": "",
    
    # OAuth - GitHub
    "oauth_github_enabled": "false",
    "oauth_github_client_id": "",
    "oauth_github_client_secret": "",

    # VIP Plans
    "payment_vip_month_enabled": "true",
    "payment_vip_month_price": "9.99",
    "payment_vip_month_stripe_id": "",
    
    "payment_vip_quarter_enabled": "false",
    "payment_vip_quarter_price": "29.99",
    "payment_vip_quarter_stripe_id": "",
    
    "payment_vip_year_enabled": "true",
    "payment_vip_year_price": "99.99",
    "payment_vip_year_stripe_id": "",
    
    "payment_vip_forever_enabled": "false",
    "payment_vip_forever_price": "2999.99",
    "payment_vip_forever_stripe_id": "",

    # Homepage Text (Dynamic JSON)
    "home_features": '[{"zh": "全球 CDN 加速", "en": "Global CDN", "zh-TW": "全球 CDN 加速"}, {"zh": "三地异地备份", "en": "Geo-redundant Backup", "zh-TW": "三地異地備份"}, {"zh": "永久免费存储", "en": "Permanent Free Storage", "zh-TW": "永久免費存儲"}]',
    "home_table_cols": '{"col_guest": {"zh": "游客", "en": "Guest", "zh-TW": "遊客"}, "col_user": {"zh": "会员", "en": "Member", "zh-TW": "會員"}, "col_vip": {"zh": "VIP", "en": "VIP", "zh-TW": "VIP"}}',
    "home_table_rows": '{"row_single_file": {"zh": "单文件", "en": "Single File", "zh-TW": "單文件"}, "row_frequency": {"zh": "频率", "en": "Frequency", "zh-TW": "頻率"}, "row_album": {"zh": "创建相册", "en": "Create Album", "zh-TW": "創建相冊"}, "row_naming": {"zh": "单图命名", "en": "Image Naming", "zh-TW": "單圖命名"}, "row_management": {"zh": "图片管理", "en": "Image Management", "zh-TW": "圖片管理"}}',
    
    # Cloudflare Settings
    "cf_purge_enabled": "false",
    "cf_api_token": "",
    "cf_api_token": "",
    "cf_zone_id": "",
    
    # AI Settings
    "ai_gemini_api_keys": "",  # Comma-separated list of keys
    "ai_analysis_enabled": "false",
}


async def load_settings_to_cache():
    """Load all settings from database to cache."""
    global _settings_cache, _cache_loaded
    
    async with _cache_lock:
        # Double-check if loaded while waiting for lock
        if _cache_loaded:
            return

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(SystemSettings))
                settings = result.scalars().all()
                
                # Start with defaults
                _settings_cache = DEFAULTS.copy()
                
                # Override with database values
                for setting in settings:
                    _settings_cache[setting.key] = setting.value or ""
                
                _cache_loaded = True
                logger.info(f"Loaded {len(settings)} settings from database")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            _settings_cache = DEFAULTS.copy()
            _cache_loaded = True


async def get_setting(key: str, default: str = "") -> str:
    """Get a single setting value."""
    global _cache_loaded
    
    if not _cache_loaded:
        await load_settings_to_cache()
    
    return _settings_cache.get(key, DEFAULTS.get(key, default))


async def get_setting_int(key: str, default: int = 0) -> int:
    """Get a setting as integer."""
    value = await get_setting(key, str(default))
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


async def get_setting_bool(key: str, default: bool = False) -> bool:
    """Get a setting as boolean."""
    value = await get_setting(key, str(default).lower())
    return value.lower() in ("true", "1", "yes", "on")


async def get_setting_list(key: str, default: str = "") -> list:
    """Get a setting as list (comma-separated)."""
    value = await get_setting(key, default)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


async def set_setting(key: str, value: str, db: AsyncSession):
    """Set a setting value in database and update cache."""
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == key))
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = value
    else:
        # Determine category from key
        category = key.split("_")[0] if "_" in key else "general"
        setting = SystemSettings(
            key=key,
            value=value,
            category=category,
            description=DEFAULTS.get(key, ""),
        )
        db.add(setting)
    
    await db.commit()
    
    # Update cache
    _settings_cache[key] = value
    
    # 如果是IP相关设置，刷新IP头缓存
    if key in ("security_real_ip_header", "security_trust_proxy"):
        try:
            from app.utils.rate_limit import refresh_ip_header_settings
            await refresh_ip_header_settings()
        except Exception as e:
            logger.warning(f"Failed to refresh IP header settings: {e}")
    
    # 如果是时区设置，刷新时区缓存
    if key == "general_timezone":
        try:
            from app.utils.timezone import refresh_timezone_cache
            refresh_timezone_cache()
            logger.info(f"Timezone cache refreshed for: {value}")
        except Exception as e:
            logger.warning(f"Failed to refresh timezone cache: {e}")


async def refresh_cache():
    """Force refresh the settings cache."""
    global _cache_loaded
    _cache_loaded = False
    await load_settings_to_cache()


def invalidate_cache():
    """Mark cache as invalid (will reload on next access)."""
    global _cache_loaded
    _cache_loaded = False


# Convenience functions for common settings
async def get_site_name() -> str:
    return await get_setting("general_site_name", "PicKoala")


async def get_site_title() -> str:
    return await get_setting("general_site_title", "考拉云图 - 简洁优雅的图床服务")


async def get_site_description() -> str:
    return await get_setting("general_site_description", "免费稳定的图片托管服务")


async def get_site_slogan() -> str:
    return await get_setting("general_site_slogan", "简洁优雅的图床服务")


async def get_site_footer() -> str:
    return await get_setting("general_site_footer", "考拉云图 - 让图片分享更简单")


async def get_site_logo() -> str:
    return await get_setting("general_site_logo", "")


async def get_site_logo_dark() -> str:
    return await get_setting("general_site_logo_dark", "")


async def get_site_favicon() -> str:
    return await get_setting("general_site_favicon", "")


async def get_site_url() -> str:
    return await get_setting("general_site_url", "http://localhost:3000")


async def get_timezone() -> str:
    return await get_setting("general_timezone", "Asia/Shanghai")


async def get_max_upload_size_guest() -> int:
    return await get_setting_int("upload_max_size_guest", 5242880)


async def get_max_upload_size_user() -> int:
    return await get_setting_int("upload_max_size_user", 10485760)


async def get_max_upload_size_vip() -> int:
    return await get_setting_int("upload_max_size_vip", 52428800)


async def get_allowed_extensions() -> list:
    return await get_setting_list("upload_allowed_extensions", "png,jpg,jpeg,gif,webp")


async def get_compression_quality() -> int:
    return await get_setting_int("upload_compression_quality", 85)


async def get_max_file_upload_size_guest() -> int:
    return await get_setting_int("upload_file_max_size_guest", 52428800)


async def get_max_file_upload_size_user() -> int:
    return await get_setting_int("upload_file_max_size_user", 104857600)


async def get_max_file_upload_size_vip() -> int:
    return await get_setting_int("upload_file_max_size_vip", 524288000)


async def get_file_allowed_extensions() -> list:
    return await get_setting_list("upload_file_allowed_extensions", "zip,rar,7z,tar,gz,pdf,doc,docx,xls,xlsx,ppt,pptx,txt,md")


async def get_max_video_upload_size_guest() -> int:
    return await get_setting_int("upload_video_max_size_guest", 52428800)


async def get_max_video_upload_size_user() -> int:
    return await get_setting_int("upload_video_max_size_user", 524288000)


async def get_max_video_upload_size_vip() -> int:
    return await get_setting_int("upload_video_max_size_vip", 2147483648)


async def get_video_allowed_extensions() -> list:
    return await get_setting_list("upload_video_allowed_extensions", "mp4,webm,ogg,mov,avi,mkv")


async def get_storage_type() -> str:
    return await get_setting("storage_type", "local")


async def get_guest_upload_limit_per_hour() -> int:
    """Get guest upload limit per hour."""
    return await get_setting_int("security_rate_limit_guest_per_hour", 10)


async def get_user_upload_limit_per_hour() -> int:
    """Get user upload limit per hour."""
    return await get_setting_int("security_rate_limit_user_per_hour", 100)


async def get_guest_upload_limit_per_minute() -> int:
    """Get guest upload limit per minute."""
    return await get_setting_int("security_rate_limit_guest_per_minute", 3)


async def get_user_upload_limit_per_minute() -> int:
    """Get user upload limit per minute."""
    return await get_setting_int("security_rate_limit_user_per_minute", 10)


async def get_guest_upload_limit_per_day() -> int:
    """Get guest upload limit per day."""
    return await get_setting_int("security_rate_limit_guest_per_day", 30)


async def get_user_upload_limit_per_day() -> int:
    """Get user upload limit per day."""
    return await get_setting_int("security_rate_limit_user_per_day", 500)


async def get_vip_upload_limit_per_minute() -> int:
    """Get VIP upload limit per minute."""
    return await get_setting_int("security_rate_limit_vip_per_minute", 30)


async def get_vip_upload_limit_per_hour() -> int:
    """Get VIP upload limit per hour."""
    return await get_setting_int("security_rate_limit_vip_per_hour", 300)


async def get_vip_upload_limit_per_day() -> int:
    """Get VIP upload limit per day."""
    return await get_setting_int("security_rate_limit_vip_per_day", 2000)


# File Rate Limits
async def get_guest_file_limit_per_minute() -> int:
    return await get_setting_int("security_rate_limit_guest_file_per_minute", 1)

async def get_user_file_limit_per_minute() -> int:
    return await get_setting_int("security_rate_limit_user_file_per_minute", 5)

async def get_vip_file_limit_per_minute() -> int:
    return await get_setting_int("security_rate_limit_vip_file_per_minute", 10)

async def get_guest_file_limit_per_hour() -> int:
    return await get_setting_int("security_rate_limit_guest_file_per_hour", 3)

async def get_user_file_limit_per_hour() -> int:
    return await get_setting_int("security_rate_limit_user_file_per_hour", 20)

async def get_vip_file_limit_per_hour() -> int:
    return await get_setting_int("security_rate_limit_vip_file_per_hour", 50)

async def get_guest_file_limit_per_day() -> int:
    return await get_setting_int("security_rate_limit_guest_file_per_day", 10)

async def get_user_file_limit_per_day() -> int:
    return await get_setting_int("security_rate_limit_user_file_per_day", 50)

async def get_vip_file_limit_per_day() -> int:
    return await get_setting_int("security_rate_limit_vip_file_per_day", 200)


# Video Rate Limits
async def get_guest_video_limit_per_minute() -> int:
    return await get_setting_int("security_rate_limit_guest_video_per_minute", 1)

async def get_user_video_limit_per_minute() -> int:
    return await get_setting_int("security_rate_limit_user_video_per_minute", 3)

async def get_vip_video_limit_per_minute() -> int:
    return await get_setting_int("security_rate_limit_vip_video_per_minute", 10)

async def get_guest_video_limit_per_hour() -> int:
    return await get_setting_int("security_rate_limit_guest_video_per_hour", 5)

async def get_user_video_limit_per_hour() -> int:
    return await get_setting_int("security_rate_limit_user_video_per_hour", 20)

async def get_vip_video_limit_per_hour() -> int:
    return await get_setting_int("security_rate_limit_vip_video_per_hour", 50)

async def get_guest_video_limit_per_day() -> int:
    return await get_setting_int("security_rate_limit_guest_video_per_day", 10)

async def get_user_video_limit_per_day() -> int:
    return await get_setting_int("security_rate_limit_user_video_per_day", 50)

async def get_vip_video_limit_per_day() -> int:
    return await get_setting_int("security_rate_limit_vip_video_per_day", 200)


async def get_real_ip_header() -> str:
    """Get the header name for real IP detection."""
    return await get_setting("security_real_ip_header", "X-Forwarded-For")


async def is_trust_proxy_enabled() -> bool:
    """Check if proxy headers should be trusted."""
    return await get_setting_bool("security_trust_proxy", True)


async def is_registration_enabled() -> bool:
    return await get_setting_bool("general_enable_registration", True)


async def is_guest_upload_enabled() -> bool:
    return await get_setting_bool("general_enable_guest_upload", True)


async def is_audit_enabled() -> bool:
    return await get_setting_bool("audit_enabled", False)


async def get_audit_provider() -> str:
    return await get_setting("audit_provider", "")


async def get_audit_api_key() -> str:
    return await get_setting("audit_api_key", "")


async def get_audit_api_secret() -> str:
    return await get_setting("audit_api_secret", "")


async def is_audit_auto_reject() -> bool:
    return await get_setting_bool("audit_auto_reject", False)


async def get_audit_violation_image() -> str:
    """Get the URL of the replacement image for rejected images.
    Uses cache for performance.
    """
    return await get_setting("audit_violation_image", "")


# Email settings
async def is_email_enabled() -> bool:
    return await get_setting_bool("email_enabled", False)


async def get_smtp_host() -> str:
    return await get_setting("email_smtp_host", "")


async def get_smtp_port() -> int:
    return await get_setting_int("email_smtp_port", 587)


async def get_smtp_user() -> str:
    return await get_setting("email_smtp_user", "")


async def get_smtp_password() -> str:
    return await get_setting("email_smtp_password", "")


async def is_smtp_ssl() -> bool:
    return await get_setting_bool("email_smtp_ssl", False)


async def get_email_from_address() -> str:
    return await get_setting("email_from_address", "")


async def get_email_from_name() -> str:
    return await get_setting("email_from_name", "PicKoala")


async def get_email_template(template_type: str) -> tuple:
    """Get email template subject and body by type (verify, reset)."""
    subject = await get_setting(f"email_template_{template_type}_subject", "")
    body = await get_setting(f"email_template_{template_type}_body", "")
    return subject, body


# Payment settings
async def is_stripe_enabled() -> bool:
    return await get_setting_bool("payment_stripe_enabled", False)


async def get_stripe_secret_key() -> str:
    return await get_setting("payment_stripe_secret_key", "")


async def get_stripe_webhook_secret() -> str:
    return await get_setting("payment_stripe_webhook_secret", "")


async def get_stripe_price_id() -> str:
    return await get_setting("payment_stripe_price_id", "")



async def get_stripe_currency() -> str:
    return await get_setting("payment_stripe_currency", "HKD")


# Alipay settings
async def is_alipay_enabled() -> bool:
    return await get_setting_bool("payment_alipay_enabled", False)


async def get_alipay_app_id() -> str:
    return await get_setting("payment_alipay_app_id", "")


async def get_alipay_private_key() -> str:
    return await get_setting("payment_alipay_private_key", "")


async def get_alipay_public_key() -> str:
    return await get_setting("payment_alipay_public_key", "")



# VIP Plans
async def get_vip_plans() -> dict:
    """Get VIP plans configuration."""
    plans = {}
    for plan in ["month", "quarter", "year", "forever"]:
        # Use payment_ prefix
        enabled = await get_setting_bool(f"payment_vip_{plan}_enabled", False)
        
        plans[plan] = {
             "enabled": enabled,
             "price": await get_setting(f"payment_vip_{plan}_price", ""),
             "stripe_id": await get_setting(f"payment_vip_{plan}_stripe_id", ""),
        }
    return plans

# AI Settings
async def get_gemini_api_keys() -> str:
    return await get_setting("ai_gemini_api_keys", "")


# Get all public settings (for frontend)
async def get_public_settings() -> dict:
    """Get settings that can be exposed to frontend."""
    # Ensure cache is loaded first to minimize lock contention during multiple lookups
    if not _cache_loaded:
        await load_settings_to_cache()
        
    return {
        "site_name": await get_site_name(),
        "site_title": await get_site_title(),
        "site_description": await get_site_description(),
        "site_slogan": await get_site_slogan(),
        "site_footer": await get_site_footer(),
        "site_logo": await get_site_logo(),
        "site_logo_dark": await get_site_logo_dark(),
        "site_favicon": await get_site_favicon(),
        "timezone": await get_timezone(),
        "max_upload_size_guest": await get_max_upload_size_guest(),
        "max_upload_size_user": await get_max_upload_size_user(),
        "max_upload_size_vip": await get_max_upload_size_vip(),
        "allowed_extensions": await get_allowed_extensions(),
        "max_file_upload_size_guest": await get_max_file_upload_size_guest(),
        "max_file_upload_size_user": await get_max_file_upload_size_user(),
        "max_file_upload_size_vip": await get_max_file_upload_size_vip(),
        "file_allowed_extensions": await get_file_allowed_extensions(),
        "max_video_upload_size_guest": await get_max_video_upload_size_guest(),
        "max_video_upload_size_user": await get_max_video_upload_size_user(),
        "max_video_upload_size_vip": await get_max_video_upload_size_vip(),
        "video_allowed_extensions": await get_video_allowed_extensions(),
        "enable_registration": await is_registration_enabled(),
        "enable_guest_upload": await is_guest_upload_enabled(),
        
        # Customer Service
        "cs_mode": await get_setting("cs_mode", "off"),
        "cs_crisp_id": await get_setting("cs_crisp_id", ""),
        "cs_custom_title": await get_setting("cs_custom_title", "联系客服"),
        "cs_custom_qr": await get_setting("cs_custom_qr", ""),
        "cs_custom_desc": await get_setting("cs_custom_desc", ""),
        "cs_custom_link": await get_setting("cs_custom_link", ""),
        "cs_custom_link_text": await get_setting("cs_custom_link_text", "联系我们"),
        # Rate limits - per minute/hour/day
        "guest_rate_limit_per_minute": await get_guest_upload_limit_per_minute(),
        "guest_rate_limit_per_hour": await get_guest_upload_limit_per_hour(),
        "guest_rate_limit_per_day": await get_guest_upload_limit_per_day(),
        "user_rate_limit_per_minute": await get_user_upload_limit_per_minute(),
        "user_rate_limit_per_hour": await get_user_upload_limit_per_hour(),
        "user_rate_limit_per_day": await get_user_upload_limit_per_day(),
        "vip_rate_limit_per_minute": await get_vip_upload_limit_per_minute(),
        "vip_rate_limit_per_hour": await get_vip_upload_limit_per_hour(),
        "vip_rate_limit_per_day": await get_vip_upload_limit_per_day(),
        
        # File Rate Limits
        "guest_file_limit_per_minute": await get_guest_file_limit_per_minute(),
        "guest_file_limit_per_hour": await get_guest_file_limit_per_hour(),
        "guest_file_limit_per_day": await get_guest_file_limit_per_day(),
        "user_file_limit_per_minute": await get_user_file_limit_per_minute(),
        "user_file_limit_per_hour": await get_user_file_limit_per_hour(),
        "user_file_limit_per_day": await get_user_file_limit_per_day(),
        "vip_file_limit_per_minute": await get_vip_file_limit_per_minute(),
        "vip_file_limit_per_hour": await get_vip_file_limit_per_hour(),
        "vip_file_limit_per_day": await get_vip_file_limit_per_day(),
        
        # Video Rate Limits
        "guest_video_limit_per_minute": await get_guest_video_limit_per_minute(),
        "guest_video_limit_per_hour": await get_guest_video_limit_per_hour(),
        "guest_video_limit_per_day": await get_guest_video_limit_per_day(),
        "user_video_limit_per_minute": await get_user_video_limit_per_minute(),
        "user_video_limit_per_hour": await get_user_video_limit_per_hour(),
        "user_video_limit_per_day": await get_user_video_limit_per_day(),
        "vip_video_limit_per_minute": await get_vip_video_limit_per_minute(),
        "vip_video_limit_per_hour": await get_vip_video_limit_per_hour(),
        "vip_video_limit_per_day": await get_vip_video_limit_per_day(),
        
        # Payment Status
        "payment_stripe_enabled": await is_stripe_enabled(),
        "payment_alipay_enabled": await is_alipay_enabled(),
        "payment_epay_enabled": await get_setting_bool("payment_epay_enabled", False),
        "payment_epay_name": await get_setting("payment_epay_name", "易支付"),
        "payment_epay_logo_url": await get_setting("payment_epay_logo_url", ""),
        
        # Casdoor Status
        
        # Direct OAuth Status
        "oauth_google_enabled": await get_setting_bool("oauth_google_enabled", False),
        "oauth_google_client_id": await get_setting("oauth_google_client_id", ""),
        "oauth_linuxdo_enabled": await get_setting_bool("oauth_linuxdo_enabled", False),
        "oauth_linuxdo_client_id": await get_setting("oauth_linuxdo_client_id", ""),
        "oauth_github_enabled": await get_setting_bool("oauth_github_enabled", False),
        "oauth_github_client_id": await get_setting("oauth_github_client_id", ""),
        
        
        # Announcement
        "announcement_popup_enabled": await get_setting_bool("announcement_popup_enabled", False),
        "announcement_popup_content": await get_setting("announcement_popup_content", ""),
        "announcement_navbar_enabled": await get_setting_bool("announcement_navbar_enabled", False),
        "announcement_navbar_content": await get_setting("announcement_navbar_content", ""),
        
        # VIP Plans
        "vip_plans": await get_vip_plans(),
        
        # Homepage Text
        "home_features": await get_setting("home_features", "[]"),
        "home_table_cols": await get_setting("home_table_cols", "{}"),
        "home_table_rows": await get_setting("home_table_rows", "{}"),
    }
async def is_ai_analysis_enabled() -> bool:
    val = await get_setting("ai_analysis_enabled", "false")
    return val.lower() == "true"
