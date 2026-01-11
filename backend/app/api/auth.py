from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import logging
import re
from app.database import get_db
from app.models.user import User, UserStatus, UserRole
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse, 
    PasswordReset, PasswordResetConfirm, RESERVED_USERNAMES
)
from app.utils.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_token,
    generate_verification_token
)
from app.utils.rate_limit import (
    get_real_ip, 
    check_login_attempts, 
    record_failed_login, 
    clear_login_attempts,
    check_rate_limit
)
from app.utils.captcha import create_captcha_redis, verify_captcha_redis
from app.services.email import send_verification_email, send_password_reset_email
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()
logger = logging.getLogger(__name__)

# OAuth 2.0 Helpers & Endpoints

class OAuthCallbackSchema(BaseModel):
    code: str
    state: str = None
    redirect_url: str

@router.get("/oauth/url/{provider}")
async def get_oauth_url(provider: str, redirect_url: str):
    """Generate OAuth authorization URL for the given provider."""
    from app.services.settings import get_setting_bool, get_setting
    from urllib.parse import urlencode
    
    if provider == "google":
        if not await get_setting_bool("oauth_google_enabled"):
            raise HTTPException(status_code=403, detail="Google login is disabled")
        client_id = await get_setting("oauth_google_client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Google Client ID not configured")
        
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_url,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account"
        }
    elif provider == "linuxdo":
        if not await get_setting_bool("oauth_linuxdo_enabled"):
            raise HTTPException(status_code=403, detail="Linux.do login is disabled")
        client_id = await get_setting("oauth_linuxdo_client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Linux.do Client ID not configured")
            
        auth_url = "https://connect.linux.do/oauth2/authorize"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_url,
            "response_type": "code",
            "scope": "openid email",
        }
    elif provider == "github":
        if not await get_setting_bool("oauth_github_enabled"):
            raise HTTPException(status_code=403, detail="GitHub login is disabled")
        client_id = await get_setting("oauth_github_client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="GitHub Client ID not configured")
            
        auth_url = "https://github.com/login/oauth/authorize"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_url,
            "scope": "read:user user:email",
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    return {"url": f"{auth_url}?{urlencode(params)}"}


@router.post("/oauth/callback/{provider}", response_model=TokenResponse)
async def oauth_callback(
    provider: str,
    data: OAuthCallbackSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle OAuth 2.0 callback and perform login/registration."""
    import httpx
    from app.services.settings import get_setting, get_setting_bool
    
    ip = get_real_ip(request)
    
    # 1. Configuration Check
    if provider == "google":
        if not await get_setting_bool("oauth_google_enabled"):
            raise HTTPException(status_code=403, detail="Google login is disabled")
        client_id = await get_setting("oauth_google_client_id")
        client_secret = await get_setting("oauth_google_client_secret")
        token_url = "https://oauth2.googleapis.com/token"
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    elif provider == "linuxdo":
        if not await get_setting_bool("oauth_linuxdo_enabled"):
            raise HTTPException(status_code=403, detail="Linux.do login is disabled")
        client_id = await get_setting("oauth_linuxdo_client_id")
        client_secret = await get_setting("oauth_linuxdo_client_secret")
        token_url = "https://connect.linux.do/oauth2/token"
        userinfo_url = "https://connect.linux.do/api/user"
    elif provider == "github":
        if not await get_setting_bool("oauth_github_enabled"):
            raise HTTPException(status_code=403, detail="GitHub login is disabled")
        client_id = await get_setting("oauth_github_client_id")
        client_secret = await get_setting("oauth_github_client_secret")
        token_url = "https://github.com/login/oauth/access_token"
        userinfo_url = "https://api.github.com/user"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail=f"{provider.capitalize()} OAuth credentials not configured")

    # 2. Exchange Code for Token
    async with httpx.AsyncClient() as client:
        try:
            token_res = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": data.code,
                    "redirect_uri": data.redirect_url,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Accept": "application/json"},
                timeout=10.0
            )
            if token_res.status_code != 200:
                logger.error(f"{provider} token exchange failed: {token_res.text}")
                raise HTTPException(status_code=400, detail=f"Failed to exchange token: {token_res.text}")
            
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Token response missing access_token")

            # 3. Get User Info
            user_res = await client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            if user_res.status_code != 200:
                logger.error(f"{provider} userinfo request failed: {user_res.text}")
                raise HTTPException(status_code=400, detail="Failed to fetch user information")
            
            user_info = user_res.json()
        except httpx.RequestError as e:
            logger.error(f"HTTP error during OAuth flow with {provider}: {e}")
            raise HTTPException(status_code=502, detail=f"OAuth service communication error")

    # 4. Extract User Data
    # Normalizing user info across providers
    external_id = None
    email = None
    username = None

    if provider == "google":
        external_id = user_info.get("sub")
        email = user_info.get("email")
        username = user_info.get("name") or email.split('@')[0] if email else None
    elif provider == "linuxdo":
        # Adjust these keys based on Linux.do API response
        external_id = str(user_info.get("id"))
        email = user_info.get("email")
        username = user_info.get("username") or user_info.get("name") or (email.split('@')[0] if email else None)
    elif provider == "github":
        external_id = str(user_info.get("id"))
        email = user_info.get("email")
        username = user_info.get("login") or user_info.get("name") or (email.split('@')[0] if email else None)
        
        # GitHub might not return email if it's private, we might need to fetch it separately
        if not email:
            try:
                emails_res = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=5.0
                )
                if emails_res.status_code == 200:
                    emails = emails_res.json()
                    primary_email = next((e["email"] for e in emails if e["primary"]), None)
                    email = primary_email or (emails[0]["email"] if emails else None)
            except Exception as e:
                logger.warning(f"Failed to fetch GitHub emails: {e}")

    if not external_id:
        logger.error(f"Could not extract unique user ID from {provider} UserInfo: {user_info}")
        raise HTTPException(status_code=400, detail=f"Failed to identify user from {provider}")

    # Prefixed external_id to avoid collisions between providers
    full_external_id = f"{provider}:{external_id}"

    # 5. Find or Create User
    # We use oauth_id column as a generic external_id
    result = await db.execute(select(User).where(User.oauth_id == full_external_id))
    user = result.scalar_one_or_none()
    
    if not user and email:
        # Try to link by email if external_id not found
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.oauth_id = full_external_id # Link existing account
    
    if not user:
        # Create new user
        if not username:
            username = f"{provider}_{external_id[:8]}"
            
        # Check for username collision
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            username = f"{username}_{str(uuid.uuid4())[:4]}"
            
        user = User(
            username=username,
            email=email or f"{external_id}@{provider}.local",
            oauth_id=full_external_id,
            hashed_password=f"OAUTH_{provider.upper()}_MANAGED", # Standard login disabled
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            email_verified=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"New user created via {provider} OAuth: {user.username}")
    else:
        # Update last login info
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip
        if user.status == UserStatus.PENDING:
            user.status = UserStatus.ACTIVE
            user.email_verified = True
        await db.commit()

    # 6. Generate JWT Tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # 7. Audit Log
    try:
        from app.api.admin.audit import create_audit_log
        await create_audit_log(
            db=db,
            action=f"login_{provider}",
            ip_address=ip,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            user_agent=request.headers.get("User-Agent"),
            details=f"User {user.username} logged in via {provider}",
            log_status="success"
        )
    except Exception as e:
        logger.error(f"Failed to create audit log for OAuth login: {e}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


# Regex patterns
USERNAME_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


# Extended schemas with captcha
class UserCreateWithCaptcha(BaseModel):
    username: str
    email: str
    password: str
    captcha_id: str
    captcha_code: str


class PasswordResetWithCaptcha(BaseModel):
    email: str
    captcha_id: str
    captcha_code: str


@router.get("/captcha")
async def get_captcha():
    """Generate a new captcha image."""
    captcha_id = str(uuid.uuid4())
    _, image_data = await create_captcha_redis(captcha_id)
    return {"captcha_id": captcha_id, "image": image_data}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateWithCaptcha,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user with captcha verification."""
    from app.services.settings import is_registration_enabled
    
    ip = get_real_ip(request)
    
    # Rate limit: max 5 registrations per IP per hour
    is_allowed, count, remaining = await check_rate_limit(f"register:{ip}", 5, 3600)
    if not is_allowed:
        logger.warning(f"Registration rate limit exceeded for IP {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="注册请求过于频繁，请稍后再试"
        )
    
    # Verify captcha FIRST (before any other validation)
    if not await verify_captcha_redis(user_data.captcha_id, user_data.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # Check if registration is enabled
    from app.services.settings import is_registration_enabled, get_setting
    if not await is_registration_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently disabled"
        )
        
    
    if not await is_registration_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently disabled"
        )
    
    # Input validation - username
    if not user_data.username or len(user_data.username) < 3 or len(user_data.username) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度必须在3-20个字符之间"
        )
    
    if not USERNAME_REGEX.match(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名只能包含字母、数字和下划线，且必须以字母开头"
        )

    # Check reserved usernames
    if user_data.username.lower() in RESERVED_USERNAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名被系统保留，无法使用"
        )
        
    # Check forbidden prefixes
    if user_data.username.lower().startswith(('admin', 'system', 'root')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名包含非法关键词"
        )
    
    # Input validation - email
    if not EMAIL_REGEX.match(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入有效的邮箱地址"
        )
    
    # Input validation - password strength
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少8位"
        )
    if not re.search(r'[a-z]', user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含小写字母"
        )
    if not re.search(r'[A-Z]', user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含大写字母"
        )
    if not re.search(r'\d', user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含数字"
        )
    
    # Check if username or email already exists
    result = await db.execute(
        select(User).where(
            or_(
                User.username == user_data.username,
                User.email == user_data.email.lower()
            )
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification token
    verify_token = generate_verification_token()
    verify_token_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email.lower(),  # Normalize email to lowercase
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.USER,
        status=UserStatus.PENDING,
        email_verify_token=verify_token,
        email_verify_token_expires=verify_token_expires,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Send verification email
    await send_verification_email(user.email, user.username, verify_token)
    
    logger.info(f"New user registered: {user.username} from IP {ip}")
    
    # 记录审计日志
    try:
        from app.api.admin.audit import create_audit_log
        await create_audit_log(
            db=db,
            action="register",
            ip_address=ip,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            user_agent=request.headers.get("User-Agent"),
            details=f"New user registered: {user.username}",
            log_status="success"
        )
    except Exception as e:
        logger.error(f"Failed to create audit log for registration: {e}")
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token."""
        
    ip = get_real_ip(request)
    
    # Debug: Log all relevant headers and detected IP
    logger.info(f"Login attempt - Detected IP: {ip}")
    logger.info(f"  X-Forwarded-For: {request.headers.get('X-Forwarded-For')}")
    logger.info(f"  X-Real-IP: {request.headers.get('X-Real-IP')}")
    logger.info(f"  CF-Connecting-IP: {request.headers.get('CF-Connecting-IP')}")
    logger.info(f"  Client host: {request.client.host if request.client else 'None'}")
    
    # Check login attempts
    is_blocked, attempts = await check_login_attempts(ip)
    logger.info(f"  Login attempts for {ip}: {attempts}, blocked: {is_blocked}")
    
    if is_blocked:
        logger.warning(f"Login blocked for IP {ip} after {attempts} attempts")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )
    
    # Find user by username or email
    result = await db.execute(
        select(User).where(
            or_(
                User.username == user_data.username,
                User.email == user_data.username
            )
        )
    )
    user = result.scalar_one_or_none()
    
    # Check if it's an OAuth managed account (starts with OAUTH_ or is CASDOOR_MANAGED legacy)
    if user and (user.hashed_password.startswith("OAUTH_") or user.hashed_password == "CASDOOR_MANAGED"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此账号通过第三方登录创建，请使用对应的第三方平台登录。"
        )
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        await record_failed_login(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check user status
    if user.status == UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    if user.status == UserStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked"
        )
    
    # Clear failed login attempts
    await clear_login_attempts(ip)
    
    # Reset failed attempts counter
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = ip
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # 记录登录审计日志
    try:
        from app.api.admin.audit import create_audit_log
        await create_audit_log(
            db=db,
            action="login",
            ip_address=ip,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            user_agent=request.headers.get("User-Agent"),
            details=f"User {user.username} logged in",
            log_status="success"
        )
    except Exception as e:
        logger.error(f"Failed to create audit log for login: {e}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Verify email address."""
    result = await db.execute(
        select(User).where(User.email_verify_token == token)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.email_verify_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    user.email_verified = True
    user.status = UserStatus.ACTIVE
    user.email_verify_token = None
    user.email_verify_token_expires = None
    
    await db.commit()
    
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    data: PasswordResetWithCaptcha,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset email with captcha verification."""
    ip = get_real_ip(request)
    from app.services.settings import get_setting
    
    # Rate limit: max 3 password reset requests per IP per hour
    is_allowed, count, remaining = await check_rate_limit(f"forgot_password:{ip}", 3, 3600)
    if not is_allowed:
        logger.warning(f"Password reset rate limit exceeded for IP {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="密码重置请求过于频繁，请稍后再试"
        )
    
    # Verify captcha FIRST
    if not await verify_captcha_redis(data.captcha_id, data.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # Validate email format
    if not EMAIL_REGEX.match(data.email):
        # Still return success to prevent enumeration
        return {"message": "If the email exists, a password reset link has been sent"}
    
    result = await db.execute(select(User).where(User.email == data.email.lower()))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user and user.status == UserStatus.ACTIVE:
        # Additional rate limit: max 1 email per user per 5 minutes
        user_allowed, _, _ = await check_rate_limit(f"forgot_password_user:{user.id}", 1, 300)
        if user_allowed:
            reset_token = generate_verification_token()
            user.password_reset_token = reset_token
            user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            await db.commit()
            
            await send_password_reset_email(user.email, user.username, reset_token)
            logger.info(f"Password reset email sent to {user.email} from IP {ip}")
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    data: PasswordResetConfirm,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using token."""
    ip = get_real_ip(request)
    
    # Rate limit: max 5 reset attempts per IP per hour
    is_allowed, count, remaining = await check_rate_limit(f"reset_password:{ip}", 5, 3600)
    if not is_allowed:
        logger.warning(f"Password reset rate limit exceeded for IP {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="密码重置请求过于频繁，请稍后再试"
        )
    
    result = await db.execute(
        select(User).where(User.password_reset_token == data.token)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    if user.password_reset_token_expires < datetime.utcnow():
        # 清除过期token
        user.password_reset_token = None
        user.password_reset_token_expires = None
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # 验证新密码强度
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少8位"
        )
    if not re.search(r'[a-z]', data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含小写字母"
        )
    if not re.search(r'[A-Z]', data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含大写字母"
        )
    if not re.search(r'\d', data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含数字"
        )
    
    user.hashed_password = get_password_hash(data.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    # 重置密码后清除登录失败计数
    user.failed_login_attempts = 0
    user.locked_until = None
    
    await db.commit()
    
    logger.info(f"Password reset successful for user {user.username} from IP {ip}")
    
    return {"message": "Password reset successfully"}
