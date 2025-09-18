#!/usr/bin/env python3
"""
SmartCompute HRM - Learning Framework for Security Solutions
===========================================================

Sistema de aprendizaje continuo que permite al HRM (Human Reasoning Machine):
- Aprender de implementaciones de seguridad exitosas
- Experimentar con soluciones seguras basadas en MITRE ATT&CK
- Razonar sobre cuándo implementar o detener cambios
- Requerir autorización de administrador para cambios críticos

Copyright (c) 2024 SmartCompute. All rights reserved.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid


class LearningStage(Enum):
    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    EXPERIMENTATION = "experimentation"
    VALIDATION = "validation"
    IMPLEMENTATION = "implementation"
    MONITORING = "monitoring"


class SecurityDomain(Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    NETWORK_SECURITY = "network_security"
    INCIDENT_RESPONSE = "incident_response"
    THREAT_DETECTION = "threat_detection"
    VULNERABILITY_MANAGEMENT = "vulnerability_management"


class ImplementationRisk(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SecuritySolution:
    """Solución de seguridad aprendida o propuesta"""
    solution_id: str
    name: str
    description: str
    domain: SecurityDomain
    mitre_techniques: List[str]  # MITRE ATT&CK techniques addressed
    implementation_complexity: int  # 1-10
    risk_level: ImplementationRisk
    success_metrics: Dict[str, Any]
    validation_criteria: List[str]
    rollback_plan: Optional[str]
    learned_from: Optional[str]  # Source of learning
    created_at: datetime
    tested_at: Optional[datetime]
    implemented_at: Optional[datetime]


@dataclass
class ExperimentResult:
    """Resultado de experimentación"""
    experiment_id: str
    solution_id: str
    stage: LearningStage
    environment: str  # sandbox, staging, production
    start_time: datetime
    end_time: Optional[datetime]
    success: bool
    metrics_collected: Dict[str, Any]
    issues_found: List[str]
    recommendations: List[str]
    admin_approval_required: bool
    admin_approved: bool
    admin_notes: Optional[str]


@dataclass
class LearningContext:
    """Contexto de aprendizaje"""
    context_id: str
    trigger_event: str  # vulnerability_found, attack_detected, etc.
    environment_data: Dict[str, Any]
    threat_landscape: Dict[str, Any]
    business_constraints: Dict[str, Any]
    compliance_requirements: List[str]
    available_resources: Dict[str, Any]


class SmartComputeHRMLearning:
    """Framework de aprendizaje HRM para soluciones de seguridad"""

    def __init__(self, data_path: str = "/var/lib/smartcompute/hrm_learning"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Rutas de archivos
        self.solutions_db = self.data_path / "learned_solutions.json"
        self.experiments_db = self.data_path / "experiments.json"
        self.learning_history = self.data_path / "learning_history.json"

        # MITRE ATT&CK knowledge base (simplificado)
        self.mitre_knowledge = self._load_mitre_knowledge()

        # Cargar datos existentes
        self.learned_solutions = self._load_learned_solutions()
        self.experiment_results = self._load_experiment_results()

    def _load_mitre_knowledge(self) -> Dict[str, Any]:
        """Carga base de conocimiento MITRE ATT&CK simplificada"""
        return {
            "T1078": {
                "name": "Valid Accounts",
                "tactics": ["Defense Evasion", "Persistence", "Privilege Escalation", "Initial Access"],
                "mitigations": ["M1015", "M1026", "M1027", "M1028", "M1032", "M1036"]
            },
            "T1110": {
                "name": "Brute Force",
                "tactics": ["Credential Access"],
                "mitigations": ["M1027", "M1028", "M1032", "M1036", "M1041"]
            },
            "T1068": {
                "name": "Exploitation for Privilege Escalation",
                "tactics": ["Privilege Escalation"],
                "mitigations": ["M1013", "M1019", "M1038", "M1048", "M1051"]
            },
            "T1059": {
                "name": "Command and Scripting Interpreter",
                "tactics": ["Execution"],
                "mitigations": ["M1038", "M1042", "M1049"]
            }
        }

    def _load_learned_solutions(self) -> List[SecuritySolution]:
        """Carga soluciones aprendidas previamente"""
        if self.solutions_db.exists():
            try:
                with open(self.solutions_db, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_security_solution(item) for item in data]
            except Exception as e:
                self.logger.error(f"Error cargando soluciones: {e}")
        return []

    def _load_experiment_results(self) -> List[ExperimentResult]:
        """Carga resultados de experimentos previos"""
        if self.experiments_db.exists():
            try:
                with open(self.experiments_db, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_experiment_result(item) for item in data]
            except Exception as e:
                self.logger.error(f"Error cargando experimentos: {e}")
        return []

    def _save_learned_solutions(self):
        """Guarda soluciones aprendidas"""
        try:
            data = [self._security_solution_to_dict(sol) for sol in self.learned_solutions]
            with open(self.solutions_db, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error guardando soluciones: {e}")

    def _save_experiment_results(self):
        """Guarda resultados de experimentos"""
        try:
            data = [self._experiment_result_to_dict(exp) for exp in self.experiment_results]
            with open(self.experiments_db, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error guardando experimentos: {e}")

    async def learn_from_successful_implementation(
        self,
        implementation_data: Dict[str, Any],
        context: LearningContext
    ) -> SecuritySolution:
        """Aprende de una implementación de seguridad exitosa"""

        solution = SecuritySolution(
            solution_id=str(uuid.uuid4()),
            name=implementation_data.get("name", "Unknown Solution"),
            description=implementation_data.get("description", ""),
            domain=SecurityDomain(implementation_data.get("domain", "threat_detection")),
            mitre_techniques=implementation_data.get("mitre_techniques", []),
            implementation_complexity=implementation_data.get("complexity", 5),
            risk_level=ImplementationRisk(implementation_data.get("risk_level", 2)),
            success_metrics=implementation_data.get("success_metrics", {}),
            validation_criteria=implementation_data.get("validation_criteria", []),
            rollback_plan=implementation_data.get("rollback_plan"),
            learned_from=implementation_data.get("source", "user_input"),
            created_at=datetime.now(),
            tested_at=None,
            implemented_at=None
        )

        self.learned_solutions.append(solution)
        self._save_learned_solutions()

        # Log del aprendizaje
        await self._log_learning_event({
            "type": "solution_learned",
            "solution_id": solution.solution_id,
            "context_id": context.context_id,
            "domain": solution.domain.value,
            "mitre_techniques": solution.mitre_techniques
        })

        self.logger.info(f"Nueva solución aprendida: {solution.name}")
        return solution

    async def analyze_security_gap(self,
                                 threat_data: Dict[str, Any],
                                 context: LearningContext) -> List[SecuritySolution]:
        """Analiza una brecha de seguridad y propone soluciones"""

        gap_techniques = threat_data.get("mitre_techniques", [])
        affected_domain = SecurityDomain(threat_data.get("domain", "threat_detection"))

        # Buscar soluciones existentes relevantes
        relevant_solutions = []
        for solution in self.learned_solutions:
            if (solution.domain == affected_domain or
                any(tech in solution.mitre_techniques for tech in gap_techniques)):
                relevant_solutions.append(solution)

        # Si no hay soluciones aprendidas, crear nuevas propuestas
        if not relevant_solutions:
            proposed_solutions = await self._generate_new_solutions(
                gap_techniques, affected_domain, context
            )
            relevant_solutions.extend(proposed_solutions)

        # Priorizar soluciones por relevancia y riesgo
        prioritized_solutions = self._prioritize_solutions(relevant_solutions, threat_data)

        return prioritized_solutions

    async def _generate_new_solutions(self,
                                    mitre_techniques: List[str],
                                    domain: SecurityDomain,
                                    context: LearningContext) -> List[SecuritySolution]:
        """Genera nuevas soluciones basadas en conocimiento MITRE"""

        solutions = []

        for technique in mitre_techniques:
            if technique in self.mitre_knowledge:
                technique_info = self.mitre_knowledge[technique]

                # Generar solución basada en mitigaciones MITRE
                solution = SecuritySolution(
                    solution_id=str(uuid.uuid4()),
                    name=f"Mitigation for {technique_info['name']}",
                    description=f"Generated solution to address {technique}",
                    domain=domain,
                    mitre_techniques=[technique],
                    implementation_complexity=self._estimate_complexity(technique),
                    risk_level=self._estimate_risk(technique, context),
                    success_metrics={
                        "attack_prevention": 0.85,
                        "false_positive_rate": 0.05
                    },
                    validation_criteria=[
                        f"Prevent {technique} attacks",
                        "Maintain system performance",
                        "Minimize false positives"
                    ],
                    rollback_plan="Automated rollback available",
                    learned_from="mitre_knowledge",
                    created_at=datetime.now(),
                    tested_at=None,
                    implemented_at=None
                )

                solutions.append(solution)

        return solutions

    def _prioritize_solutions(self, solutions: List[SecuritySolution],
                            threat_data: Dict[str, Any]) -> List[SecuritySolution]:
        """Prioriza soluciones basado en múltiples factores"""

        def priority_score(solution: SecuritySolution) -> float:
            score = 0.0

            # Factor de relevancia técnica
            relevant_techniques = set(solution.mitre_techniques) & set(threat_data.get("mitre_techniques", []))
            score += len(relevant_techniques) * 10

            # Factor de riesgo (menor riesgo = mayor prioridad)
            score += (5 - solution.risk_level.value) * 5

            # Factor de complejidad (menor complejidad = mayor prioridad)
            score += (11 - solution.implementation_complexity) * 2

            # Factor de experiencia previa
            if solution.tested_at:
                score += 15
            if solution.implemented_at:
                score += 20

            return score

        return sorted(solutions, key=priority_score, reverse=True)

    async def should_proceed_with_implementation(self,
                                              solution: SecuritySolution,
                                              current_stage: LearningStage,
                                              experiment_results: List[ExperimentResult]) -> Tuple[bool, str]:
        """Razona sobre si proceder con la implementación"""

        # Análisis de resultados de experimentos
        successful_experiments = [exp for exp in experiment_results if exp.success]
        failed_experiments = [exp for exp in experiment_results if not exp.success]

        success_rate = len(successful_experiments) / len(experiment_results) if experiment_results else 0

        # Criterios de decisión
        if solution.risk_level == ImplementationRisk.CRITICAL:
            if success_rate < 0.95:
                return False, "Critical risk solution requires 95%+ success rate"

        elif solution.risk_level == ImplementationRisk.HIGH:
            if success_rate < 0.85:
                return False, "High risk solution requires 85%+ success rate"

        elif solution.risk_level == ImplementationRisk.MEDIUM:
            if success_rate < 0.70:
                return False, "Medium risk solution requires 70%+ success rate"

        # Verificar si hay problemas recurrentes
        common_issues = self._analyze_common_issues(failed_experiments)
        if len(common_issues) > 2:
            return False, f"Recurring issues found: {', '.join(common_issues)}"

        # Verificar disponibilidad de rollback
        if not solution.rollback_plan and solution.risk_level.value >= 3:
            return False, "High/Critical risk solutions require rollback plan"

        # Verificar aprobación de admin para cambios críticos
        if solution.risk_level.value >= 3:
            admin_approved = any(exp.admin_approved for exp in experiment_results)
            if not admin_approved:
                return False, "Admin approval required for high/critical risk changes"

        return True, "All criteria met for implementation"

    def _analyze_common_issues(self, failed_experiments: List[ExperimentResult]) -> List[str]:
        """Analiza problemas comunes en experimentos fallidos"""
        all_issues = []
        for exp in failed_experiments:
            all_issues.extend(exp.issues_found)

        # Contar frecuencia de problemas
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Retornar problemas que aparecen en >50% de fallas
        threshold = len(failed_experiments) * 0.5
        return [issue for issue, count in issue_counts.items() if count >= threshold]

    async def run_experiment(self,
                           solution: SecuritySolution,
                           environment: str = "sandbox") -> ExperimentResult:
        """Ejecuta un experimento de seguridad"""

        experiment = ExperimentResult(
            experiment_id=str(uuid.uuid4()),
            solution_id=solution.solution_id,
            stage=LearningStage.EXPERIMENTATION,
            environment=environment,
            start_time=datetime.now(),
            end_time=None,
            success=False,
            metrics_collected={},
            issues_found=[],
            recommendations=[],
            admin_approval_required=solution.risk_level.value >= 3,
            admin_approved=False,
            admin_notes=None
        )

        try:
            # Simular experimento (en implementación real, aquí iría lógica específica)
            await self._simulate_security_experiment(solution, experiment)

            experiment.end_time = datetime.now()
            experiment.success = len(experiment.issues_found) == 0

            # Determinar si requiere aprobación de admin
            if experiment.admin_approval_required and not experiment.admin_approved:
                experiment.recommendations.append("Requiere aprobación de administrador antes de implementar")

        except Exception as e:
            experiment.end_time = datetime.now()
            experiment.success = False
            experiment.issues_found.append(f"Experiment failed: {str(e)}")

        self.experiment_results.append(experiment)
        self._save_experiment_results()

        await self._log_learning_event({
            "type": "experiment_completed",
            "experiment_id": experiment.experiment_id,
            "solution_id": solution.solution_id,
            "success": experiment.success,
            "environment": environment
        })

        return experiment

    async def _simulate_security_experiment(self,
                                          solution: SecuritySolution,
                                          experiment: ExperimentResult):
        """Simula la ejecución de un experimento de seguridad"""

        # Simulación básica - en implementación real tendría lógica específica
        import random

        # Simular métricas de performance
        experiment.metrics_collected = {
            "cpu_impact": random.uniform(0.1, 0.3),
            "memory_impact": random.uniform(0.05, 0.15),
            "latency_increase": random.uniform(0.02, 0.08),
            "detection_rate": random.uniform(0.75, 0.95),
            "false_positive_rate": random.uniform(0.01, 0.10)
        }

        # Simular posibles problemas basados en complejidad
        if solution.implementation_complexity > 7:
            if random.random() < 0.3:  # 30% chance de problema en soluciones complejas
                experiment.issues_found.append("High complexity solution showed integration issues")

        if solution.risk_level == ImplementationRisk.CRITICAL:
            if random.random() < 0.2:  # 20% chance de problema en soluciones críticas
                experiment.issues_found.append("Critical risk solution requires additional validation")

        # Generar recomendaciones
        if experiment.metrics_collected["cpu_impact"] > 0.25:
            experiment.recommendations.append("Consider optimizing for CPU usage")

        if experiment.metrics_collected["false_positive_rate"] > 0.05:
            experiment.recommendations.append("Tune detection thresholds to reduce false positives")

    async def request_admin_approval(self,
                                   experiment: ExperimentResult,
                                   justification: str) -> bool:
        """Solicita aprobación de administrador para implementación"""

        approval_request = {
            "experiment_id": experiment.experiment_id,
            "solution_id": experiment.solution_id,
            "justification": justification,
            "risk_assessment": self._generate_risk_assessment(experiment),
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        }

        # En implementación real, esto enviaría notificación al admin
        # Por ahora, simular aprobación automática para testing
        print(f"\n🔐 SOLICITUD DE APROBACIÓN DE ADMINISTRADOR")
        print(f"Experimento ID: {experiment.experiment_id}")
        print(f"Justificación: {justification}")
        print(f"Evaluación de riesgo: {approval_request['risk_assessment']}")
        print("\nEsperando aprobación de administrador...")

        # Simular respuesta de admin (en implementación real sería input real)
        import random
        approved = random.random() > 0.3  # 70% approval rate

        experiment.admin_approved = approved
        experiment.admin_notes = "Auto-approved for demo" if approved else "Requires additional review"

        await self._log_learning_event({
            "type": "admin_approval_requested",
            "experiment_id": experiment.experiment_id,
            "approved": approved,
            "justification": justification
        })

        return approved

    def _generate_risk_assessment(self, experiment: ExperimentResult) -> str:
        """Genera evaluación de riesgo para solicitud de aprobación"""
        assessment = []

        if experiment.success:
            assessment.append("✅ Experiment completed successfully")
        else:
            assessment.append("❌ Experiment had issues")

        if experiment.issues_found:
            assessment.append(f"⚠️  Issues: {', '.join(experiment.issues_found)}")

        if experiment.metrics_collected:
            cpu_impact = experiment.metrics_collected.get("cpu_impact", 0)
            if cpu_impact > 0.2:
                assessment.append(f"⚠️  High CPU impact: {cpu_impact:.1%}")
            else:
                assessment.append(f"✅ Acceptable CPU impact: {cpu_impact:.1%}")

        return " | ".join(assessment)

    async def _log_learning_event(self, event_data: Dict[str, Any]):
        """Registra eventos de aprendizaje para auditoría"""
        try:
            if self.learning_history.exists():
                with open(self.learning_history, 'r') as f:
                    history = json.load(f)
            else:
                history = []

            event_data["timestamp"] = datetime.now().isoformat()
            event_data["event_id"] = str(uuid.uuid4())

            history.append(event_data)

            # Mantener solo últimos 1000 eventos
            history = history[-1000:]

            with open(self.learning_history, 'w') as f:
                json.dump(history, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error logging learning event: {e}")

    def _estimate_complexity(self, mitre_technique: str) -> int:
        """Estima complejidad de implementación basada en técnica MITRE"""
        complexity_map = {
            "T1078": 6,  # Valid Accounts - medium complexity
            "T1110": 4,  # Brute Force - lower complexity
            "T1068": 8,  # Privilege Escalation - high complexity
            "T1059": 7   # Command and Scripting - medium-high complexity
        }
        return complexity_map.get(mitre_technique, 5)

    def _estimate_risk(self, mitre_technique: str, context: LearningContext) -> ImplementationRisk:
        """Estima riesgo de implementación"""
        base_risk_map = {
            "T1078": ImplementationRisk.MEDIUM,
            "T1110": ImplementationRisk.LOW,
            "T1068": ImplementationRisk.HIGH,
            "T1059": ImplementationRisk.HIGH
        }

        base_risk = base_risk_map.get(mitre_technique, ImplementationRisk.MEDIUM)

        # Ajustar basado en contexto
        if "production" in context.environment_data.get("environment", "").lower():
            if base_risk.value < 4:
                return ImplementationRisk(min(4, base_risk.value + 1))

        return base_risk

    # Métodos de conversión para serialización
    def _security_solution_to_dict(self, solution: SecuritySolution) -> Dict[str, Any]:
        result = asdict(solution)
        result["domain"] = solution.domain.value
        result["risk_level"] = solution.risk_level.value
        return result

    def _dict_to_security_solution(self, data: Dict[str, Any]) -> SecuritySolution:
        data["domain"] = SecurityDomain(data["domain"])
        data["risk_level"] = ImplementationRisk(data["risk_level"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("tested_at"):
            data["tested_at"] = datetime.fromisoformat(data["tested_at"])
        if data.get("implemented_at"):
            data["implemented_at"] = datetime.fromisoformat(data["implemented_at"])
        return SecuritySolution(**data)

    def _experiment_result_to_dict(self, experiment: ExperimentResult) -> Dict[str, Any]:
        result = asdict(experiment)
        result["stage"] = experiment.stage.value
        return result

    def _dict_to_experiment_result(self, data: Dict[str, Any]) -> ExperimentResult:
        data["stage"] = LearningStage(data["stage"])
        data["start_time"] = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        return ExperimentResult(**data)


# Ejemplo de uso del framework
async def demo_hrm_learning():
    """Demostración del framework de aprendizaje HRM"""

    print("🧠 SmartCompute HRM Learning Framework Demo")
    print("=" * 50)

    # Inicializar framework
    hrm = SmartComputeHRMLearning()

    # Contexto de aprendizaje
    context = LearningContext(
        context_id=str(uuid.uuid4()),
        trigger_event="brute_force_attack_detected",
        environment_data={"environment": "production", "users": 1000},
        threat_landscape={"attack_vectors": ["ssh", "web"], "severity": "high"},
        business_constraints={"downtime_tolerance": "minimal"},
        compliance_requirements=["SOX", "PCI-DSS"],
        available_resources={"compute": "high", "storage": "medium"}
    )

    # 1. Aprender de implementación exitosa
    implementation_data = {
        "name": "Advanced Brute Force Protection",
        "description": "Multi-layer brute force protection with ML",
        "domain": "authentication",
        "mitre_techniques": ["T1110"],
        "complexity": 6,
        "risk_level": 2,
        "success_metrics": {"attack_prevention": 0.92, "false_positive_rate": 0.03},
        "validation_criteria": ["Block 90%+ brute force", "FP rate < 5%"],
        "rollback_plan": "Automatic rollback on high false positives"
    }

    learned_solution = await hrm.learn_from_successful_implementation(implementation_data, context)
    print(f"✅ Aprendido: {learned_solution.name}")

    # 2. Analizar brecha de seguridad
    threat_data = {
        "mitre_techniques": ["T1110", "T1078"],
        "domain": "authentication",
        "severity": "high"
    }

    proposed_solutions = await hrm.analyze_security_gap(threat_data, context)
    print(f"✅ Propuestas: {len(proposed_solutions)} soluciones")

    # 3. Experimentar con solución
    if proposed_solutions:
        solution = proposed_solutions[0]
        experiment = await hrm.run_experiment(solution, "sandbox")
        print(f"✅ Experimento: {'Exitoso' if experiment.success else 'Falló'}")

        # 4. Evaluar si proceder
        should_proceed, reason = await hrm.should_proceed_with_implementation(
            solution, LearningStage.EXPERIMENTATION, [experiment]
        )
        print(f"✅ Decisión: {'Proceder' if should_proceed else 'Detener'} - {reason}")

        # 5. Solicitar aprobación si es necesario
        if experiment.admin_approval_required:
            approved = await hrm.request_admin_approval(
                experiment,
                f"Solution addresses critical security gap: {threat_data['mitre_techniques']}"
            )
            print(f"✅ Aprobación: {'Concedida' if approved else 'Denegada'}")


if __name__ == "__main__":
    asyncio.run(demo_hrm_learning())