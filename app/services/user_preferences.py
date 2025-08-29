#!/usr/bin/env python3
"""
SmartCompute User Preferences Management
Secure customization system for dashboard labels, units, and display preferences
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from enum import Enum


class PreferenceType(Enum):
    """Types of user preferences"""
    LABEL = "label"
    UNIT = "unit"
    DISPLAY = "display"
    LANGUAGE = "language"
    THEME = "theme"


@dataclass
class UserPreference:
    """User preference data structure"""
    key: str
    value: str
    original_value: str
    preference_type: str
    created_at: str
    modified_at: str


class UserPreferencesManager:
    """
    Manages user interface customizations with security separation
    """
    
    def __init__(self, preferences_dir: str = "/tmp/smartcompute_preferences"):
        self.preferences_dir = preferences_dir
        self.preferences: Dict[str, Dict[str, UserPreference]] = {}
        
        # Ensure preferences directory exists
        os.makedirs(self.preferences_dir, exist_ok=True)
        
        # Default labels and their translations
        self._init_default_labels()
        
        # Allowed unit conversions
        self._init_unit_conversions()
        
        # Security validation patterns
        self._init_security_patterns()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("User preferences manager initialized")
    
    def _init_default_labels(self):
        """Initialize default label mappings"""
        
        self.default_labels = {
            # Cost and financial terms
            "cost": "Cost",
            "price": "Price", 
            "expense": "Expense",
            "spending": "Spending",
            "budget": "Budget",
            "savings": "Savings",
            
            # Token related terms
            "tokens": "Tokens",
            "token_usage": "Token Usage",
            "token_count": "Token Count",
            "consumption": "Consumption",
            "usage": "Usage",
            
            # Performance metrics
            "efficiency": "Efficiency",
            "performance": "Performance",
            "speed": "Speed",
            "response_time": "Response Time",
            "latency": "Latency",
            "throughput": "Throughput",
            
            # System metrics
            "cpu_usage": "CPU Usage",
            "memory_usage": "Memory Usage",
            "temperature": "Temperature",
            "status": "Status",
            "health": "Health",
            
            # Time related
            "duration": "Duration",
            "time": "Time",
            "timestamp": "Timestamp",
            "last_updated": "Last Updated",
            
            # Common UI elements
            "dashboard": "Dashboard",
            "settings": "Settings",
            "preferences": "Preferences",
            "profile": "Profile",
            "alerts": "Alerts",
            "notifications": "Notifications"
        }
        
        # Language translations
        self.translations = {
            "spanish": {
                "cost": "Costo",
                "price": "Precio",
                "expense": "Gasto",
                "spending": "Gastos",
                "budget": "Presupuesto",
                "savings": "Ahorros",
                "tokens": "Tokens",
                "token_usage": "Uso de Tokens",
                "efficiency": "Eficiencia",
                "performance": "Rendimiento",
                "speed": "Velocidad",
                "response_time": "Tiempo de Respuesta",
                "cpu_usage": "Uso de CPU",
                "memory_usage": "Uso de Memoria",
                "temperature": "Temperatura",
                "dashboard": "Panel de Control",
                "settings": "Configuración",
                "alerts": "Alertas"
            },
            "portuguese": {
                "cost": "Custo",
                "price": "Preço",
                "expense": "Despesa",
                "spending": "Gastos",
                "budget": "Orçamento",
                "tokens": "Tokens",
                "efficiency": "Eficiência",
                "performance": "Desempenho",
                "dashboard": "Painel"
            }
        }
    
    def _init_unit_conversions(self):
        """Initialize allowed unit conversions"""
        
        self.unit_conversions = {
            # Temperature
            "temperature": {
                "celsius": {"symbol": "°C", "from_base": lambda x: x, "to_base": lambda x: x},
                "fahrenheit": {"symbol": "°F", "from_base": lambda x: x * 9/5 + 32, "to_base": lambda x: (x - 32) * 5/9},
                "kelvin": {"symbol": "K", "from_base": lambda x: x + 273.15, "to_base": lambda x: x - 273.15}
            },
            
            # Currency
            "currency": {
                "usd": {"symbol": "$", "rate": 1.0},
                "eur": {"symbol": "€", "rate": 0.85},  # Approximate rates
                "gbp": {"symbol": "£", "rate": 0.75},
                "mxn": {"symbol": "MX$", "rate": 18.0},
                "cop": {"symbol": "COP$", "rate": 4000.0},
                "brl": {"symbol": "R$", "rate": 5.0}
            },
            
            # Memory
            "memory": {
                "bytes": {"symbol": "B", "multiplier": 1},
                "kilobytes": {"symbol": "KB", "multiplier": 1024},
                "megabytes": {"symbol": "MB", "multiplier": 1024**2},
                "gigabytes": {"symbol": "GB", "multiplier": 1024**3},
                "terabytes": {"symbol": "TB", "multiplier": 1024**4}
            },
            
            # Time
            "time": {
                "milliseconds": {"symbol": "ms", "multiplier": 1},
                "seconds": {"symbol": "s", "multiplier": 1000},
                "minutes": {"symbol": "min", "multiplier": 60000},
                "hours": {"symbol": "h", "multiplier": 3600000}
            },
            
            # Percentage
            "percentage": {
                "decimal": {"symbol": "", "multiplier": 1},
                "percent": {"symbol": "%", "multiplier": 100}
            }
        }
    
    def _init_security_patterns(self):
        """Initialize security validation patterns"""
        
        # Allowed characters in custom labels (alphanumeric, spaces, basic punctuation)
        self.label_pattern = re.compile(r'^[a-zA-Z0-9áéíóúñüÁÉÍÓÚÑÜ\s\-_.:()]+$')
        
        # Maximum length for custom labels
        self.max_label_length = 50
        
        # Forbidden keywords that could indicate malicious intent
        self.forbidden_keywords = [
            'script', 'javascript', 'eval', 'exec', 'import', 'require',
            'document', 'window', 'alert', 'confirm', 'prompt', 'fetch',
            'xhr', 'ajax', 'onload', 'onclick', 'onerror', 'iframe',
            'embed', 'object', 'link', 'style', 'meta', 'base'
        ]
    
    def load_user_preferences(self, user_id: str) -> bool:
        """Load user preferences from file"""
        
        preferences_file = os.path.join(self.preferences_dir, f"{user_id}_preferences.json")
        
        try:
            if os.path.exists(preferences_file):
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert to UserPreference objects
                user_prefs = {}
                for key, pref_data in data.get('preferences', {}).items():
                    user_prefs[key] = UserPreference(**pref_data)
                
                self.preferences[user_id] = user_prefs
                self.logger.info(f"Loaded preferences for user {user_id}")
                return True
            else:
                # Initialize with empty preferences
                self.preferences[user_id] = {}
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load preferences for user {user_id}: {e}")
            self.preferences[user_id] = {}
            return False
    
    def save_user_preferences(self, user_id: str) -> bool:
        """Save user preferences to file"""
        
        if user_id not in self.preferences:
            return True
        
        preferences_file = os.path.join(self.preferences_dir, f"{user_id}_preferences.json")
        
        try:
            # Convert UserPreference objects to dict
            prefs_data = {}
            for key, preference in self.preferences[user_id].items():
                prefs_data[key] = asdict(preference)
            
            data = {
                'user_id': user_id,
                'saved_at': datetime.now().isoformat(),
                'preferences': prefs_data
            }
            
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved preferences for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save preferences for user {user_id}: {e}")
            return False
    
    def validate_label(self, label: str) -> tuple[bool, Optional[str]]:
        """Validate a custom label for security and format"""
        
        if not label or len(label.strip()) == 0:
            return False, "Label cannot be empty"
        
        label = label.strip()
        
        if len(label) > self.max_label_length:
            return False, f"Label too long (max {self.max_label_length} characters)"
        
        if not self.label_pattern.match(label):
            return False, "Label contains invalid characters"
        
        # Check for forbidden keywords
        label_lower = label.lower()
        for keyword in self.forbidden_keywords:
            if keyword in label_lower:
                return False, f"Label contains forbidden keyword: {keyword}"
        
        return True, None
    
    def set_label_preference(self, user_id: str, key: str, custom_label: str) -> tuple[bool, str]:
        """Set a custom label for a dashboard element"""
        
        # Validate the custom label
        is_valid, error_msg = self.validate_label(custom_label)
        if not is_valid:
            return False, f"Invalid label: {error_msg}"
        
        # Ensure user preferences are loaded
        if user_id not in self.preferences:
            self.load_user_preferences(user_id)
        
        # Get original value
        original_value = self.default_labels.get(key, key)
        
        # Create preference
        now = datetime.now().isoformat()
        preference = UserPreference(
            key=key,
            value=custom_label.strip(),
            original_value=original_value,
            preference_type=PreferenceType.LABEL.value,
            created_at=now,
            modified_at=now
        )
        
        self.preferences[user_id][key] = preference
        
        # Save to file
        self.save_user_preferences(user_id)
        
        self.logger.info(f"Set label preference for user {user_id}: {key} = '{custom_label}'")
        return True, "Label preference saved successfully"
    
    def set_unit_preference(self, user_id: str, metric: str, unit: str) -> tuple[bool, str]:
        """Set unit preference for a metric"""
        
        # Validate unit exists for this metric
        if metric not in self.unit_conversions:
            return False, f"Unknown metric: {metric}"
        
        if unit not in self.unit_conversions[metric]:
            available_units = list(self.unit_conversions[metric].keys())
            return False, f"Invalid unit '{unit}' for {metric}. Available: {available_units}"
        
        # Ensure user preferences are loaded
        if user_id not in self.preferences:
            self.load_user_preferences(user_id)
        
        # Create preference
        now = datetime.now().isoformat()
        preference_key = f"{metric}_unit"
        preference = UserPreference(
            key=preference_key,
            value=unit,
            original_value="default",
            preference_type=PreferenceType.UNIT.value,
            created_at=now,
            modified_at=now
        )
        
        self.preferences[user_id][preference_key] = preference
        
        # Save to file
        self.save_user_preferences(user_id)
        
        self.logger.info(f"Set unit preference for user {user_id}: {metric} = '{unit}'")
        return True, "Unit preference saved successfully"
    
    def apply_language_preset(self, user_id: str, language: str) -> tuple[bool, str]:
        """Apply a language preset to all labels"""
        
        if language not in self.translations:
            available_langs = list(self.translations.keys())
            return False, f"Language '{language}' not available. Available: {available_langs}"
        
        # Ensure user preferences are loaded
        if user_id not in self.preferences:
            self.load_user_preferences(user_id)
        
        # Apply all translations
        translation_dict = self.translations[language]
        now = datetime.now().isoformat()
        
        for key, translated_value in translation_dict.items():
            original_value = self.default_labels.get(key, key)
            
            preference = UserPreference(
                key=key,
                value=translated_value,
                original_value=original_value,
                preference_type=PreferenceType.LANGUAGE.value,
                created_at=now,
                modified_at=now
            )
            
            self.preferences[user_id][key] = preference
        
        # Save language preference
        lang_preference = UserPreference(
            key="interface_language",
            value=language,
            original_value="english",
            preference_type=PreferenceType.LANGUAGE.value,
            created_at=now,
            modified_at=now
        )
        
        self.preferences[user_id]["interface_language"] = lang_preference
        
        # Save to file
        self.save_user_preferences(user_id)
        
        self.logger.info(f"Applied language preset '{language}' for user {user_id}")
        return True, f"Language changed to {language.title()}"
    
    def get_display_value(self, user_id: str, key: str, original_value: Any = None) -> str:
        """Get display value for a key, applying user preferences"""
        
        # Load user preferences if not already loaded
        if user_id not in self.preferences:
            self.load_user_preferences(user_id)
        
        user_prefs = self.preferences.get(user_id, {})
        
        # Check for custom label
        if key in user_prefs:
            preference = user_prefs[key]
            if preference.preference_type == PreferenceType.LABEL.value:
                return preference.value
        
        # Return default or original value
        return original_value or self.default_labels.get(key, key)
    
    def convert_value(self, user_id: str, metric: str, value: float) -> tuple[float, str]:
        """Convert a value to user's preferred unit"""
        
        # Load user preferences if not already loaded
        if user_id not in self.preferences:
            self.load_user_preferences(user_id)
        
        user_prefs = self.preferences.get(user_id, {})
        unit_key = f"{metric}_unit"
        
        # Check for unit preference
        if unit_key in user_prefs:
            preferred_unit = user_prefs[unit_key].value
            
            if metric in self.unit_conversions and preferred_unit in self.unit_conversions[metric]:
                unit_config = self.unit_conversions[metric][preferred_unit]
                
                if metric == "temperature" and "from_base" in unit_config:
                    # Temperature conversion from Celsius base
                    converted_value = unit_config["from_base"](value)
                    return converted_value, unit_config["symbol"]
                
                elif "multiplier" in unit_config:
                    # Simple multiplier conversion
                    if metric == "currency":
                        converted_value = value * unit_config["rate"]
                    else:
                        converted_value = value / unit_config["multiplier"]
                    return converted_value, unit_config["symbol"]
                
                elif "rate" in unit_config:
                    # Currency conversion
                    converted_value = value * unit_config["rate"]
                    return converted_value, unit_config["symbol"]
        
        # Return original value with default unit
        default_units = {
            "temperature": "°C",
            "currency": "$",
            "memory": "MB",
            "time": "ms",
            "percentage": "%"
        }
        
        return value, default_units.get(metric, "")
    
    def get_user_preferences_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's current preferences"""
        
        if user_id not in self.preferences:
            self.load_user_preferences(user_id)
        
        user_prefs = self.preferences.get(user_id, {})
        
        summary = {
            "user_id": user_id,
            "total_preferences": len(user_prefs),
            "labels": {},
            "units": {},
            "language": "english",
            "last_modified": None
        }
        
        for key, preference in user_prefs.items():
            if preference.preference_type == PreferenceType.LABEL.value:
                summary["labels"][key] = preference.value
            elif preference.preference_type == PreferenceType.UNIT.value:
                summary["units"][key] = preference.value
            elif key == "interface_language":
                summary["language"] = preference.value
            
            # Track most recent modification
            if summary["last_modified"] is None or preference.modified_at > summary["last_modified"]:
                summary["last_modified"] = preference.modified_at
        
        return summary
    
    def reset_user_preferences(self, user_id: str) -> bool:
        """Reset all user preferences to defaults"""
        
        try:
            # Clear in-memory preferences
            if user_id in self.preferences:
                del self.preferences[user_id]
            
            # Remove preferences file
            preferences_file = os.path.join(self.preferences_dir, f"{user_id}_preferences.json")
            if os.path.exists(preferences_file):
                os.remove(preferences_file)
            
            self.logger.info(f"Reset preferences for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset preferences for user {user_id}: {e}")
            return False
    
    def export_preferences(self, user_id: str, filepath: str) -> bool:
        """Export user preferences to a file"""
        
        if user_id not in self.preferences:
            self.load_user_preferences(user_id)
        
        try:
            summary = self.get_user_preferences_summary(user_id)
            summary["export_timestamp"] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported preferences for user {user_id} to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export preferences: {e}")
            return False