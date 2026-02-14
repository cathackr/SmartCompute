#!/usr/bin/env python3
"""
SmartCompute MITRE-based Security Experimentation Module
========================================================

Módulo especializado que implementa experimentación segura basada en MITRE ATT&CK:
- Mapeo de técnicas MITRE a soluciones de seguridad
- Experimentación controlada en entornos seguros
- Validación de efectividad contra marcos MITRE
- Integración con Node.js para testing dinámico
- Autorización de administrador para cambios críticos

Copyright (c) 2024 SmartCompute. All rights reserved.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
import yaml


class MitreTactic(Enum):
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"


class ExperimentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ADMIN_APPROVAL_REQUIRED = "admin_approval_required"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class MitreExperiment:
    """Experimento basado en MITRE ATT&CK"""
    experiment_id: str
    name: str
    description: str
    mitre_technique_id: str
    mitre_technique_name: str
    tactics: List[MitreTactic]
    test_scenario: Dict[str, Any]
    security_solution: Dict[str, Any]
    environment: str  # sandbox, staging, production
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: ExperimentStatus
    results: Dict[str, Any]
    metrics: Dict[str, float]
    issues_found: List[str]
    recommendations: List[str]
    admin_notes: Optional[str]
    nodejs_components: List[str]  # Node.js modules for testing
    rollback_executed: bool


@dataclass
class MitreKnowledgeBase:
    """Base de conocimiento MITRE ATT&CK"""
    technique_id: str
    name: str
    description: str
    tactics: List[MitreTactic]
    platforms: List[str]
    data_sources: List[str]
    mitigations: List[str]
    detection_methods: List[str]
    references: List[str]


class SmartComputeMitreExperimenter:
    """Experimentador de seguridad basado en MITRE ATT&CK"""

    def __init__(self, workspace_path: str = "/var/lib/smartcompute/mitre_experiments"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Rutas importantes
        self.experiments_db = self.workspace_path / "experiments.json"
        self.knowledge_base_file = self.workspace_path / "mitre_knowledge.json"
        self.nodejs_sandbox = self.workspace_path / "nodejs_sandbox"
        self.nodejs_sandbox.mkdir(exist_ok=True)

        # Cargar base de conocimiento MITRE
        self.mitre_kb = self._load_mitre_knowledge_base()

        # Cargar experimentos existentes
        self.experiments = self._load_experiments()

        # Configurar sandbox Node.js
        self._setup_nodejs_sandbox()

    def _load_mitre_knowledge_base(self) -> Dict[str, MitreKnowledgeBase]:
        """Carga la base de conocimiento MITRE ATT&CK"""
        if self.knowledge_base_file.exists():
            try:
                with open(self.knowledge_base_file, 'r') as f:
                    data = json.load(f)
                    return {k: self._dict_to_mitre_kb(v) for k, v in data.items()}
            except Exception as e:
                self.logger.error(f"Error loading MITRE knowledge base: {e}")

        # Si no existe, crear base de conocimiento básica
        return self._create_default_mitre_kb()

    def _create_default_mitre_kb(self) -> Dict[str, MitreKnowledgeBase]:
        """Crea base de conocimiento MITRE por defecto"""
        default_kb = {
            "T1078": MitreKnowledgeBase(
                technique_id="T1078",
                name="Valid Accounts",
                description="Adversaries may obtain and abuse credentials of existing accounts",
                tactics=[MitreTactic.DEFENSE_EVASION, MitreTactic.PERSISTENCE,
                        MitreTactic.PRIVILEGE_ESCALATION, MitreTactic.INITIAL_ACCESS],
                platforms=["Linux", "Windows", "macOS", "Network"],
                data_sources=["Authentication logs", "Process monitoring"],
                mitigations=["M1015", "M1026", "M1027", "M1028", "M1032", "M1036"],
                detection_methods=["Monitor login patterns", "Account usage analysis"],
                references=["https://attack.mitre.org/techniques/T1078/"]
            ),
            "T1110": MitreKnowledgeBase(
                technique_id="T1110",
                name="Brute Force",
                description="Adversaries may use brute force techniques to gain access",
                tactics=[MitreTactic.CREDENTIAL_ACCESS],
                platforms=["Linux", "Windows", "macOS", "Network"],
                data_sources=["Authentication logs", "Network traffic"],
                mitigations=["M1027", "M1028", "M1032", "M1036", "M1041"],
                detection_methods=["Failed login monitoring", "Rate limiting"],
                references=["https://attack.mitre.org/techniques/T1110/"]
            ),
            "T1059": MitreKnowledgeBase(
                technique_id="T1059",
                name="Command and Scripting Interpreter",
                description="Adversaries may abuse command and script interpreters",
                tactics=[MitreTactic.EXECUTION],
                platforms=["Linux", "Windows", "macOS"],
                data_sources=["Process monitoring", "Command history"],
                mitigations=["M1038", "M1042", "M1049"],
                detection_methods=["Process monitoring", "Script execution analysis"],
                references=["https://attack.mitre.org/techniques/T1059/"]
            )
        }

        # Guardar base de conocimiento por defecto
        self._save_mitre_knowledge_base(default_kb)
        return default_kb

    def _setup_nodejs_sandbox(self):
        """Configura el entorno sandbox de Node.js"""
        try:
            # Crear package.json para el sandbox
            package_json = {
                "name": "smartcompute-security-sandbox",
                "version": "1.0.0",
                "description": "Security testing sandbox for SmartCompute",
                "main": "index.js",
                "dependencies": {
                    "express": "^4.18.0",
                    "helmet": "^6.0.0",
                    "bcrypt": "^5.1.0",
                    "jsonwebtoken": "^9.0.0",
                    "crypto": "^1.0.1",
                    "node-rate-limiter-flexible": "^2.4.0",
                    "winston": "^3.8.0"
                },
                "scripts": {
                    "test": "node test_runner.js",
                    "security-test": "node security_test.js"
                }
            }

            package_json_path = self.nodejs_sandbox / "package.json"
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f, indent=2)

            # Crear script base de testing
            self._create_nodejs_test_scripts()

        except Exception as e:
            self.logger.error(f"Error setting up Node.js sandbox: {e}")

    def _create_nodejs_test_scripts(self):
        """Crea scripts de testing en Node.js"""

        # Script principal de testing de seguridad
        security_test_script = '''
const express = require('express');
const helmet = require('helmet');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const { RateLimiterMemory } = require('rate-limiter-flexible');
const winston = require('winston');

class SecurityTester {
    constructor() {
        this.logger = winston.createLogger({
            level: 'info',
            format: winston.format.json(),
            transports: [
                new winston.transports.File({ filename: 'security_test.log' })
            ]
        });
    }

    async testBruteForceProtection(config) {
        console.log('Testing Brute Force Protection (T1110)...');

        const rateLimiter = new RateLimiterMemory({
            keyGenerator: (req) => req.ip,
            points: config.maxAttempts || 5,
            duration: config.windowSeconds || 60,
        });

        const results = {
            technique: 'T1110',
            test_name: 'Brute Force Protection',
            attempts_blocked: 0,
            attempts_allowed: 0,
            protection_effective: false,
            response_times: []
        };

        // Simular intentos de fuerza bruta
        for (let i = 0; i < (config.testAttempts || 10); i++) {
            const startTime = Date.now();

            try {
                await rateLimiter.consume('test_ip');
                results.attempts_allowed++;
            } catch (rejRes) {
                results.attempts_blocked++;
            }

            results.response_times.push(Date.now() - startTime);
        }

        results.protection_effective = results.attempts_blocked > results.attempts_allowed;

        this.logger.info('Brute force test completed', results);
        return results;
    }

    async testAuthenticationBypass(config) {
        console.log('Testing Authentication Bypass (T1078)...');

        const results = {
            technique: 'T1078',
            test_name: 'Authentication Bypass',
            bypass_attempts: 0,
            successful_bypasses: 0,
            protection_effective: true,
            vulnerabilities_found: []
        };

        // Test casos comunes de bypass
        const bypassAttempts = [
            { username: 'admin', password: '' },
            { username: 'admin', password: 'admin' },
            { username: "admin'--", password: 'anything' },
            { username: 'admin', password: "' OR '1'='1" }
        ];

        for (const attempt of bypassAttempts) {
            results.bypass_attempts++;

            // Simular validación de autenticación
            if (this.isSecureAuth(attempt, config)) {
                // Bypass falló - bueno
                continue;
            } else {
                // Bypass exitoso - problema de seguridad
                results.successful_bypasses++;
                results.vulnerabilities_found.push(`Bypass successful with: ${JSON.stringify(attempt)}`);
            }
        }

        results.protection_effective = results.successful_bypasses === 0;

        this.logger.info('Authentication bypass test completed', results);
        return results;
    }

    isSecureAuth(credentials, config) {
        // Simular validación segura
        const { username, password } = credentials;

        // Checks básicos de seguridad
        if (!username || !password) return false;
        if (username.includes("'") || username.includes("--")) return false;
        if (password.includes("'") || password.includes("OR")) return false;

        // Validación de hash (simulada)
        const expectedHash = config.expectedPasswordHash || '$2b$10$example';
        return bcrypt.compareSync(password, expectedHash);
    }

    async testCommandInjection(config) {
        console.log('Testing Command Injection (T1059)...');

        const results = {
            technique: 'T1059',
            test_name: 'Command Injection',
            injection_attempts: 0,
            successful_injections: 0,
            protection_effective: true,
            dangerous_inputs: []
        };

        // Payloads de inyección comunes
        const injectionPayloads = [
            '; ls -la',
            '&& cat /etc/passwd',
            '| whoami',
            '`id`',
            '$(uname -a)',
            '; rm -rf /',
            '& net user'
        ];

        for (const payload of injectionPayloads) {
            results.injection_attempts++;

            if (this.isVulnerableToInjection(payload, config)) {
                results.successful_injections++;
                results.dangerous_inputs.push(payload);
            }
        }

        results.protection_effective = results.successful_injections === 0;

        this.logger.info('Command injection test completed', results);
        return results;
    }

    isVulnerableToInjection(input, config) {
        // Simular detección de inyección
        const dangerousChars = [';', '&', '|', '`', '$', '(', ')'];
        const dangerousCommands = ['rm', 'del', 'format', 'shutdown', 'cat', 'type'];

        // Si no hay protección configurada, es vulnerable
        if (!config.inputValidation) return true;

        // Check caracteres peligrosos
        if (dangerousChars.some(char => input.includes(char))) {
            return !config.inputValidation.blockDangerousChars;
        }

        // Check comandos peligrosos
        if (dangerousCommands.some(cmd => input.toLowerCase().includes(cmd))) {
            return !config.inputValidation.blockDangerousCommands;
        }

        return false;
    }

    async runComprehensiveTest(testConfig) {
        console.log('Running comprehensive MITRE-based security test...');

        const results = {
            test_id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            techniques_tested: [],
            overall_security_score: 0,
            critical_vulnerabilities: 0,
            recommendations: []
        };

        try {
            // Test T1110 - Brute Force
            if (testConfig.testBruteForce) {
                const bruteForceResults = await this.testBruteForceProtection(testConfig.bruteForce || {});
                results.techniques_tested.push(bruteForceResults);
                if (!bruteForceResults.protection_effective) {
                    results.critical_vulnerabilities++;
                    results.recommendations.push('Implement rate limiting for authentication');
                }
            }

            // Test T1078 - Valid Accounts
            if (testConfig.testAuthBypass) {
                const authResults = await this.testAuthenticationBypass(testConfig.authentication || {});
                results.techniques_tested.push(authResults);
                if (!authResults.protection_effective) {
                    results.critical_vulnerabilities++;
                    results.recommendations.push('Strengthen authentication validation');
                }
            }

            // Test T1059 - Command Injection
            if (testConfig.testCommandInjection) {
                const injectionResults = await this.testCommandInjection(testConfig.commandInjection || {});
                results.techniques_tested.push(injectionResults);
                if (!injectionResults.protection_effective) {
                    results.critical_vulnerabilities++;
                    results.recommendations.push('Implement input sanitization');
                }
            }

            // Calcular score general
            const totalTests = results.techniques_tested.length;
            const effectiveProtections = results.techniques_tested.filter(test => test.protection_effective).length;
            results.overall_security_score = totalTests > 0 ? (effectiveProtections / totalTests) * 100 : 0;

            this.logger.info('Comprehensive test completed', results);
            return results;

        } catch (error) {
            this.logger.error('Test failed', { error: error.message });
            throw error;
        }
    }
}

// Función principal para ejecutar desde Python
async function runSecurityTest(configPath) {
    try {
        const fs = require('fs');
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

        const tester = new SecurityTester();
        const results = await tester.runComprehensiveTest(config);

        // Guardar resultados
        const resultsPath = configPath.replace('.json', '_results.json');
        fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));

        console.log('Security test completed. Results saved to:', resultsPath);
        return results;

    } catch (error) {
        console.error('Security test failed:', error.message);
        process.exit(1);
    }
}

// Ejecutar si se llama directamente
if (require.main === module) {
    const configPath = process.argv[2] || './test_config.json';
    runSecurityTest(configPath);
}

module.exports = { SecurityTester, runSecurityTest };
'''

        security_test_path = self.nodejs_sandbox / "security_test.js"
        with open(security_test_path, 'w') as f:
            f.write(security_test_script)

    async def create_mitre_experiment(self,
                                    technique_id: str,
                                    security_solution: Dict[str, Any],
                                    environment: str = "sandbox") -> MitreExperiment:
        """Crea un nuevo experimento basado en técnica MITRE"""

        if technique_id not in self.mitre_kb:
            raise ValueError(f"Unknown MITRE technique: {technique_id}")

        technique = self.mitre_kb[technique_id]

        experiment = MitreExperiment(
            experiment_id=str(uuid.uuid4()),
            name=f"Test {technique.name} Protection",
            description=f"Evaluate security solution against {technique_id}",
            mitre_technique_id=technique_id,
            mitre_technique_name=technique.name,
            tactics=technique.tactics,
            test_scenario=self._generate_test_scenario(technique),
            security_solution=security_solution,
            environment=environment,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            status=ExperimentStatus.PENDING,
            results={},
            metrics={},
            issues_found=[],
            recommendations=[],
            admin_notes=None,
            nodejs_components=self._get_nodejs_components_for_technique(technique_id),
            rollback_executed=False
        )

        self.experiments.append(experiment)
        self._save_experiments()

        self.logger.info(f"Created MITRE experiment: {experiment.name} ({experiment.experiment_id})")
        return experiment

    def _generate_test_scenario(self, technique: MitreKnowledgeBase) -> Dict[str, Any]:
        """Genera escenario de prueba para una técnica MITRE"""

        scenarios = {
            "T1078": {
                "test_type": "authentication_bypass",
                "attack_vectors": ["credential_stuffing", "default_credentials", "sql_injection"],
                "success_criteria": ["block_invalid_credentials", "detect_suspicious_patterns"],
                "test_duration_minutes": 5
            },
            "T1110": {
                "test_type": "brute_force_protection",
                "attack_vectors": ["password_spray", "dictionary_attack", "credential_brute_force"],
                "success_criteria": ["rate_limiting", "account_lockout", "anomaly_detection"],
                "test_duration_minutes": 10
            },
            "T1059": {
                "test_type": "command_injection",
                "attack_vectors": ["shell_injection", "script_injection", "os_command_injection"],
                "success_criteria": ["input_sanitization", "command_filtering", "execution_prevention"],
                "test_duration_minutes": 7
            }
        }

        return scenarios.get(technique.technique_id, {
            "test_type": "generic_protection",
            "attack_vectors": ["generic_attack"],
            "success_criteria": ["basic_protection"],
            "test_duration_minutes": 5
        })

    def _get_nodejs_components_for_technique(self, technique_id: str) -> List[str]:
        """Determina componentes Node.js necesarios para testing"""

        components_map = {
            "T1078": ["express", "bcrypt", "jsonwebtoken", "helmet"],
            "T1110": ["express", "node-rate-limiter-flexible", "winston"],
            "T1059": ["express", "validator", "shell-escape"]
        }

        return components_map.get(technique_id, ["express", "helmet"])

    async def run_experiment(self, experiment_id: str, admin_approval: bool = False) -> Dict[str, Any]:
        """Ejecuta un experimento MITRE"""

        experiment = next((exp for exp in self.experiments if exp.experiment_id == experiment_id), None)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")

        # Verificar si necesita aprobación de admin
        if experiment.environment == "production" and not admin_approval:
            experiment.status = ExperimentStatus.ADMIN_APPROVAL_REQUIRED
            self._save_experiments()
            return {
                "status": "admin_approval_required",
                "message": "Production environment requires admin approval",
                "experiment_id": experiment_id
            }

        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()
        self._save_experiments()

        try:
            # Preparar configuración de testing
            test_config = self._prepare_test_config(experiment)

            # Ejecutar test en Node.js
            nodejs_results = await self._run_nodejs_test(experiment, test_config)

            # Analizar resultados
            analysis = self._analyze_test_results(experiment, nodejs_results)

            # Actualizar experimento con resultados
            experiment.completed_at = datetime.now()
            experiment.status = ExperimentStatus.COMPLETED
            experiment.results = nodejs_results
            experiment.metrics = analysis["metrics"]
            experiment.issues_found = analysis["issues"]
            experiment.recommendations = analysis["recommendations"]

            # Determinar si implementar o hacer rollback
            if analysis["critical_issues"] > 0:
                await self._execute_rollback(experiment)

            self._save_experiments()

            self.logger.info(f"Experiment completed: {experiment_id}")
            return {
                "status": "completed",
                "experiment_id": experiment_id,
                "results": experiment.results,
                "metrics": experiment.metrics,
                "issues_found": experiment.issues_found,
                "recommendations": experiment.recommendations
            }

        except Exception as e:
            experiment.status = ExperimentStatus.FAILED
            experiment.completed_at = datetime.now()
            experiment.issues_found.append(f"Experiment failed: {str(e)}")
            self._save_experiments()

            self.logger.error(f"Experiment failed: {experiment_id} - {e}")
            return {
                "status": "failed",
                "experiment_id": experiment_id,
                "error": str(e)
            }

    def _prepare_test_config(self, experiment: MitreExperiment) -> Dict[str, Any]:
        """Prepara configuración de testing para Node.js"""

        base_config = {
            "experiment_id": experiment.experiment_id,
            "technique_id": experiment.mitre_technique_id,
            "environment": experiment.environment
        }

        # Configuración específica por técnica
        if experiment.mitre_technique_id == "T1110":
            base_config.update({
                "testBruteForce": True,
                "bruteForce": {
                    "maxAttempts": experiment.security_solution.get("rate_limit", 5),
                    "windowSeconds": experiment.security_solution.get("window_seconds", 60),
                    "testAttempts": 15
                }
            })

        elif experiment.mitre_technique_id == "T1078":
            base_config.update({
                "testAuthBypass": True,
                "authentication": {
                    "expectedPasswordHash": experiment.security_solution.get("password_hash"),
                    "enableSqlInjectionProtection": experiment.security_solution.get("sql_protection", True)
                }
            })

        elif experiment.mitre_technique_id == "T1059":
            base_config.update({
                "testCommandInjection": True,
                "commandInjection": {
                    "inputValidation": {
                        "blockDangerousChars": experiment.security_solution.get("block_dangerous_chars", True),
                        "blockDangerousCommands": experiment.security_solution.get("block_dangerous_commands", True)
                    }
                }
            })

        return base_config

    async def _run_nodejs_test(self, experiment: MitreExperiment, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta test de seguridad en Node.js"""

        # Guardar configuración de test
        config_path = self.nodejs_sandbox / f"test_config_{experiment.experiment_id}.json"
        with open(config_path, 'w') as f:
            json.dump(test_config, f, indent=2)

        try:
            # Ejecutar test de Node.js
            result = subprocess.run([
                "node", "security_test.js", str(config_path)
            ], cwd=self.nodejs_sandbox, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise Exception(f"Node.js test failed: {result.stderr}")

            # Cargar resultados
            results_path = str(config_path).replace('.json', '_results.json')
            with open(results_path, 'r') as f:
                return json.load(f)

        finally:
            # Limpiar archivos temporales
            if config_path.exists():
                config_path.unlink()
            results_path = Path(str(config_path).replace('.json', '_results.json'))
            if results_path.exists():
                results_path.unlink()

    def _analyze_test_results(self, experiment: MitreExperiment, nodejs_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza resultados de testing y genera recomendaciones"""

        analysis = {
            "metrics": {
                "security_score": nodejs_results.get("overall_security_score", 0),
                "techniques_tested": len(nodejs_results.get("techniques_tested", [])),
                "critical_vulnerabilities": nodejs_results.get("critical_vulnerabilities", 0),
                "protection_effectiveness": 0
            },
            "issues": [],
            "recommendations": nodejs_results.get("recommendations", []),
            "critical_issues": 0
        }

        # Calcular efectividad de protección
        techniques_tested = nodejs_results.get("techniques_tested", [])
        if techniques_tested:
            effective_protections = sum(1 for test in techniques_tested if test.get("protection_effective", False))
            analysis["metrics"]["protection_effectiveness"] = (effective_protections / len(techniques_tested)) * 100

        # Identificar problemas críticos
        for test_result in techniques_tested:
            if not test_result.get("protection_effective", True):
                issue = f"Protection ineffective for {test_result.get('technique', 'unknown')}"
                analysis["issues"].append(issue)

                if test_result.get("technique") in ["T1078", "T1110"]:  # Técnicas críticas
                    analysis["critical_issues"] += 1

        # Analizar métricas específicas
        if analysis["metrics"]["security_score"] < 70:
            analysis["issues"].append("Overall security score below acceptable threshold (70%)")
            analysis["critical_issues"] += 1

        if analysis["metrics"]["critical_vulnerabilities"] > 0:
            analysis["issues"].append(f"Found {analysis['metrics']['critical_vulnerabilities']} critical vulnerabilities")
            analysis["critical_issues"] += analysis["metrics"]["critical_vulnerabilities"]

        return analysis

    async def _execute_rollback(self, experiment: MitreExperiment):
        """Ejecuta rollback del experimento si es necesario"""

        if experiment.environment in ["staging", "production"]:
            self.logger.warning(f"Executing rollback for experiment {experiment.experiment_id}")

            # En implementación real, aquí se ejecutaría rollback específico
            # Por ahora, solo marcar como ejecutado
            experiment.rollback_executed = True
            experiment.admin_notes = "Automatic rollback executed due to critical issues"

    async def request_admin_approval(self, experiment_id: str, justification: str) -> bool:
        """Solicita aprobación de administrador para experimento"""

        experiment = next((exp for exp in self.experiments if exp.experiment_id == experiment_id), None)
        if not experiment:
            return False

        approval_data = {
            "experiment_id": experiment_id,
            "technique": f"{experiment.mitre_technique_id} - {experiment.mitre_technique_name}",
            "environment": experiment.environment,
            "risk_assessment": self._generate_risk_assessment(experiment),
            "justification": justification,
            "requested_at": datetime.now().isoformat()
        }

        print(f"\n🔐 SOLICITUD DE APROBACIÓN - EXPERIMENTO MITRE")
        print(f"Experimento: {approval_data['technique']}")
        print(f"Entorno: {approval_data['environment']}")
        print(f"Justificación: {approval_data['justification']}")
        print(f"Evaluación de riesgo: {approval_data['risk_assessment']}")

        # Simular respuesta de admin (en implementación real sería input real)
        import random
        approved = random.random() > 0.2  # 80% approval rate

        if approved:
            experiment.status = ExperimentStatus.APPROVED
            experiment.admin_notes = f"Approved: {justification}"
        else:
            experiment.status = ExperimentStatus.REJECTED
            experiment.admin_notes = "Requires additional security review"

        self._save_experiments()
        return approved

    def _generate_risk_assessment(self, experiment: MitreExperiment) -> str:
        """Genera evaluación de riesgo para experimento"""

        risk_factors = []

        # Factor de entorno
        if experiment.environment == "production":
            risk_factors.append("HIGH - Production environment")
        elif experiment.environment == "staging":
            risk_factors.append("MEDIUM - Staging environment")
        else:
            risk_factors.append("LOW - Sandbox environment")

        # Factor de técnica MITRE
        critical_techniques = ["T1078", "T1110", "T1068"]
        if experiment.mitre_technique_id in critical_techniques:
            risk_factors.append("HIGH - Critical security technique")
        else:
            risk_factors.append("MEDIUM - Standard security technique")

        # Factor de solución
        if not experiment.security_solution.get("rollback_plan"):
            risk_factors.append("MEDIUM - No rollback plan specified")
        else:
            risk_factors.append("LOW - Rollback plan available")

        return " | ".join(risk_factors)

    def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Obtiene estado de un experimento"""

        experiment = next((exp for exp in self.experiments if exp.experiment_id == experiment_id), None)
        if not experiment:
            return {"error": "Experiment not found"}

        return {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "technique": f"{experiment.mitre_technique_id} - {experiment.mitre_technique_name}",
            "status": experiment.status.value,
            "environment": experiment.environment,
            "created_at": experiment.created_at.isoformat(),
            "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
            "completed_at": experiment.completed_at.isoformat() if experiment.completed_at else None,
            "metrics": experiment.metrics,
            "issues_found": experiment.issues_found,
            "recommendations": experiment.recommendations,
            "admin_notes": experiment.admin_notes
        }

    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[Dict[str, Any]]:
        """Lista experimentos con filtro opcional por estado"""

        filtered_experiments = self.experiments
        if status:
            filtered_experiments = [exp for exp in self.experiments if exp.status == status]

        return [self.get_experiment_status(exp.experiment_id) for exp in filtered_experiments]

    # Métodos de persistencia
    def _save_experiments(self):
        """Guarda experimentos a disco"""
        try:
            data = [self._experiment_to_dict(exp) for exp in self.experiments]
            with open(self.experiments_db, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving experiments: {e}")

    def _load_experiments(self) -> List[MitreExperiment]:
        """Carga experimentos desde disco"""
        if self.experiments_db.exists():
            try:
                with open(self.experiments_db, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_experiment(item) for item in data]
            except Exception as e:
                self.logger.error(f"Error loading experiments: {e}")
        return []

    def _save_mitre_knowledge_base(self, knowledge_base: Dict[str, MitreKnowledgeBase]):
        """Guarda base de conocimiento MITRE"""
        try:
            data = {k: asdict(v) for k, v in knowledge_base.items()}
            with open(self.knowledge_base_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving MITRE knowledge base: {e}")

    # Métodos de conversión
    def _experiment_to_dict(self, experiment: MitreExperiment) -> Dict[str, Any]:
        result = asdict(experiment)
        result["tactics"] = [tactic.value for tactic in experiment.tactics]
        result["status"] = experiment.status.value
        return result

    def _dict_to_experiment(self, data: Dict[str, Any]) -> MitreExperiment:
        data["tactics"] = [MitreTactic(tactic) for tactic in data["tactics"]]
        data["status"] = ExperimentStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        return MitreExperiment(**data)

    def _dict_to_mitre_kb(self, data: Dict[str, Any]) -> MitreKnowledgeBase:
        data["tactics"] = [MitreTactic(tactic) for tactic in data["tactics"]]
        return MitreKnowledgeBase(**data)


# Ejemplo de uso
async def demo_mitre_experimenter():
    """Demostración del experimentador MITRE"""

    print("🎯 SmartCompute MITRE Experimenter Demo")
    print("=" * 50)

    # Inicializar experimentador
    experimenter = SmartComputeMitreExperimenter()

    # Crear experimento para T1110 (Brute Force)
    security_solution = {
        "rate_limit": 5,
        "window_seconds": 60,
        "account_lockout": True,
        "rollback_plan": "Disable rate limiting if false positives > 10%"
    }

    experiment = await experimenter.create_mitre_experiment(
        technique_id="T1110",
        security_solution=security_solution,
        environment="sandbox"
    )

    print(f"✅ Experimento creado: {experiment.name}")

    # Ejecutar experimento
    results = await experimenter.run_experiment(experiment.experiment_id)
    print(f"✅ Experimento ejecutado: {results['status']}")

    if results['status'] == 'completed':
        print(f"   Score de seguridad: {results['metrics']['security_score']:.1f}%")
        print(f"   Problemas encontrados: {len(results['issues_found'])}")

    # Listar experimentos
    all_experiments = experimenter.list_experiments()
    print(f"✅ Total de experimentos: {len(all_experiments)}")


if __name__ == "__main__":
    asyncio.run(demo_mitre_experimenter())