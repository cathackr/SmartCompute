import hashlib
from cryptography.fernet import Fernet
import json
import os
import datetime
import logging
from pathlib import Path

# =================================================================
# SISTEMA DE SEGURIDAD CON ROTACIÓN AUTOMÁTICA DE CLAVES
# =================================================================

logger = logging.getLogger(__name__)

# 🔑 Configuración de claves
KEY_FILE = "secret.key"
KEY_ROTATION_DAYS = int(os.getenv("KEY_ROTATION_DAYS", "30"))  # Rotar cada 30 días
BACKUP_KEYS_DIR = "vault/key_backups"

def ensure_key_backup_dir():
    """Asegurar que existe el directorio de backup de claves"""
    Path(BACKUP_KEYS_DIR).mkdir(parents=True, exist_ok=True)

def get_key_age_days():
    """Obtener edad de la clave en días"""
    try:
        stat = os.stat(KEY_FILE)
        key_date = datetime.datetime.fromtimestamp(stat.st_mtime)
        age = datetime.datetime.now() - key_date
        return age.days
    except FileNotFoundError:
        return KEY_ROTATION_DAYS + 1  # Forzar generación

def backup_current_key():
    """Respaldar clave actual antes de rotar"""
    if os.path.exists(KEY_FILE):
        ensure_key_backup_dir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{BACKUP_KEYS_DIR}/secret_key_backup_{timestamp}.key"
        
        with open(KEY_FILE, "rb") as src, open(backup_path, "wb") as dst:
            dst.write(src.read())
        
        logger.info(f"🔄 Clave respaldada en: {backup_path}")
        return backup_path
    return None

def load_or_generate_key():
    """Cargar clave existente o generar nueva con rotación automática"""
    key_age = get_key_age_days()
    
    # Verificar si necesita rotación
    if key_age >= KEY_ROTATION_DAYS:
        logger.warning(f"🔑 Clave antigua detectada ({key_age} días). Rotando...")
        backup_current_key()
        
        # Generar nueva clave
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        
        logger.info("🔄 Nueva clave generada y guardada")
        return key
    
    # Cargar clave existente
    try:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
        logger.info(f"🔑 Clave cargada (edad: {key_age} días)")
        return key
    except FileNotFoundError:
        # Primera ejecución - generar clave
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        logger.info("🔑 Primera clave generada")
        return key

def get_encryption_key():
    """Obtener clave de cifrado desde variables de entorno o archivo"""
    # Prioridad: Variable de entorno > Archivo local
    env_key = os.getenv("ENCRYPTION_KEY")
    if env_key:
        try:
            # Convertir string base64 a bytes
            import base64
            return base64.b64decode(env_key.encode())
        except Exception:
            logger.warning("🔑 Clave de entorno inválida, usando archivo local")
    
    return load_or_generate_key()

# Inicializamos cifrado con sistema mejorado
KEY = get_encryption_key()
CIPHER = Fernet(KEY)

# ----------------------
# Hashing de datos
# ----------------------
def hash_value(value: str) -> str:
    """
    Devuelve un hash SHA256 de un valor dado.
    """
    return hashlib.sha256(value.encode()).hexdigest()

# ----------------------
# Cifrado y descifrado
# ----------------------
def encrypt_value(value: str) -> str:
    """
    Cifra un valor y devuelve bytes codificados en base64.
    """
    return CIPHER.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """
    Descifra un valor cifrado previamente.
    """
    return CIPHER.decrypt(encrypted_value.encode()).decode()

# ----------------------
# Ejemplo de procesamiento de datos de sensores
# ----------------------
def secure_sensor_data(sensor_dict: dict, hash_keys=None, encrypt_keys=None) -> dict:
    """
    sensor_dict: diccionario con datos de sensores
    hash_keys: lista de llaves que se deben hashear
    encrypt_keys: lista de llaves que se deben cifrar
    """
    hash_keys = hash_keys or []
    encrypt_keys = encrypt_keys or []

    secured = {}
    for k, v in sensor_dict.items():
        if k in hash_keys:
            secured[k] = hash_value(str(v))
        elif k in encrypt_keys:
            secured[k] = encrypt_value(str(v))
        else:
            secured[k] = v
    return secured

# ----------------------
# Guardar JSON seguro
# ----------------------
def save_secure_json(data: dict, filename: str):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
