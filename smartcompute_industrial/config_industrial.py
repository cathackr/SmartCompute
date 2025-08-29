"""
Configuración para SmartCompute Industrial
"""

# Configuración de Seguridad
SECURITY_CONFIG = {
    "encryption_algorithm": "AES-256",
    "hash_algorithm": "SHA-256",
    "key_rotation_days": 30,
    "secure_storage": True
}

# Configuración de Simulación
SIMULATION_CONFIG = {
    "update_interval": 5.0,  # segundos
    "default_devices": 10,
    "realistic_noise": True,
    "save_history": True
}

# Configuración de Dispositivos por Defecto
DEFAULT_DEVICES = [
    {
        "name": "Temp_Sensor_01",
        "type": "temperature",
        "range": {"min": 20, "max": 80},
        "simulation": "sine_wave"
    },
    {
        "name": "Pressure_Sensor_01", 
        "type": "pressure",
        "range": {"min": 0, "max": 100},
        "simulation": "random_walk"
    },
    {
        "name": "Motor_01",
        "type": "motor",
        "range": {"min": 0, "max": 3000},
        "simulation": "step_function"
    },
    {
        "name": "Valve_01",
        "type": "valve",
        "range": {"min": 0, "max": 100},
        "simulation": "binary_toggle"
    }
]

# Configuración de Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "smartcompute_industrial.log",
    "max_size": "10MB",
    "backup_count": 5
}
