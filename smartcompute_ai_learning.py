#!/usr/bin/env python3
"""
SmartCompute Industrial - Sistema de Aprendizaje Continuo de IA
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Sistema de aprendizaje continuo que analiza intervenciones, resultados y feedback
para mejorar las recomendaciones futuras de la IA.
"""

import json
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import pickle
import hashlib
import statistics
from collections import defaultdict, Counter
import threading
import time

@dataclass
class InterventionRecord:
    intervention_id: str
    session_id: str
    operator_id: str
    timestamp: datetime
    problem_description: str
    ai_recommendations: List[Dict[str, Any]]
    actions_taken: List[Dict[str, Any]]
    outcome: str  # "successful", "partial", "failed"
    resolution_time: float  # minutos
    feedback_score: Optional[float] = None  # 1-5
    lesson_learned: Optional[str] = None

@dataclass
class LearningPattern:
    pattern_id: str
    pattern_type: str  # "success_factor", "failure_mode", "optimization"
    description: str
    conditions: Dict[str, Any]
    outcomes: Dict[str, Any]
    confidence: float
    frequency: int
    last_updated: datetime

@dataclass
class AIModelMetrics:
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    total_predictions: int
    correct_predictions: int
    last_updated: datetime

class SmartComputeAILearning:
    """
    Sistema de aprendizaje continuo para SmartCompute Industrial
    """

    def __init__(self, db_path: str = "smartcompute_learning.db"):
        self.db_path = db_path
        self.learning_patterns = {}
        self.intervention_history = {}
        self.model_metrics = {}
        self.feedback_buffer = []

        # Configuración de aprendizaje
        self.config = {
            "min_pattern_frequency": 3,
            "confidence_threshold": 0.75,
            "feedback_window_hours": 24,
            "model_update_interval": 3600,  # segundos
            "max_history_days": 90
        }

        self.initialize_database()
        self.load_existing_patterns()

        # Hilo de procesamiento continuo
        self.learning_thread = threading.Thread(target=self._continuous_learning_loop, daemon=True)
        self.learning_thread.start()

    def initialize_database(self):
        """Inicializar base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla de intervenciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interventions (
                intervention_id TEXT PRIMARY KEY,
                session_id TEXT,
                operator_id TEXT,
                timestamp TEXT,
                problem_description TEXT,
                ai_recommendations TEXT,
                actions_taken TEXT,
                outcome TEXT,
                resolution_time REAL,
                feedback_score REAL,
                lesson_learned TEXT
            )
        ''')

        # Tabla de patrones aprendidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                description TEXT,
                conditions TEXT,
                outcomes TEXT,
                confidence REAL,
                frequency INTEGER,
                last_updated TEXT
            )
        ''')

        # Tabla de métricas del modelo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                model_version TEXT PRIMARY KEY,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                total_predictions INTEGER,
                correct_predictions INTEGER,
                last_updated TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print("📊 Base de datos de aprendizaje inicializada")

    def load_existing_patterns(self):
        """Cargar patrones existentes desde la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM learning_patterns")
        for row in cursor.fetchall():
            pattern = LearningPattern(
                pattern_id=row[0],
                pattern_type=row[1],
                description=row[2],
                conditions=json.loads(row[3]),
                outcomes=json.loads(row[4]),
                confidence=row[5],
                frequency=row[6],
                last_updated=datetime.fromisoformat(row[7])
            )
            self.learning_patterns[pattern.pattern_id] = pattern

        conn.close()
        print(f"🧠 {len(self.learning_patterns)} patrones de aprendizaje cargados")

    def record_intervention(self, intervention: InterventionRecord):
        """Registrar una nueva intervención para aprendizaje"""

        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO interventions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            intervention.intervention_id,
            intervention.session_id,
            intervention.operator_id,
            intervention.timestamp.isoformat(),
            intervention.problem_description,
            json.dumps(intervention.ai_recommendations, default=str),
            json.dumps(intervention.actions_taken, default=str),
            intervention.outcome,
            intervention.resolution_time,
            intervention.feedback_score,
            intervention.lesson_learned
        ))

        conn.commit()
        conn.close()

        # Guardar en memoria para procesamiento
        self.intervention_history[intervention.intervention_id] = intervention

        # Disparar análisis inmediato si es una intervención crítica
        if intervention.outcome == "failed" or (intervention.feedback_score and intervention.feedback_score <= 2):
            self._analyze_failure_immediately(intervention)

        print(f"📝 Intervención registrada: {intervention.intervention_id}")

    def add_feedback(self, intervention_id: str, feedback_score: float,
                    detailed_feedback: str = None):
        """Agregar feedback de usuario sobre una intervención"""

        if intervention_id in self.intervention_history:
            intervention = self.intervention_history[intervention_id]
            intervention.feedback_score = feedback_score
            intervention.lesson_learned = detailed_feedback

            # Actualizar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE interventions
                SET feedback_score = ?, lesson_learned = ?
                WHERE intervention_id = ?
            ''', (feedback_score, detailed_feedback, intervention_id))

            conn.commit()
            conn.close()

            # Agregar a buffer para procesamiento
            self.feedback_buffer.append({
                "intervention_id": intervention_id,
                "feedback_score": feedback_score,
                "feedback_text": detailed_feedback,
                "timestamp": datetime.now()
            })

            print(f"💬 Feedback agregado para {intervention_id}: {feedback_score}/5")

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analizar patrones en las intervenciones"""

        print("🔍 Analizando patrones de aprendizaje...")

        analysis_results = {
            "success_patterns": self._analyze_success_patterns(),
            "failure_patterns": self._analyze_failure_patterns(),
            "efficiency_patterns": self._analyze_efficiency_patterns(),
            "operator_patterns": self._analyze_operator_patterns(),
            "equipment_patterns": self._analyze_equipment_patterns()
        }

        # Actualizar patrones existentes
        self._update_learning_patterns(analysis_results)

        return analysis_results

    def _analyze_success_patterns(self) -> List[Dict[str, Any]]:
        """Analizar patrones de intervenciones exitosas"""

        successful = [i for i in self.intervention_history.values()
                     if i.outcome == "successful" and i.feedback_score and i.feedback_score >= 4]

        if len(successful) < self.config["min_pattern_frequency"]:
            return []

        patterns = []

        # Agrupar por tipo de problema
        problem_groups = defaultdict(list)
        for intervention in successful:
            problem_type = self._categorize_problem(intervention.problem_description)
            problem_groups[problem_type].append(intervention)

        for problem_type, interventions in problem_groups.items():
            if len(interventions) >= self.config["min_pattern_frequency"]:

                # Analizar acciones comunes
                common_actions = self._find_common_actions(interventions)
                avg_resolution_time = statistics.mean([i.resolution_time for i in interventions])
                avg_feedback = statistics.mean([i.feedback_score for i in interventions if i.feedback_score])

                pattern = {
                    "pattern_type": "success_factor",
                    "problem_category": problem_type,
                    "common_actions": common_actions,
                    "avg_resolution_time": avg_resolution_time,
                    "avg_feedback_score": avg_feedback,
                    "frequency": len(interventions),
                    "confidence": min(0.95, len(interventions) / 10)
                }

                patterns.append(pattern)

        return patterns

    def _analyze_failure_patterns(self) -> List[Dict[str, Any]]:
        """Analizar patrones de intervenciones fallidas"""

        failed = [i for i in self.intervention_history.values()
                 if i.outcome == "failed" or (i.feedback_score and i.feedback_score <= 2)]

        if len(failed) < 2:
            return []

        patterns = []

        # Analizar causas comunes de falla
        failure_reasons = Counter()
        for intervention in failed:
            if intervention.lesson_learned:
                # Extraer palabras clave de lecciones aprendidas
                keywords = self._extract_keywords(intervention.lesson_learned)
                for keyword in keywords:
                    failure_reasons[keyword] += 1

        # Identificar patrones de falla más comunes
        for reason, frequency in failure_reasons.most_common(5):
            if frequency >= 2:
                related_interventions = [
                    i for i in failed
                    if i.lesson_learned and reason.lower() in i.lesson_learned.lower()
                ]

                pattern = {
                    "pattern_type": "failure_mode",
                    "failure_reason": reason,
                    "frequency": frequency,
                    "related_problems": [i.problem_description for i in related_interventions],
                    "avg_resolution_time": statistics.mean([i.resolution_time for i in related_interventions]),
                    "confidence": min(0.9, frequency / 5)
                }

                patterns.append(pattern)

        return patterns

    def _analyze_efficiency_patterns(self) -> List[Dict[str, Any]]:
        """Analizar patrones de eficiencia"""

        all_interventions = list(self.intervention_history.values())
        if len(all_interventions) < 5:
            return []

        patterns = []

        # Analizar tiempo de resolución por operador
        operator_times = defaultdict(list)
        for intervention in all_interventions:
            operator_times[intervention.operator_id].append(intervention.resolution_time)

        # Identificar operadores más eficientes
        operator_efficiency = {}
        for operator_id, times in operator_times.items():
            if len(times) >= 3:
                avg_time = statistics.mean(times)
                operator_efficiency[operator_id] = avg_time

        if operator_efficiency:
            best_operators = sorted(operator_efficiency.items(), key=lambda x: x[1])[:3]

            pattern = {
                "pattern_type": "efficiency_optimization",
                "category": "operator_performance",
                "best_performers": best_operators,
                "optimization_potential": max(operator_efficiency.values()) - min(operator_efficiency.values()),
                "confidence": 0.8
            }

            patterns.append(pattern)

        return patterns

    def _analyze_operator_patterns(self) -> Dict[str, Any]:
        """Analizar patrones específicos por operador"""

        operator_stats = defaultdict(lambda: {
            "total_interventions": 0,
            "successful": 0,
            "avg_resolution_time": 0,
            "avg_feedback": 0,
            "specialties": []
        })

        for intervention in self.intervention_history.values():
            stats = operator_stats[intervention.operator_id]
            stats["total_interventions"] += 1

            if intervention.outcome == "successful":
                stats["successful"] += 1

            if intervention.resolution_time:
                stats["avg_resolution_time"] = (
                    (stats["avg_resolution_time"] * (stats["total_interventions"] - 1) +
                     intervention.resolution_time) / stats["total_interventions"]
                )

            if intervention.feedback_score:
                stats["avg_feedback"] = (
                    (stats["avg_feedback"] * (stats["total_interventions"] - 1) +
                     intervention.feedback_score) / stats["total_interventions"]
                )

        return dict(operator_stats)

    def _analyze_equipment_patterns(self) -> Dict[str, Any]:
        """Analizar patrones por tipo de equipo"""

        equipment_stats = defaultdict(lambda: {
            "total_problems": 0,
            "common_issues": Counter(),
            "resolution_success_rate": 0,
            "avg_resolution_time": 0
        })

        for intervention in self.intervention_history.values():
            # Extraer tipo de equipo del problema
            equipment_type = self._extract_equipment_type(intervention.problem_description)

            stats = equipment_stats[equipment_type]
            stats["total_problems"] += 1

            # Categorizar issue
            issue_type = self._categorize_problem(intervention.problem_description)
            stats["common_issues"][issue_type] += 1

            if intervention.outcome == "successful":
                stats["resolution_success_rate"] += 1

            if intervention.resolution_time:
                stats["avg_resolution_time"] = (
                    (stats["avg_resolution_time"] * (stats["total_problems"] - 1) +
                     intervention.resolution_time) / stats["total_problems"]
                )

        # Calcular tasas de éxito
        for equipment_type, stats in equipment_stats.items():
            if stats["total_problems"] > 0:
                stats["resolution_success_rate"] = stats["resolution_success_rate"] / stats["total_problems"]

        return dict(equipment_stats)

    def generate_improved_recommendations(self, problem_description: str,
                                        context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar recomendaciones mejoradas basadas en aprendizaje"""

        print(f"🤖 Generando recomendaciones mejoradas para: {problem_description[:50]}...")

        # Categorizar problema
        problem_category = self._categorize_problem(problem_description)
        equipment_type = self._extract_equipment_type(problem_description)

        # Buscar patrones relevantes
        relevant_patterns = self._find_relevant_patterns(problem_category, equipment_type, context)

        # Generar recomendaciones base
        base_recommendations = self._generate_base_recommendations(problem_description, context)

        # Mejorar con patrones aprendidos
        improved_recommendations = self._enhance_with_learned_patterns(
            base_recommendations, relevant_patterns
        )

        # Ordenar por probabilidad de éxito
        improved_recommendations = self._rank_by_success_probability(
            improved_recommendations, problem_category, equipment_type
        )

        return improved_recommendations

    def _find_relevant_patterns(self, problem_category: str, equipment_type: str,
                               context: Dict[str, Any]) -> List[LearningPattern]:
        """Encontrar patrones relevantes para el problema actual"""

        relevant = []

        for pattern in self.learning_patterns.values():
            relevance_score = 0

            # Coincidencia de categoría
            if pattern.conditions.get("problem_category") == problem_category:
                relevance_score += 0.4

            # Coincidencia de equipo
            if pattern.conditions.get("equipment_type") == equipment_type:
                relevance_score += 0.3

            # Coincidencia de contexto
            for key, value in context.items():
                if pattern.conditions.get(key) == value:
                    relevance_score += 0.1

            # Filtrar por confianza y relevancia
            if relevance_score >= 0.3 and pattern.confidence >= self.config["confidence_threshold"]:
                relevant.append(pattern)

        return sorted(relevant, key=lambda p: p.confidence, reverse=True)

    def _enhance_with_learned_patterns(self, base_recommendations: List[Dict[str, Any]],
                                     patterns: List[LearningPattern]) -> List[Dict[str, Any]]:
        """Mejorar recomendaciones con patrones aprendidos"""

        enhanced = base_recommendations.copy()

        for pattern in patterns:
            if pattern.pattern_type == "success_factor":
                # Agregar acciones exitosas conocidas
                for action in pattern.outcomes.get("common_actions", []):
                    if not any(rec["action"] == action for rec in enhanced):
                        enhanced.append({
                            "action": action,
                            "priority": "alta",
                            "confidence": pattern.confidence,
                            "source": "learned_pattern",
                            "pattern_id": pattern.pattern_id,
                            "success_rate": pattern.outcomes.get("success_rate", 0.8)
                        })

            elif pattern.pattern_type == "failure_mode":
                # Agregar advertencias sobre acciones que suelen fallar
                for rec in enhanced:
                    if any(keyword in rec["action"].lower()
                          for keyword in pattern.conditions.get("failure_keywords", [])):
                        rec["warnings"] = rec.get("warnings", [])
                        rec["warnings"].append(f"Precaución: {pattern.description}")

        return enhanced

    def _rank_by_success_probability(self, recommendations: List[Dict[str, Any]],
                                   problem_category: str, equipment_type: str) -> List[Dict[str, Any]]:
        """Ordenar recomendaciones por probabilidad de éxito"""

        for rec in recommendations:
            # Calcular probabilidad basada en historial
            success_prob = self._calculate_action_success_probability(
                rec["action"], problem_category, equipment_type
            )
            rec["success_probability"] = success_prob

        # Ordenar por probabilidad de éxito
        return sorted(recommendations, key=lambda r: r.get("success_probability", 0.5), reverse=True)

    def _calculate_action_success_probability(self, action: str, problem_category: str,
                                           equipment_type: str) -> float:
        """Calcular probabilidad de éxito de una acción específica"""

        relevant_interventions = []

        for intervention in self.intervention_history.values():
            # Buscar intervenciones similares
            if (self._categorize_problem(intervention.problem_description) == problem_category and
                self._extract_equipment_type(intervention.problem_description) == equipment_type):

                # Verificar si se usó acción similar
                for taken_action in intervention.actions_taken:
                    if self._actions_are_similar(action, taken_action.get("action", "")):
                        relevant_interventions.append(intervention)
                        break

        if not relevant_interventions:
            return 0.5  # Probabilidad neutral sin datos

        successful = sum(1 for i in relevant_interventions if i.outcome == "successful")
        return successful / len(relevant_interventions)

    def _continuous_learning_loop(self):
        """Bucle continuo de aprendizaje en hilo separado"""

        while True:
            try:
                # Procesar feedback pendiente
                if self.feedback_buffer:
                    self._process_feedback_buffer()

                # Actualizar patrones cada hora
                if int(time.time()) % self.config["model_update_interval"] == 0:
                    self.analyze_patterns()
                    self._cleanup_old_data()

                time.sleep(60)  # Verificar cada minuto

            except Exception as e:
                print(f"❌ Error en bucle de aprendizaje: {e}")
                time.sleep(300)  # Esperar 5 minutos en caso de error

    def _process_feedback_buffer(self):
        """Procesar feedback acumulado"""

        for feedback in self.feedback_buffer:
            intervention_id = feedback["intervention_id"]

            if intervention_id in self.intervention_history:
                intervention = self.intervention_history[intervention_id]

                # Actualizar métricas del modelo
                self._update_model_metrics(intervention, feedback)

                # Si es feedback negativo, analizar inmediatamente
                if feedback["feedback_score"] <= 2:
                    self._analyze_failure_immediately(intervention)

        self.feedback_buffer.clear()

    def _update_model_metrics(self, intervention: InterventionRecord, feedback: Dict[str, Any]):
        """Actualizar métricas del modelo de IA"""

        model_version = "v2.0"  # Versión actual

        if model_version not in self.model_metrics:
            self.model_metrics[model_version] = AIModelMetrics(
                model_version=model_version,
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                total_predictions=0,
                correct_predictions=0,
                last_updated=datetime.now()
            )

        metrics = self.model_metrics[model_version]
        metrics.total_predictions += 1

        # Considerar predicción correcta si feedback >= 4 y outcome successful
        if feedback["feedback_score"] >= 4 and intervention.outcome == "successful":
            metrics.correct_predictions += 1

        # Recalcular accuracy
        metrics.accuracy = metrics.correct_predictions / metrics.total_predictions
        metrics.last_updated = datetime.now()

    def get_learning_summary(self) -> Dict[str, Any]:
        """Obtener resumen del aprendizaje del sistema"""

        total_interventions = len(self.intervention_history)
        successful = sum(1 for i in self.intervention_history.values() if i.outcome == "successful")

        avg_resolution_time = 0
        avg_feedback = 0

        if total_interventions > 0:
            valid_times = [i.resolution_time for i in self.intervention_history.values() if i.resolution_time]
            if valid_times:
                avg_resolution_time = statistics.mean(valid_times)

            valid_feedback = [i.feedback_score for i in self.intervention_history.values() if i.feedback_score]
            if valid_feedback:
                avg_feedback = statistics.mean(valid_feedback)

        return {
            "total_interventions": total_interventions,
            "success_rate": successful / total_interventions if total_interventions > 0 else 0,
            "avg_resolution_time_minutes": round(avg_resolution_time, 1),
            "avg_feedback_score": round(avg_feedback, 1),
            "patterns_learned": len(self.learning_patterns),
            "model_accuracy": self.model_metrics.get("v2.0", {}).accuracy if "v2.0" in self.model_metrics else 0,
            "last_analysis": datetime.now().isoformat()
        }

    # Métodos auxiliares
    def _categorize_problem(self, description: str) -> str:
        """Categorizar problema basado en descripción"""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ["comunicación", "red", "network", "timeout"]):
            return "communication"
        elif any(word in desc_lower for word in ["sensor", "medición", "lectura"]):
            return "sensor"
        elif any(word in desc_lower for word in ["motor", "actuador", "movimiento"]):
            return "mechanical"
        elif any(word in desc_lower for word in ["temperatura", "térmica", "calor"]):
            return "thermal"
        elif any(word in desc_lower for word in ["eléctrico", "voltaje", "corriente"]):
            return "electrical"
        else:
            return "general"

    def _extract_equipment_type(self, description: str) -> str:
        """Extraer tipo de equipo de la descripción"""
        desc_lower = description.lower()

        if "plc" in desc_lower or "controlador" in desc_lower:
            return "plc"
        elif "hmi" in desc_lower or "pantalla" in desc_lower:
            return "hmi"
        elif "ups" in desc_lower:
            return "ups"
        elif "switch" in desc_lower:
            return "switch"
        elif "sensor" in desc_lower:
            return "sensor"
        elif "motor" in desc_lower:
            return "motor"
        else:
            return "unknown"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extraer palabras clave de texto"""
        import re

        # Palabras relevantes para problemas industriales
        relevant_words = re.findall(r'\b\w{4,}\b', text.lower())

        # Filtrar palabras comunes
        stop_words = {"para", "esta", "este", "con", "sin", "por", "que", "una", "como", "muy"}
        keywords = [word for word in relevant_words if word not in stop_words]

        return keywords[:10]  # Top 10 keywords

    def _find_common_actions(self, interventions: List[InterventionRecord]) -> List[str]:
        """Encontrar acciones comunes en intervenciones"""
        action_counter = Counter()

        for intervention in interventions:
            for action in intervention.actions_taken:
                action_text = action.get("action", "")
                if action_text:
                    action_counter[action_text] += 1

        # Retornar acciones que aparecen en al menos 30% de las intervenciones
        min_frequency = max(1, len(interventions) * 0.3)
        return [action for action, count in action_counter.items() if count >= min_frequency]

    def _actions_are_similar(self, action1: str, action2: str) -> bool:
        """Determinar si dos acciones son similares"""
        # Implementación simple basada en palabras clave comunes
        words1 = set(action1.lower().split())
        words2 = set(action2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        similarity = len(intersection) / len(union) if union else 0
        return similarity >= 0.6

    def _generate_base_recommendations(self, problem_description: str,
                                     context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar recomendaciones base (simuladas)"""
        return [
            {
                "action": "Verificar conexiones físicas",
                "priority": "alta",
                "confidence": 0.8,
                "source": "base_rules"
            },
            {
                "action": "Revisar configuración de red",
                "priority": "media",
                "confidence": 0.7,
                "source": "base_rules"
            }
        ]

    def _analyze_failure_immediately(self, intervention: InterventionRecord):
        """Analizar falla inmediatamente para aprendizaje rápido"""
        print(f"⚠️ Analizando falla inmediata: {intervention.intervention_id}")

        # Crear patrón de falla inmediato
        pattern_id = f"FAIL-{int(time.time())}"

        failure_pattern = LearningPattern(
            pattern_id=pattern_id,
            pattern_type="immediate_failure",
            description=f"Falla inmediata: {intervention.problem_description[:100]}",
            conditions={
                "problem_category": self._categorize_problem(intervention.problem_description),
                "equipment_type": self._extract_equipment_type(intervention.problem_description),
                "operator_id": intervention.operator_id
            },
            outcomes={
                "failed_actions": [action.get("action", "") for action in intervention.actions_taken],
                "resolution_time": intervention.resolution_time,
                "lesson": intervention.lesson_learned
            },
            confidence=0.9,
            frequency=1,
            last_updated=datetime.now()
        )

        self.learning_patterns[pattern_id] = failure_pattern

    def _update_learning_patterns(self, analysis_results: Dict[str, Any]):
        """Actualizar patrones de aprendizaje en base de datos"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for category, patterns in analysis_results.items():
            for pattern_data in patterns:
                if isinstance(pattern_data, dict):
                    pattern_id = f"{category}-{hashlib.md5(str(pattern_data).encode()).hexdigest()[:8]}"

                    cursor.execute('''
                        INSERT OR REPLACE INTO learning_patterns VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pattern_id,
                        pattern_data.get("pattern_type", category),
                        str(pattern_data),
                        json.dumps(pattern_data.get("conditions", {})),
                        json.dumps(pattern_data.get("outcomes", pattern_data)),
                        pattern_data.get("confidence", 0.7),
                        pattern_data.get("frequency", 1),
                        datetime.now().isoformat()
                    ))

        conn.commit()
        conn.close()

    def _cleanup_old_data(self):
        """Limpiar datos antiguos"""
        cutoff_date = datetime.now() - timedelta(days=self.config["max_history_days"])

        old_interventions = [
            iid for iid, intervention in self.intervention_history.items()
            if intervention.timestamp < cutoff_date
        ]

        for iid in old_interventions:
            del self.intervention_history[iid]

        if old_interventions:
            print(f"🧹 Limpieza: {len(old_interventions)} intervenciones antiguas eliminadas")

