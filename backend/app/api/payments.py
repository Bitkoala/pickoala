import logging
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.payment import PaymentTransaction, PaymentStatus
from app.services.settings import (
    is_stripe_enabled,
    get_stripe_secret_key,
    get_stripe_webhook_secret,
    get_stripe_price_id,
    get_site_url,
    is_alipay_enabled,
    get_alipay_app_id,
    get_alipay_private_key,
    get_alipay_public_key,
    get_vip_plans,
    get_setting,
    get_setting_bool
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

class CheckoutRequest(BaseModel):
    plan: str

@router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe Checkout Session for VIP upgrade.
    """
    if not await is_stripe_enabled():
        raise HTTPException(status_code=400, detail="Stripe payments are disabled.")

    secret_key = await get_stripe_secret_key()
    if not secret_key:
        raise HTTPException(status_code=500, detail="Stripe configuration missing (Secret Key).")
    
    stripe.api_key = secret_key

    vip_plans = await get_vip_plans()
    selected_plan = vip_plans.get(request.plan)
    
    if not selected_plan or not selected_plan["enabled"]:
        raise HTTPException(status_code=400, detail="Invalid or disabled plan selected.")
        
    target_price_id = selected_plan["stripe_id"]
    
    if not target_price_id:
        # Fallback to global if exists (legacy support) or Error
        target_price_id = await get_stripe_price_id()
        
    if not target_price_id:
        raise HTTPException(status_code=400, detail="No VIP Price ID configured for this plan.")

    site_url = await get_site_url()

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': target_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f"{site_url}/vip/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{site_url}/vip/cancel",
            client_reference_id=str(current_user.id),
            metadata={
                "user_id": str(current_user.id),
                "type": "vip_upgrade",
                "plan": request.plan
            }
        )

        # Create pending transaction
        transaction = PaymentTransaction(
            user_id=current_user.id,
            stripe_session_id=checkout_session.id,
            amount=checkout_session.amount_total or 0,
            currency=checkout_session.currency or "cny",
            status=PaymentStatus.PENDING
        )
        db.add(transaction)
        await db.commit()

        return {"url": checkout_session.url}
    except Exception as e:
        print(f"Stripe Checkout Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: AsyncSession = Depends(get_db)):
    """
    Handle Stripe webhooks to fulfill orders.
    """
    webhook_secret = await get_stripe_webhook_secret()
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe Webhook Secret not configured.")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_checkout_completed(session, db)

    return {"status": "success"}

async def handle_checkout_completed(session, db: AsyncSession):
    session_id = session.get("id")
    client_reference_id = session.get("client_reference_id")
    
    if not client_reference_id:
        print("Webhook Warning: No client_reference_id in session.")
        return

    user_id = int(client_reference_id)

    # 1. Update Transaction
    result = await db.execute(select(PaymentTransaction).where(PaymentTransaction.stripe_session_id == session_id))
    transaction = result.scalars().first()
    
    if transaction:
        transaction.status = PaymentStatus.PAID
        transaction.amount = session.get("amount_total") or transaction.amount
        transaction.currency = session.get("currency") or transaction.currency
    else:
        # Create if missing
        transaction = PaymentTransaction(
            user_id=user_id,
            stripe_session_id=session_id,
            amount=session.get("amount_total") or 0,
            currency=session.get("currency") or "cny",
            status=PaymentStatus.PAID
        )
        db.add(transaction)
    
    # 2. Grant VIP
    result_user = await db.execute(select(User).where(User.id == user_id))
    user = result_user.scalars().first()
    
    if user:
        now = datetime.utcnow()
        current_expire = user.vip_expire_at
        
        # Calculate duration based on plan
        plan = session.get("metadata", {}).get("plan", "month")
        
        duration_map = {
            "month": 30,
            "quarter": 90,
            "year": 365,
            "forever": 36500
        }
        days = duration_map.get(plan, 30)
        
        # Extend
        if current_expire and current_expire > now:
            new_expire = current_expire + timedelta(days=days)
        else:
            new_expire = now + timedelta(days=days)
            
        user.vip_expire_at = new_expire
        print(f"VIP Granted to User {user.username} until {new_expire} (Plan: {plan})")
    
    await db.commit()


# ==========================================
# Alipay Integration
# ==========================================

async def get_alipay_client():
    """Initialize Alipay client with settings."""
    app_id = await get_alipay_app_id()
    app_private_key_string = await get_alipay_private_key()
    alipay_public_key_string = await get_alipay_public_key()
    
    if not app_id or not app_private_key_string or not alipay_public_key_string:
        # If any config is missing, return None or raise
        # Raise generic to be caught
        raise Exception("Alipay configuration missing.")
        
    from alipay import AliPay
    
    # Ensure keys have BEGIN/END markers if missing (simple check)
    if "-----BEGIN RSA PRIVATE KEY" not in app_private_key_string and "-----BEGIN PRIVATE KEY" not in app_private_key_string:
         app_private_key_string = f"-----BEGIN RSA PRIVATE KEY-----\n{app_private_key_string}\n-----END RSA PRIVATE KEY-----"
         
    if "-----BEGIN PUBLIC KEY" not in alipay_public_key_string:
         alipay_public_key_string = f"-----BEGIN PUBLIC KEY-----\n{alipay_public_key_string}\n-----END PUBLIC KEY-----"

    return AliPay(
        appid=app_id,
        app_notify_url=None, 
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",
        debug=False 
    )

@router.post("/alipay/pay")
async def alipay_pay(
    request: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Alipay Pre-create QR Code for VIP upgrade.
    """
    if not await is_alipay_enabled():
        raise HTTPException(status_code=400, detail="Alipay payments are disabled.")
    
    vip_plans = await get_vip_plans()
    selected_plan = vip_plans.get(request.plan)
    
    if not selected_plan or not selected_plan["enabled"]:
        raise HTTPException(status_code=400, detail="Invalid or disabled plan selected.")
    
    try:
        amount = float(selected_plan["price"])
    except (ValueError, TypeError):
         raise HTTPException(status_code=500, detail="Invalid price configuration for this plan.")
         
    duration_map = {
        "month": 30,
        "quarter": 90,
        "year": 365,
        "forever": 36500 # 100 years
    }
    duration_days = duration_map.get(request.plan, 30)
    
    out_trade_no = f"VIP_{request.plan}_{current_user.id}_{int(datetime.utcnow().timestamp())}"
    subject = f"VIP Membership ({request.plan})"
    
    try:
        client = await get_alipay_client()
        
        # Create order with page_pay for browser redirection (Automatic PC/Mobile)
        # Note: Alipay will handle device detection and show WAP or Page automatically 
        # iff using the latest SDK and corresponding API
        site_url = await get_site_url()
        return_url = f"{site_url}/vip/success"

        # Use api_alipay_trade_precreate for "Face-to-Face" (当面付)
        formatted_amount = "{:.2f}".format(amount)
        
        result = client.api_alipay_trade_precreate(
            subject=subject,
            out_trade_no=out_trade_no,
            total_amount=formatted_amount
        )
        
        if result.get("code") != "10000":
             msg = result.get("sub_msg") or result.get("msg")
             raise HTTPException(status_code=400, detail=f"Alipay Error: {msg}")
             
        qr_code_url = result.get("qr_code")

        # Create Transaction
        transaction = PaymentTransaction(
            user_id=current_user.id,
            provider="alipay",
            out_trade_no=out_trade_no,
            stripe_session_id=None,
            amount=int(amount * 100), 
            currency="cny",
            status=PaymentStatus.PENDING,
            qr_code=qr_code_url
        )
        db.add(transaction)
        await db.commit()
        
        return {
            "qr_code": qr_code_url,
            "out_trade_no": out_trade_no,
            "amount": amount
        }
        
    except Exception as e:
        print(f"Alipay Pay Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alipay/notify")
async def alipay_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Alipay asynchronous notification.
    """
    data = await request.form()
    data_dict = dict(data)
    
    try:
        client = await get_alipay_client()
        signature = data_dict.pop("sign", None)
        
        # Verify signature
        success = client.verify(data_dict, signature)
        if success and data_dict.get("trade_status") in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            out_trade_no = data_dict.get("out_trade_no")
            await handle_alipay_success(out_trade_no, db)
            return "success"
        else:
            return "failure"
            
    except Exception as e:
        print(f"Alipay Notify Error: {e}")
        return "failure"

@router.get("/alipay/check/{out_trade_no}")
async def check_alipay_status(
    out_trade_no: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check status of an Alipay transaction.
    """
    result = await db.execute(select(PaymentTransaction).where(
        PaymentTransaction.out_trade_no == out_trade_no,
        PaymentTransaction.user_id == current_user.id
    ))
    transaction = result.scalars().first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    if transaction.status == PaymentStatus.PAID:
        return {"status": "paid"}
        
    # Query Alipay if pending
    try:
        client = await get_alipay_client()
        res = client.api_alipay_trade_query(out_trade_no=out_trade_no)
        if res.get("code") == "10000" and res.get("trade_status") in ("TRADE_SUCCESS", "TRADE_FINISHED"):
             await handle_alipay_success(out_trade_no, db)
             return {"status": "paid"}
             
    except Exception as e:
        logger.error(f"Alipay Query Error: {e}")
        
    return {"status": "pending"}

# ==========================================
# Epay (易支付) Integration
# ==========================================

async def get_epay_config():
    """Get Epay configuration from settings."""
    return {
        "api_url": await get_setting("payment_epay_api_url"),
        "partner_id": await get_setting("payment_epay_partner_id"),
        "partner_key": await get_setting("payment_epay_partner_key"),
    }

def generate_epay_sign(params: dict, partner_key: str) -> str:
    """Generate MD5 signature for Epay."""
    import hashlib
    # Filter out empty, sign and sign_type
    filtered_params = {k: v for k, v in params.items() if v and k not in ["sign", "sign_type"]}
    # Sort keys alphabetically
    sorted_keys = sorted(filtered_params.keys())
    # Join into a query string
    query_string = "&".join([f"{k}={filtered_params[k]}" for k in sorted_keys])
    # Append partner key
    sign_str = query_string + partner_key
    # Calculate MD5
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()

@router.post("/epay/pay")
async def epay_pay(
    request: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Epay payment URL for VIP upgrade."""
    
    if not await get_setting_bool("payment_epay_enabled", False):
        raise HTTPException(status_code=400, detail="Epay payments are disabled.")
    
    vip_plans = await get_vip_plans()
    selected_plan = vip_plans.get(request.plan)
    if not selected_plan or not selected_plan["enabled"]:
        raise HTTPException(status_code=400, detail="Invalid or disabled plan selected.")
    
    config = await get_epay_config()
    if not config["api_url"] or not config["partner_id"] or not config["partner_key"]:
        raise HTTPException(status_code=500, detail="Epay configuration missing.")
    
    out_trade_no = f"VIP_EPAY_{request.plan}_{current_user.id}_{int(datetime.utcnow().timestamp())}"
    site_url = await get_site_url()
    
    # Standard Epay Parameters
    params = {
        "pid": config["partner_id"],
        "type": "alipay", # Default to alipay, can be extended to wxpay/qqpay
        "out_trade_no": out_trade_no,
        "notify_url": f"{site_url}/api/payments/epay/notify",
        "return_url": f"{site_url}/vip/success",
        "name": f"VIP Membership ({request.plan})",
        "money": selected_plan["price"],
        "sitename": "PicKoala"
    }
    
    params["sign"] = generate_epay_sign(params, config["partner_key"])
    params["sign_type"] = "MD5"
    
    # Construct the final payment URL for redirection
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    pay_url = f"{config['api_url']}?{query_string}"
    
    # Create Transaction
    transaction = PaymentTransaction(
        user_id=current_user.id,
        provider="epay",
        out_trade_no=out_trade_no,
        amount=int(float(selected_plan["price"]) * 100),
        currency="cny",
        status=PaymentStatus.PENDING
    )
    db.add(transaction)
    await db.commit()
    
    return {"url": pay_url}

@router.get("/epay/notify")
@router.post("/epay/notify")
async def epay_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Epay asynchronous notification."""
    # Epay usually sends via GET/POST
    if request.method == "POST":
        data = await request.form()
    else:
        data = request.query_params
    
    data_dict = dict(data)
    config = await get_epay_config()
    
    signature = data_dict.get("sign")
    if not signature:
        return "fail"
    
    expected_sign = generate_epay_sign(data_dict, config["partner_key"])
    if signature != expected_sign:
        logger.warning(f"Epay Signature mismatch. Received: {signature}, Expected: {expected_sign}")
        return "fail"
    
    if data_dict.get("trade_status") == "TRADE_SUCCESS":
        out_trade_no = data_dict.get("out_trade_no")
        await handle_epay_success(out_trade_no, db)
        return "success"
    
    return "fail"

async def handle_epay_success(out_trade_no: str, db: AsyncSession):
    """Process a successful Epay payment."""
    result = await db.execute(select(PaymentTransaction).where(PaymentTransaction.out_trade_no == out_trade_no))
    transaction = result.scalars().first()
    
    if transaction and transaction.status != PaymentStatus.PAID:
        transaction.status = PaymentStatus.PAID
        
        # Grant VIP
        result_user = await db.execute(select(User).where(User.id == transaction.user_id))
        user = result_user.scalars().first()
        
        if user:
            now = datetime.utcnow()
            current_expire = user.vip_expire_at
            
            # Format: VIP_EPAY_{plan}_{uid}_{ts}
            parts = out_trade_no.split("_")
            plan = "month"
            if len(parts) >= 4:
                plan = parts[2] # Part 0: VIP, Part 1: EPAY, Part 2: plan
                
            duration_map = {
                "month": 30,
                "quarter": 90,
                "year": 365,
                "forever": 36500
            }
            days = duration_map.get(plan, 30)

            if current_expire and current_expire > now:
                new_expire = current_expire + timedelta(days=days)
            else:
                new_expire = now + timedelta(days=days)
            user.vip_expire_at = new_expire
            logger.info(f"Epay VIP Granted to User {user.username} (Plan: {plan})")
            
        await db.commit()
