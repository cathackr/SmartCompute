#!/usr/bin/env python3
"""
SmartCompute False Positive Detection System
Advanced ML-based system to minimize false alerts and improve accuracy
"""

import numpy as np
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import statistics
from collections import deque, defaultdict
import threading
import pickle
import os


@dataclass
class AlertEvent:
    """Structure for alert events"""
    timestamp: datetime
    alert_type: str
    severity: str
    metrics: Dict[str, float]
    was_false_positive: Optional[bool] = None
    confidence_score: float = 0.0
    context: Dict[str, Any] = None


class PatternLearningEngine:
    """
    Machine learning engine that learns from historical data
    to identify false positive patterns
    """
    
    def __init__(self, model_file: str = "fp_detection_model.pkl"):
        self.model_file = model_file
        self.alert_history: deque = deque(maxlen=10000)
        self.pattern_weights = defaultdict(float)
        self.learned_patterns = {}
        self.confidence_threshold = 0.7
        self.learning_enabled = True
        
        # Load existing model if available
        self._load_model()
    
    def add_alert_event(self, event: AlertEvent) -> None:
        """Add new alert event to history"""
        self.alert_history.append(event)
        
        # Auto-learn patterns if enough data
        if len(self.alert_history) > 100 and len(self.alert_history) % 50 == 0:
            self._update_learned_patterns()
    
    def predict_false_positive_probability(self, 
                                         alert_type: str, 
                                         metrics: Dict[str, float],
                                         context: Dict[str, Any] = None) -> float:
        """Predict probability that an alert is a false positive"""
        
        # Feature extraction
        features = self._extract_features(alert_type, metrics, context or {})
        
        # Pattern matching
        pattern_score = self._match_learned_patterns(features)
        
        # Time-based analysis
        time_score = self._analyze_temporal_patterns(alert_type, metrics)
        
        # Context analysis
        context_score = self._analyze_context_patterns(context or {})
        
        # Combine scores
        combined_score = (pattern_score * 0.4 + 
                         time_score * 0.3 + 
                         context_score * 0.3)
        
        return min(max(combined_score, 0.0), 1.0)  # Clamp to [0,1]
    
    def _extract_features(self, 
                         alert_type: str, 
                         metrics: Dict[str, float],
                         context: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features from alert data"""
        features = {
            'cpu_usage': metrics.get('cpu', 0),
            'memory_usage': metrics.get('memory', 0),
            'disk_io': metrics.get('disk_io', 0),
            'network_activity': metrics.get('network', 0),
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
        }
        
        # Alert type encoding
        alert_types = {'cpu': 1, 'memory': 2, 'disk': 3, 'network': 4, 'anomaly': 5}
        features['alert_type_code'] = alert_types.get(alert_type.lower(), 0)
        
        # Context features
        features['process_count'] = context.get('process_count', 0)
        features['system_load'] = context.get('system_load', 0)
        features['recent_alerts'] = context.get('recent_alert_count', 0)
        
        return features
    
    def _match_learned_patterns(self, features: Dict[str, float]) -> float:
        """Match against learned false positive patterns"""
        if not self.learned_patterns:
            return 0.5  # Neutral score if no patterns learned
        
        best_match_score = 0.0
        
        for pattern_name, pattern_data in self.learned_patterns.items():
            similarity = self._calculate_pattern_similarity(features, pattern_data['features'])
            
            if similarity > 0.8:  # High similarity threshold
                fp_probability = pattern_data.get('fp_probability', 0.5)
                confidence = pattern_data.get('confidence', 0.5)
                
                match_score = similarity * fp_probability * confidence
                best_match_score = max(best_match_score, match_score)
        
        return best_match_score
    
    def _calculate_pattern_similarity(self, 
                                    features1: Dict[str, float], 
                                    features2: Dict[str, float]) -> float:
        """Calculate cosine similarity between feature vectors"""
        common_keys = set(features1.keys()) & set(features2.keys())
        
        if not common_keys:
            return 0.0
        
        # Convert to vectors
        vec1 = np.array([features1[k] for k in common_keys])
        vec2 = np.array([features2[k] for k in common_keys])
        
        # Normalize to prevent division by zero
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)
        return max(0.0, similarity)  # Ensure non-negative
    
    def _analyze_temporal_patterns(self, 
                                 alert_type: str, 
                                 metrics: Dict[str, float]) -> float:
        """Analyze temporal patterns for false positives"""
        current_time = datetime.now()
        hour = current_time.hour
        day_of_week = current_time.weekday()
        
        # Get recent similar alerts
        recent_alerts = [
            event for event in self.alert_history
            if (current_time - event.timestamp).total_seconds() < 3600  # Last hour
            and event.alert_type == alert_type
        ]
        
        if len(recent_alerts) == 0:
            return 0.3  # Neutral if no recent data
        
        # Check for burst patterns (many similar alerts = likely false positive)
        if len(recent_alerts) > 5:
            return 0.8  # High probability of false positive
        
        # Check for known false positive time patterns
        false_positive_hours = {2, 3, 4, 5}  # Early morning hours
        if hour in false_positive_hours:
            return 0.6
        
        # Weekend patterns
        if day_of_week >= 5:  # Weekend
            return 0.4
        
        return 0.2  # Lower probability during business hours
    
    def _analyze_context_patterns(self, context: Dict[str, Any]) -> float:
        """Analyze contextual information for false positive indicators"""
        fp_score = 0.0
        
        # High system load often causes false positives
        system_load = context.get('system_load', 0)
        if system_load > 80:
            fp_score += 0.3
        
        # Many processes can cause resource spikes
        process_count = context.get('process_count', 0)
        if process_count > 150:
            fp_score += 0.2
        
        # Recent system changes
        if context.get('recent_install', False):
            fp_score += 0.4
        
        # Maintenance windows
        if context.get('maintenance_mode', False):
            fp_score += 0.6
        
        return min(fp_score, 1.0)
    
    def _update_learned_patterns(self) -> None:
        """Update learned patterns from historical data"""
        if not self.learning_enabled or len(self.alert_history) < 50:
            return
        
        # Group alerts by type and analyze patterns
        alert_groups = defaultdict(list)
        
        for event in self.alert_history:
            if event.was_false_positive is not None:  # Only confirmed cases
                alert_groups[event.alert_type].append(event)
        
        # Learn patterns for each alert type
        for alert_type, events in alert_groups.items():
            if len(events) < 10:  # Need minimum data
                continue
            
            false_positives = [e for e in events if e.was_false_positive]
            true_positives = [e for e in events if not e.was_false_positive]
            
            if len(false_positives) < 5:  # Need minimum false positives
                continue
            
            # Calculate average features for false positives
            fp_features = self._calculate_average_features(false_positives)
            tp_features = self._calculate_average_features(true_positives) if true_positives else {}
            
            # Calculate false positive probability
            fp_probability = len(false_positives) / len(events)
            
            pattern_key = f"{alert_type}_pattern"
            self.learned_patterns[pattern_key] = {
                'features': fp_features,
                'fp_probability': fp_probability,
                'confidence': min(len(events) / 50.0, 1.0),  # Confidence based on data size
                'sample_size': len(events),
                'last_updated': datetime.now().isoformat()
            }
        
        # Save updated model
        self._save_model()
    
    def _calculate_average_features(self, events: List[AlertEvent]) -> Dict[str, float]:
        """Calculate average features from a list of events"""
        if not events:
            return {}
        
        feature_sums = defaultdict(float)
        feature_counts = defaultdict(int)
        
        for event in events:
            features = self._extract_features(
                event.alert_type, 
                event.metrics, 
                event.context or {}
            )
            
            for key, value in features.items():
                feature_sums[key] += value
                feature_counts[key] += 1
        
        # Calculate averages
        avg_features = {}
        for key, total in feature_sums.items():
            count = feature_counts[key]
            if count > 0:
                avg_features[key] = total / count
        
        return avg_features
    
    def mark_alert_outcome(self, 
                          alert_timestamp: datetime, 
                          was_false_positive: bool,
                          confidence: float = 1.0) -> None:
        """Mark the outcome of a previous alert for learning"""
        # Find matching alert in history
        for event in self.alert_history:
            if abs((event.timestamp - alert_timestamp).total_seconds()) < 60:  # 1 minute tolerance
                event.was_false_positive = was_false_positive
                event.confidence_score = confidence
                break
        
        # Trigger pattern update if enough new confirmations
        confirmed_events = [e for e in self.alert_history if e.was_false_positive is not None]
        if len(confirmed_events) % 25 == 0:  # Every 25 confirmations
            self._update_learned_patterns()
    
    def _save_model(self) -> None:
        """Save learned patterns to disk"""
        try:
            model_data = {
                'learned_patterns': self.learned_patterns,
                'pattern_weights': dict(self.pattern_weights),
                'confidence_threshold': self.confidence_threshold,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.model_file, 'wb') as f:
                pickle.dump(model_data, f)
                
        except Exception as e:
            print(f"⚠️ Failed to save FP detection model: {e}")
    
    def _load_model(self) -> None:
        """Load learned patterns from disk"""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.learned_patterns = model_data.get('learned_patterns', {})
                self.pattern_weights = defaultdict(float, model_data.get('pattern_weights', {}))
                self.confidence_threshold = model_data.get('confidence_threshold', 0.7)
                
                print(f"✅ Loaded FP detection model with {len(self.learned_patterns)} patterns")
        
        except Exception as e:
            print(f"⚠️ Failed to load FP detection model: {e}")
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get statistics about the learned model"""
        confirmed_alerts = [e for e in self.alert_history if e.was_false_positive is not None]
        false_positives = [e for e in confirmed_alerts if e.was_false_positive]
        
        return {
            'total_alerts_processed': len(self.alert_history),
            'confirmed_alerts': len(confirmed_alerts),
            'confirmed_false_positives': len(false_positives),
            'false_positive_rate': len(false_positives) / len(confirmed_alerts) if confirmed_alerts else 0,
            'learned_patterns': len(self.learned_patterns),
            'confidence_threshold': self.confidence_threshold,
            'learning_enabled': self.learning_enabled
        }


class FalsePositiveFilter:
    """
    Real-time false positive filtering system
    """
    
    def __init__(self):
        self.learning_engine = PatternLearningEngine()
        self.alert_buffer = deque(maxlen=1000)
        self.suppression_rules = []
        self.active = True
        
        # Initialize default suppression rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default suppression rules"""
        self.suppression_rules = [
            {
                'name': 'burst_suppression',
                'condition': lambda alerts: len(alerts) > 5,
                'timeframe': 300,  # 5 minutes
                'description': 'Suppress if more than 5 similar alerts in 5 minutes'
            },
            {
                'name': 'low_severity_night',
                'condition': lambda alerts: (
                    datetime.now().hour in range(0, 6) and 
                    any(a.severity == 'low' for a in alerts)
                ),
                'timeframe': 3600,  # 1 hour
                'description': 'Suppress low severity alerts during night hours'
            },
            {
                'name': 'maintenance_window',
                'condition': lambda alerts: any(
                    a.context and a.context.get('maintenance_mode', False) 
                    for a in alerts
                ),
                'timeframe': 7200,  # 2 hours
                'description': 'Suppress during maintenance windows'
            }
        ]
    
    def filter_alert(self, 
                    alert_type: str,
                    severity: str,
                    metrics: Dict[str, float],
                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Filter an alert and determine if it should be suppressed
        Returns filtering decision with reasoning
        """
        
        current_time = datetime.now()
        context = context or {}
        
        # Create alert event
        alert_event = AlertEvent(
            timestamp=current_time,
            alert_type=alert_type,
            severity=severity,
            metrics=metrics,
            context=context
        )
        
        self.alert_buffer.append(alert_event)
        
        # Predict false positive probability
        fp_probability = self.learning_engine.predict_false_positive_probability(
            alert_type, metrics, context
        )
        
        # Check suppression rules
        suppression_triggered = self._check_suppression_rules(alert_event)
        
        # Make filtering decision
        should_suppress = (
            fp_probability > self.learning_engine.confidence_threshold or
            suppression_triggered['triggered']
        )
        
        decision = {
            'suppress': should_suppress,
            'fp_probability': fp_probability,
            'confidence': 1.0 - abs(fp_probability - 0.5) * 2,  # Confidence in decision
            'suppression_rules_triggered': suppression_triggered,
            'reasoning': self._generate_reasoning(fp_probability, suppression_triggered),
            'timestamp': current_time.isoformat()
        }
        
        # Add to learning engine if not suppressed
        if not should_suppress:
            self.learning_engine.add_alert_event(alert_event)
        
        return decision
    
    def _check_suppression_rules(self, alert_event: AlertEvent) -> Dict[str, Any]:
        """Check if any suppression rules are triggered"""
        triggered_rules = []
        
        for rule in self.suppression_rules:
            # Get recent similar alerts within timeframe
            cutoff_time = alert_event.timestamp - timedelta(seconds=rule['timeframe'])
            recent_alerts = [
                a for a in self.alert_buffer
                if a.timestamp > cutoff_time and a.alert_type == alert_event.alert_type
            ]
            
            # Check rule condition
            if rule['condition'](recent_alerts):
                triggered_rules.append({
                    'name': rule['name'],
                    'description': rule['description'],
                    'timeframe': rule['timeframe']
                })
        
        return {
            'triggered': len(triggered_rules) > 0,
            'rules': triggered_rules
        }
    
    def _generate_reasoning(self, 
                          fp_probability: float, 
                          suppression_data: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the decision"""
        reasons = []
        
        if fp_probability > 0.7:
            reasons.append(f"High false positive probability ({fp_probability:.1%})")
        elif fp_probability < 0.3:
            reasons.append(f"Low false positive probability ({fp_probability:.1%})")
        
        if suppression_data['triggered']:
            rule_names = [r['name'] for r in suppression_data['rules']]
            reasons.append(f"Suppression rules triggered: {', '.join(rule_names)}")
        
        if not reasons:
            reasons.append("Standard evaluation - no special conditions detected")
        
        return "; ".join(reasons)
    
    def add_suppression_rule(self, 
                           name: str, 
                           condition, 
                           timeframe: int, 
                           description: str) -> None:
        """Add custom suppression rule"""
        rule = {
            'name': name,
            'condition': condition,
            'timeframe': timeframe,
            'description': description
        }
        
        self.suppression_rules.append(rule)
    
    def get_filter_statistics(self) -> Dict[str, Any]:
        """Get filtering statistics"""
        total_alerts = len(self.alert_buffer)
        
        if total_alerts == 0:
            return {'total_processed': 0}
        
        # Calculate suppression rate from recent alerts
        recent_time = datetime.now() - timedelta(hours=24)
        recent_alerts = [a for a in self.alert_buffer if a.timestamp > recent_time]
        
        # Get learning engine stats
        learning_stats = self.learning_engine.get_model_statistics()
        
        return {
            'total_processed': total_alerts,
            'recent_24h': len(recent_alerts),
            'learning_engine': learning_stats,
            'suppression_rules': len(self.suppression_rules),
            'filter_active': self.active
        }


if __name__ == "__main__":
    # Demo false positive detection
    fp_filter = FalsePositiveFilter()
    
    # Simulate alert filtering
    test_alert = fp_filter.filter_alert(
        alert_type="cpu",
        severity="medium", 
        metrics={'cpu': 85, 'memory': 60},
        context={'process_count': 120, 'system_load': 70}
    )
    
    print("False Positive Filter Demo:")
    print(f"Suppress: {test_alert['suppress']}")
    print(f"FP Probability: {test_alert['fp_probability']:.1%}")
    print(f"Reasoning: {test_alert['reasoning']}")