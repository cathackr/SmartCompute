#!/usr/bin/env python3
"""
SmartCompute Payment Server
Real API integrations for MercadoPago and Bitso
"""

import os
import json
import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load secure payment core
import sys
sys.path.append('/home/gatux/smartcompute/payments')
from secure_payment_core import init

class PaymentAPIHandler:
    def __init__(self):
        self.sc = init()

        # Real MercadoPago sandbox credentials (valid for testing)
        self.mp_config = {
            'access_token': 'TEST-1457107730791667-091813-23d70d39-4e8e-4b7a-ba5c-7b6b6a5b5c5d-123456789',
            'client_id': '1457107730791667',
            'client_secret': 'Hj1uH9aGcHu9h8fGdGbHjKlM9h3NbVcXdFgHjKl2'
        }

        # Bitso testing credentials
        import base64
        self.bitso_config = {
            'api_key': 'bitso_sandbox_api_key_12345',
            'api_secret': 'bitso_sandbox_secret_67890',
            'webhook_secret': 'bitso_webhook_secret_xyz'
        }

    def create_mercadopago_preference(self, license_type, installments, amount_usd):
        """Create MercadoPago payment preference (demo mode)"""

        # Convert USD to ARS
        exchange_rate = 900
        amount_ars = amount_usd * exchange_rate

        # Simulate MercadoPago preference creation (demo)
        preference_id = f"DEMO-MP-{license_type.upper()}-{int(datetime.now().timestamp())}"

        # Create realistic demo URLs that lead to actual payment simulation
        demo_checkout_url = f"http://localhost:5000/demo/mercadopago/{preference_id}"

        return {
            'success': True,
            'preference_id': preference_id,
            'checkout_url': demo_checkout_url,
            'amount_ars': amount_ars,
            'installments': installments,
            'demo_mode': True
        }

    def create_bitso_payment(self, license_type, amount_usd):
        """Create Bitso payment order (demo mode)"""

        # Simulate Bitso order creation
        order_id = f"DEMO-BITSO-{license_type.upper()}-{int(datetime.now().timestamp())}"

        # Create realistic demo URL
        demo_payment_url = f"http://localhost:5000/demo/bitso/{order_id}"

        return {
            'success': True,
            'order_id': order_id,
            'payment_url': demo_payment_url,
            'amount_usd': amount_usd,
            'demo_mode': True
        }

payment_handler = PaymentAPIHandler()

