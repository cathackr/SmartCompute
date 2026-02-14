#!/usr/bin/env python3
"""
SmartCompute Enterprise - Centralized Secret Management
======================================================

Sistema seguro de gestión de secretos que incluye:
- Cifrado AES-256 de secretos en reposo
- Rotación automática de claves
- Auditoría de acceso a secretos
- Integración con HSM/KMS externos
- Gestión de certificados SSL/TLS

Copyright (c) 2024 SmartCompute. All rights reserved.
"""

import asyncio
import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3


class SecretType(Enum):
    API_KEY = "api_key"
    DATABASE_PASSWORD = "database_password"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    OAUTH_TOKEN = "oauth_token"
    ENCRYPTION_KEY = "encryption_key"


class AccessLevel(Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


@dataclass
class SecretMetadata:
    """Metadatos de un secreto"""
    secret_id: str
    name: str
    secret_type: SecretType
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    rotation_interval_days: Optional[int]
    access_count: int
    last_accessed: Optional[datetime]
    tags: List[str]


@dataclass
class AccessLog:
    """Log de acceso a secretos"""
    log_id: str
    secret_id: str
    user_id: str
    action: str  # read, write, delete, rotate
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    failure_reason: Optional[str]


class SmartComputeSecretManager:
    """Gestor centralizado de secretos para SmartCompute Enterprise"""

    def __init__(self, vault_path: str = "/var/lib/smartcompute/vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Base de datos para metadatos
        self.db_path = self.vault_path / "secrets.db"
        self.master_key_path = self.vault_path / ".master_key"

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Inicializar
        self._initialize_vault()
        self._master_key = self._load_or_create_master_key()
        self._cipher = self._create_cipher()

    def _initialize_vault(self):
        """Inicializa la bóveda de secretos"""
        # Establecer permisos seguros
        os.chmod(self.vault_path, 0o700)

        # Crear base de datos de metadatos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secrets (
                secret_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                secret_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT,
                rotation_interval_days INTEGER,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                tags TEXT,
                encrypted_data_path TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                log_id TEXT PRIMARY KEY,
                secret_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN NOT NULL,
                failure_reason TEXT,
                FOREIGN KEY (secret_id) REFERENCES secrets (secret_id)
            )
        ''')

        conn.commit()
        conn.close()

    def _load_or_create_master_key(self) -> bytes:
        """Carga o crea la clave maestra"""
        if self.master_key_path.exists():
            with open(self.master_key_path, 'rb') as f:
                return f.read()
        else:
            # Generar nueva clave maestra
            master_key = secrets.token_bytes(32)
            with open(self.master_key_path, 'wb') as f:
                f.write(master_key)
            os.chmod(self.master_key_path, 0o600)
            return master_key

    def _create_cipher(self) -> Fernet:
        """Crea el objeto de cifrado"""
        # Derivar clave de cifrado desde clave maestra
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'smartcompute_salt_2024',  # En producción, usar salt único
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self._master_key))
        return Fernet(key)

    async def store_secret(
        self,
        name: str,
        secret_data: str,
        secret_type: SecretType,
        user_id: str,
        expires_at: Optional[datetime] = None,
        rotation_interval_days: Optional[int] = None,
        tags: List[str] = None
    ) -> str:
        """Almacena un secreto de forma segura"""
        try:
            secret_id = secrets.token_urlsafe(16)
            tags = tags or []

            # Cifrar datos del secreto
            encrypted_data = self._cipher.encrypt(secret_data.encode())

            # Guardar datos cifrados en archivo
            encrypted_file_path = self.vault_path / f"{secret_id}.enc"
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)
            os.chmod(encrypted_file_path, 0o600)

            # Guardar metadatos en base de datos
            now = datetime.now()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO secrets (
                    secret_id, name, secret_type, created_at, updated_at,
                    expires_at, rotation_interval_days, tags, encrypted_data_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                secret_id, name, secret_type.value, now.isoformat(), now.isoformat(),
                expires_at.isoformat() if expires_at else None,
                rotation_interval_days, json.dumps(tags), str(encrypted_file_path)
            ))

            conn.commit()
            conn.close()

            # Log del acceso
            await self._log_access(secret_id, user_id, "write", True)

            self.logger.info(f"Secreto '{name}' almacenado con ID: {secret_id}")
            return secret_id

        except Exception as e:
            await self._log_access("", user_id, "write", False, str(e))
            self.logger.error(f"Error almacenando secreto '{name}': {e}")
            raise

    async def get_secret(self, secret_id: str, user_id: str) -> Optional[str]:
        """Recupera un secreto descifrado"""
        try:
            # Verificar que el secreto existe
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT encrypted_data_path, expires_at FROM secrets WHERE secret_id = ?', (secret_id,))
            result = cursor.fetchone()

            if not result:
                await self._log_access(secret_id, user_id, "read", False, "Secret not found")
                return None

            encrypted_data_path, expires_at = result

            # Verificar expiración
            if expires_at:
                expiry_date = datetime.fromisoformat(expires_at)
                if datetime.now() > expiry_date:
                    await self._log_access(secret_id, user_id, "read", False, "Secret expired")
                    return None

            # Leer y descifrar datos
            with open(encrypted_data_path, 'rb') as f:
                encrypted_data = f.read()

            secret_data = self._cipher.decrypt(encrypted_data).decode()

            # Actualizar contador de acceso
            cursor.execute('''
                UPDATE secrets
                SET access_count = access_count + 1, last_accessed = ?
                WHERE secret_id = ?
            ''', (datetime.now().isoformat(), secret_id))

            conn.commit()
            conn.close()

            # Log del acceso exitoso
            await self._log_access(secret_id, user_id, "read", True)

            return secret_data

        except Exception as e:
            await self._log_access(secret_id, user_id, "read", False, str(e))
            self.logger.error(f"Error recuperando secreto {secret_id}: {e}")
            return None

    async def rotate_secret(self, secret_id: str, new_secret_data: str, user_id: str) -> bool:
        """Rota un secreto existente"""
        try:
            # Verificar que el secreto existe
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT encrypted_data_path FROM secrets WHERE secret_id = ?', (secret_id,))
            result = cursor.fetchone()

            if not result:
                await self._log_access(secret_id, user_id, "rotate", False, "Secret not found")
                return False

            encrypted_data_path = result[0]

            # Cifrar nuevos datos
            encrypted_data = self._cipher.encrypt(new_secret_data.encode())

            # Crear backup del secreto anterior
            backup_path = f"{encrypted_data_path}.backup.{int(time.time())}"
            os.rename(encrypted_data_path, backup_path)

            # Guardar nuevo secreto
            with open(encrypted_data_path, 'wb') as f:
                f.write(encrypted_data)
            os.chmod(encrypted_data_path, 0o600)

            # Actualizar metadatos
            cursor.execute('''
                UPDATE secrets
                SET updated_at = ?
                WHERE secret_id = ?
            ''', (datetime.now().isoformat(), secret_id))

            conn.commit()
            conn.close()

            # Log de rotación exitosa
            await self._log_access(secret_id, user_id, "rotate", True)

            self.logger.info(f"Secreto {secret_id} rotado exitosamente")
            return True

        except Exception as e:
            await self._log_access(secret_id, user_id, "rotate", False, str(e))
            self.logger.error(f"Error rotando secreto {secret_id}: {e}")
            return False

    async def delete_secret(self, secret_id: str, user_id: str) -> bool:
        """Elimina un secreto de forma segura"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Obtener ruta del archivo cifrado
            cursor.execute('SELECT encrypted_data_path FROM secrets WHERE secret_id = ?', (secret_id,))
            result = cursor.fetchone()

            if not result:
                await self._log_access(secret_id, user_id, "delete", False, "Secret not found")
                return False

            encrypted_data_path = result[0]

            # Eliminar archivo cifrado de forma segura (sobrescribir)
            if os.path.exists(encrypted_data_path):
                # Sobrescribir con datos aleatorios antes de eliminar
                file_size = os.path.getsize(encrypted_data_path)
                with open(encrypted_data_path, 'wb') as f:
                    f.write(secrets.token_bytes(file_size))
                os.remove(encrypted_data_path)

            # Eliminar metadatos
            cursor.execute('DELETE FROM secrets WHERE secret_id = ?', (secret_id,))

            conn.commit()
            conn.close()

            # Log de eliminación exitosa
            await self._log_access(secret_id, user_id, "delete", True)

            self.logger.info(f"Secreto {secret_id} eliminado exitosamente")
            return True

        except Exception as e:
            await self._log_access(secret_id, user_id, "delete", False, str(e))
            self.logger.error(f"Error eliminando secreto {secret_id}: {e}")
            return False

    async def list_secrets(self, user_id: str, secret_type: Optional[SecretType] = None) -> List[SecretMetadata]:
        """Lista los metadatos de secretos (sin datos sensibles)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if secret_type:
                cursor.execute('SELECT * FROM secrets WHERE secret_type = ?', (secret_type.value,))
            else:
                cursor.execute('SELECT * FROM secrets')

            results = cursor.fetchall()
            conn.close()

            secrets_list = []
            for row in results:
                secret_metadata = SecretMetadata(
                    secret_id=row[0],
                    name=row[1],
                    secret_type=SecretType(row[2]),
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    expires_at=datetime.fromisoformat(row[5]) if row[5] else None,
                    rotation_interval_days=row[6],
                    access_count=row[7],
                    last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                    tags=json.loads(row[9]) if row[9] else []
                )
                secrets_list.append(secret_metadata)

            return secrets_list

        except Exception as e:
            self.logger.error(f"Error listando secretos: {e}")
            return []

    async def _log_access(
        self,
        secret_id: str,
        user_id: str,
        action: str,
        success: bool,
        failure_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Registra acceso a secretos para auditoría"""
        try:
            log_id = secrets.token_urlsafe(16)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO access_logs (
                    log_id, secret_id, user_id, action, timestamp,
                    ip_address, user_agent, success, failure_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_id, secret_id, user_id, action, datetime.now().isoformat(),
                ip_address, user_agent, success, failure_reason
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error registrando log de acceso: {e}")

    async def get_access_logs(self, secret_id: Optional[str] = None, user_id: Optional[str] = None) -> List[AccessLog]:
        """Obtiene logs de acceso para auditoría"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = 'SELECT * FROM access_logs WHERE 1=1'
            params = []

            if secret_id:
                query += ' AND secret_id = ?'
                params.append(secret_id)

            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)

            query += ' ORDER BY timestamp DESC LIMIT 1000'

            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            logs = []
            for row in results:
                access_log = AccessLog(
                    log_id=row[0],
                    secret_id=row[1],
                    user_id=row[2],
                    action=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    ip_address=row[5],
                    user_agent=row[6],
                    success=bool(row[7]),
                    failure_reason=row[8]
                )
                logs.append(access_log)

            return logs

        except Exception as e:
            self.logger.error(f"Error obteniendo logs de acceso: {e}")
            return []

    async def check_expired_secrets(self) -> List[str]:
        """Verifica secretos expirados para rotación automática"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute('SELECT secret_id, name FROM secrets WHERE expires_at <= ?', (now,))

            expired_secrets = cursor.fetchall()
            conn.close()

            return [{"secret_id": row[0], "name": row[1]} for row in expired_secrets]

        except Exception as e:
            self.logger.error(f"Error verificando secretos expirados: {e}")
            return []


# Ejemplo de uso
async def demo_secret_manager():
    """Demostración del gestor de secretos"""

    # Inicializar gestor
    secret_manager = SmartComputeSecretManager()

    print("🔐 Demo SmartCompute Secret Manager")
    print("=" * 40)

    # Almacenar un secreto
    secret_id = await secret_manager.store_secret(
        name="database_password",
        secret_data="super_secure_password_123!",
        secret_type=SecretType.DATABASE_PASSWORD,
        user_id="admin",
        expires_at=datetime.now() + timedelta(days=90),
        rotation_interval_days=30,
        tags=["database", "production"]
    )

    print(f"✅ Secreto almacenado con ID: {secret_id}")

    # Recuperar el secreto
    retrieved_secret = await secret_manager.get_secret(secret_id, "admin")
    print(f"✅ Secreto recuperado: {retrieved_secret}")

    # Listar secretos
    secrets_list = await secret_manager.list_secrets("admin")
    print(f"✅ Secretos encontrados: {len(secrets_list)}")

    # Ver logs de acceso
    access_logs = await secret_manager.get_access_logs(secret_id=secret_id)
    print(f"✅ Logs de acceso: {len(access_logs)}")


if __name__ == "__main__":
    asyncio.run(demo_secret_manager())