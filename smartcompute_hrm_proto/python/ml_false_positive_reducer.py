#!/usr/bin/env python3
import json
import numpy as np
import pickle
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MLFeatures:
    process_features: List[float]
    behavioral_features: List[float]
    temporal_features: List[float]
    text_features: List[float]

class FalsePositiveMLReducer:
    def __init__(self):
        self.models = {
            "isolation_forest": IsolationForest(contamination=0.1, random_state=42),
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
        }
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []

    def extract_features(self, event_data: Dict, behavioral_analysis: Dict = None) -> MLFeatures:
        """Extraer features para ML"""

        # Features del proceso
        process_features = self._extract_process_features(event_data)

        # Features comportamentales
        behavioral_features = self._extract_behavioral_features(behavioral_analysis or {})

        # Features temporales
        temporal_features = self._extract_temporal_features(event_data)

        # Features de texto
        text_features = self._extract_text_features(event_data)

        return MLFeatures(
            process_features=process_features,
            behavioral_features=behavioral_features,
            temporal_features=temporal_features,
            text_features=text_features
        )

    def _extract_process_features(self, event_data: Dict) -> List[float]:
        """Extraer features relacionadas con el proceso"""
        features = []

        process_path = event_data.get("process_path", "").lower()
        description = event_data.get("description", "").lower()

        # Features binarias del proceso
        features.append(1.0 if "chrome.exe" in process_path else 0.0)
        features.append(1.0 if "firefox.exe" in process_path else 0.0)
        features.append(1.0 if "program files" in process_path else 0.0)
        features.append(1.0 if "system32" in process_path else 0.0)
        features.append(1.0 if "temp" in process_path else 0.0)

        # Features de técnicas de injection
        features.append(1.0 if "createremotethread" in description else 0.0)
        features.append(1.0 if "writeprocessmemory" in description else 0.0)
        features.append(1.0 if "virtualallocex" in description else 0.0)
        features.append(1.0 if "loadlibrary" in description else 0.0)

        # Longitud del path (normalizada)
        features.append(min(len(process_path) / 100.0, 1.0))

        return features

    def _extract_behavioral_features(self, behavioral_analysis: Dict) -> List[float]:
        """Extraer features comportamentales"""
        features = []

        behavioral_score = behavioral_analysis.get("behavioral_score", 0.0)
        features.append(behavioral_score / 10.0)  # Normalizar

        context_insights = behavioral_analysis.get("context_insights", {})

        # Features de proceso
        process_insights = context_insights.get("process", {})
        features.append(1.0 if process_insights.get("is_known_process", False) else 0.0)
        features.append(len(process_insights.get("behavioral_anomalies", [])) / 5.0)  # Normalizar

        # Features de usuario
        user_insights = context_insights.get("user", {})
        features.append(1.0 if user_insights.get("is_known_user", False) else 0.0)
        features.append(1.0 if user_insights.get("location_anomaly", False) else 0.0)
        features.append(1.0 if user_insights.get("time_anomaly", False) else 0.0)

        # Features temporales
        temporal_insights = context_insights.get("temporal", {})
        features.append(1.0 if temporal_insights.get("is_business_hours", False) else 0.0)
        features.append(len(temporal_insights.get("temporal_anomalies", [])) / 3.0)  # Normalizar

        return features

    def _extract_temporal_features(self, event_data: Dict) -> List[float]:
        """Extraer features temporales"""
        features = []

        timestamp = event_data.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

                # Hora del día (0-23) normalizada
                features.append(dt.hour / 23.0)

                # Día de la semana (0-6) normalizada
                features.append(dt.weekday() / 6.0)

                # Es fin de semana
                features.append(1.0 if dt.weekday() >= 5 else 0.0)

                # Es horario nocturno
                features.append(1.0 if dt.hour < 6 or dt.hour > 22 else 0.0)

            except:
                features = [0.0, 0.0, 0.0, 0.0]  # Features por defecto
        else:
            features = [0.0, 0.0, 0.0, 0.0]

        return features

    def _extract_text_features(self, event_data: Dict) -> List[float]:
        """Extraer features de texto usando TF-IDF"""
        description = event_data.get("description", "")
        raw_payload = event_data.get("raw_payload", "")

        # Combinar textos
        combined_text = f"{description} {raw_payload}"

        if not hasattr(self, '_text_features_fitted'):
            # Para el primer uso, crear vocabulario básico
            basic_vocab = [
                "createremotethread", "chrome", "process", "thread", "memory",
                "inject", "dll", "library", "suspicious", "malware"
            ]
            # Simular features de texto
            text_features = []
            for word in basic_vocab[:10]:  # Usar solo las primeras 10
                text_features.append(1.0 if word.lower() in combined_text.lower() else 0.0)
            return text_features

        return [0.0] * 10  # Placeholder

    def generate_training_data(self, num_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generar datos de entrenamiento sintéticos"""
        print(f"Generating {num_samples} synthetic training samples...")

        X = []
        y = []

        for i in range(num_samples):
            # Generar evento sintético
            if i % 2 == 0:
                # Evento legítimo
                event = self._generate_legitimate_event()
                label = 0  # No es falso positivo
            else:
                # Evento potencialmente falso positivo
                event = self._generate_false_positive_event()
                label = 1  # Es falso positivo

            # Extraer features
            features = self.extract_features(event)
            combined_features = (
                features.process_features +
                features.behavioral_features +
                features.temporal_features +
                features.text_features
            )

            X.append(combined_features)
            y.append(label)

        return np.array(X), np.array(y)

    def _generate_legitimate_event(self) -> Dict:
        """Generar evento legítimo para entrenamiento"""
        events = [
            {
                "event_id": np.random.randint(1, 1000),
                "description": "CreateRemoteThread observed targeting malware.exe",
                "process_path": "C:\\Users\\Public\\malware.exe",
                "raw_payload": "CreateRemoteThread suspicious activity detected",
                "timestamp": "2025-09-15T03:23:00Z",  # Horario sospechoso
                "severity": "CRITICAL"
            },
            {
                "event_id": np.random.randint(1, 1000),
                "description": "DLL injection detected in unknown process",
                "process_path": "C:\\temp\\suspicious.exe",
                "raw_payload": "LoadLibrary and GetProcAddress sequence",
                "timestamp": "2025-09-15T14:23:00Z",
                "severity": "HIGH"
            }
        ]
        return np.random.choice(events)

    def _generate_false_positive_event(self) -> Dict:
        """Generar evento de falso positivo para entrenamiento"""
        events = [
            {
                "event_id": np.random.randint(1, 1000),
                "description": "CreateRemoteThread observed targeting chrome.exe",
                "process_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "raw_payload": "CreateRemoteThread to process chrome extension loading",
                "timestamp": "2025-09-15T14:23:00Z",  # Horario normal
                "severity": "MEDIUM"
            },
            {
                "event_id": np.random.randint(1, 1000),
                "description": "DLL injection detected in system process",
                "process_path": "C:\\Windows\\System32\\svchost.exe",
                "raw_payload": "LoadLibrary legitimate system operation",
                "timestamp": "2025-09-15T10:30:00Z",
                "severity": "LOW"
            }
        ]
        return np.random.choice(events)

    def train_models(self, X: np.ndarray, y: np.ndarray):
        """Entrenar modelos ML"""
        print("Training ML models...")

        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)

        # Entrenar Random Forest para clasificación
        self.models["random_forest"].fit(X_scaled, y)

        # Entrenar Isolation Forest para detección de anomalías
        # Para Isolation Forest, usamos solo eventos no-falso-positivo como "normales"
        X_normal = X_scaled[y == 0]
        self.models["isolation_forest"].fit(X_normal)

        self.is_trained = True
        print("Models trained successfully!")

    def predict_false_positive_probability(self, event_data: Dict, behavioral_analysis: Dict = None) -> Dict:
        """Predecir probabilidad de falso positivo"""
        if not self.is_trained:
            return {"error": "Models not trained yet"}

        # Extraer features
        features = self.extract_features(event_data, behavioral_analysis)
        combined_features = np.array([
            features.process_features +
            features.behavioral_features +
            features.temporal_features +
            features.text_features
        ])

        # Normalizar
        X_scaled = self.scaler.transform(combined_features)

        # Predicciones
        rf_prob = self.models["random_forest"].predict_proba(X_scaled)[0][1]  # Prob de falso positivo
        isolation_score = self.models["isolation_forest"].decision_function(X_scaled)[0]

        # Combinar scores
        combined_confidence = (rf_prob + max(0, (isolation_score + 0.5))) / 2

        return {
            "false_positive_probability": float(rf_prob),
            "anomaly_score": float(isolation_score),
            "combined_confidence": float(combined_confidence),
            "recommendation": self._generate_ml_recommendation(rf_prob, isolation_score)
        }

    def _generate_ml_recommendation(self, fp_prob: float, anomaly_score: float) -> str:
        """Generar recomendación basada en ML"""
        if fp_prob > 0.7:
            return "HIGH_CONFIDENCE_FALSE_POSITIVE: Consider lowering alert priority"
        elif fp_prob > 0.4:
            return "POSSIBLE_FALSE_POSITIVE: Requires additional analysis"
        elif anomaly_score < -0.3:
            return "HIGH_CONFIDENCE_THREAT: Immediate investigation required"
        else:
            return "MEDIUM_CONFIDENCE: Standard investigation protocol"

def main():
    # Crear y entrenar el reductor de falsos positivos
    ml_reducer = FalsePositiveMLReducer()

    # Generar datos de entrenamiento
    X, y = ml_reducer.generate_training_data(500)

    # Entrenar modelos
    ml_reducer.train_models(X, y)

    # Cargar evento real para análisis
    with open("../redacted_output.json", "r") as f:
        data = json.load(f)

    # Cargar análisis comportamental si existe
    try:
        with open("../plans/behavioral_analysis_8.json", "r") as f:
            behavioral_analysis = json.load(f)
    except:
        behavioral_analysis = None

    if "findings" in data:
        for finding in data["findings"]:
            print(f"\n=== ML False Positive Analysis for Event {finding.get('event_id', 'Unknown')} ===")

            # Predecir probabilidad de falso positivo
            ml_result = ml_reducer.predict_false_positive_probability(finding, behavioral_analysis)

            print(f"False Positive Probability: {ml_result['false_positive_probability']:.3f}")
            print(f"Anomaly Score: {ml_result['anomaly_score']:.3f}")
            print(f"Combined Confidence: {ml_result['combined_confidence']:.3f}")
            print(f"ML Recommendation: {ml_result['recommendation']}")

            # Guardar resultado
            output_file = f"../plans/ml_analysis_{finding.get('event_id', 'unknown')}.json"
            with open(output_file, "w") as f:
                json.dump(ml_result, f, indent=2)
            print(f"\nML analysis saved to: {output_file}")

if __name__ == "__main__":
    main()