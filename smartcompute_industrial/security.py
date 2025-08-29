import hashlib
from cryptography.fernet import Fernet
import json

# 🔑 Clave de cifrado (generar una vez y guardar segura)
KEY_FILE = "secret.key"

def load_or_generate_key():
    try:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    return key

# Inicializamos cifrado
KEY = load_or_generate_key()
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
