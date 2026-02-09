#!/usr/bin/env node
/**
 * SmartCompute HRM - Sistema de Detección Inteligente
 * Detecta automáticamente la fuente real de alertas y aprende de los datos del sistema
 */

import fs from 'fs';
import { promises as fsPromises } from 'fs';
import path from 'path';
import os from 'os';
import { spawn, exec } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class SmartSystemDetector {
    constructor() {
        this.systemProfile = {
            os: os.type(),
            platform: os.platform(),
            arch: os.arch(),
            hostname: os.hostname(),
            uptime: os.uptime(),
            loadavg: os.loadavg(),
            totalmem: os.totalmem(),
            freemem: os.freemem(),
            cpus: os.cpus()
        };

        this.detectedSources = new Map();
        this.learningData = [];
        this.hrmModels = new Map();

        this.initializeDetectors();
    }

    async initializeDetectors() {
        console.log('🔍 Inicializando detectores de sistema...');

        // Detectar fuentes disponibles en el sistema actual
        await this.detectAvailableSources();

        // Cargar modelos HRM existentes
        await this.loadHRMModels();

        console.log('✅ Sistema de detección inicializado');
        this.printSystemProfile();
    }

    async detectAvailableSources() {
        const sources = [];

        // 1. Detectar logs del sistema
        await this.detectSystemLogs(sources);

        // 2. Detectar procesos activos
        await this.detectActiveProcesses(sources);

        // 3. Detectar conexiones de red
        await this.detectNetworkConnections(sources);

        // 4. Detectar hardware/sensores
        await this.detectHardwareSensors(sources);

        // 5. Detectar servicios de seguridad
        await this.detectSecurityServices(sources);

        this.detectedSources.set('available_sources', sources);
        return sources;
    }

    async detectSystemLogs(sources) {
        const logPaths = [
            '/var/log/syslog',
            '/var/log/auth.log',
            '/var/log/kern.log',
            '/var/log/daemon.log',
            '/var/log/messages',
            '/var/log/secure',
            '/var/log/audit/audit.log'
        ];

        for (const logPath of logPaths) {
            try {
                if (fs.existsSync(logPath)) {
                    const stats = fs.statSync(logPath);
                    sources.push({
                        type: 'system_log',
                        path: logPath,
                        size: stats.size,
                        modified: stats.mtime,
                        accessible: true,
                        category: 'system_events'
                    });
                }
            } catch (error) {
                sources.push({
                    type: 'system_log',
                    path: logPath,
                    accessible: false,
                    error: error.message,
                    category: 'system_events'
                });
            }
        }
    }

    async detectActiveProcesses(sources) {
        return new Promise((resolve) => {
            exec('ps aux --no-headers', (error, stdout) => {
                if (!error && stdout) {
                    const processes = stdout.split('\n')
                        .filter(line => line.trim())
                        .map(line => {
                            const parts = line.trim().split(/\s+/);
                            return {
                                user: parts[0],
                                pid: parts[1],
                                cpu: parts[2],
                                mem: parts[3],
                                command: parts.slice(10).join(' ')
                            };
                        });

                    // Detectar procesos sospechosos o de seguridad
                    const securityProcesses = processes.filter(p =>
                        p.command.includes('antivirus') ||
                        p.command.includes('firewall') ||
                        p.command.includes('audit') ||
                        p.command.includes('security') ||
                        p.command.includes('monitor')
                    );

                    const suspiciousProcesses = processes.filter(p =>
                        p.command.includes('temp') ||
                        p.command.includes('tmp') ||
                        p.cpu > 80 ||
                        p.mem > 20
                    );

                    sources.push({
                        type: 'process_monitor',
                        total_processes: processes.length,
                        security_processes: securityProcesses.length,
                        suspicious_processes: suspiciousProcesses.length,
                        high_cpu_processes: processes.filter(p => p.cpu > 50).length,
                        category: 'process_analysis',
                        accessible: true
                    });
                }
                resolve();
            });
        });
    }

    async detectNetworkConnections(sources) {
        return new Promise((resolve) => {
            exec('netstat -tuln 2>/dev/null || ss -tuln', (error, stdout) => {
                if (!error && stdout) {
                    const connections = stdout.split('\n')
                        .filter(line => line.includes(':'))
                        .length;

                    sources.push({
                        type: 'network_monitor',
                        active_connections: connections,
                        interfaces: Object.keys(os.networkInterfaces()),
                        category: 'network_analysis',
                        accessible: true
                    });
                }
                resolve();
            });
        });
    }

    async detectHardwareSensors(sources) {
        // Detectar sensores de temperatura, voltaje, etc.
        const sensorPaths = [
            '/sys/class/hwmon',
            '/sys/class/thermal',
            '/proc/acpi',
            '/dev/input'
        ];

        const sensors = [];

        for (const sensorPath of sensorPaths) {
            try {
                if (fs.existsSync(sensorPath)) {
                    const items = fs.readdirSync(sensorPath);
                    sensors.push({
                        path: sensorPath,
                        count: items.length,
                        items: items.slice(0, 5) // Primeros 5 para ejemplo
                    });
                }
            } catch (error) {
                // Sensor no accesible
            }
        }

        if (sensors.length > 0) {
            sources.push({
                type: 'hardware_sensors',
                sensors: sensors,
                category: 'industrial_monitoring',
                accessible: true
            });
        }
    }

    async detectSecurityServices(sources) {
        return new Promise((resolve) => {
            // Detectar servicios de seguridad comunes en Linux
            const securityServices = [
                'fail2ban',
                'ufw',
                'iptables',
                'apparmor',
                'selinux',
                'auditd',
                'ossec',
                'suricata',
                'snort'
            ];

            let detectedServices = 0;
            let checkedServices = 0;

            securityServices.forEach(service => {
                exec(`systemctl is-active ${service} 2>/dev/null`, (error, stdout) => {
                    checkedServices++;
                    if (stdout.trim() === 'active') {
                        detectedServices++;
                    }

                    if (checkedServices === securityServices.length) {
                        sources.push({
                            type: 'security_services',
                            total_checked: securityServices.length,
                            active_services: detectedServices,
                            category: 'security_infrastructure',
                            accessible: true
                        });
                        resolve();
                    }
                });
            });
        });
    }

    async generateRealAlert() {
        const sources = this.detectedSources.get('available_sources') || [];

        // Seleccionar fuente real basada en el sistema actual
        const activeSource = this.selectMostRelevantSource(sources);

        // Leer datos reales de esa fuente
        const realData = await this.extractRealData(activeSource);

        // Generar alerta contextual
        const alert = await this.createContextualAlert(activeSource, realData);

        // Aprender de este evento
        await this.learnFromEvent(alert, activeSource, realData);

        return alert;
    }

    selectMostRelevantSource(sources) {
        // Priorizar fuentes por relevancia de seguridad
        const priorities = {
            'system_log': 10,
            'security_services': 9,
            'process_monitor': 8,
            'network_monitor': 7,
            'hardware_sensors': 6
        };

        const accessibleSources = sources.filter(s => s.accessible);

        if (accessibleSources.length === 0) {
            return this.createMockSource();
        }

        return accessibleSources.sort((a, b) =>
            (priorities[b.type] || 0) - (priorities[a.type] || 0)
        )[0];
    }

    async extractRealData(source) {
        switch (source.type) {
            case 'system_log':
                return await this.readSystemLog(source);
            case 'process_monitor':
                return await this.analyzeProcesses();
            case 'network_monitor':
                return await this.analyzeNetwork();
            case 'hardware_sensors':
                return await this.readSensors(source);
            case 'security_services':
                return await this.checkSecurityStatus();
            default:
                return await this.generateMockData(source);
        }
    }

    async readSystemLog(source) {
        try {
            const data = await fsPromises.readFile(source.path, 'utf8');
            const lines = data.split('\n').slice(-100); // Últimas 100 líneas

            const events = lines
                .filter(line => line.includes('error') || line.includes('failed') || line.includes('denied'))
                .slice(-10); // Últimos 10 eventos relevantes

            return {
                source_type: 'system_log',
                log_file: source.path,
                total_lines: lines.length,
                error_events: events.length,
                sample_events: events.slice(0, 3),
                timestamp: new Date().toISOString(),
                size_mb: (source.size / 1024 / 1024).toFixed(2)
            };
        } catch (error) {
            return {
                source_type: 'system_log',
                error: 'No access to log file',
                log_file: source.path,
                timestamp: new Date().toISOString()
            };
        }
    }

    async analyzeProcesses() {
        return new Promise((resolve) => {
            exec('ps aux --sort=-%cpu | head -20', (error, stdout) => {
                if (error) {
                    resolve({
                        source_type: 'process_monitor',
                        error: error.message,
                        timestamp: new Date().toISOString()
                    });
                    return;
                }

                const processes = stdout.split('\n').slice(1)
                    .filter(line => line.trim())
                    .map(line => {
                        const parts = line.trim().split(/\s+/);
                        return {
                            user: parts[0],
                            pid: parts[1],
                            cpu: parseFloat(parts[2]),
                            mem: parseFloat(parts[3]),
                            command: parts.slice(10).join(' ').substring(0, 50)
                        };
                    });

                const suspicious = processes.filter(p =>
                    p.cpu > 50 ||
                    p.mem > 20 ||
                    p.command.includes('/tmp') ||
                    p.command.includes('python -c') ||
                    p.command.includes('bash -c')
                );

                resolve({
                    source_type: 'process_monitor',
                    total_processes: processes.length,
                    high_cpu_count: processes.filter(p => p.cpu > 10).length,
                    suspicious_processes: suspicious,
                    top_process: processes[0],
                    timestamp: new Date().toISOString()
                });
            });
        });
    }

    async analyzeNetwork() {
        return new Promise((resolve) => {
            exec('netstat -tuln 2>/dev/null || ss -tuln', (error, stdout) => {
                const interfaces = os.networkInterfaces();
                const connections = stdout ? stdout.split('\n').filter(l => l.includes(':')).length : 0;

                resolve({
                    source_type: 'network_monitor',
                    interfaces: Object.keys(interfaces),
                    active_connections: connections,
                    external_ips: this.extractExternalIPs(interfaces),
                    timestamp: new Date().toISOString()
                });
            });
        });
    }

    extractExternalIPs(interfaces) {
        const external = [];
        Object.values(interfaces).flat().forEach(iface => {
            if (!iface.internal && iface.family === 'IPv4') {
                external.push(iface.address);
            }
        });
        return external;
    }

    async readSensors(source) {
        const sensorData = {
            source_type: 'hardware_sensors',
            sensors_available: source.sensors.length,
            temperature_readings: [],
            timestamp: new Date().toISOString()
        };

        // Intentar leer temperatura de CPU
        try {
            await fsPromises.access('/sys/class/thermal/thermal_zone0/temp');
            const temp = await fsPromises.readFile('/sys/class/thermal/thermal_zone0/temp', 'utf8');
            sensorData.cpu_temperature = parseInt(temp) / 1000; // Convertir a Celsius
        } catch (error) {
            sensorData.cpu_temperature_error = error.message;
        }

        return sensorData;
    }

    async createContextualAlert(source, realData) {
        const alertId = `REAL-${Date.now()}`;
        const timestamp = new Date().toISOString();

        let alert = {
            event_id: alertId,
            timestamp: timestamp,
            source_system: `${this.systemProfile.platform}_${this.systemProfile.hostname}`,
            detection_method: 'smartcompute_hrm_live',
            real_source: source,
            extracted_data: realData
        };

        // Generar descripción y severidad basada en datos reales
        alert = await this.analyzeAndClassify(alert, source, realData);

        return alert;
    }

    async analyzeAndClassify(alert, source, realData) {
        let severity = 'LOW';
        let description = 'System activity detected';
        let recommendations = [];

        switch (source.type) {
            case 'system_log':
                if (realData.error_events > 5) {
                    severity = 'HIGH';
                    description = `Multiple system errors detected in ${realData.log_file}`;
                    recommendations.push('Review system logs for patterns');
                    recommendations.push('Check disk space and system health');
                } else if (realData.error_events > 0) {
                    severity = 'MEDIUM';
                    description = `System errors found in ${realData.log_file}`;
                    recommendations.push('Monitor error trends');
                }
                break;

            case 'process_monitor':
                if (realData.suspicious_processes && realData.suspicious_processes.length > 0) {
                    severity = 'CRITICAL';
                    description = `${realData.suspicious_processes.length} suspicious processes detected`;
                    recommendations.push('Investigate high-resource processes');
                    recommendations.push('Check for unauthorized executions');
                } else if (realData.high_cpu_count > 5) {
                    severity = 'MEDIUM';
                    description = `${realData.high_cpu_count} high-CPU processes detected`;
                    recommendations.push('Monitor resource usage');
                }
                break;

            case 'network_monitor':
                if (realData.active_connections > 100) {
                    severity = 'MEDIUM';
                    description = `High number of network connections (${realData.active_connections})`;
                    recommendations.push('Review network activity');
                } else {
                    severity = 'LOW';
                    description = `Normal network activity (${realData.active_connections} connections)`;
                }
                break;

            case 'hardware_sensors':
                if (realData.cpu_temperature && realData.cpu_temperature > 80) {
                    severity = 'HIGH';
                    description = `High CPU temperature detected (${realData.cpu_temperature}°C)`;
                    recommendations.push('Check cooling systems');
                    recommendations.push('Monitor thermal conditions');
                } else if (realData.cpu_temperature) {
                    severity = 'LOW';
                    description = `Normal thermal conditions (${realData.cpu_temperature}°C)`;
                }
                break;
        }

        alert.severity = severity;
        alert.description = description;
        alert.recommendations = recommendations;
        alert.analysis_context = {
            system_load: this.systemProfile.loadavg[0],
            memory_usage_percent: ((this.systemProfile.totalmem - this.systemProfile.freemem) / this.systemProfile.totalmem * 100).toFixed(1),
            uptime_hours: (this.systemProfile.uptime / 3600).toFixed(1)
        };

        return alert;
    }

    async learnFromEvent(alert, source, realData) {
        const learningEntry = {
            timestamp: new Date().toISOString(),
            alert_id: alert.event_id,
            source_type: source.type,
            severity: alert.severity,
            features: this.extractFeatures(alert, source, realData),
            system_context: this.systemProfile,
            outcome: null // Se actualizará con feedback del usuario
        };

        this.learningData.push(learningEntry);

        // Mantener solo últimos 1000 eventos para entrenamiento
        if (this.learningData.length > 1000) {
            this.learningData.shift();
        }

        // Actualizar modelo HRM
        await this.updateHRMModel(source.type, learningEntry);
    }

    extractFeatures(alert, source, realData) {
        const features = {
            source_type: source.type,
            data_size: JSON.stringify(realData).length,
            system_load: this.systemProfile.loadavg[0],
            memory_pressure: (this.systemProfile.totalmem - this.systemProfile.freemem) / this.systemProfile.totalmem,
            time_of_day: new Date().getHours(),
            day_of_week: new Date().getDay()
        };

        // Features específicos por tipo de fuente
        switch (source.type) {
            case 'system_log':
                features.error_count = realData.error_events || 0;
                features.log_size = realData.size_mb || 0;
                break;
            case 'process_monitor':
                features.process_count = realData.total_processes || 0;
                features.suspicious_count = realData.suspicious_processes?.length || 0;
                features.high_cpu_count = realData.high_cpu_count || 0;
                break;
            case 'network_monitor':
                features.connection_count = realData.active_connections || 0;
                features.interface_count = realData.interfaces?.length || 0;
                break;
            case 'hardware_sensors':
                features.temperature = realData.cpu_temperature || 0;
                features.sensor_count = realData.sensors_available || 0;
                break;
        }

        return features;
    }

    async updateHRMModel(sourceType, learningEntry) {
        if (!this.hrmModels.has(sourceType)) {
            this.hrmModels.set(sourceType, {
                events_count: 0,
                severity_distribution: { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
                feature_averages: {},
                patterns: []
            });
        }

        const model = this.hrmModels.get(sourceType);
        model.events_count++;
        model.severity_distribution[learningEntry.severity]++;

        // Actualizar promedios de features
        Object.keys(learningEntry.features).forEach(feature => {
            if (typeof learningEntry.features[feature] === 'number') {
                if (!model.feature_averages[feature]) {
                    model.feature_averages[feature] = { sum: 0, count: 0 };
                }
                model.feature_averages[feature].sum += learningEntry.features[feature];
                model.feature_averages[feature].count++;
            }
        });

        this.hrmModels.set(sourceType, model);
    }

    async loadHRMModels() {
        const modelsPath = path.join(__dirname, '..', 'models', 'hrm_models.json');
        try {
            await fsPromises.access(modelsPath);
            const modelsData = JSON.parse(await fsPromises.readFile(modelsPath, 'utf8'));
            Object.keys(modelsData).forEach(key => {
                this.hrmModels.set(key, modelsData[key]);
            });
            console.log(`📚 Cargados ${this.hrmModels.size} modelos HRM existentes`);
        } catch (error) {
            console.log('📚 No hay modelos HRM previos, iniciando entrenamiento desde cero');
        }
    }

    async saveHRMModels() {
        const modelsPath = path.join(__dirname, '..', 'models');
        try {
            await fsPromises.access(modelsPath);
        } catch {
            await fsPromises.mkdir(modelsPath, { recursive: true });
        }

        const modelsData = {};
        this.hrmModels.forEach((value, key) => {
            modelsData[key] = value;
        });

        await fsPromises.writeFile(
            path.join(modelsPath, 'hrm_models.json'),
            JSON.stringify(modelsData, null, 2)
        );

        console.log('💾 Modelos HRM guardados');
    }

    printSystemProfile() {
        console.log('\n📊 PERFIL DEL SISTEMA DETECTADO:');
        console.log(`🖥️  OS: ${this.systemProfile.os} (${this.systemProfile.platform})`);
        console.log(`🏠 Hostname: ${this.systemProfile.hostname}`);
        console.log(`⚡ Uptime: ${(this.systemProfile.uptime / 3600).toFixed(1)} horas`);
        console.log(`💾 Memoria: ${(this.systemProfile.freemem / 1024 / 1024 / 1024).toFixed(1)}GB libre de ${(this.systemProfile.totalmem / 1024 / 1024 / 1024).toFixed(1)}GB`);
        console.log(`🔥 Load Average: ${this.systemProfile.loadavg.map(l => l.toFixed(2)).join(', ')}`);

        const sources = this.detectedSources.get('available_sources') || [];
        console.log(`\n🔍 FUENTES DETECTADAS: ${sources.length}`);
        sources.forEach(source => {
            const status = source.accessible ? '✅' : '❌';
            console.log(`  ${status} ${source.type}: ${source.category}`);
        });
    }

    createMockSource() {
        return {
            type: 'system_monitor',
            category: 'system_analysis',
            accessible: true
        };
    }

    async generateMockData(source) {
        return {
            source_type: 'system_monitor',
            message: 'Mock data for demonstration',
            system_profile: this.systemProfile,
            timestamp: new Date().toISOString()
        };
    }

    async initialize() {
        await this.initializeDetectors();
    }

    async getSystemStatus() {
        return {
            hostname: this.systemProfile.hostname,
            platform: this.systemProfile.platform,
            uptime: `${(this.systemProfile.uptime / 3600).toFixed(1)} horas`,
            memory: `${(this.systemProfile.freemem / 1024**3).toFixed(1)}GB libre de ${(this.systemProfile.totalmem / 1024**3).toFixed(1)}GB`,
            loadavg: this.systemProfile.loadavg,
            cpu_count: this.systemProfile.cpus.length
        };
    }

    async performComprehensiveAnalysis() {
        // Actualizar información del sistema
        this.systemProfile.uptime = os.uptime();
        this.systemProfile.freemem = os.freemem();
        this.systemProfile.loadavg = os.loadavg();

        const analysis = {
            system: {
                hostname: this.systemProfile.hostname,
                platform: this.systemProfile.platform,
                cpu_usage: this.systemProfile.loadavg[0] * 100 / this.systemProfile.cpus.length,
                load_average: this.systemProfile.loadavg,
                cores: this.systemProfile.cpus.length,
                running_processes: 0,
                memory: {
                    total: this.systemProfile.totalmem,
                    available: this.systemProfile.freemem
                }
            },
            logs: {
                system: await this.getSystemLogs()
            },
            processes: {
                running: await this.getRunningProcesses()
            },
            network: {
                connections: await this.getNetworkConnections(),
                listening_ports: [],
                interfaces: Object.keys(os.networkInterfaces())
            },
            disk: {
                usage: 50 // Placeholder - requiere comando externo
            }
        };

        return analysis;
    }

    async getSystemLogs() {
        // Simular logs del sistema para demo
        return [
            {
                level: 'info',
                message: 'System running normally',
                service: 'systemd',
                timestamp: new Date().toISOString()
            },
            {
                level: 'warning',
                message: 'High memory usage detected',
                service: 'kernel',
                timestamp: new Date().toISOString()
            }
        ];
    }

    async getRunningProcesses() {
        // Simular procesos para demo
        const processes = [];
        for (let i = 0; i < 10; i++) {
            processes.push({
                pid: 1000 + i,
                name: `process_${i}`,
                cpu: Math.random() * 100,
                memory: Math.random() * 1000,
                user: 'gatux'
            });
        }
        return processes;
    }

    async getNetworkConnections() {
        // Simular conexiones de red
        const connections = [];
        for (let i = 0; i < 25; i++) {
            connections.push({
                local_address: `127.0.0.1:${3000 + i}`,
                remote_address: `0.0.0.0:0`,
                state: 'ESTABLISHED'
            });
        }
        return connections;
    }
}

// Exportar para uso en el servidor web
export default SmartSystemDetector;

// Si se ejecuta directamente, hacer demo
if (import.meta.url === `file://${process.argv[1]}`) {
    async function demo() {
        console.log('🚀 Demo SmartCompute HRM - Detección Real');
        console.log('==========================================');

        const detector = new SmartSystemDetector();

        // Esperar a que termine la inicialización
        await new Promise(resolve => setTimeout(resolve, 2000));

        console.log('\n🔍 Generando alerta basada en datos reales del sistema...\n');

        const realAlert = await detector.generateRealAlert();

        console.log('📊 ALERTA GENERADA A PARTIR DE DATOS REALES:');
        console.log('============================================');
        console.log(JSON.stringify(realAlert, null, 2));

        console.log('\n🧠 MODELOS HRM ACTUALES:');
        console.log('========================');
        detector.hrmModels.forEach((model, sourceType) => {
            console.log(`📈 ${sourceType}: ${model.events_count} eventos procesados`);
            console.log(`   Severidades: ${JSON.stringify(model.severity_distribution)}`);
        });

        // Guardar modelos
        await detector.saveHRMModels();

        console.log('\n✅ Demo completado. Los modelos HRM han aprendido de los datos reales del sistema.');
    }

    demo().catch(console.error);
}