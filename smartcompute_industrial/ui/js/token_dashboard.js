/**
 * SmartCompute Token Dashboard JavaScript
 * Interactive dashboard with real-time updates and customization
 */

class TokenDashboard {
    constructor() {
        this.currentUser = 'default';
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.preferences = {};
        this.isCustomizationOpen = false;
        
        // API endpoints
        this.apiBase = '/api';
        this.endpoints = {
            metrics: `${this.apiBase}/metrics`,
            preferences: `${this.apiBase}/preferences`,
            providers: `${this.apiBase}/providers`
        };
        
        // Initialize dashboard
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing SmartCompute Token Dashboard');
        
        try {
            // Load user preferences
            await this.loadUserPreferences();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize charts
            this.initializeCharts();
            
            // Load initial data
            await this.loadDashboardData();
            
            // Setup customization panel
            this.setupCustomizationPanel();
            
            // Start auto-refresh
            this.startAutoRefresh();
            
            console.log('✅ Dashboard initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize dashboard:', error);
            this.showNotification('Error', 'Failed to initialize dashboard', 'error');
        }
    }
    
    setupEventListeners() {
        // Settings button
        const settingsBtn = document.getElementById('settingsBtn');
        settingsBtn?.addEventListener('click', () => this.toggleCustomizationPanel());
        
        // Panel close button
        const panelClose = document.getElementById('panelClose');
        panelClose?.addEventListener('click', () => this.closeCustomizationPanel());
        
        // Time range selector
        const costTimeRange = document.getElementById('costTimeRange');
        costTimeRange?.addEventListener('change', (e) => this.updateCostChart(e.target.value));
        
        // Language buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.changeLanguage(e.target.dataset.lang));
        });
        
        // Unit selectors
        document.querySelectorAll('.unit-select').forEach(select => {
            select.addEventListener('change', (e) => 
                this.changeUnit(e.target.dataset.metric, e.target.value)
            );
        });
        
        // Action buttons
        const resetBtn = document.getElementById('resetPreferences');
        resetBtn?.addEventListener('click', () => this.resetPreferences());
        
        const exportBtn = document.getElementById('exportPreferences');
        exportBtn?.addEventListener('click', () => this.exportPreferences());
        
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('customizationPanel');
            const settingsBtn = document.getElementById('settingsBtn');
            
            if (this.isCustomizationOpen && 
                !panel.contains(e.target) && 
                !settingsBtn.contains(e.target)) {
                this.closeCustomizationPanel();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isCustomizationOpen) {
                this.closeCustomizationPanel();
            }
        });
    }
    
    async loadUserPreferences() {
        try {
            // For demo purposes, use localStorage
            const stored = localStorage.getItem(`smartcompute_prefs_${this.currentUser}`);
            if (stored) {
                this.preferences = JSON.parse(stored);
                this.applyPreferences();
            } else {
                // Set default preferences
                this.preferences = {
                    language: 'spanish',
                    currency: 'usd',
                    temperature: 'celsius',
                    time: 'seconds',
                    labels: {}
                };
            }
        } catch (error) {
            console.warn('Failed to load preferences:', error);
            this.preferences = { language: 'spanish', labels: {} };
        }
    }
    
    async saveUserPreferences() {
        try {
            localStorage.setItem(
                `smartcompute_prefs_${this.currentUser}`, 
                JSON.stringify(this.preferences)
            );
            return true;
        } catch (error) {
            console.error('Failed to save preferences:', error);
            return false;
        }
    }
    
    applyPreferences() {
        // Apply language
        if (this.preferences.language) {
            this.updateLanguageButtons(this.preferences.language);
        }
        
        // Apply unit preferences
        ['currency', 'temperature', 'time'].forEach(unit => {
            if (this.preferences[unit]) {
                const select = document.querySelector(`[data-metric="${unit}"]`);
                if (select) select.value = this.preferences[unit];
            }
        });
        
        // Apply custom labels
        Object.entries(this.preferences.labels || {}).forEach(([key, value]) => {
            const element = document.querySelector(`[data-key="${key}"]`);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    initializeCharts() {
        // Cost chart
        const costCtx = document.getElementById('costChart');
        if (costCtx) {
            this.charts.cost = new Chart(costCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Costo por Hora ($)',
                        data: [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Model usage chart
        const modelCtx = document.getElementById('modelChart');
        if (modelCtx) {
            this.charts.model = new Chart(modelCtx, {
                type: 'doughnut',
                data: {
                    labels: ['GPT-4', 'GPT-3.5', 'Claude-3', 'Otros'],
                    datasets: [{
                        data: [45, 30, 20, 5],
                        backgroundColor: [
                            '#3498db',
                            '#2ecc71',
                            '#f39c12',
                            '#e74c3c'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
            
            // Create custom legend
            this.createModelLegend();
        }
    }
    
    createModelLegend() {
        const legendContainer = document.getElementById('modelLegend');
        const colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c'];
        const labels = ['GPT-4', 'GPT-3.5', 'Claude-3', 'Otros'];
        
        legendContainer.innerHTML = labels.map((label, index) => `
            <div class="legend-item">
                <div class="legend-color" style="background-color: ${colors[index]}"></div>
                <span>${label}</span>
            </div>
        `).join('');
    }
    
    async loadDashboardData() {
        this.showLoading(true);
        
        try {
            // Simulate API calls with mock data for demo
            const mockData = await this.generateMockData();
            
            // Update metrics
            this.updateMetrics(mockData.metrics);
            
            // Update charts
            this.updateCharts(mockData.charts);
            
            // Update provider status
            this.updateProviderStatus(mockData.providers);
            
            // Update transparency indicator
            this.updateTransparencyIndicator(mockData.transparency);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showNotification('Error', 'Failed to load dashboard data', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async generateMockData() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const now = new Date();
        const hours = Array.from({length: 24}, (_, i) => {
            const hour = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);
            return hour.getHours() + ':00';
        });
        
        const costs = hours.map(() => Math.random() * 5 + 1);
        
        return {
            metrics: {
                dailyCost: 24.50 + Math.random() * 10,
                efficiency: 94 + Math.random() * 5,
                tokenCount: 1240 + Math.floor(Math.random() * 100),
                responseTime: 1.2 + Math.random() * 0.5
            },
            charts: {
                cost: {
                    labels: hours,
                    data: costs
                },
                model: {
                    labels: ['GPT-4', 'GPT-3.5', 'Claude-3', 'Otros'],
                    data: [45, 30, 20, 5]
                }
            },
            providers: {
                openai: {
                    status: 'online',
                    apiStatus: 'connected',
                    accuracy: '99.2%',
                    lastSync: '2 min'
                },
                anthropic: {
                    status: 'learning',
                    apiStatus: 'learning_mode',
                    accuracy: '94.1% ± 3%',
                    improvement: '+1.2% esta semana'
                }
            },
            transparency: {
                status: 'realtime',
                message: 'Datos en tiempo real'
            }
        };
    }
    
    updateMetrics(metrics) {
        // Convert values based on user preferences
        const currency = this.preferences.currency || 'usd';
        const timeUnit = this.preferences.time || 'seconds';
        
        // Daily cost
        const dailyCostElement = document.getElementById('dailyCost');
        if (dailyCostElement) {
            const convertedCost = this.convertCurrency(metrics.dailyCost, currency);
            dailyCostElement.textContent = convertedCost;
        }
        
        // Efficiency
        const efficiencyElement = document.getElementById('efficiency');
        if (efficiencyElement) {
            efficiencyElement.textContent = Math.round(metrics.efficiency) + '%';
        }
        
        // Token count
        const tokenCountElement = document.getElementById('tokenCount');
        if (tokenCountElement) {
            tokenCountElement.textContent = metrics.tokenCount.toLocaleString();
        }
        
        // Response time
        const responseTimeElement = document.getElementById('responseTime');
        if (responseTimeElement) {
            const convertedTime = this.convertTime(metrics.responseTime, timeUnit);
            responseTimeElement.textContent = convertedTime;
        }
        
        // Update metric changes (simulate)
        this.updateMetricChanges();
    }
    
    updateMetricChanges() {
        const changes = [
            { id: 'costChange', value: '+12%', type: 'positive' },
            { id: 'efficiencyChange', value: '+2%', type: 'positive' },
            { id: 'tokenChange', value: '+15', type: 'neutral' },
            { id: 'responseChange', value: '-0.3s', type: 'positive' }
        ];
        
        changes.forEach(change => {
            const element = document.getElementById(change.id);
            if (element) {
                element.textContent = change.value;
                element.className = `metric-change ${change.type}`;
            }
        });
    }
    
    updateCharts(chartData) {
        // Update cost chart
        if (this.charts.cost) {
            this.charts.cost.data.labels = chartData.cost.labels;
            this.charts.cost.data.datasets[0].data = chartData.cost.data;
            this.charts.cost.update('none');
        }
        
        // Update model chart
        if (this.charts.model) {
            this.charts.model.data.datasets[0].data = chartData.model.data;
            this.charts.model.update('none');
        }
    }
    
    updateProviderStatus(providers) {
        Object.entries(providers).forEach(([provider, data]) => {
            const card = document.querySelector(`[data-provider="${provider}"]`);
            if (!card) return;
            
            // Update status dot
            const statusDot = card.querySelector('.provider-status');
            if (statusDot) {
                statusDot.className = `provider-status ${data.status}`;
            }
            
            // Update details
            const details = card.querySelectorAll('.detail-value');
            details.forEach((detail, index) => {
                switch (index) {
                    case 0: // API Status
                        detail.textContent = data.apiStatus === 'connected' ? 'Conectado' : 'Modo aprendizaje';
                        detail.className = `detail-value ${data.apiStatus === 'connected' ? 'api-connected' : 'learning-mode'}`;
                        break;
                    case 1: // Accuracy
                        detail.textContent = data.accuracy;
                        break;
                    case 2: // Last sync or improvement
                        detail.textContent = data.lastSync || data.improvement;
                        break;
                }
            });
        });
    }
    
    updateTransparencyIndicator(transparency) {
        const indicator = document.getElementById('indicatorDot');
        const text = document.getElementById('indicatorText');
        
        if (indicator && text) {
            indicator.className = `indicator-dot ${transparency.status === 'learning' ? 'learning' : ''}`;
            text.textContent = transparency.message;
        }
    }
    
    convertCurrency(amount, targetCurrency) {
        const rates = {
            usd: { symbol: '$', rate: 1.0 },
            eur: { symbol: '€', rate: 0.85 },
            mxn: { symbol: 'MX$', rate: 18.0 },
            cop: { symbol: 'COP$', rate: 4000.0 }
        };
        
        const currency = rates[targetCurrency] || rates.usd;
        const converted = amount * currency.rate;
        
        return currency.symbol + converted.toFixed(2);
    }
    
    convertTime(timeInSeconds, targetUnit) {
        const conversions = {
            milliseconds: { factor: 1000, symbol: 'ms' },
            seconds: { factor: 1, symbol: 's' },
            minutes: { factor: 1/60, symbol: 'min' }
        };
        
        const conversion = conversions[targetUnit] || conversions.seconds;
        const converted = timeInSeconds * conversion.factor;
        
        return converted.toFixed(converted < 1 ? 3 : 1) + conversion.symbol;
    }
    
    setupCustomizationPanel() {
        this.populateLabelCustomization();
    }
    
    populateLabelCustomization() {
        const labelList = document.getElementById('labelList');
        if (!labelList) return;
        
        const defaultLabels = {
            'cost': 'Gastos Hoy',
            'efficiency': 'Eficiencia',
            'tokens': 'Tokens',
            'response_time': 'Respuesta',
            'cost_analysis': 'Análisis de Costos',
            'model_usage': 'Uso por Modelo',
            'budget_status': 'Estado del Presupuesto',
            'optimization_suggestions': 'Sugerencias de Optimización',
            'provider_status': 'Estado de Proveedores'
        };
        
        labelList.innerHTML = Object.entries(defaultLabels).map(([key, defaultValue]) => {
            const currentValue = this.preferences.labels[key] || defaultValue;
            return `
                <div class="label-item">
                    <label>${defaultValue}:</label>
                    <input type="text" class="label-input" 
                           data-key="${key}" 
                           value="${currentValue}"
                           placeholder="${defaultValue}">
                </div>
            `;
        }).join('');
        
        // Add event listeners to label inputs
        labelList.querySelectorAll('.label-input').forEach(input => {
            input.addEventListener('input', this.debounce((e) => {
                this.updateLabel(e.target.dataset.key, e.target.value);
            }, 500));
        });
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    updateLabel(key, value) {
        if (this.validateLabel(value)) {
            this.preferences.labels[key] = value;
            this.saveUserPreferences();
            
            // Apply immediately
            const element = document.querySelector(`[data-key="${key}"]`);
            if (element) {
                element.textContent = value;
            }
            
            this.showNotification('Éxito', 'Etiqueta actualizada', 'success');
        } else {
            this.showNotification('Error', 'Etiqueta inválida', 'error');
        }
    }
    
    validateLabel(label) {
        if (!label || label.length === 0) return false;
        if (label.length > 50) return false;
        
        // Check for forbidden characters/keywords
        const forbidden = ['<', '>', 'script', 'javascript', 'eval'];
        return !forbidden.some(word => label.toLowerCase().includes(word));
    }
    
    changeLanguage(language) {
        this.preferences.language = language;
        this.saveUserPreferences();
        
        // Update UI
        this.updateLanguageButtons(language);
        this.applyLanguagePreset(language);
        
        this.showNotification('Éxito', `Idioma cambiado a ${language}`, 'success');
    }
    
    updateLanguageButtons(activeLanguage) {
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === activeLanguage);
        });
    }
    
    applyLanguagePreset(language) {
        const translations = {
            spanish: {
                'cost': 'Gastos Hoy',
                'efficiency': 'Eficiencia', 
                'tokens': 'Tokens',
                'response_time': 'Respuesta'
            },
            english: {
                'cost': 'Cost Today',
                'efficiency': 'Efficiency',
                'tokens': 'Tokens', 
                'response_time': 'Response'
            },
            portuguese: {
                'cost': 'Custos Hoje',
                'efficiency': 'Eficiência',
                'tokens': 'Tokens',
                'response_time': 'Resposta'
            }
        };
        
        const langTranslations = translations[language];
        if (langTranslations) {
            Object.entries(langTranslations).forEach(([key, value]) => {
                this.preferences.labels[key] = value;
                const element = document.querySelector(`[data-key="${key}"]`);
                if (element) {
                    element.textContent = value;
                }
            });
            
            this.saveUserPreferences();
            this.populateLabelCustomization(); // Refresh the customization panel
        }
    }
    
    changeUnit(metric, unit) {
        this.preferences[metric] = unit;
        this.saveUserPreferences();
        
        // Trigger data refresh to apply new units
        this.loadDashboardData();
        
        this.showNotification('Éxito', `Unidad de ${metric} actualizada`, 'success');
    }
    
    async resetPreferences() {
        if (confirm('¿Está seguro de que desea restaurar todas las configuraciones por defecto?')) {
            this.preferences = {
                language: 'spanish',
                currency: 'usd',
                temperature: 'celsius',
                time: 'seconds',
                labels: {}
            };
            
            await this.saveUserPreferences();
            this.applyPreferences();
            this.populateLabelCustomization();
            
            // Reload data to apply default units
            this.loadDashboardData();
            
            this.showNotification('Éxito', 'Configuraciones restauradas', 'success');
        }
    }
    
    exportPreferences() {
        const data = {
            exported_at: new Date().toISOString(),
            user_id: this.currentUser,
            preferences: this.preferences
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `smartcompute_preferences_${this.currentUser}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Éxito', 'Configuraciones exportadas', 'success');
    }
    
    toggleCustomizationPanel() {
        if (this.isCustomizationOpen) {
            this.closeCustomizationPanel();
        } else {
            this.openCustomizationPanel();
        }
    }
    
    openCustomizationPanel() {
        const panel = document.getElementById('customizationPanel');
        if (panel) {
            panel.classList.add('open');
            this.isCustomizationOpen = true;
            
            // Focus first input
            setTimeout(() => {
                const firstInput = panel.querySelector('input, select');
                if (firstInput) firstInput.focus();
            }, 300);
        }
    }
    
    closeCustomizationPanel() {
        const panel = document.getElementById('customizationPanel');
        if (panel) {
            panel.classList.remove('open');
            this.isCustomizationOpen = false;
        }
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.toggle('active', show);
        }
    }
    
    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notifications');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        `;
        
        container.appendChild(notification);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
    
    updateCostChart(timeRange) {
        // Generate mock data based on time range
        let labels, data;
        
        switch (timeRange) {
            case 'today':
                labels = Array.from({length: 24}, (_, i) => i + ':00');
                data = labels.map(() => Math.random() * 5 + 1);
                break;
            case 'week':
                labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
                data = labels.map(() => Math.random() * 50 + 20);
                break;
            case 'month':
                labels = Array.from({length: 30}, (_, i) => `${i + 1}`);
                data = labels.map(() => Math.random() * 200 + 100);
                break;
        }
        
        if (this.charts.cost) {
            this.charts.cost.data.labels = labels;
            this.charts.cost.data.datasets[0].data = data;
            this.charts.cost.update();
        }
    }
    
    startAutoRefresh() {
        // Refresh data every 30 seconds
        setInterval(() => {
            if (!this.isCustomizationOpen) { // Don't refresh while user is customizing
                this.loadDashboardData();
            }
        }, this.updateInterval);
        
        console.log(`🔄 Auto-refresh started (${this.updateInterval/1000}s interval)`);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TokenDashboard();
});

// Handle page visibility changes (pause updates when tab is not active)
document.addEventListener('visibilitychange', () => {
    if (window.dashboard) {
        if (document.hidden) {
            console.log('⏸️ Dashboard paused (tab not active)');
        } else {
            console.log('▶️ Dashboard resumed (tab active)');
            window.dashboard.loadDashboardData();
        }
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    if (window.dashboard) {
        window.dashboard.showNotification('Conexión', 'Conectado a internet', 'success');
        window.dashboard.loadDashboardData();
    }
});

window.addEventListener('offline', () => {
    if (window.dashboard) {
        window.dashboard.showNotification('Conexión', 'Sin conexión a internet', 'warning');
    }
});