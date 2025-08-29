"""
SmartCompute Payment Gateway Service
Isolated microservice for secure payment processing
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import hmac
import hashlib
import logging
import os
import json
import sys
from datetime import datetime, timedelta
import asyncio

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from services.secrets.secret_manager import secret_manager
except ImportError:
    # Fallback if secret manager not available
    secret_manager = None
    logger.warning("Secret manager not available, using environment variables")

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"service": "payment-gateway", "level": "%(levelname)s", "message": "%(message)s", "timestamp": "%(asctime)s"}'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartCompute Payment Gateway",
    description="Isolated payment processing service",
    version="1.0.0",
    docs_url=None,  # Disable docs for security
    redoc_url=None
)


class PaymentRequest(BaseModel):
    """Payment request model"""
    amount_usd: float
    currency: str = "BTC"  # BTC, ETH, USDT
    customer_id: str
    order_id: str
    metadata: Optional[Dict[str, Any]] = None


class PaymentResponse(BaseModel):
    """Payment response model"""
    payment_id: str
    status: str  # pending, confirmed, failed
    wallet_address: str
    amount_crypto: float
    currency: str
    expires_at: str
    qr_code_url: Optional[str] = None


class WebhookPayload(BaseModel):
    """Webhook payload model"""
    payment_id: str
    status: str
    transaction_hash: Optional[str] = None
    confirmations: int = 0
    timestamp: str


def get_webhook_secret() -> str:
    """Get webhook secret from environment or secret manager"""
    # In production, retrieve from HashiCorp Vault or AWS Secrets Manager
    secret = os.getenv("WEBHOOK_SECRET")
    if not secret:
        logger.warning("WEBHOOK_SECRET not configured - using development default")
        return "dev-webhook-secret-change-in-production"
    return secret


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature using HMAC"""
    try:
        # Expected format: sha256=<hex_digest>
        if not signature.startswith("sha256="):
            return False
        
        received_hash = signature[7:]  # Remove 'sha256=' prefix
        expected_hash = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(received_hash, expected_hash)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return False


# In-memory payment store (replace with database in production)
payments_db: Dict[str, PaymentResponse] = {}
webhook_events: Dict[str, WebhookPayload] = {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "payment-gateway",
        "version": "1.0.0",
        "active_payments": len(payments_db),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/create-payment", response_model=PaymentResponse)
async def create_payment(request: PaymentRequest):
    """Create a new payment request"""
    logger.info(f"Creating payment request: order_id={request.order_id}, amount={request.amount_usd} USD")
    
    try:
        # Generate payment ID
        payment_id = f"pay_{request.order_id}_{int(datetime.utcnow().timestamp())}"
        
        # Mock crypto address generation (use real crypto service in production)
        wallet_addresses = {
            "BTC": f"bc1q{payment_id[:20]}mock",
            "ETH": f"0x{payment_id[:20]}{'0' * 20}",
            "USDT": f"0x{payment_id[:20]}{'1' * 20}"
        }
        
        # Mock exchange rates (use real API in production)
        exchange_rates = {"BTC": 45000, "ETH": 3000, "USDT": 1}
        rate = exchange_rates.get(request.currency, 1)
        amount_crypto = request.amount_usd / rate
        
        # Create payment response
        payment = PaymentResponse(
            payment_id=payment_id,
            status="pending",
            wallet_address=wallet_addresses.get(request.currency, wallet_addresses["BTC"]),
            amount_crypto=round(amount_crypto, 8),
            currency=request.currency,
            expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat(),
            qr_code_url=f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={wallet_addresses.get(request.currency)}"
        )
        
        # Store payment
        payments_db[payment_id] = payment
        
        logger.info(f"Payment created: {payment_id}")
        return payment
        
    except Exception as e:
        logger.error(f"Payment creation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment creation failed")


@app.get("/payment/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Get payment status by ID"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payments_db[payment_id]


@app.post("/webhook")
async def payment_webhook(
    request: Request,
    webhook_signature: str = Header(..., alias="X-Webhook-Signature")
):
    """Handle payment status webhooks with signature verification"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature
        webhook_secret = get_webhook_secret()
        if not verify_webhook_signature(body, webhook_signature, webhook_secret):
            logger.warning("Webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook payload
        try:
            payload_data = json.loads(body.decode('utf-8'))
            webhook_payload = WebhookPayload(**payload_data)
        except Exception as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
        
        logger.info(f"Webhook received: payment_id={webhook_payload.payment_id}, status={webhook_payload.status}")
        
        # Update payment status
        if webhook_payload.payment_id in payments_db:
            payment = payments_db[webhook_payload.payment_id]
            payment.status = webhook_payload.status
            payments_db[webhook_payload.payment_id] = payment
            
            logger.info(f"Payment status updated: {webhook_payload.payment_id} -> {webhook_payload.status}")
        else:
            logger.warning(f"Webhook for unknown payment: {webhook_payload.payment_id}")
        
        # Store webhook event
        event_id = f"evt_{webhook_payload.payment_id}_{int(datetime.utcnow().timestamp())}"
        webhook_events[event_id] = webhook_payload
        
        return {"status": "ok", "event_id": event_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@app.get("/status/payments")
async def get_payments_summary():
    """Get payment statistics summary"""
    statuses = {}
    for payment in payments_db.values():
        status = payment.status
        statuses[status] = statuses.get(status, 0) + 1
    
    return {
        "total_payments": len(payments_db),
        "status_breakdown": statuses,
        "webhook_events": len(webhook_events),
        "timestamp": datetime.utcnow().isoformat()
    }


# Cleanup expired payments periodically
@app.on_event("startup")
async def startup_cleanup():
    """Start background cleanup tasks"""
    logger.info("Payment gateway service starting...")
    
    # Initialize credentials from secret manager
    if secret_manager:
        try:
            service_creds = await secret_manager.get_service_credentials()
            # Update webhook secret from secure storage
            global WEBHOOK_SECRET
            WEBHOOK_SECRET = service_creds.get('PAYMENT_WEBHOOK_SECRET', WEBHOOK_SECRET)
            logger.info("Loaded payment credentials from secret manager")
        except Exception as e:
            logger.warning(f"Failed to load credentials from secret manager: {e}")
    
    async def cleanup_expired():
        while True:
            try:
                now = datetime.utcnow()
                expired_payments = []
                
                for payment_id, payment in payments_db.items():
                    expires_at = datetime.fromisoformat(payment.expires_at.replace('Z', '+00:00'))
                    if now > expires_at and payment.status == "pending":
                        expired_payments.append(payment_id)
                
                for payment_id in expired_payments:
                    payments_db[payment_id].status = "expired"
                    logger.info(f"Payment expired: {payment_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Cleanup task failed: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    asyncio.create_task(cleanup_expired())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)