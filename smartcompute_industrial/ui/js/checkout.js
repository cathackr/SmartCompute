/**
 * SmartCompute Checkout JavaScript
 * Handles payment method selection and processing
 */

class SmartComputeCheckout {
    constructor() {
        this.selectedPlan = null;
        this.selectedPaymentMethod = null;
        this.planPricing = {
            'enterprise-annual': { 
                name: 'SmartCompute Enterprise', 
                price: 200, 
                period: 'año',
                features: [
                    '✅ IA avanzada para análisis predictivo',
                    '✅ APIs empresariales completas', 
                    '✅ Dashboard personalizable',
                    '✅ Soporte técnico prioritario'
                ]
            },
            'enterprise-biannual': { 
                name: 'SmartCompute Enterprise', 
                price: 400, 
                period: '2 años',
                features: [
                    '✅ IA avanzada para análisis predictivo',
                    '✅ APIs empresariales completas', 
                    '✅ Dashboard personalizable',
                    '✅ Soporte técnico prioritario',
                    '✅ 65% de descuento'
                ]
            },
            'enterprise-premium': { 
                name: 'SmartCompute Enterprise Premium', 
                price: 750, 
                period: 'año',
                features: [
                    '✅ Todo de Enterprise +',
                    '✅ Consultoría personalizada',
                    '✅ Integración de sistemas custom',
                    '✅ SLA garantizado 99.9%'
                ]
            },
            'industrial-full': { 
                name: 'SmartCompute Industrial', 
                price: 4000, 
                period: '3 años',
                features: [
                    '✅ Monitoreo de protocolos industriales',
                    '✅ Detección de conflictos en tiempo real', 
                    '✅ Análisis de dispositivos PLCs/HMIs',
                    '✅ Consultoría de implementación incluida',
                    '✅ Certificaciones ISA/IEC 62443'
                ]
            },
            'industrial-installments': { 
                name: 'SmartCompute Industrial', 
                price: 1667, 
                period: 'año (3 cuotas)',
                features: [
                    '✅ Monitoreo de protocolos industriales',
                    '✅ Detección de conflictos en tiempo real', 
                    '✅ Análisis de dispositivos PLCs/HMIs',
                    '✅ Implementación escalonada',
                    '✅ Certificaciones ISA/IEC 62443'
                ]
            }
        };
        
        this.init();
    }

    init() {
        this.loadPlanFromURL();
        this.setupEventListeners();
        this.updatePlanDisplay();
    }

    loadPlanFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        this.selectedPlan = urlParams.get('plan') || 'enterprise-annual';
    }

    setupEventListeners() {
        // Payment method selection
        const paymentOptions = document.querySelectorAll('.payment-option');
        paymentOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectPaymentMethod(option);
            });
        });

        // Radio button changes
        const radioButtons = document.querySelectorAll('input[name="paymentMethod"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const option = e.target.closest('.payment-option');
                this.selectPaymentMethod(option);
            });
        });

        // Process payment button
        const processBtn = document.getElementById('processPaymentBtn');
        processBtn.addEventListener('click', () => {
            this.processPayment();
        });

        // Form validation
        const form = document.getElementById('checkoutForm');
        const inputs = form.querySelectorAll('input[required], select[required]');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                this.validateForm();
            });
        });

        // Modal close
        const modalClose = document.getElementById('modalClose');
        modalClose.addEventListener('click', () => {
            this.closeModal();
        });
    }

    selectPaymentMethod(option) {
        // Remove previous selection
        document.querySelectorAll('.payment-option').forEach(opt => {
            opt.classList.remove('selected');
        });

        // Add selection to clicked option
        option.classList.add('selected');
        
        // Update radio button
        const radio = option.querySelector('input[type="radio"]');
        if (radio) {
            radio.checked = true;
            this.selectedPaymentMethod = radio.value;
        }

        // Update button text
        this.updatePaymentButton();
    }

    updatePlanDisplay() {
        const plan = this.planPricing[this.selectedPlan];
        if (!plan) return;

        document.getElementById('planName').textContent = plan.name;
        document.getElementById('planPrice').textContent = `$${plan.price} USD/${plan.period}`;
        
        const featuresContainer = document.getElementById('planFeatures');
        featuresContainer.innerHTML = '<ul>' + 
            plan.features.map(feature => `<li>${feature}</li>`).join('') + 
            '</ul>';

        document.getElementById('subtotal').textContent = `$${plan.price}.00 USD`;
        document.getElementById('total').textContent = `$${plan.price}.00 USD`;
        
        // Update pay button
        document.getElementById('payButtonPrice').textContent = `$${plan.price} USD`;
    }

    updatePaymentButton() {
        const buttonText = document.getElementById('payButtonText');
        const methodLabels = {
            'mercadopago': 'Pagar con MercadoPago',
            'bitso': 'Pagar con Crypto',
            'international': 'Pagar Internacional'
        };

        if (this.selectedPaymentMethod) {
            buttonText.textContent = methodLabels[this.selectedPaymentMethod] || 'Continuar con el Pago';
        }
    }

    validateForm() {
        const form = document.getElementById('checkoutForm');
        const requiredInputs = form.querySelectorAll('input[required], select[required]');
        const processBtn = document.getElementById('processPaymentBtn');
        
        let allValid = true;
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                allValid = false;
            }
        });

        // Check checkboxes
        const acceptTerms = document.getElementById('acceptTerms').checked;
        const acceptRefund = document.getElementById('acceptRefund').checked;
        
        if (!acceptTerms || !acceptRefund || !this.selectedPaymentMethod) {
            allValid = false;
        }

        processBtn.disabled = !allValid;
    }

    async processPayment() {
        if (!this.selectedPaymentMethod) {
            alert('Por favor selecciona un método de pago');
            return;
        }

        this.showLoading(true);

        try {
            const formData = this.getFormData();
            
            switch (this.selectedPaymentMethod) {
                case 'mercadopago':
                    await this.processMercadoPago(formData);
                    break;
                case 'bitso':
                    await this.processBitso(formData);
                    break;
                case 'international':
                    await this.processInternational(formData);
                    break;
                default:
                    throw new Error('Método de pago no válido');
            }
        } catch (error) {
            console.error('Error processing payment:', error);
            alert('Error al procesar el pago. Por favor intenta nuevamente.');
        } finally {
            this.showLoading(false);
        }
    }

    getFormData() {
        const plan = this.planPricing[this.selectedPlan];
        
        return {
            plan: this.selectedPlan,
            planName: plan.name,
            amount: plan.price,
            currency: this.selectedPaymentMethod === 'mercadopago' ? 'ARS' : 'USD',
            customer: {
                name: document.getElementById('customerName').value,
                email: document.getElementById('customerEmail').value,
                company: document.getElementById('companyName').value,
                country: document.getElementById('country').value
            },
            paymentMethod: this.selectedPaymentMethod
        };
    }

    async processMercadoPago(formData) {
        this.updateLoadingText('Conectando con MercadoPago...');

        // Convert USD to ARS (approximate rate)
        const usdToArs = 800; // This should come from your API
        const amountARS = Math.round(formData.amount * usdToArs);

        const response = await fetch('/api/payments/mercadopago/create-preference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...formData,
                amount: amountARS,
                currency: 'ARS'
            })
        });

        const result = await response.json();
        
        if (result.success) {
            this.showPaymentModal('MercadoPago', result.checkoutUrl);
        } else {
            throw new Error(result.error || 'Error creating MercadoPago preference');
        }
    }

    async processBitso(formData) {
        this.updateLoadingText('Generando dirección crypto...');

        const response = await fetch('/api/payments/bitso/create-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (result.success) {
            this.showCryptoPayment(result.paymentData);
        } else {
            throw new Error(result.error || 'Error creating crypto payment');
        }
    }

    async processInternational(formData) {
        this.updateLoadingText('Generando instrucciones de pago...');

        const response = await fetch('/api/payments/international/create-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (result.success) {
            this.showInternationalInstructions(result.paymentInstructions);
        } else {
            throw new Error(result.error || 'Error creating international payment');
        }
    }

    showPaymentModal(title, content) {
        document.getElementById('modalTitle').textContent = title;
        
        if (typeof content === 'string' && content.startsWith('http')) {
            // It's a URL, create iframe
            document.getElementById('modalBody').innerHTML = 
                `<iframe src="${content}" width="100%" height="500" style="border: none; border-radius: 8px;"></iframe>`;
        } else {
            // It's HTML content
            document.getElementById('modalBody').innerHTML = content;
        }
        
        document.getElementById('paymentModal').style.display = 'flex';
    }

    showCryptoPayment(paymentData) {
        const cryptoContent = `
            <div class="crypto-payment">
                <h4>Pagar con ${paymentData.cryptocurrency}</h4>
                <div class="crypto-details">
                    <div class="crypto-amount">
                        <label>Cantidad a enviar:</label>
                        <div class="amount-display">
                            <span class="crypto-value">${paymentData.cryptoAmount}</span>
                            <span class="crypto-symbol">${paymentData.cryptocurrency}</span>
                        </div>
                    </div>
                    
                    <div class="crypto-address">
                        <label>Dirección de destino:</label>
                        <div class="address-container">
                            <code class="crypto-address-text">${paymentData.address}</code>
                            <button onclick="navigator.clipboard.writeText('${paymentData.address}')" class="copy-btn">📋 Copiar</button>
                        </div>
                    </div>
                    
                    <div class="qr-code">
                        <img src="${paymentData.qrCode}" alt="QR Code" style="width: 200px; height: 200px;">
                        <p>Escanea con tu wallet</p>
                    </div>
                    
                    <div class="payment-timer">
                        ⏰ Este pago expira en: <span id="countdown">15:00</span>
                    </div>
                    
                    <div class="payment-status">
                        <p>Estado: <span id="paymentStatus">Esperando pago...</span></p>
                        <div class="status-indicator waiting"></div>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p><strong>⚠️ Importante:</strong></p>
                    <ul style="margin-left: 20px; color: #666;">
                        <li>Envía exactamente la cantidad mostrada</li>
                        <li>Usa la dirección proporcionada</li>
                        <li>El pago será confirmado automáticamente</li>
                        <li>Recibirás un email de confirmación</li>
                    </ul>
                </div>
            </div>
        `;
        
        this.showPaymentModal('Pago con Criptomonedas', cryptoContent);
        
        // Start countdown timer
        this.startPaymentTimer(15 * 60); // 15 minutes
        
        // Start payment monitoring
        this.monitorCryptoPayment(paymentData.paymentId);
    }

    showInternationalInstructions(instructions) {
        const intlContent = `
            <div class="international-payment">
                <h4>Instrucciones de Pago Internacional</h4>
                <div class="payment-methods">
                    
                    <div class="payment-method-section">
                        <h5>🏦 Transferencia Bancaria Internacional (SWIFT)</h5>
                        <div class="bank-details">
                            <p><strong>Beneficiario:</strong> ${instructions.swift.beneficiary}</p>
                            <p><strong>Banco:</strong> ${instructions.swift.bank}</p>
                            <p><strong>SWIFT Code:</strong> ${instructions.swift.swiftCode}</p>
                            <p><strong>Cuenta:</strong> ${instructions.swift.accountNumber}</p>
                            <p><strong>Referencia:</strong> ${instructions.reference}</p>
                        </div>
                    </div>
                    
                    <div class="payment-method-section">
                        <h5>💸 PayPal</h5>
                        <p>Envía <strong>$${instructions.amount} USD</strong> a:</p>
                        <p><strong>${instructions.paypal.email}</strong></p>
                        <p><strong>Referencia:</strong> ${instructions.reference}</p>
                    </div>
                    
                    <div class="payment-method-section">
                        <h5>💱 Wise (ex TransferWise)</h5>
                        <p>Busca: <strong>${instructions.wise.email}</strong></p>
                        <p><strong>Cantidad:</strong> $${instructions.amount} USD</p>
                        <p><strong>Referencia:</strong> ${instructions.reference}</p>
                    </div>
                    
                </div>
                
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p><strong>📋 Después del pago:</strong></p>
                    <ul style="margin-left: 20px; color: #666;">
                        <li>Envía el comprobante a: <strong>payments@smartcompute.ar</strong></li>
                        <li>Incluye la referencia: <strong>${instructions.reference}</strong></li>
                        <li>Procesamos el pago en 1-2 días hábiles</li>
                        <li>Recibirás acceso por email</li>
                    </ul>
                </div>
            </div>
        `;
        
        this.showPaymentModal('Pago Internacional', intlContent);
    }

    startPaymentTimer(seconds) {
        const countdownEl = document.getElementById('countdown');
        if (!countdownEl) return;

        const timer = setInterval(() => {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            
            countdownEl.textContent = 
                `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
            
            seconds--;
            
            if (seconds < 0) {
                clearInterval(timer);
                countdownEl.textContent = 'EXPIRADO';
                countdownEl.style.color = '#e74c3c';
            }
        }, 1000);
    }

    async monitorCryptoPayment(paymentId) {
        const statusEl = document.getElementById('paymentStatus');
        const indicator = document.querySelector('.status-indicator');
        
        const checkStatus = async () => {
            try {
                const response = await fetch(`/api/payments/status/${paymentId}`);
                const result = await response.json();
                
                if (result.status === 'confirmed') {
                    statusEl.textContent = '✅ Pago confirmado!';
                    statusEl.style.color = '#27ae60';
                    indicator.className = 'status-indicator confirmed';
                    
                    setTimeout(() => {
                        window.location.href = `/success?payment=${paymentId}`;
                    }, 2000);
                    
                    return true;
                } else if (result.status === 'expired') {
                    statusEl.textContent = '❌ Pago expirado';
                    statusEl.style.color = '#e74c3c';
                    indicator.className = 'status-indicator expired';
                    return true;
                }
            } catch (error) {
                console.error('Error checking payment status:', error);
            }
            
            return false;
        };
        
        // Check immediately
        const completed = await checkStatus();
        if (!completed) {
            // Then check every 30 seconds
            const statusTimer = setInterval(async () => {
                const completed = await checkStatus();
                if (completed) {
                    clearInterval(statusTimer);
                }
            }, 30000);
        }
    }

    showLoading(show, text = 'Procesando pago seguro...') {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            document.getElementById('loadingText').textContent = text;
            overlay.style.display = 'flex';
        } else {
            overlay.style.display = 'none';
        }
    }

    updateLoadingText(text) {
        document.getElementById('loadingText').textContent = text;
    }

    closeModal() {
        document.getElementById('paymentModal').style.display = 'none';
    }
}

// Initialize checkout when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.checkout = new SmartComputeCheckout();
});

// Add some utility CSS for crypto payment
const style = document.createElement('style');
style.textContent = `
    .crypto-payment {
        text-align: center;
    }
    
    .crypto-details {
        margin: 20px 0;
    }
    
    .crypto-amount {
        margin-bottom: 20px;
    }
    
    .amount-display {
        font-size: 24px;
        font-weight: bold;
        color: #27ae60;
        margin: 10px 0;
    }
    
    .crypto-address {
        margin-bottom: 20px;
    }
    
    .address-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 10px 0;
    }
    
    .crypto-address-text {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 12px;
        word-break: break-all;
        flex: 1;
    }
    
    .copy-btn {
        background: #3498db;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
    }
    
    .payment-timer {
        background: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 6px;
        margin: 20px 0;
        font-weight: bold;
    }
    
    .payment-status {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #ffc107;
        animation: pulse 2s infinite;
    }
    
    .status-indicator.confirmed {
        background: #27ae60;
        animation: none;
    }
    
    .status-indicator.expired {
        background: #e74c3c;
        animation: none;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .payment-method-section {
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .payment-method-section h5 {
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .bank-details p {
        margin: 5px 0;
        font-family: monospace;
    }
`;

document.head.appendChild(style);