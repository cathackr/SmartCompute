#!/usr/bin/env python3
"""
SmartCompute Payment API
Handles MercadoPago and Bitso integrations for checkout
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartCompute Payment API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Configuration (in production, use environment variables)
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', 'TEST-your-access-token')
BITSO_API_KEY = os.getenv('BITSO_API_KEY', 'your-bitso-api-key')
BITSO_API_SECRET = os.getenv('BITSO_API_SECRET', 'your-bitso-secret')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret')

# Models
class CustomerInfo(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    country: str

class PaymentRequest(BaseModel):
    plan: str
    planName: str
    amount: float
    currency: str
    customer: CustomerInfo
    paymentMethod: str

class PaymentResponse(BaseModel):
    success: bool
    checkoutUrl: Optional[str] = None
    paymentData: Optional[Dict[str, Any]] = None
    paymentInstructions: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory storage (in production, use a proper database)
payments_db = {}
crypto_payments_db = {}

@app.get("/")
async def root():
    return {"message": "SmartCompute Payment API", "version": "1.0.0"}

@app.post("/api/payments/mercadopago/create-preference")
async def create_mercadopago_preference(request: PaymentRequest) -> PaymentResponse:
    """Create MercadoPago payment preference"""
    try:
        # Generate unique payment ID
        payment_id = str(uuid.uuid4())
        
        # MercadoPago preference data
        preference_data = {
            "items": [
                {
                    "title": request.planName,
                    "description": f"Suscripción {request.planName}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": request.amount
                }
            ],
            "payer": {
                "name": request.customer.name,
                "email": request.customer.email
            },
            "payment_methods": {
                "excluded_payment_methods": [],
                "excluded_payment_types": [],
                "installments": 12
            },
            "back_urls": {
                "success": f"http://localhost:8002/payment-success?id={payment_id}",
                "failure": f"http://localhost:8002/payment-failure?id={payment_id}",
                "pending": f"http://localhost:8002/payment-pending?id={payment_id}"
            },
            "auto_return": "approved",
            "external_reference": payment_id,
            "notification_url": f"http://localhost:8002/api/payments/mercadopago/webhook"
        }
        
        # Call MercadoPago API
        headers = {
            "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # For testing, we'll simulate the MercadoPago response
        if MERCADOPAGO_ACCESS_TOKEN.startswith('TEST-'):
            # Simulate successful preference creation
            checkout_url = f"https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=test-preference-{payment_id}"
        else:
            response = requests.post(
                "https://api.mercadopago.com/checkout/preferences",
                json=preference_data,
                headers=headers
            )
            
            if response.status_code != 201:
                raise HTTPException(status_code=400, detail="Error creating MercadoPago preference")
            
            preference = response.json()
            checkout_url = preference.get("init_point")
        
        # Store payment info
        payments_db[payment_id] = {
            "id": payment_id,
            "plan": request.plan,
            "amount": request.amount,
            "currency": request.currency,
            "customer": request.customer.dict(),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "payment_method": "mercadopago"
        }
        
        logger.info(f"Created MercadoPago preference for payment {payment_id}")
        
        return PaymentResponse(
            success=True,
            checkoutUrl=checkout_url
        )
        
    except Exception as e:
        logger.error(f"Error creating MercadoPago preference: {str(e)}")
        return PaymentResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/payments/bitso/create-payment")
async def create_bitso_payment(request: PaymentRequest) -> PaymentResponse:
    """Create Bitso cryptocurrency payment"""
    try:
        payment_id = str(uuid.uuid4())
        
        # For demonstration, we'll simulate crypto payment data
        # In production, integrate with Bitso API to get real addresses
        
        crypto_data = {
            "paymentId": payment_id,
            "cryptocurrency": "BTC",
            "cryptoAmount": request.amount / 50000,  # Simulated BTC price
            "address": generate_btc_address(),
            "qrCode": f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # Placeholder QR
            "expiresAt": (datetime.utcnow() + timedelta(minutes=15)).isoformat()
        }
        
        # Store crypto payment
        crypto_payments_db[payment_id] = {
            "id": payment_id,
            "plan": request.plan,
            "amount": request.amount,
            "currency": request.currency,
            "customer": request.customer.dict(),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "payment_method": "bitso",
            "crypto_data": crypto_data,
            "expires_at": crypto_data["expiresAt"]
        }
        
        logger.info(f"Created Bitso payment for {payment_id}")
        
        return PaymentResponse(
            success=True,
            paymentData=crypto_data
        )
        
    except Exception as e:
        logger.error(f"Error creating Bitso payment: {str(e)}")
        return PaymentResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/payments/international/create-payment")
async def create_international_payment(request: PaymentRequest) -> PaymentResponse:
    """Create international payment instructions"""
    try:
        payment_id = str(uuid.uuid4())
        reference = f"SMART-{payment_id[:8].upper()}"
        
        instructions = {
            "amount": request.amount,
            "reference": reference,
            "swift": {
                "beneficiary": "SmartCompute Argentina SRL",
                "bank": "Banco Santander Argentina",
                "swiftCode": "BSCHARAN",
                "accountNumber": "4152-0158-7/1 USD"
            },
            "paypal": {
                "email": "payments@smartcompute.ar"
            },
            "wise": {
                "email": "martin.iribarne@smartcompute.ar"
            }
        }
        
        # Store payment info
        payments_db[payment_id] = {
            "id": payment_id,
            "plan": request.plan,
            "amount": request.amount,
            "currency": request.currency,
            "customer": request.customer.dict(),
            "status": "pending_manual",
            "created_at": datetime.utcnow().isoformat(),
            "payment_method": "international",
            "reference": reference
        }
        
        logger.info(f"Created international payment instructions for {payment_id}")
        
        return PaymentResponse(
            success=True,
            paymentInstructions=instructions
        )
        
    except Exception as e:
        logger.error(f"Error creating international payment: {str(e)}")
        return PaymentResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/payments/status/{payment_id}")
async def get_payment_status(payment_id: str):
    """Get payment status"""
    
    # Check regular payments
    if payment_id in payments_db:
        payment = payments_db[payment_id]
        return {
            "id": payment_id,
            "status": payment["status"],
            "updated_at": datetime.utcnow().isoformat()
        }
    
    # Check crypto payments
    if payment_id in crypto_payments_db:
        payment = crypto_payments_db[payment_id]
        
        # Check if payment expired
        expires_at = datetime.fromisoformat(payment["expires_at"].replace('Z', '+00:00'))
        if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
            payment["status"] = "expired"
            
        return {
            "id": payment_id,
            "status": payment["status"],
            "updated_at": datetime.utcnow().isoformat()
        }
    
    raise HTTPException(status_code=404, detail="Payment not found")

@app.post("/api/payments/mercadopago/webhook")
async def mercadopago_webhook(request: dict):
    """Handle MercadoPago webhook notifications"""
    try:
        if request.get("type") == "payment":
            payment_id = request.get("data", {}).get("id")
            external_reference = request.get("external_reference")
            
            # Update payment status
            if external_reference and external_reference in payments_db:
                # In production, verify the payment with MercadoPago API
                payments_db[external_reference]["status"] = "confirmed"
                payments_db[external_reference]["mp_payment_id"] = payment_id
                payments_db[external_reference]["updated_at"] = datetime.utcnow().isoformat()
                
                logger.info(f"Payment {external_reference} confirmed via webhook")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing MercadoPago webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/payment-success")
async def payment_success(id: str):
    """Payment success page"""
    if id in payments_db:
        payments_db[id]["status"] = "confirmed"
    
    return {
        "message": "¡Pago exitoso!",
        "payment_id": id,
        "next_steps": "Recibirás un email con los detalles de acceso en los próximos minutos."
    }

@app.get("/payment-failure")
async def payment_failure(id: str):
    """Payment failure page"""
    if id in payments_db:
        payments_db[id]["status"] = "failed"
    
    return {
        "message": "Pago fallido",
        "payment_id": id,
        "action": "Por favor intenta nuevamente o contacta soporte."
    }

@app.get("/payment-pending")
async def payment_pending(id: str):
    """Payment pending page"""
    return {
        "message": "Pago pendiente",
        "payment_id": id,
        "action": "Tu pago está siendo procesado. Te notificaremos cuando esté completado."
    }

# Utility functions
def generate_btc_address():
    """Generate a simulated Bitcoin address"""
    import random
    import string
    
    # Generate a realistic-looking Bitcoin address
    chars = string.ascii_letters + string.digits
    address = '1' + ''.join(random.choice(chars) for _ in range(33))
    return address

def verify_webhook_signature(payload: str, signature: str) -> bool:
    """Verify webhook signature"""
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

if __name__ == "__main__":
    import uvicorn
    # 🔒 SEGURIDAD: Solo localhost - usar nginx como proxy para acceso externo
    uvicorn.run(app, host="127.0.0.1", port=8003)