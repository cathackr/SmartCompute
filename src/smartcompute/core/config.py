#!/usr/bin/env python3
"""
SmartCompute Secure Configuration Loader
=========================================

Carga configuración de forma segura desde:
1. Variables de entorno (prioridad máxima)
2. Archivo .env
3. Archivo de configuración con fallback a valores por defecto

NUNCA expone credenciales en logs o errores.
"""

import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SecureConfigLoader:
    """Cargador de configuración seguro con soporte para variables de entorno"""

    def __init__(self, config_file: str = "client_config.json", env_file: str = ".env"):
        self.config_file = Path(config_file)
        self.env_file = Path(env_file)
        self._config_cache: Optional[Dict[str, Any]] = None

        # Cargar variables de entorno desde .env si existe
        self._load_env_file()

    def _load_env_file(self):
        """Carga variables de entorno desde archivo .env"""
        if not self.env_file.exists():
            logger.debug(f"No .env file found at {self.env_file}")
            return

        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Ignorar comentarios y líneas vacías
                    if not line or line.startswith('#'):
                        continue

                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Solo establecer si no existe ya en el entorno
                        if key and not os.getenv(key):
                            os.environ[key] = value

            logger.info("✅ Environment variables loaded from .env")
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")

    def _expand_env_vars(self, value: Any) -> Any:
        """
        Expande variables de entorno en valores de configuración
        Formato: ${VAR_NAME} o ${VAR_NAME:-default_value}
        """
        if not isinstance(value, str):
            return value

        # Si no contiene ${, retornar directamente
        if '${' not in value:
            return value

        # Buscar patrón ${VAR_NAME} o ${VAR_NAME:-default}
        import re
        pattern = r'\$\{([^}:]+)(?::-(.[^}]*))?\}'

        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)

        return re.sub(pattern, replace_var, value)

    def _expand_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Expande variables de entorno recursivamente en un diccionario"""
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._expand_dict(value)
            elif isinstance(value, list):
                result[key] = [self._expand_env_vars(item) for item in value]
            else:
                result[key] = self._expand_env_vars(value)
        return result

    def load_config(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Carga configuración de forma segura

        Args:
            use_cache: Si es True, usa caché si ya se cargó

        Returns:
            Diccionario con configuración expandida
        """
        if use_cache and self._config_cache is not None:
            return self._config_cache

        # Intentar cargar archivo de configuración
        if not self.config_file.exists():
            # Si no existe, buscar archivo .example
            example_file = Path(str(self.config_file) + ".example")
            if example_file.exists():
                logger.warning(f"⚠️  Configuration file not found: {self.config_file}")
                logger.warning(f"📄 Copy {example_file} to {self.config_file} and configure your credentials")
                raise FileNotFoundError(
                    f"Configuration file not found. "
                    f"Copy {example_file} to {self.config_file} and configure your credentials."
                )
            else:
                raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Expandir variables de entorno
            config = self._expand_dict(config)

            # Validar configuración crítica
            self._validate_config(config)

            # Guardar en caché
            self._config_cache = config

            logger.info(f"✅ Configuration loaded from {self.config_file}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading configuration: {e}")
            raise

    def _validate_config(self, config: Dict[str, Any]):
        """Valida que la configuración tenga los campos requeridos"""
        required_fields = ['server_url', 'api_key']

        missing_fields = []
        for field in required_fields:
            value = config.get(field)
            # Verificar que exista y no sea un placeholder
            if not value or value.startswith('${') or value in ['your-', 'placeholder']:
                missing_fields.append(field)

        if missing_fields:
            logger.error(f"❌ Missing or invalid required configuration fields: {missing_fields}")
            logger.error(f"💡 Set environment variables or update {self.config_file}")
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}. "
                f"Set environment variables or update configuration file."
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración"""
        config = self.load_config()
        return config.get(key, default)

    def get_nested(self, *keys, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración anidado
        Ejemplo: get_nested('client_settings', 'auto_submit')
        """
        config = self.load_config()
        value = config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default

        return value


# Instancia global para uso fácil
_default_loader = None

def get_config_loader(config_file: str = "client_config.json") -> SecureConfigLoader:
    """Obtiene o crea el cargador de configuración global"""
    global _default_loader
    if _default_loader is None:
        _default_loader = SecureConfigLoader(config_file)
    return _default_loader


def load_config(config_file: str = "client_config.json") -> Dict[str, Any]:
    """
    Función helper para cargar configuración rápidamente

    Usage:
        from secure_config_loader import load_config
        config = load_config()
        api_key = config['api_key']
    """
    loader = get_config_loader(config_file)
    return loader.load_config()


if __name__ == "__main__":
    # Test del cargador
    logging.basicConfig(level=logging.INFO)

    print("🔒 SmartCompute Secure Configuration Loader")
    print("=" * 50)

    try:
        loader = SecureConfigLoader()
        config = loader.load_config()

        print(f"✅ Configuration loaded successfully")
        print(f"📡 Server URL: {config.get('server_url')}")
        print(f"🔑 API Key: {'*' * 20} (hidden for security)")
        print(f"⚙️  Auto-submit: {loader.get_nested('client_settings', 'auto_submit')}")

    except Exception as e:
        print(f"❌ Error: {e}")