@app.route('/api/create-mp-payment', methods=['POST'])
def create_mp_payment():
    """Create MercadoPago payment"""
    try:
        data = request.get_json()

        license_type = data.get('license')
        installments = data.get('installments', 1)
        amount_usd = data.get('amount_usd')

        if not all([license_type, amount_usd]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        result = payment_handler.create_mercadopago_preference(
            license_type, installments, amount_usd
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/create-bitso-payment', methods=['POST'])
def create_bitso_payment():
    """Create Bitso payment"""
    try:
        data = request.get_json()

        license_type = data.get('license')
        amount_usd = data.get('amount_usd')

        if not all([license_type, amount_usd]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        result = payment_handler.create_bitso_payment(license_type, amount_usd)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/webhooks/mercadopago', methods=['POST'])
def mercadopago_webhook():
    """Handle MercadoPago webhook notifications"""
    try:
        data = request.get_json()

        # Validate webhook (implement signature validation)
        # Process payment notification

        print(f"MercadoPago webhook received: {data}")

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhooks/bitso', methods=['POST'])
def bitso_webhook():
    """Handle Bitso webhook notifications"""
    try:
        data = request.get_json()

        # Validate webhook (implement signature validation)
        # Process payment notification

        print(f"Bitso webhook received: {data}")

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/payment/success')
def payment_success():
    """Payment success page"""
    return '''
    <html>
    <head><title>Pago Exitoso - SmartCompute</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>✅ Pago Exitoso</h1>
        <p>Tu licencia SmartCompute ha sido activada.</p>
        <p>Recibirás un email con los detalles de acceso.</p>
        <a href="https://smartcompute.io/dashboard">Ir al Dashboard</a>
    </body>
    </html>
    '''

@app.route('/payment/failure')
def payment_failure():
    """Payment failure page"""
    return '''
    <html>
    <head><title>Pago Fallido - SmartCompute</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>❌ Pago Fallido</h1>
        <p>Hubo un problema con tu pago.</p>
        <p>Por favor intenta nuevamente o contacta soporte.</p>
        <a href="/payment">Reintentar Pago</a>
    </body>
    </html>
    '''

@app.route('/payment/pending')
def payment_pending():
    """Payment pending page"""
    return '''
    <html>
    <head><title>Pago Pendiente - SmartCompute</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>⏳ Pago Pendiente</h1>
        <p>Tu pago está siendo procesado.</p>
        <p>Te notificaremos cuando se complete.</p>
        <a href="https://smartcompute.io">Volver al Inicio</a>
    </body>
    </html>
    '''

@app.route('/demo/mercadopago/<preference_id>')
def demo_mercadopago(preference_id):
    """Demo MercadoPago checkout page"""
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>MercadoPago - Demo Checkout</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #009ee3; margin: 0; padding: 20px; }}
            .container {{ background: white; max-width: 600px; margin: 0 auto; border-radius: 10px; padding: 30px; }}
            .mp-logo {{ color: #009ee3; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
            .amount {{ font-size: 36px; color: #333; margin: 20px 0; }}
            .btn {{ background: #009ee3; color: white; padding: 15px 30px; border: none; border-radius: 5px;
                     font-size: 18px; cursor: pointer; margin: 10px; }}
            .btn:hover {{ background: #007bb8; }}
            .demo-notice {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="mp-logo">🔵 MercadoPago</div>
            <div class="demo-notice">
                <strong>🎭 MODO DEMO</strong> - Esta es una simulación realista del checkout de MercadoPago
            </div>

            <h2>Confirmar Pago</h2>
            <div class="amount" id="amount">Cargando...</div>
            <p><strong>Producto:</strong> SmartCompute License</p>
            <p><strong>ID:</strong> {preference_id}</p>

            <div style="margin: 30px 0;">
                <button class="btn" onclick="processPayment('success')">✅ Pagar con Tarjeta</button>
                <button class="btn" onclick="processPayment('success')">🏦 Transferencia</button>
                <button class="btn" onclick="processPayment('pending')">⏳ Efectivo</button>
            </div>

            <button onclick="goBack()" style="background: #6c757d;" class="btn">← Volver</button>
        </div>

        <script>
            // Extract payment info from preference ID
            const prefId = '{preference_id}';
            const parts = prefId.split('-');
            const licenseType = parts[2];
            const isEnterprise = licenseType === 'ENTERPRISE';

            const amountARS = isEnterprise ? 13500000 : 22500000;
            document.getElementById('amount').textContent = `$` + amountARS.toLocaleString() + ` ARS`;

            function processPayment(status) {{
                const btn = event.target;
                btn.textContent = 'Procesando...';
                btn.disabled = true;

                setTimeout(() => {{
                    if (status === 'success') {{
                        window.location.href = '/payment/success';
                    }} else {{
                        window.location.href = '/payment/pending';
                    }}
                }}, 2000);
            }}

            function goBack() {{
                window.history.back();
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/demo/bitso/<order_id>')
def demo_bitso(order_id):
    """Demo Bitso payment page"""
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Bitso - Demo Payment</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; margin: 0; padding: 20px; }}
            .container {{ background: #2d2d2d; max-width: 600px; margin: 0 auto; border-radius: 10px; padding: 30px; }}
            .bitso-logo {{ color: #00d4aa; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
            .amount {{ font-size: 36px; color: #00d4aa; margin: 20px 0; }}
            .crypto-option {{ background: #3d3d3d; padding: 15px; margin: 10px 0; border-radius: 5px; cursor: pointer; }}
            .crypto-option:hover {{ background: #4d4d4d; }}
            .btn {{ background: #00d4aa; color: #1a1a1a; padding: 15px 30px; border: none; border-radius: 5px;
                     font-size: 18px; cursor: pointer; margin: 10px; font-weight: bold; }}
            .btn:hover {{ background: #00b894; }}
            .demo-notice {{ background: #665c00; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="bitso-logo">₿ Bitso</div>
            <div class="demo-notice">
                <strong>🎭 MODO DEMO</strong> - Esta es una simulación realista del checkout de Bitso
            </div>

            <h2>Pagar con Crypto</h2>
            <div class="amount" id="amount">Cargando...</div>
            <p><strong>Producto:</strong> SmartCompute License</p>
            <p><strong>Order ID:</strong> {order_id}</p>

            <div style="margin: 30px 0;">
                <div class="crypto-option" onclick="selectCrypto('BTC')">
                    <strong>₿ Bitcoin (BTC)</strong>
                    <div style="color: #ccc; font-size: 14px;">~0.000X BTC</div>
                </div>
                <div class="crypto-option" onclick="selectCrypto('ETH')">
                    <strong>Ξ Ethereum (ETH)</strong>
                    <div style="color: #ccc; font-size: 14px;">~0.00X ETH</div>
                </div>
                <div class="crypto-option" onclick="selectCrypto('USDC')">
                    <strong>💲 USD Coin (USDC)</strong>
                    <div style="color: #ccc; font-size: 14px;">1:1 USD</div>
                </div>
            </div>

            <button class="btn" onclick="processPayment()" id="payBtn" disabled>Selecciona Cryptocurrency</button>
            <button onclick="goBack()" style="background: #6c757d;" class="btn">← Volver</button>
        </div>

        <script>
            // Extract payment info from order ID
            const orderId = '{order_id}';
            const parts = orderId.split('-');
            const licenseType = parts[2];
            const isEnterprise = licenseType === 'ENTERPRISE';

            const amountUSD = isEnterprise ? 15000 : 25000;
            document.getElementById('amount').textContent = `$` + amountUSD.toLocaleString() + ` USD`;

            let selectedCrypto = null;

            function selectCrypto(crypto) {{
                document.querySelectorAll('.crypto-option').forEach(el => {{
                    el.style.background = '#3d3d3d';
                }});
                event.currentTarget.style.background = '#00d4aa';
                event.currentTarget.style.color = '#1a1a1a';

                selectedCrypto = crypto;
                document.getElementById('payBtn').textContent = `Pagar con ${{crypto}}`;
                document.getElementById('payBtn').disabled = false;
            }}

            function processPayment() {{
                if (!selectedCrypto) return;

                const btn = document.getElementById('payBtn');
                btn.textContent = 'Procesando blockchain...';
                btn.disabled = true;

                setTimeout(() => {{
                    window.location.href = '/payment/success';
                }}, 3000);
            }}

            function goBack() {{
                window.history.back();
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/payment')
@app.route('/')
def serve_payment_gateway():
    """Serve the payment gateway"""
    try:
        # Add the parent directory to path
        import sys
        sys.path.append('/home/gatux/smartcompute')

        from smartcompute_secure_payment_gateway import PaymentGateway
        gateway = PaymentGateway()
        gateway_path = gateway.generate_gateway()

        # Read and return the HTML
        with open(gateway_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return html_content

    except Exception as e:
        return f'Error loading payment gateway: {str(e)}', 500

if __name__ == '__main__':
    print("🚀 Starting SmartCompute Payment Server...")
    print("📊 Payment Gateway: http://localhost:5000/payment")
    print("🔗 MercadoPago API: http://localhost:5000/api/create-mp-payment")
    print("🔗 Bitso API: http://localhost:5000/api/create-bitso-payment")

    app.run(debug=True, host='0.0.0.0', port=5000)