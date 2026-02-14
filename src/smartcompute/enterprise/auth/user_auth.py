#!/usr/bin/env python3
"""
SmartCompute Enterprise - User Authentication & Personalization System
======================================================================

Sistema de autenticación y personalización que permite a cada usuario:
- Iniciar sesión con su propia cuenta
- Análisis personalizados basados en su perfil
- Configuraciones específicas por usuario
- Historial de análisis personalizado
- Integración con sus propias herramientas de IA

Copyright (c) 2024 SmartCompute. All rights reserved.
"""

import asyncio
import json
import logging
import os
import hashlib
import secrets
import time
import re
import getpass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3
from dataclasses import dataclass, asdict
import uuid


@dataclass
class UserProfile:
    """Perfil de usuario SmartCompute Enterprise"""
    user_id: str
    username: str
    email: str
    organization: str
    role: str
    ai_integrations: Dict[str, Any]
    security_preferences: Dict[str, Any]
    analysis_history: List[Dict]
    created_at: datetime
    last_login: datetime
    subscription_tier: str


@dataclass
class UserSession:
    """Sesión activa de usuario"""
    session_id: str
    user_id: str
    username: str
    login_time: datetime
    expires_at: datetime
    permissions: List[str]
    active_integrations: Dict[str, Any]


class SmartComputeUserAuthSystem:
    """
    Sistema de autenticación y gestión de usuarios para SmartCompute Enterprise
    """

    def __init__(self, data_dir: str = "/tmp/smartcompute_users"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.db_path = self.data_dir / "users.db"
        self.sessions_file = self.data_dir / "active_sessions.json"

        self.logger = self._setup_logging()
        self.active_sessions = {}

        self._initialize_database()
        self._load_active_sessions()

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('SmartCompute.Auth')

    def _initialize_database(self):
        """Inicializar base de datos de usuarios"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    organization TEXT,
                    role TEXT DEFAULT 'user',
                    ai_integrations TEXT DEFAULT '{}',
                    security_preferences TEXT DEFAULT '{}',
                    analysis_history TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    subscription_tier TEXT DEFAULT 'basic',
                    is_active INTEGER DEFAULT 1
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_analysis_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    analysis_type TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    results TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

    def _load_active_sessions(self):
        """Cargar sesiones activas"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    sessions_data = json.load(f)

                current_time = datetime.now()
                for session_id, session_data in sessions_data.items():
                    expires_at = datetime.fromisoformat(session_data['expires_at'])
                    if expires_at > current_time:
                        self.active_sessions[session_id] = UserSession(**session_data)

            except Exception as e:
                self.logger.error(f"Error cargando sesiones: {e}")

    def _save_active_sessions(self):
        """Guardar sesiones activas"""
        sessions_data = {}
        for session_id, session in self.active_sessions.items():
            sessions_data[session_id] = asdict(session)

        with open(self.sessions_file, 'w') as f:
            json.dump(sessions_data, f, default=str, indent=2)

    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Crear hash seguro de contraseña"""
        if salt is None:
            salt = secrets.token_hex(32)

        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )

        return password_hash.hex(), salt

    async def register_user(self,
                           username: str,
                           email: str,
                           password: str,
                           organization: str = "",
                           role: str = "user",
                           subscription_tier: str = "basic") -> Dict[str, Any]:
        """Registrar nuevo usuario"""

        try:
            # Validar datos
            if len(username) < 3:
                return {"success": False, "error": "Username debe tener al menos 3 caracteres"}

            if len(password) < 8:
                return {"success": False, "error": "Password debe tener al menos 8 caracteres"}

            if "@" not in email:
                return {"success": False, "error": "Email inválido"}

            # Verificar si usuario ya existe
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT username FROM users WHERE username = ? OR email = ?",
                    (username, email)
                )

                if cursor.fetchone():
                    return {"success": False, "error": "Usuario o email ya existe"}

            # Crear usuario
            user_id = str(uuid.uuid4())
            password_hash, salt = self._hash_password(password)

            default_ai_integrations = {
                "claude": {"enabled": False, "api_key": "", "model": "claude-3-sonnet"},
                "openai": {"enabled": False, "api_key": "", "model": "gpt-4"},
                "local_llm": {"enabled": False, "endpoint": "", "model": ""}
            }

            default_security_preferences = {
                "analysis_sensitivity": "medium",
                "false_positive_tolerance": "medium",
                "alert_threshold": "medium",
                "auto_investigation": True,
                "data_retention_days": 30
            }

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO users (
                        user_id, username, email, password_hash, salt,
                        organization, role, ai_integrations, security_preferences,
                        subscription_tier
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, username, email, password_hash, salt,
                    organization, role,
                    json.dumps(default_ai_integrations),
                    json.dumps(default_security_preferences),
                    subscription_tier
                ))

            self.logger.info(f"Usuario registrado: {username} ({user_id})")

            return {
                "success": True,
                "user_id": user_id,
                "message": f"Usuario {username} registrado exitosamente"
            }

        except Exception as e:
            self.logger.error(f"Error registrando usuario: {e}")
            return {"success": False, "error": "Error interno del sistema"}

    async def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Iniciar sesión de usuario"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT user_id, username, email, password_hash, salt,
                           organization, role, ai_integrations, security_preferences,
                           subscription_tier
                    FROM users
                    WHERE username = ? AND is_active = 1
                ''', (username,))

                user_data = cursor.fetchone()

                if not user_data:
                    return {"success": False, "error": "Usuario no encontrado"}

            # Verificar contraseña
            stored_hash = user_data[3]
            salt = user_data[4]
            password_hash, _ = self._hash_password(password, salt)

            if password_hash != stored_hash:
                return {"success": False, "error": "Contraseña incorrecta"}

            # Crear sesión
            session_id = str(uuid.uuid4())
            login_time = datetime.now()
            expires_at = login_time + timedelta(hours=8)  # 8 horas de sesión

            # Determinar permisos basados en role y subscription
            permissions = self._get_user_permissions(user_data[6], user_data[9])

            session = UserSession(
                session_id=session_id,
                user_id=user_data[0],
                username=user_data[1],
                login_time=login_time,
                expires_at=expires_at,
                permissions=permissions,
                active_integrations=json.loads(user_data[7])
            )

            self.active_sessions[session_id] = session
            self._save_active_sessions()

            # Actualizar último login
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (login_time, user_data[0])
                )

            self.logger.info(f"Usuario logueado: {username} (Session: {session_id})")

            return {
                "success": True,
                "session_id": session_id,
                "user_id": user_data[0],
                "username": user_data[1],
                "organization": user_data[5],
                "role": user_data[6],
                "subscription_tier": user_data[9],
                "permissions": permissions,
                "expires_at": expires_at.isoformat(),
                "message": f"Bienvenido, {user_data[1]}"
            }

        except Exception as e:
            self.logger.error(f"Error en login: {e}")
            return {"success": False, "error": "Error interno del sistema"}

    def _get_user_permissions(self, role: str, subscription_tier: str) -> List[str]:
        """Obtener permisos de usuario"""
        base_permissions = ["basic_analysis", "view_reports"]

        if subscription_tier in ["professional", "enterprise"]:
            base_permissions.extend([
                "advanced_analysis", "ai_integration", "export_reports",
                "custom_dashboards", "real_time_monitoring"
            ])

        if subscription_tier == "enterprise":
            base_permissions.extend([
                "multi_user_management", "api_access", "custom_integrations",
                "compliance_reports", "advanced_security"
            ])

        if role in ["admin", "security_analyst"]:
            base_permissions.extend([
                "user_management", "system_config", "security_policies"
            ])

        return base_permissions

    async def get_user_profile(self, session_id: str) -> Dict[str, Any]:
        """Obtener perfil de usuario autenticado"""

        session = self.active_sessions.get(session_id)
        if not session or session.expires_at < datetime.now():
            return {"success": False, "error": "Sesión inválida o expirada"}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT user_id, username, email, organization, role,
                           ai_integrations, security_preferences, analysis_history,
                           created_at, last_login, subscription_tier
                    FROM users WHERE user_id = ?
                ''', (session.user_id,))

                user_data = cursor.fetchone()

                if not user_data:
                    return {"success": False, "error": "Usuario no encontrado"}

            profile = {
                "user_id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
                "organization": user_data[3],
                "role": user_data[4],
                "ai_integrations": json.loads(user_data[5]),
                "security_preferences": json.loads(user_data[6]),
                "analysis_history": json.loads(user_data[7]),
                "created_at": user_data[8],
                "last_login": user_data[9],
                "subscription_tier": user_data[10],
                "current_session": {
                    "session_id": session_id,
                    "login_time": session.login_time.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "permissions": session.permissions
                }
            }

            return {"success": True, "profile": profile}

        except Exception as e:
            self.logger.error(f"Error obteniendo perfil: {e}")
            return {"success": False, "error": "Error interno del sistema"}

    async def update_ai_integrations(self, session_id: str, integrations: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar integraciones de IA del usuario"""

        session = self.active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Sesión inválida"}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE users SET ai_integrations = ? WHERE user_id = ?",
                    (json.dumps(integrations), session.user_id)
                )

            # Actualizar sesión activa
            session.active_integrations = integrations
            self._save_active_sessions()

            self.logger.info(f"Integraciones IA actualizadas para {session.username}")

            return {"success": True, "message": "Integraciones actualizadas"}

        except Exception as e:
            self.logger.error(f"Error actualizando integraciones: {e}")
            return {"success": False, "error": "Error interno del sistema"}

    async def save_analysis_session(self,
                                   session_id: str,
                                   analysis_type: str,
                                   results: Dict[str, Any]) -> Dict[str, Any]:
        """Guardar sesión de análisis del usuario"""

        session = self.active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Sesión inválida"}

        try:
            analysis_session_id = str(uuid.uuid4())

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO user_analysis_sessions
                    (session_id, user_id, analysis_type, start_time, end_time, results)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    analysis_session_id,
                    session.user_id,
                    analysis_type,
                    results.get('start_time', datetime.now()),
                    results.get('end_time', datetime.now()),
                    json.dumps(results)
                ))

            self.logger.info(f"Análisis guardado para {session.username}: {analysis_type}")

            return {
                "success": True,
                "analysis_session_id": analysis_session_id,
                "message": "Análisis guardado exitosamente"
            }

        except Exception as e:
            self.logger.error(f"Error guardando análisis: {e}")
            return {"success": False, "error": "Error interno del sistema"}

    async def get_user_analysis_history(self, session_id: str, limit: int = 10) -> Dict[str, Any]:
        """Obtener historial de análisis del usuario"""

        session = self.active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Sesión inválida"}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT session_id, analysis_type, start_time, end_time, results
                    FROM user_analysis_sessions
                    WHERE user_id = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                ''', (session.user_id, limit))

                history = []
                for row in cursor.fetchall():
                    history.append({
                        "session_id": row[0],
                        "analysis_type": row[1],
                        "start_time": row[2],
                        "end_time": row[3],
                        "results_summary": json.loads(row[4])
                    })

            return {"success": True, "history": history}

        except Exception as e:
            self.logger.error(f"Error obteniendo historial: {e}")
            return {"success": False, "error": "Error interno del sistema"}

    async def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Cerrar sesión de usuario"""

        if session_id in self.active_sessions:
            username = self.active_sessions[session_id].username
            del self.active_sessions[session_id]
            self._save_active_sessions()

            self.logger.info(f"Usuario deslogueado: {username}")

            return {"success": True, "message": "Sesión cerrada exitosamente"}

        return {"success": False, "error": "Sesión no encontrada"}

    def list_users(self) -> List[Dict[str, Any]]:
        """Listar usuarios (solo para admins)"""

        users = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT user_id, username, email, organization, role,
                           created_at, last_login, subscription_tier, is_active
                    FROM users
                    ORDER BY created_at DESC
                ''')

                for row in cursor.fetchall():
                    users.append({
                        "user_id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "organization": row[3],
                        "role": row[4],
                        "created_at": row[5],
                        "last_login": row[6],
                        "subscription_tier": row[7],
                        "is_active": bool(row[8])
                    })

        except Exception as e:
            self.logger.error(f"Error listando usuarios: {e}")

        return users

    def get_active_sessions_count(self) -> int:
        """Obtener número de sesiones activas"""
        current_time = datetime.now()
        active_count = sum(
            1 for session in self.active_sessions.values()
            if session.expires_at > current_time
        )
        return active_count