def main():
    """Función principal de demostración"""
    print("=== SmartCompute Industrial - Sistema de Aprendizaje Continuo ===")
    print("Desarrollado por: ggwre04p0@mozmail.com")
    print("LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
    print()

    # Inicializar sistema de aprendizaje
    learning_system = SmartComputeAILearning()

    # Simular algunas intervenciones
    demo_interventions = [
        InterventionRecord(
            intervention_id="INT-001",
            session_id="SES-001",
            operator_id="OP001",
            timestamp=datetime.now() - timedelta(hours=2),
            problem_description="PLC Siemens S7-1214C no responde a comandos HMI",
            ai_recommendations=[
                {"action": "Verificar conexión Ethernet", "priority": "alta"},
                {"action": "Reiniciar PLC", "priority": "media"}
            ],
            actions_taken=[
                {"action": "Verificar conexión Ethernet", "result": "Cable dañado encontrado"},
                {"action": "Reemplazar cable Ethernet", "result": "Comunicación restaurada"}
            ],
            outcome="successful",
            resolution_time=25.5,
            feedback_score=5.0,
            lesson_learned="Cables Ethernet en ambiente industrial requieren protección adicional"
        ),
        InterventionRecord(
            intervention_id="INT-002",
            session_id="SES-002",
            operator_id="OP001",
            timestamp=datetime.now() - timedelta(hours=1),
            problem_description="Sensor de temperatura en horno muestra lecturas erráticas",
            ai_recommendations=[
                {"action": "Calibrar sensor", "priority": "alta"},
                {"action": "Verificar alimentación", "priority": "media"}
            ],
            actions_taken=[
                {"action": "Calibrar sensor", "result": "Sin mejora"},
                {"action": "Reemplazar sensor", "result": "Problema resuelto"}
            ],
            outcome="successful",
            resolution_time=45.0,
            feedback_score=4.0,
            lesson_learned="Sensores térmicos en ambientes extremos tienen vida útil reducida"
        )
    ]

    # Registrar intervenciones
    for intervention in demo_interventions:
        learning_system.record_intervention(intervention)

    # Agregar feedback adicional
    learning_system.add_feedback("INT-001", 5.0, "Excelente diagnóstico, problema resuelto rápidamente")

    # Analizar patrones
    patterns = learning_system.analyze_patterns()

    # Generar recomendaciones mejoradas
    improved_recs = learning_system.generate_improved_recommendations(
        "PLC Allen-Bradley no se comunica con sistema SCADA",
        {"equipment_type": "plc", "location": "planta_principal"}
    )

    # Mostrar resultados
    print("📊 RESULTADOS DEL APRENDIZAJE:")
    summary = learning_system.get_learning_summary()

    print(f"  📈 Total intervenciones: {summary['total_interventions']}")
    print(f"  ✅ Tasa de éxito: {summary['success_rate']:.1%}")
    print(f"  ⏱️ Tiempo promedio resolución: {summary['avg_resolution_time_minutes']} min")
    print(f"  ⭐ Puntuación promedio: {summary['avg_feedback_score']}/5")
    print(f"  🧠 Patrones aprendidos: {summary['patterns_learned']}")

    print(f"\n🔍 PATRONES IDENTIFICADOS:")
    for category, pattern_list in patterns.items():
        if pattern_list:
            print(f"  {category.replace('_', ' ').title()}: {len(pattern_list)} patrones")

    print(f"\n🤖 RECOMENDACIONES MEJORADAS:")
    for i, rec in enumerate(improved_recs[:3], 1):
        prob = rec.get("success_probability", 0) * 100
        print(f"  {i}. {rec['action']} (Éxito: {prob:.0f}%)")

    print("\n✅ SISTEMA DE APRENDIZAJE INICIADO")
    print("💡 El sistema continúa aprendiendo en segundo plano")

if __name__ == "__main__":
    main()