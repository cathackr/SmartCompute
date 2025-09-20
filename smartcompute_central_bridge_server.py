#!/usr/bin/env python3
"""
SmartCompute Central Bridge Server - Servidor administrativo centralizado

Funcionalidades:
- Control de acceso granular entre Enterprise e Industrial
- Autenticación y autorización de usuarios
- Gestión de permisos por roles y ubicaciones
- Dashboard administrativo en tiempo real
- Logging y auditoría de todas las operaciones
- API REST para integración con GUIs

Author: SmartCompute Team
Version: 2.0.0 Central Bridge
Date: 2025-09-19
"""

from flask import Flask, jsonify, request, render_template_string
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime, timedelta
import jwt
import hashlib
import sqlite3
from pathlib import Path
import logging
from typing import Dict, List, Optional
import asyncio
import websockets

class SmartComputeCentralServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = '***REMOVED***'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Base de datos
        self.db_path = Path(__file__).parent / "smartcompute_bridge.db"
        self.init_database()

        # Estado del sistema
        self.connected_clients = {}
        self.active_sessions = {}
        self.bridge_status = {
            'enterprise_gui': {'connected': False, 'last_seen': None},
            'industrial_gui': {'connected': False, 'last_seen': None},
            'network_bridge': {'connected': False, 'last_seen': None}
        }

        # Configurar rutas y eventos
        self.setup_routes()
        self.setup_socket_events()

        # Iniciar servicios
        self.start_background_services()

        self.logger = self.setup_logging()
        self.logger.info("🏛️ SmartCompute Central Bridge Server iniciado")

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('Central-Bridge-Server')

    def init_database(self):
        """Inicializar base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                permissions TEXT NOT NULL,
                enterprise_access BOOLEAN DEFAULT 0,
                industrial_access BOOLEAN DEFAULT 0,
                admin_access BOOLEAN DEFAULT 0,
                location_access TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                client_type TEXT NOT NULL,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Tabla de auditoría
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Tabla de permisos de ubicación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS location_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plant_section TEXT NOT NULL,
                zone_access TEXT NOT NULL,
                equipment_access TEXT,
                permission_level TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Crear usuario administrador por defecto
        admin_password = hashlib.sha256('***REMOVED***'.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users
            (username, password_hash, role, permissions, enterprise_access, industrial_access, admin_access, location_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin',
            admin_password,
            'super_admin',
            json.dumps(['all']),
            True, True, True,
            json.dumps(['all_locations'])
        ))

        # Crear usuarios de prueba
        operator_password = hashlib.sha256('***REMOVED***'.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users
            (username, password_hash, role, permissions, enterprise_access, industrial_access, admin_access, location_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'operator_industrial',
            operator_password,
            'operator',
            json.dumps(['read', 'control_plc']),
            False, True, False,
            json.dumps(['planta_a', 'sector_produccion'])
        ))

        conn.commit()
        conn.close()

    def setup_routes(self):
        """Configurar rutas REST API"""

        @self.app.route('/')
        def dashboard():
            return render_template_string(self.get_dashboard_template())

        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            client_type = data.get('client_type', 'web')

            user = self.authenticate_user(username, password)
            if user:
                token = self.create_session(user, client_type, request.remote_addr)
                self.log_audit(user['id'], 'login', 'auth', f'Successful login from {client_type}', request.remote_addr, True)

                return jsonify({
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'role': user['role'],
                        'permissions': json.loads(user['permissions']),
                        'enterprise_access': bool(user['enterprise_access']),
                        'industrial_access': bool(user['industrial_access']),
                        'admin_access': bool(user['admin_access'])
                    }
                })
            else:
                self.log_audit(None, 'login_failed', 'auth', f'Failed login attempt for {username}', request.remote_addr, False)
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        @self.app.route('/api/auth/validate', methods=['POST'])
        def validate_token():
            data = request.get_json()
            token = data.get('token')

            session = self.validate_session(token)
            if session:
                return jsonify({'valid': True, 'session': session})
            else:
                return jsonify({'valid': False}), 401

        @self.app.route('/api/bridge/status')
        def bridge_status():
            return jsonify(self.get_bridge_status())

        @self.app.route('/api/bridge/connect', methods=['POST'])
        def register_client():
            data = request.get_json()
            client_type = data.get('type')  # 'enterprise', 'industrial', 'network_bridge'
            token = data.get('token')

            session = self.validate_session(token)
            if session:
                self.register_bridge_client(client_type, session, request.remote_addr)
                return jsonify({'success': True, 'registered': True})
            else:
                return jsonify({'success': False, 'message': 'Invalid session'}), 401

        @self.app.route('/api/permissions/check', methods=['POST'])
        def check_permissions():
            data = request.get_json()
            token = data.get('token')
            action = data.get('action')
            resource = data.get('resource')
            location = data.get('location')

            session = self.validate_session(token)
            if session:
                has_permission = self.check_user_permission(session['user_id'], action, resource, location)
                return jsonify({'allowed': has_permission})
            else:
                return jsonify({'allowed': False}), 401

        @self.app.route('/api/communications/route', methods=['POST'])
        def route_communication():
            data = request.get_json()
            token = data.get('token')
            source = data.get('source')  # 'enterprise' or 'industrial'
            target = data.get('target')  # 'industrial' or 'enterprise'
            message = data.get('message')

            session = self.validate_session(token)
            if session:
                # Verificar permisos de comunicación cruzada
                if self.can_communicate_across_domains(session['user_id'], source, target):
                    result = self.route_cross_domain_communication(source, target, message, session)
                    return jsonify({'success': True, 'routed': result})
                else:
                    return jsonify({'success': False, 'message': 'Cross-domain communication not authorized'}), 403
            else:
                return jsonify({'success': False, 'message': 'Invalid session'}), 401

    def setup_socket_events(self):
        """Configurar eventos WebSocket"""

        @self.socketio.on('connect')
        def handle_connect():
            print(f"Client connected: {request.sid}")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"Client disconnected: {request.sid}")

        @self.socketio.on('gui_status_update')
        def handle_gui_status(data):
            gui_type = data.get('type')
            status = data.get('status')
            self.update_gui_status(gui_type, status)

            # Broadcast a todos los clientes
            self.socketio.emit('bridge_status_update', {
                'type': gui_type,
                'status': status,
                'timestamp': datetime.now().isoformat()
            })

        @self.socketio.on('cross_domain_request')
        def handle_cross_domain_request(data):
            token = data.get('token')
            source_domain = data.get('source_domain')
            target_domain = data.get('target_domain')
            request_data = data.get('request_data')

            session = self.validate_session(token)
            if session and self.can_communicate_across_domains(session['user_id'], source_domain, target_domain):
                # Reenviar solicitud al dominio objetivo
                self.socketio.emit(f'{target_domain}_request', {
                    'source': source_domain,
                    'data': request_data,
                    'session': session
                }, room=target_domain)

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Autenticar usuario"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, password_hash, role, permissions,
                   enterprise_access, industrial_access, admin_access, location_access
            FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'id': result[0],
                'username': result[1],
                'password_hash': result[2],
                'role': result[3],
                'permissions': result[4],
                'enterprise_access': result[5],
                'industrial_access': result[6],
                'admin_access': result[7],
                'location_access': result[8]
            }
        return None

    def create_session(self, user: Dict, client_type: str, ip_address: str) -> str:
        """Crear sesión de usuario"""
        # Generar token JWT
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'client_type': client_type,
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm='HS256')

        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, client_type, ip_address, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user['id'], token, client_type, ip_address,
            datetime.utcnow() + timedelta(hours=8)
        ))

        # Actualizar último login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                      (datetime.utcnow(), user['id']))

        conn.commit()
        conn.close()

        return token

    def validate_session(self, token: str) -> Optional[Dict]:
        """Validar token de sesión"""
        try:
            payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT s.*, u.username, u.role, u.permissions, u.enterprise_access, u.industrial_access, u.admin_access
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.active = 1 AND s.expires_at > ?
            ''', (token, datetime.utcnow()))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'session_id': result[0],
                    'user_id': result[1],
                    'token': result[2],
                    'client_type': result[3],
                    'ip_address': result[4],
                    'username': result[7],
                    'role': result[8],
                    'permissions': json.loads(result[9]),
                    'enterprise_access': bool(result[10]),
                    'industrial_access': bool(result[11]),
                    'admin_access': bool(result[12])
                }
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

        return None

    def check_user_permission(self, user_id: int, action: str, resource: str, location: str = None) -> bool:
        """Verificar permisos de usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Obtener permisos del usuario
        cursor.execute('SELECT permissions, admin_access, location_access FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

        if not result:
            return False

        permissions = json.loads(result[0])
        admin_access = bool(result[1])
        location_access = json.loads(result[2]) if result[2] else []

        # Admin tiene todos los permisos
        if admin_access:
            return True

        # Verificar permiso específico
        if action in permissions or 'all' in permissions:
            # Si se especifica ubicación, verificar acceso
            if location and location_access and 'all_locations' not in location_access:
                return location in location_access
            return True

        conn.close()
        return False

    def can_communicate_across_domains(self, user_id: int, source_domain: str, target_domain: str) -> bool:
        """Verificar si el usuario puede comunicarse entre dominios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT enterprise_access, industrial_access, admin_access, role
            FROM users WHERE id = ?
        ''', (user_id,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return False

        enterprise_access, industrial_access, admin_access, role = result

        # Admin puede comunicarse entre cualquier dominio
        if admin_access:
            return True

        # Verificar acceso específico
        if source_domain == 'enterprise' and target_domain == 'industrial':
            return enterprise_access and industrial_access
        elif source_domain == 'industrial' and target_domain == 'enterprise':
            return industrial_access and enterprise_access

        return False

    def register_bridge_client(self, client_type: str, session: Dict, ip_address: str):
        """Registrar cliente bridge"""
        self.connected_clients[client_type] = {
            'session': session,
            'ip_address': ip_address,
            'connected_at': datetime.now().isoformat(),
            'last_ping': datetime.now().isoformat()
        }

        self.bridge_status[client_type] = {
            'connected': True,
            'last_seen': datetime.now().isoformat()
        }

        self.logger.info(f"🔗 Cliente {client_type} registrado desde {ip_address}")

    def update_gui_status(self, gui_type: str, status: Dict):
        """Actualizar estado de GUI"""
        if gui_type in self.bridge_status:
            self.bridge_status[gui_type].update(status)
            self.bridge_status[gui_type]['last_seen'] = datetime.now().isoformat()

    def route_cross_domain_communication(self, source: str, target: str, message: Dict, session: Dict) -> bool:
        """Rutear comunicación entre dominios"""
        try:
            # Log de auditoría
            self.log_audit(
                session['user_id'],
                'cross_domain_communication',
                f'{source}->{target}',
                json.dumps(message),
                session['ip_address'],
                True
            )

            # Enviar mensaje via WebSocket al dominio objetivo
            self.socketio.emit(f'{target}_message', {
                'source': source,
                'message': message,
                'session_info': {
                    'username': session['username'],
                    'role': session['role']
                },
                'timestamp': datetime.now().isoformat()
            }, room=target)

            return True

        except Exception as e:
            self.logger.error(f"Error routing cross-domain communication: {e}")
            return False

    def log_audit(self, user_id: Optional[int], action: str, resource: str,
                  details: str, ip_address: str, success: bool):
        """Registrar evento de auditoría"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO audit_log (user_id, action, resource, details, ip_address, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, action, resource, details, ip_address, success))

        conn.commit()
        conn.close()

    def get_bridge_status(self) -> Dict:
        """Obtener estado del bridge"""
        return {
            'bridge_status': self.bridge_status,
            'connected_clients': len(self.connected_clients),
            'active_sessions': len(self.active_sessions),
            'server_uptime': time.time(),
            'timestamp': datetime.now().isoformat()
        }

    def start_background_services(self):
        """Iniciar servicios en segundo plano"""
        def heartbeat_checker():
            while True:
                try:
                    # Verificar clientes conectados
                    current_time = datetime.now()
                    for client_type, client_info in list(self.connected_clients.items()):
                        last_ping = datetime.fromisoformat(client_info['last_ping'])
                        if (current_time - last_ping).total_seconds() > 60:  # 60 segundos timeout
                            self.bridge_status[client_type]['connected'] = False
                            del self.connected_clients[client_type]
                            self.logger.warning(f"⚠️ Cliente {client_type} desconectado por timeout")

                    time.sleep(30)
                except Exception as e:
                    self.logger.error(f"Error in heartbeat checker: {e}")
                    time.sleep(60)

        heartbeat_thread = threading.Thread(target=heartbeat_checker)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    def get_dashboard_template(self) -> str:
        """Template HTML del dashboard"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>SmartCompute Central Bridge Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: white; }
        .header { text-align: center; margin-bottom: 30px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .status-card { background: #16213e; padding: 20px; border-radius: 10px; border: 1px solid #3282b8; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 10px; }
        .connected { background-color: #4CAF50; }
        .disconnected { background-color: #f44336; }
        .metric { margin: 10px 0; }
        .metric-label { font-weight: bold; color: #3282b8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ SmartCompute Central Bridge Dashboard</h1>
        <p>Sistema de Control de Conectividad Enterprise-Industrial</p>
    </div>

    <div class="status-grid">
        <div class="status-card">
            <h3>🏢 Enterprise GUI</h3>
            <div class="metric">
                <span class="status-indicator" id="enterprise-indicator"></span>
                Estado: <span id="enterprise-status">Desconectado</span>
            </div>
            <div class="metric">
                <span class="metric-label">Última comunicación:</span>
                <span id="enterprise-last-seen">N/A</span>
            </div>
        </div>

        <div class="status-card">
            <h3>🏭 Industrial GUI</h3>
            <div class="metric">
                <span class="status-indicator" id="industrial-indicator"></span>
                Estado: <span id="industrial-status">Desconectado</span>
            </div>
            <div class="metric">
                <span class="metric-label">Última comunicación:</span>
                <span id="industrial-last-seen">N/A</span>
            </div>
        </div>

        <div class="status-card">
            <h3>🌐 Network Bridge</h3>
            <div class="metric">
                <span class="status-indicator" id="bridge-indicator"></span>
                Estado: <span id="bridge-status">Desconectado</span>
            </div>
            <div class="metric">
                <span class="metric-label">Última comunicación:</span>
                <span id="bridge-last-seen">N/A</span>
            </div>
        </div>
    </div>

    <script>
        const socket = io();

        socket.on('bridge_status_update', function(data) {
            updateStatus(data.type, data.status, data.timestamp);
        });

        function updateStatus(type, status, timestamp) {
            const indicator = document.getElementById(type + '-indicator');
            const statusText = document.getElementById(type + '-status');
            const lastSeen = document.getElementById(type + '-last-seen');

            if (status.connected) {
                indicator.className = 'status-indicator connected';
                statusText.textContent = 'Conectado';
            } else {
                indicator.className = 'status-indicator disconnected';
                statusText.textContent = 'Desconectado';
            }

            lastSeen.textContent = timestamp;
        }

        // Actualizar estado cada 5 segundos
        setInterval(function() {
            fetch('/api/bridge/status')
                .then(response => response.json())
                .then(data => {
                    Object.keys(data.bridge_status).forEach(type => {
                        const status = data.bridge_status[type];
                        updateStatus(type.replace('_gui', '').replace('_', '-'), status, status.last_seen);
                    });
                });
        }, 5000);
    </script>
</body>
</html>
        '''

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecutar servidor"""
        self.logger.info(f"🚀 Iniciando servidor central en {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """Función principal"""
    print("🏛️ SmartCompute Central Bridge Server")
    print("=" * 50)

    server = SmartComputeCentralServer()

    try:
        server.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
    except Exception as e:
        print(f"❌ Error crítico: {e}")


if __name__ == "__main__":
    main()