class SmartComputeAuthCLI:
    """CLI para gestión de autenticación SmartCompute"""

    def __init__(self):
        self.auth_system = SmartComputeUserAuthSystem()

    async def interactive_login(self) -> Optional[str]:
        """Login interactivo"""
        print("🔐 SmartCompute Enterprise - Autenticación")
        print("=" * 50)

        choice = input("¿Tienes una cuenta? (y/n): ").lower()

        if choice == 'n':
            return await self._interactive_register()
        else:
            return await self._interactive_login()

    def _validate_username(self, username: str) -> bool:
        """Valida formato de username"""
        if not username or len(username) < 3 or len(username) > 20:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))

    def _validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_password(self, password: str) -> bool:
        """Valida seguridad de password"""
        if len(password) < 8:
            return False
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        return has_upper and has_lower and has_digit and has_special

    async def _interactive_register(self) -> Optional[str]:
        """Registro interactivo con validación de seguridad"""
        print("\n📝 Registro de Nueva Cuenta")
        print("-" * 30)

        # Validación de username
        while True:
            username = input("Username (3-20 chars, alfanumérico): ").strip()
            if self._validate_username(username):
                break
            print("❌ Username inválido. Use 3-20 caracteres alfanuméricos.")

        # Validación de email
        while True:
            email = input("Email: ").strip()
            if self._validate_email(email):
                break
            print("❌ Email inválido. Use formato válido (ejemplo@dominio.com)")

        # Validación de password
        while True:
            password = getpass.getpass("Password (mín. 8 chars, mayús/min/num/especial): ")
            if self._validate_password(password):
                break
            print("❌ Password inseguro. Mínimo 8 chars con mayúscula, minúscula, número y carácter especial.")

        organization = input("Organización (opcional): ").strip()
        if organization:
            # Sanitizar organización
            organization = re.sub(r'[^a-zA-Z0-9\s\-_.]', '', organization)[:100]

        result = await self.auth_system.register_user(
            username=username,
            email=email,
            password=password,
            organization=organization
        )

        if result["success"]:
            print(f"✅ {result['message']}")
            print("Ahora puedes iniciar sesión...")
            return await self._interactive_login()
        else:
            print(f"❌ Error: {result['error']}")
            return None

    async def _interactive_login(self) -> Optional[str]:
        """Login interactivo"""
        print("\n🔑 Iniciar Sesión")
        print("-" * 20)

        username = input("Username: ")
        password = input("Password: ")

        result = await self.auth_system.login_user(username, password)

        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"Session ID: {result['session_id']}")
            print(f"Organización: {result['organization']}")
            print(f"Tier: {result['subscription_tier']}")
            print(f"Permisos: {', '.join(result['permissions'])}")

            return result["session_id"]
        else:
            print(f"❌ Error: {result['error']}")
            return None

    async def show_profile(self, session_id: str):
        """Mostrar perfil de usuario"""
        result = await self.auth_system.get_user_profile(session_id)

        if result["success"]:
            profile = result["profile"]
            print(f"\n👤 Perfil de Usuario")
            print("=" * 30)
            print(f"Usuario: {profile['username']}")
            print(f"Email: {profile['email']}")
            print(f"Organización: {profile['organization']}")
            print(f"Role: {profile['role']}")
            print(f"Tier: {profile['subscription_tier']}")
            print(f"Creado: {profile['created_at']}")
            print(f"Último login: {profile['last_login']}")
            print(f"Sesión expira: {profile['current_session']['expires_at']}")
        else:
            print(f"❌ Error: {result['error']}")


async def demo_auth_system():
    """Demo del sistema de autenticación"""

    cli = SmartComputeAuthCLI()

    print("🚀 SmartCompute Enterprise - Demo Sistema de Autenticación")
    print("=" * 60)

    # Login interactivo
    session_id = await cli.interactive_login()

    if session_id:
        # Mostrar perfil
        await cli.show_profile(session_id)

        # Simular guardar análisis
        analysis_results = {
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "security_score": 85,
            "threats_detected": 3,
            "recommendations": ["Update system", "Check connections"]
        }

        save_result = await cli.auth_system.save_analysis_session(
            session_id, "mcp_integrated_analysis", analysis_results
        )

        if save_result["success"]:
            print(f"\n💾 {save_result['message']}")

        # Mostrar historial
        history_result = await cli.auth_system.get_user_analysis_history(session_id)

        if history_result["success"]:
            print(f"\n📊 Historial de Análisis:")
            for analysis in history_result["history"]:
                print(f"  • {analysis['analysis_type']} - {analysis['start_time']}")

        # Logout
        logout_result = await cli.auth_system.logout_user(session_id)
        if logout_result["success"]:
            print(f"\n👋 {logout_result['message']}")


if __name__ == "__main__":
    asyncio.run(demo_auth_system())