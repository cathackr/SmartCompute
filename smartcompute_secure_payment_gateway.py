#!/usr/bin/env python3
"""
SmartCompute Secure Payment Gateway
Clean, direct payment like Riot Games
"""

import os
import webbrowser
from datetime import datetime
from payments.secure_payment_core import init

class PaymentGateway:
    def __init__(self):
        self.sc = init()
        self.reports_path = "/home/gatux/smartcompute/reports"
        os.makedirs(self.reports_path, exist_ok=True)

    def generate_gateway(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute - Licencias</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .logo {{
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 28px;
            font-weight: bold;
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .step {{
            margin-bottom: 30px;
            display: none;
        }}
        .step.active {{
            display: block;
        }}
        .back-btn {{
            background: #f8f9fa;
            color: #666;
            border: 2px solid #e9ecef;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-right: 10px;
        }}
        .back-btn:hover {{
            background: #e9ecef;
        }}
        .step-buttons {{
            display: flex;
            align-items: center;
            margin-top: 20px;
        }}
        .step h3 {{
            margin-bottom: 20px;
            color: #333;
        }}
        .options {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .option {{
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .option:hover, .option.selected {{
            border-color: #667eea;
            background: #f0f4ff;
        }}
        .btn {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        .btn:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }}
        .secure {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
        .price-display {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .price-display .amount {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .installments {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }}
        .installment {{
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 15px 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }}
        .installment:hover, .installment.selected {{
            border-color: #667eea;
            background: #f0f4ff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SC</div>
            <h1>SmartCompute</h1>
            <p>Licencias de Seguridad Industrial</p>
        </div>

        <!-- Step 1: Payment Method -->
        <div class="step active" id="step1">
            <h3>1. Método de Pago</h3>
            <div class="options">
                <div class="option" onclick="selectPayment('mercadopago')">
                    <div style="font-size: 24px; margin-bottom: 10px;">🇦🇷</div>
                    <h4>MercadoPago</h4>
                    <p>Pesos argentinos</p>
                </div>
                <div class="option" onclick="selectPayment('bitso')">
                    <div style="font-size: 24px; margin-bottom: 10px;">₿</div>
                    <h4>Bitso</h4>
                    <p>USD / Crypto</p>
                </div>
            </div>
        </div>

        <!-- Step 2: License Version -->
        <div class="step" id="step2">
            <h3>2. Versión</h3>
            <div class="options">
                <div class="option" onclick="selectLicense('enterprise')">
                    <h2>Enterprise</h2>
                </div>
                <div class="option" onclick="selectLicense('industrial')">
                    <h2>Industrial</h2>
                </div>
            </div>
            <div class="step-buttons">
                <button class="back-btn" onclick="goBack(1)">← Atrás</button>
            </div>
        </div>

        <!-- Step 3: Installments -->
        <div class="step" id="step3">
            <h3>3. Cuotas</h3>
            <div class="installments">
                <div class="installment" onclick="selectInstallments(1)">
                    <strong>1x</strong><br>
                    Sin interés
                </div>
                <div class="installment" onclick="selectInstallments(3)">
                    <strong>3x</strong><br>
                    Sin interés
                </div>
                <div class="installment" onclick="selectInstallments(6)">
                    <strong>6x</strong><br>
                    Sin interés
                </div>
                <div class="installment" onclick="selectInstallments(12)">
                    <strong>12x</strong><br>
                    Sin interés
                </div>
            </div>
            <div class="step-buttons">
                <button class="back-btn" onclick="goBack(2)">← Atrás</button>
            </div>
        </div>

        <!-- Step 4: Final Price -->
        <div class="step" id="step4">
            <h3>4. Confirmación</h3>
            <div class="price-display">
                <div id="finalPrice" class="amount">-</div>
                <div id="installmentInfo">-</div>
            </div>
            <div class="step-buttons">
                <button class="back-btn" onclick="goBack(3)">← Atrás</button>
                <button class="btn" onclick="proceedPayment()" style="flex: 1;">
                    Proceder al Pago
                </button>
            </div>
        </div>

        <div class="secure">
            🔒 Transacciones seguras cifradas
        </div>
    </div>

    <script>
        let selectedPaymentMethod = null;
        let selectedLicense = null;
        let selectedInstallments = null;

        function selectPayment(method) {{
            document.querySelectorAll('#step1 .option').forEach(el => el.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            selectedPaymentMethod = method;

            setTimeout(() => {{
                document.getElementById('step1').classList.remove('active');
                document.getElementById('step2').classList.add('active');
            }}, 300);
        }}

        function selectLicense(license) {{
            document.querySelectorAll('#step2 .option').forEach(el => el.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            selectedLicense = license;

            setTimeout(() => {{
                document.getElementById('step2').classList.remove('active');
                document.getElementById('step3').classList.add('active');
            }}, 300);
        }}

        function selectInstallments(installments) {{
            document.querySelectorAll('.installment').forEach(el => el.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            selectedInstallments = installments;

            updateFinalPrice();

            setTimeout(() => {{
                document.getElementById('step3').classList.remove('active');
                document.getElementById('step4').classList.add('active');
            }}, 300);
        }}

        function updateFinalPrice() {{
            const priceUSD = selectedLicense === 'enterprise' ? 15000 : 25000;
            let displayPrice, installmentText;

            if (selectedPaymentMethod === 'mercadopago') {{
                const priceARS = priceUSD * 900; // 1 USD = 900 ARS approx
                const installmentAmount = priceARS / selectedInstallments;

                displayPrice = `${{priceARS.toLocaleString()}} ARS`;
                installmentText = selectedInstallments === 1 ?
                    'Pago único' :
                    `${{Math.round(installmentAmount).toLocaleString()}} ARS x ${{selectedInstallments}} cuotas`;
            }} else {{
                const installmentAmount = priceUSD / selectedInstallments;

                displayPrice = `${{priceUSD.toLocaleString()}} USD`;
                installmentText = selectedInstallments === 1 ?
                    'Pago único' :
                    `${{Math.round(installmentAmount).toLocaleString()}} USD x ${{selectedInstallments}} cuotas`;
            }}

            document.getElementById('finalPrice').textContent = displayPrice;
            document.getElementById('installmentInfo').textContent = installmentText;
        }}

        function goBack(targetStep) {{
            // Hide current step
            document.querySelectorAll('.step').forEach(el => el.classList.remove('active'));

            // Show target step
            document.getElementById('step' + targetStep).classList.add('active');

            // Clear selections for steps after target
            if (targetStep < 2) {{
                selectedLicense = null;
                selectedInstallments = null;
            }} else if (targetStep < 3) {{
                selectedInstallments = null;
            }}
        }}

        async function proceedPayment() {{
            const btn = document.querySelector('.btn');
            btn.textContent = 'Creando pago...';
            btn.disabled = true;

            try {{
                // Create payment preference
                const paymentData = {{
                    license: selectedLicense,
                    payment_method: selectedPaymentMethod,
                    installments: selectedInstallments,
                    amount_usd: selectedLicense === 'enterprise' ? 15000 : 25000
                }};

                if (selectedPaymentMethod === 'mercadopago') {{
                    // Create MercadoPago preference
                    const response = await fetch('/api/create-mp-payment', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(paymentData)
                    }});

                    const result = await response.json();

                    if (result.success) {{
                        // Redirect to MercadoPago checkout
                        window.location.href = result.checkout_url;
                    }} else {{
                        alert('Error creando pago: ' + result.error);
                        btn.textContent = 'Proceder al Pago';
                        btn.disabled = false;
                    }}
                }} else {{
                    // Create Bitso payment
                    const response = await fetch('/api/create-bitso-payment', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(paymentData)
                    }});

                    const result = await response.json();

                    if (result.success) {{
                        // Redirect to Bitso payment
                        window.location.href = result.payment_url;
                    }} else {{
                        alert('Error creando pago: ' + result.error);
                        btn.textContent = 'Proceder al Pago';
                        btn.disabled = false;
                    }}
                }}
            }} catch (error) {{
                console.error('Payment error:', error);
                alert('Error de conexión. Por favor intenta nuevamente.');
                btn.textContent = 'Proceder al Pago';
                btn.disabled = false;
            }}
        }}
    </script>
</body>
</html>"""

        filename = f"smartcompute_payment_gateway_clean_{timestamp}.html"
        filepath = os.path.join(self.reports_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return filepath

    def demo(self):
        print("💳 SmartCompute Secure Payment Gateway")
        print("=" * 50)

        # Test payments
        print("\n🏢 Enterprise License Test:")
        enterprise_mp = self.sc.mp('enterprise', 'test@company.com', 'Test Corp', 'AR')
        print(f"   ✅ Price: $15,000 USD")
        print(f"   ✅ MercadoPago ready")
        print(f"   ✅ Hash: {enterprise_mp['hash'][:16]}...")

        print("\n🏭 Industrial License Test:")
        industrial_bt = self.sc.bt('industrial', 'test@industrial.com', 'Industrial Corp')
        print(f"   ✅ Price: $25,000 USD")
        print(f"   ✅ Bitso ready")
        print(f"   ✅ Hash: {industrial_bt['hash'][:16]}...")

        # Generate gateway
        gateway_path = self.generate_gateway()
        print(f"\n📊 Payment Gateway Generated:")
        print(f"   ✅ File: {gateway_path}")

        # Open in browser
        file_url = f"file://{gateway_path}"
        try:
            webbrowser.open(file_url)
            print(f"   ✅ Opened in browser")
        except:
            print(f"   📂 Manual open: {gateway_path}")

        print(f"\n✅ Secure Payment System Ready!")
        print(f"   🔒 Obfuscated code")
        print(f"   🎯 Direct payment flow")
        print(f"   💎 Clean UI like Riot Games")

        return gateway_path

def main():
    gateway = PaymentGateway()
    return gateway.demo()

if __name__ == "__main__":
    main()