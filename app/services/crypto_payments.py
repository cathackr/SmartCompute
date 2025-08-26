"""
SmartCompute Crypto Payment Service
Handles crypto payments via Bitso API
"""

import os
import json
import hashlib
import hmac
import requests
import uuid
import time
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone, timedelta
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CryptoPaymentRequest(BaseModel):
    """Crypto payment request model"""
    amount_usd: float
    service_type: str  # 'audit', 'installation', 'monitoring'
    customer_email: str
    customer_name: str
    crypto_currency: str = "USDT"  # BTC, ETH, USDT, etc.
    description: str = "SmartCompute Service Payment"

class PaymentResponse(BaseModel):
    """Payment response model"""
    payment_id: str
    crypto_currency: str
    amount_crypto: float
    amount_mxn: float
    amount_usd: float
    current_rate: float
    payment_address: str
    qr_code_data: str
    payment_instructions: str
    expires_at: str
    status: str
    discount_applied: bool
    final_price_mxn: float

class BitsoPaymentService:
    """Handles crypto payments with Bitso API"""
    
    def __init__(self):
        self.api_key = os.getenv('BITSO_API_KEY')
        self.api_secret = os.getenv('BITSO_API_SECRET')
        self.webhook_secret = os.getenv('CRYPTO_WEBHOOK_SECRET')
        self.base_url = os.getenv('BITSO_API_URL', 'https://api.bitso.com/v3/')
        
        # Service prices in USD
        self.service_prices = {
            'audit': 299.0,
            'installation': 199.0,
            'monitoring': 150.0
        }
    
    def get_usd_to_mxn_rate(self) -> float:
        """Get current USD to MXN exchange rate from Bitso"""
        try:
            response = requests.get(f"{self.base_url}ticker/?book=usd_mxn")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('payload'):
                    ticker = data['payload']
                    return float(ticker.get('last', 20.0))  # Default fallback rate
            return 20.0  # Fallback rate
        except:
            return 20.0  # Fallback rate
    
    def get_crypto_price_in_mxn(self, crypto: str) -> float:
        """Get current crypto price in MXN from Bitso"""
        try:
            book = f"{crypto.lower()}_mxn"
            response = requests.get(f"{self.base_url}ticker/?book={book}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('payload'):
                    ticker = data['payload']
                    return float(ticker.get('last', 0))
            return 0
        except:
            return 0
    
    def get_available_cryptocurrencies(self) -> List[str]:
        """Get list of available cryptocurrencies for payments"""
        try:
            response = requests.get(f"{self.base_url}available_books/")
            if response.status_code == 200:
                data = response.json()
                books = data.get('payload', [])
                
                cryptos = []
                for book in books:
                    book_name = book.get('book', '')
                    if '_mxn' in book_name.lower():
                        crypto = book_name.replace('_mxn', '').upper()
                        if crypto not in ['EUR', 'USD']:  # Exclude fiat
                            cryptos.append(crypto)
                return cryptos
        except:
            pass
        
        # Fallback list
        return ['BTC', 'ETH', 'USDT', 'LTC', 'XRP']
    
    def create_payment(self, request: CryptoPaymentRequest) -> PaymentResponse:
        """Create a new crypto payment request using Bitso rates"""
        try:
            # Validate service type and amount
            if request.service_type not in self.service_prices:
                raise ValueError(f"Invalid service type: {request.service_type}")
            
            expected_amount = self.service_prices[request.service_type]
            if abs(request.amount_usd - expected_amount) > 0.01:
                raise ValueError(f"Amount mismatch. Expected: ${expected_amount}, Got: ${request.amount_usd}")
            
            # Apply crypto discount (5% off)
            discounted_amount_usd = request.amount_usd * 0.95
            
            # Get current rates
            usd_to_mxn_rate = self.get_usd_to_mxn_rate()
            discounted_price_mxn = discounted_amount_usd * usd_to_mxn_rate
            
            # Get crypto price in MXN
            crypto_price_mxn = self.get_crypto_price_in_mxn(request.crypto_currency)
            if crypto_price_mxn == 0:
                raise ValueError(f"Cryptocurrency {request.crypto_currency} not available")
            
            # Calculate crypto amount needed
            crypto_amount = discounted_price_mxn / crypto_price_mxn
            
            # Generate payment ID and wallet address (simplified for demo)
            payment_id = str(uuid.uuid4())
            
            # Create static wallet addresses for demo (in production, use dynamic addresses)
            wallet_addresses = {
                'BTC': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'ETH': '0x742d35cc6634c0532925a3b8d29af156c066e80b',
                'USDT': 'TQn9Y2khEsLJW1ChVWFMSMeRDow5AAGAAQ',  # TRON USDT
                'LTC': 'LTC1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P',
                'XRP': 'rDdXdYpShTLdgzAhey78eGZU1XRmHQzCb5',
            }
            
            payment_address = wallet_addresses.get(request.crypto_currency, 'N/A')
            
            # Create QR code data
            qr_data = f"{request.crypto_currency.lower()}:{payment_address}?amount={crypto_amount:.8f}&label=SmartCompute Payment"
            
            # Payment instructions
            instructions = f"""
Payment Instructions for {request.crypto_currency}:
1. Send exactly {crypto_amount:.8f} {request.crypto_currency} to: {payment_address}
2. Payment must be received within 1 hour
3. Use the exact amount shown - do not round
4. Include payment ID in transaction memo: {payment_id}
5. Contact support if payment is not confirmed within 2 hours

Network: {'TRON (TRC20)' if request.crypto_currency == 'USDT' else request.crypto_currency + ' Mainnet'}
"""
            
            # Calculate expiration (1 hour from now)
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            
            return PaymentResponse(
                payment_id=payment_id,
                crypto_currency=request.crypto_currency,
                amount_crypto=round(crypto_amount, 8),
                amount_mxn=round(discounted_price_mxn, 2),
                amount_usd=round(discounted_amount_usd, 2),
                current_rate=round(crypto_price_mxn, 2),
                payment_address=payment_address,
                qr_code_data=qr_data,
                payment_instructions=instructions,
                expires_at=expires_at,
                status='pending',
                discount_applied=True,
                final_price_mxn=round(discounted_price_mxn, 2)
            )
            
        except Exception as e:
            logger.error(f"Error creating crypto payment: {str(e)}")
            raise
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Verify payment status - simplified for demo without API permissions"""
        try:
            # In a real implementation, you would:
            # 1. Check blockchain for transaction
            # 2. Verify amount and recipient
            # 3. Update database status
            
            # For demo purposes, return pending status
            # This would be replaced with actual blockchain verification
            logger.info(f"Verifying payment {payment_id}")
            
            return {
                'payment_id': payment_id,
                'status': 'pending',
                'confirmed': False,
                'confirmations': 0,
                'transaction_id': None,
                'verified_at': None
            }
                
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            raise
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        try:
            if not self.webhook_secret:
                logger.warning("Webhook secret not configured")
                return False
                
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
    
    def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook notification"""
        try:
            payment_id = payload.get('payment_id')
            transaction_id = payload.get('transaction_id')
            status = payload.get('status', 'pending')
            amount = float(payload.get('amount', 0))
            
            logger.info(f"Processing webhook for payment {payment_id}: status={status}")
            
            if status == 'confirmed':
                return {
                    'event': 'payment_confirmed',
                    'payment_id': payment_id,
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            elif status == 'failed':
                return {
                    'event': 'payment_failed',
                    'payment_id': payment_id,
                    'reason': 'transaction_failed',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    'event': 'payment_pending',
                    'payment_id': payment_id,
                    'status': status,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise
    
    def get_payment_rates(self) -> Dict[str, Any]:
        """Get current payment rates for all supported cryptocurrencies"""
        try:
            rates = {}
            usd_to_mxn = self.get_usd_to_mxn_rate()
            
            for crypto in self.get_available_cryptocurrencies():
                crypto_price_mxn = self.get_crypto_price_in_mxn(crypto)
                if crypto_price_mxn > 0:
                    rates[crypto] = {
                        'price_mxn': crypto_price_mxn,
                        'price_usd': crypto_price_mxn / usd_to_mxn,
                        'available': True
                    }
                else:
                    rates[crypto] = {
                        'price_mxn': 0,
                        'price_usd': 0,
                        'available': False
                    }
            
            return {
                'rates': rates,
                'usd_to_mxn_rate': usd_to_mxn,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting payment rates: {str(e)}")
            raise

# Service instance - updated to use BitsoPaymentService
crypto_service = BitsoPaymentService()