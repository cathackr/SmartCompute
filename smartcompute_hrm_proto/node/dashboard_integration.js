#!/usr/bin/env node
/**
 * SmartCompute HRM - Dashboard Integration Bridge
 * Conecta el análisis de sistema real con el dashboard operacional
 */

import SmartSystemDetector from './smart_detector.js';
import fs from 'fs/promises';
import path from 'path';
import http from 'http';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class DashboardIntegration {
    constructor() {
        this.detector = new SmartSystemDetector();
        this.realAlerts = [];
        this.systemMetrics = {
            threatScore: 0.0,
            eventsCount: 0,
            falsePositive: 0,
            incidents: 0
        };
        this.isRunning = false;
    }

    async initialize() {
        console.log('🔄 Inicializando integración SmartCompute HRM...');

        // Inicializar detector de sistema real
        await this.detector.initialize();

        // Detectar fuentes disponibles en el sistema
        const availableSources = await this.detector.detectAvailableSources();
        console.log('📡 Fuentes detectadas:', Object.keys(availableSources).length);

        // Crear servidor para servir el dashboard
        this.setupDashboardServer();

        console.log('✅ Integración inicializada correctamente');
    }

    async startRealTimeAnalysis() {
        if (this.isRunning) return;

        this.isRunning = true;
        console.log('🚀 Iniciando análisis en tiempo real...');

        // Análisis continuo cada 10 segundos
        setInterval(async () => {
            await this.performSystemAnalysis();
        }, 10000);

        // Primera ejecución inmediata
        await this.performSystemAnalysis();
    }

    async performSystemAnalysis() {
        try {
            // Ejecutar análisis del sistema
            const systemAnalysis = await this.detector.performComprehensiveAnalysis();

            // Procesar alertas del sistema real
            await this.processRealSystemAlerts(systemAnalysis);

            // Actualizar métricas del dashboard
            await this.updateDashboardMetrics(systemAnalysis);

            // Generar alertas contextuales
            await this.generateContextualAlerts(systemAnalysis);

        } catch (error) {
            console.error('❌ Error en análisis del sistema:', error.message);
        }
    }

    async processRealSystemAlerts(analysis) {
        const timestamp = new Date().toLocaleTimeString();
        const alerts = [];

        // Analizar carga del sistema
        if (analysis.system.cpu_usage > 80) {
            alerts.push({
                id: `CPU-${Date.now()}`,
                time: timestamp,
                score: 3.2,
                fp: 5,
                level: "high",
                description: `CPU usage crítico: ${analysis.system.cpu_usage}%`,
                system: "linux",
                source: "system_monitor",
                details: {
                    cpu_usage: analysis.system.cpu_usage,
                    load_average: analysis.system.load_average,
                    processes: analysis.system.running_processes
                },
                action_needed: "Investigar procesos con alto consumo"
            });
        }

        // Analizar memoria
        const memoryUsagePercent = ((analysis.system.memory.total - analysis.system.memory.available) / analysis.system.memory.total) * 100;
        if (memoryUsagePercent > 85) {
            alerts.push({
                id: `MEM-${Date.now()}`,
                time: timestamp,
                score: 2.8,
                fp: 10,
                level: "medium",
                description: `Uso de memoria elevado: ${memoryUsagePercent.toFixed(1)}%`,
                system: "linux",
                source: "memory_monitor",
                details: {
                    total: `${(analysis.system.memory.total / 1024**3).toFixed(1)}GB`,
                    available: `${(analysis.system.memory.available / 1024**3).toFixed(1)}GB`,
                    usage_percent: memoryUsagePercent.toFixed(1)
                },
                action_needed: "Verificar aplicaciones con alto uso de memoria"
            });
        }

        // Analizar logs del sistema
        for (const logEntry of analysis.logs.system) {
            if (logEntry.level === 'error' || logEntry.level === 'critical') {
                alerts.push({
                    id: `LOG-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
                    time: timestamp,
                    score: logEntry.level === 'critical' ? 4.0 : 2.5,
                    fp: 15,
                    level: logEntry.level === 'critical' ? "critical" : "medium",
                    description: `Error del sistema detectado: ${logEntry.message.substring(0, 60)}...`,
                    system: "linux",
                    source: "system_logs",
                    details: {
                        full_message: logEntry.message,
                        service: logEntry.service,
                        timestamp: logEntry.timestamp
                    },
                    action_needed: "Revisar logs completos del sistema"
                });
            }
        }

        // Analizar procesos sospechosos
        for (const process of analysis.processes.running) {
            // Detectar procesos con comportamiento anómalo
            if (process.cpu > 50 && process.name.includes('unknown')) {
                alerts.push({
                    id: `PROC-${Date.now()}-${process.pid}`,
                    time: timestamp,
                    score: 3.5,
                    fp: 25,
                    level: "high",
                    description: `Proceso sospechoso con alto CPU: ${process.name}`,
                    system: "linux",
                    source: "process_monitor",
                    details: {
                        pid: process.pid,
                        name: process.name,
                        cpu: process.cpu,
                        memory: process.memory,
                        user: process.user
                    },
                    action_needed: "Investigar origen y legitimidad del proceso"
                });
            }
        }

        // Analizar red
        if (analysis.network.connections.length > 100) {
            alerts.push({
                id: `NET-${Date.now()}`,
                time: timestamp,
                score: 2.3,
                fp: 30,
                level: "medium",
                description: `Alto número de conexiones de red: ${analysis.network.connections.length}`,
                system: "linux",
                source: "network_monitor",
                details: {
                    total_connections: analysis.network.connections.length,
                    listening_ports: analysis.network.listening_ports.length,
                    interfaces: analysis.network.interfaces.length
                },
                action_needed: "Analizar conexiones de red activas"
            });
        }

        // Agregar alertas reales a la lista
        this.realAlerts = [...alerts.slice(-10), ...this.realAlerts.slice(0, 5)]; // Mantener últimas 15 alertas

        // Actualizar contadores
        this.systemMetrics.eventsCount += alerts.length;
    }

    async updateDashboardMetrics(analysis) {
        // Calcular threat score basado en análisis real
        let threatScore = 0;

        // Factores que contribuyen al threat score
        const cpuFactor = Math.min(analysis.system.cpu_usage / 100, 1) * 2;
        const memoryFactor = Math.min((analysis.system.memory.total - analysis.system.memory.available) / analysis.system.memory.total, 1) * 1.5;
        const errorLogsFactor = Math.min(analysis.logs.system.filter(l => l.level === 'error').length / 10, 1) * 2;
        const processFactor = Math.min(analysis.processes.running.length / 200, 1) * 1;

        threatScore = cpuFactor + memoryFactor + errorLogsFactor + processFactor;

        this.systemMetrics.threatScore = Math.min(threatScore, 10).toFixed(1);

        // Calcular porcentaje de falsos positivos (mejorado por ML)
        const totalAlerts = this.realAlerts.length;
        const highConfidenceAlerts = this.realAlerts.filter(a => a.fp < 30).length;
        this.systemMetrics.falsePositive = totalAlerts > 0
            ? Math.max(0, ((totalAlerts - highConfidenceAlerts) / totalAlerts * 100)).toFixed(0)
            : 0;

        // Contar incidentes críticos
        this.systemMetrics.incidents = this.realAlerts.filter(a => a.level === 'critical').length;
    }

    async generateContextualAlerts(analysis) {
        // Generar recomendaciones basadas en el análisis real
        const recommendations = [];

        if (analysis.system.cpu_usage > 70) {
            recommendations.push({
                type: 'performance',
                message: `CPU al ${analysis.system.cpu_usage}%. Considerar optimización de procesos.`,
                action: 'Ejecutar "top" para identificar procesos problemáticos'
            });
        }

        if (analysis.system.load_average[0] > analysis.system.cores) {
            recommendations.push({
                type: 'load',
                message: `Load average (${analysis.system.load_average[0]}) supera número de cores (${analysis.system.cores}).`,
                action: 'Revisar procesos en espera o considerar balanceador de carga'
            });
        }

        const diskUsage = analysis.disk?.usage || 0;
        if (diskUsage > 85) {
            recommendations.push({
                type: 'storage',
                message: `Uso de disco al ${diskUsage}%. Limpieza recomendada.`,
                action: 'Ejecutar limpieza de logs y archivos temporales'
            });
        }

        // Agregar recomendaciones al contexto
        this.contextualRecommendations = recommendations;
    }

    setupDashboardServer() {
        const server = http.createServer(async (req, res) => {
            if (req.url === '/api/alerts') {
                // API endpoint para obtener alertas reales
                res.writeHead(200, {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                });
                res.end(JSON.stringify({
                    alerts: this.realAlerts,
                    metrics: this.systemMetrics,
                    recommendations: this.contextualRecommendations || [],
                    timestamp: new Date().toISOString()
                }));
            } else if (req.url === '/api/system-status') {
                // API endpoint para status del sistema
                const systemStatus = await this.detector.getSystemStatus();
                res.writeHead(200, {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                });
                res.end(JSON.stringify(systemStatus));
            } else if (req.url === '/' || req.url === '/dashboard') {
                // Servir dashboard actualizado
                try {
                    const dashboardPath = path.join(__dirname, '../enhanced_dashboard_real.html');
                    const dashboard = await fs.readFile(dashboardPath, 'utf8');
                    res.writeHead(200, { 'Content-Type': 'text/html' });
                    res.end(dashboard);
                } catch (error) {
                    res.writeHead(404, { 'Content-Type': 'text/plain' });
                    res.end('Dashboard no encontrado');
                }
            } else {
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                res.end('Not Found');
            }
        });

        server.listen(3000, () => {
            console.log('🌐 Servidor dashboard iniciado en http://localhost:3000');
        });
    }

    async generateSystemReport() {
        const report = {
            timestamp: new Date().toISOString(),
            system_info: await this.detector.getSystemStatus(),
            alerts_summary: {
                total: this.realAlerts.length,
                critical: this.realAlerts.filter(a => a.level === 'critical').length,
                high: this.realAlerts.filter(a => a.level === 'high').length,
                medium: this.realAlerts.filter(a => a.level === 'medium').length,
                low: this.realAlerts.filter(a => a.level === 'low').length
            },
            metrics: this.systemMetrics,
            top_sources: this.getTopAlertSources(),
            recommendations: this.contextualRecommendations || []
        };

        return report;
    }

    getTopAlertSources() {
        const sources = {};
        this.realAlerts.forEach(alert => {
            sources[alert.source] = (sources[alert.source] || 0) + 1;
        });

        return Object.entries(sources)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([source, count]) => ({ source, count }));
    }

    async stop() {
        this.isRunning = false;
        console.log('⏹️ Análisis detenido');
    }
}

// Función principal
async function main() {
    console.log('🚀 SmartCompute HRM - Dashboard Integration');
    console.log('==========================================');

    const integration = new DashboardIntegration();

    try {
        await integration.initialize();
        await integration.startRealTimeAnalysis();

        // Generar reporte inicial después de 30 segundos
        setTimeout(async () => {
            const report = await integration.generateSystemReport();
            console.log('\n📊 REPORTE INICIAL DEL SISTEMA:');
            console.log('================================');
            console.log(`🖥️  Sistema: ${report.system_info.hostname} (${report.system_info.platform})`);
            console.log(`⏱️  Uptime: ${report.system_info.uptime}`);
            console.log(`🧠 Memoria: ${report.system_info.memory}`);
            console.log(`🚨 Alertas: ${report.alerts_summary.total} total (${report.alerts_summary.critical} críticas)`);
            console.log(`📈 Threat Score: ${report.metrics.threatScore}`);
            console.log('\n🌐 Dashboard disponible en: http://localhost:3000');
            console.log('📡 API alertas en: http://localhost:3000/api/alerts');

            if (report.recommendations.length > 0) {
                console.log('\n💡 RECOMENDACIONES INMEDIATAS:');
                report.recommendations.forEach((rec, i) => {
                    console.log(`   ${i + 1}. [${rec.type.toUpperCase()}] ${rec.message}`);
                });
            }
        }, 30000);

        // Mantener el proceso activo
        process.on('SIGINT', async () => {
            console.log('\n🛑 Deteniendo SmartCompute HRM...');
            await integration.stop();
            process.exit(0);
        });

    } catch (error) {
        console.error('❌ Error fatal:', error.message);
        process.exit(1);
    }
}

// Ejecutar si es llamado directamente
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export { DashboardIntegration };