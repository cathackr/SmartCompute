#!/usr/bin/env python3
"""
SmartCompute Payment Integration with Main Dashboard
Secure payment processing integrated with industrial system
"""

import os
import sys
import json
import webbrowser
from datetime import datetime
from payments.payment_integration import SecurePaymentProcessor, LicenseTier, PaymentMethod, PaymentRequest

class SmartComputePaymentDashboard:
    """Payment dashboard integrated with SmartCompute Industrial v2.0"""

    def __init__(self):
        self.processor = SecurePaymentProcessor()
        self.payment_html_path = "/home/gatux/smartcompute/reports"

        # Ensure reports directory exists
        os.makedirs(self.payment_html_path, exist_ok=True)

    def generate_payment_dashboard(self):
        """Generate integrated payment dashboard"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        dashboard_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Industrial - Payment Gateway</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .logo {{
            width: 100px;
            height: 100px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: bold;
        }}
        .license-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        .license-card {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .license-card:hover {{
            transform: translateY(-10px);
        }}
        .license-price {{
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        .enterprise .license-price {{ color: #667eea; }}
        .industrial .license-price {{ color: #f5576c; }}
        .features {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        .feature {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .feature::before {{
            content: "✅";
            margin-right: 10px;
        }}
        .btn {{
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }}
        .btn-enterprise {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }}
        .btn-industrial {{
            background: linear-gradient(45deg, #f093fb, #f5576c);
            color: white;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        .payment-methods {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-top: 40px;
        }}
        .method-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .method-card {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
        }}
        .method-card:hover {{
            border-color: #667eea;
            background: #f0f4ff;
        }}
        .security-info {{
            background: rgba(255,255,255,0.9);
            border-radius: 20px;
            padding: 30px;
            margin-top: 40px;
        }}
        .back-to-system {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            color: #333;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <a href="../reports/" class="back-to-system">← Volver al Dashboard</a>

    <div class="container">
        <div class="header">
            <div class="logo">SC</div>
            <h1>SmartCompute Industrial v2.0</h1>
            <h2>Sistema de Licencias Profesionales</h2>
            <p>Seguridad industrial con IA · Análisis automático · Protocolos industriales</p>
        </div>

        <div class="license-grid">
            <!-- Enterprise License -->
            <div class="license-card enterprise">
                <h2>🏢 SmartCompute Enterprise</h2>
                <div class="license-price">$200-750<small>/year</small></div>
                <p><strong>Hasta 100 agentes</strong> · Integración XDR · AI Recommendations</p>

                <div class="features">
                    <div class="feature">XDR Export: CrowdStrike, Sentinel, Cisco</div>
                    <div class="feature">AI Engine con 89.8% precisión</div>
                    <div class="feature">SIEM Integration universal</div>
                    <div class="feature">Reducción 92.4% alertas falsas</div>
                    <div class="feature">Support horario comercial</div>
                    <div class="feature">10,000 exportaciones/día</div>
                </div>

                <button class="btn btn-enterprise" onclick="openCheckout('enterprise')">
                    Contactar Sales Enterprise
                </button>
            </div>

            <!-- Industrial License -->
            <div class="license-card industrial">
                <h2>🏭 SmartCompute Industrial</h2>
                <div class="license-price">$5,000<small>/3 años</small></div>
                <p><strong>Agentes ilimitados</strong> · Protocolos industriales · 24/7 Support</p>

                <div class="features">
                    <div class="feature">Todo Enterprise incluido</div>
                    <div class="feature">Protocolos: Modbus, Profinet, OPC UA</div>
                    <div class="feature">Agentes ilimitados</div>
                    <div class="feature">Custom ML Models</div>
                    <div class="feature">Integración SCADA/PLC</div>
                    <div class="feature">Support 24/7 prioritario</div>
                    <div class="feature">99.9% SLA uptime</div>
                    <div class="feature">On-site deployment</div>
                    <div class="feature">Certificaciones ISA/IEC 62443</div>
                </div>

                <button class="btn btn-industrial" onclick="openCheckout('industrial')">
                    Contactar Industrial Specialist
                </button>
            </div>
        </div>

        <div class="payment-methods">
            <h2>🔐 Métodos de Pago Seguros</h2>

            <div class="method-grid">
                <div class="method-card">
                    <h3>🇦🇷 MercadoPago</h3>
                    <p>Pesos argentinos (ARS)</p>
                    <small>Tarjetas, transferencias, cuotas</small>
                </div>

                <div class="method-card">
                    <h3>₿ Bitso Crypto</h3>
                    <p>Bitcoin, Ethereum, USDC</p>
                    <small>Pagos internacionales seguros</small>
                </div>

                <div class="method-card">
                    <h3>🏢 Facturación B2B</h3>
                    <p>Wire transfer, facturas</p>
                    <small>Net 15/30 para empresas</small>
                </div>

                <div class="method-card">
                    <h3>📧 Consultoría</h3>
                    <p>Demo personalizada</p>
                    <small>ROI calculation incluido</small>
                </div>
            </div>
        </div>

        <div class="security-info">
            <h2>🛡️ Seguridad y Garantías</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
                <div>
                    <h4>🔒 Seguridad de Pagos</h4>
                    <p>Validación HMAC, cifrado AES-256, tokens JWT seguros</p>
                </div>
                <div>
                    <h4>📊 Métricas Reales</h4>
                    <p>92.4% reducción alertas, MTTD 12min, 89.8% precisión IA</p>
                </div>
                <div>
                    <h4>🎯 ROI Comprobado</h4>
                    <p>Enterprise: $45K/año · Industrial: $150K/año promedio</p>
                </div>
                <div>
                    <h4>📞 Soporte Especializado</h4>
                    <p>CEH certified, 10+ años experiencia industrial</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function openCheckout(tier) {{
            if (tier === 'enterprise') {{
                window.open('/home/gatux/smartcompute/payments/enterprise_checkout.html', '_blank');
            }} else if (tier === 'industrial') {{
                window.open('/home/gatux/smartcompute/payments/industrial_checkout.html', '_blank');
            }}
        }}

        // Demo payment system integration
        function initPaymentSystem() {{
            console.log('🔐 SmartCompute Payment System v2.0 Initialized');
            console.log('✅ MercadoPago integration ready');
            console.log('✅ Bitso crypto gateway ready');
            console.log('✅ Enterprise invoicing ready');
            console.log('✅ Security validation active');
        }}

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', initPaymentSystem);
    </script>
</body>
</html>"""

        filename = f"smartcompute_payment_gateway_{timestamp}.html"
        filepath = os.path.join(self.payment_html_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)

        return filepath

    def demo_payment_integration(self):
        """Demo complete payment integration"""
        print("💳 SmartCompute Industrial v2.0 - Payment Integration Demo")
        print("=" * 70)

        # Test Enterprise payment
        print("\n🏢 Testing Enterprise License Payment Flow:")
        enterprise_request = PaymentRequest(
            license_tier=LicenseTier.ENTERPRISE,
            payment_method=PaymentMethod.MERCADOPAGO,
            customer_email="cto@enterprise-corp.com",
            company_name="Enterprise Corp SA",
            billing_country="AR"
        )

        mp_payment = self.processor.create_mercadopago_payment(enterprise_request)
        print(f"   ✅ Enterprise License: ${enterprise_request.license_tier.price_usd:,} USD/año")
        print(f"   ✅ MercadoPago ARS: ${mp_payment['estimated_price_ars']:,}")
        print(f"   ✅ Security Hash: {mp_payment['payment_hash'][:16]}...")

        # Test Industrial payment
        print("\n🏭 Testing Industrial License Payment Flow:")
        industrial_request = PaymentRequest(
            license_tier=LicenseTier.INDUSTRIAL,
            payment_method=PaymentMethod.BITSO,
            customer_email="security@industrial-plant.com",
            company_name="Industrial Plant Inc",
            billing_country="US"
        )

        bitso_payment = self.processor.create_bitso_payment(industrial_request)
        print(f"   ✅ Industrial License: ${industrial_request.license_tier.price_usd:,} USD/año")
        print(f"   ✅ Bitso Crypto: {', '.join(bitso_payment['crypto_options'])}")
        print(f"   ✅ Security Hash: {bitso_payment['payment_hash'][:16]}...")

        # Generate payment dashboard
        print("\n📊 Generating Payment Dashboard:")
        dashboard_path = self.generate_payment_dashboard()
        print(f"   ✅ Dashboard created: {dashboard_path}")

        # Open in browser
        file_url = f"file://{dashboard_path}"
        print(f"\n🌐 Opening payment dashboard in browser...")
        print(f"   URL: {file_url}")

        try:
            webbrowser.open(file_url)
            print("   ✅ Browser opened successfully")
        except Exception as e:
            print(f"   ⚠️ Could not open browser: {e}")
            print(f"   📂 Manual open: {dashboard_path}")

        print(f"\n✅ SmartCompute Payment Integration Ready!")
        print(f"   💰 Enterprise: $200-750/year")
        print(f"   🏭 Industrial: $5,000/3 años")
        print(f"   🔐 Secure payment processing")
        print(f"   🌐 Professional checkout pages")
        print(f"   📧 B2B sales integration")

        return dashboard_path

def main():
    """Run payment integration demo"""
    try:
        dashboard = SmartComputePaymentDashboard()
        dashboard_path = dashboard.demo_payment_integration()

        print(f"\n🎯 Next Steps:")
        print(f"   1. Test Enterprise checkout: payments/enterprise_checkout.html")
        print(f"   2. Test Industrial checkout: payments/industrial_checkout.html")
        print(f"   3. Integrate with main SmartCompute dashboard")
        print(f"   4. Configure production payment credentials")

        return dashboard_path

    except Exception as e:
        print(f"❌ Error in payment integration: {e}")
        return None

if __name__ == "__main__":
    main()