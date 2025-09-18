#!/usr/bin/env python3
"""
SmartCompute Central Server - MCP-Based Virtual Server
=====================================================

Servidor central basado en MCP (Model Context Protocol) que permite:
- Centralización de datos de SmartCompute Enterprise e Industrial
- Gestión de incidentes y respuestas automatizadas
- Backup configurables con RAID
- Despliegue en nubes públicas y privadas (Google Cloud, AWS)
- Acceso seguro para gestión de incidentes
"""

import asyncio
import json
import ssl
import sqlite3
import hashlib
import hmac
import os
import logging
import aiohttp
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import yaml
import jwt
from cryptography.fernet import Fernet
import redis.asyncio as redis
from aiohttp import web, WSMsgType
import websockets
import base64

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisData:
    """Estructura de datos de análisis"""
    client_id: str
    analysis_type: str  # enterprise, industrial
    timestamp: str
    data: Dict[str, Any]
    severity: str
    status: str = "active"
    incident_id: Optional[str] = None

@dataclass
class Incident:
    """Estructura de incidente"""
    incident_id: str
    title: str
    description: str
    severity: str  # low, medium, high, critical
    status: str  # open, investigating, resolved, closed
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None
    source_analysis: List[str] = None
    resolution_steps: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Client:
    """Cliente conectado"""
    client_id: str
    client_type: str  # enterprise, industrial
    hostname: str
    ip_address: str
    last_seen: str
    version: str
    status: str = "online"

class SmartComputeCentralServer:
    """Servidor central SmartCompute con protocolo MCP"""

    def __init__(self, config_path: str = "server_config.yaml"):
        self.config = self._load_config(config_path)
        self.clients: Dict[str, Client] = {}
        self.incidents: Dict[str, Incident] = {}
        self.analysis_cache = {}

        # Configuración de base de datos
        self.db_path = self.config.get('database', {}).get('path', 'smartcompute.db')

        # Configuración de Redis para caché
        self.redis_client = None

        # Configuración de cifrado
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)

        # JWT secret para autenticación
        self.jwt_secret = self.config.get('security', {}).get('jwt_secret', self._generate_jwt_secret())

        # WebSocket connections
        self.websocket_connections = set()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Cargar configuración del servidor"""
        default_config = {
            'server': {
                'host': '0.0.0.0',
                'port': 8080,
                'ssl_port': 8443,
                'ssl_enabled': True,
                'ssl_cert': 'server.crt',
                'ssl_key': 'server.key'
            },
            'database': {
                'path': 'smartcompute.db',
                'backup_enabled': True,
                'backup_interval': 3600,  # 1 hora
                'raid_config': 'raid1'  # raid0, raid1, raid5, raid10
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0
            },
            'cloud': {
                'provider': 'local',  # local, gcp, aws, azure, private
                'region': 'us-central1',
                'backup_bucket': 'smartcompute-backups'
            },
            'security': {
                'api_key_required': True,
                'jwt_expiration': 86400,  # 24 horas
                'rate_limiting': True,
                'allowed_origins': ['*']
            },
            'incident_management': {
                'auto_escalation': True,
                'escalation_timeout': 1800,  # 30 minutos
                'notification_webhook': None
            }
        }

        if Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    # Merge configurations
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")

        return default_config

    def _get_or_create_encryption_key(self) -> bytes:
        """Obtener o crear clave de cifrado"""
        key_file = Path('.encryption_key')
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Solo lectura para el propietario
            return key

    def _generate_jwt_secret(self) -> str:
        """Generar secreto JWT"""
        return base64.b64encode(os.urandom(32)).decode()

    async def initialize_database(self):
        """Inicializar base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla de análisis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data_encrypted TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                incident_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de incidentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                assigned_to TEXT,
                resolution_steps TEXT,
                metadata_encrypted TEXT,
                resolved_at TIMESTAMP
            )
        ''')

        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                client_type TEXT NOT NULL,
                hostname TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT DEFAULT 'online',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de backups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                backup_id TEXT PRIMARY KEY,
                backup_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cloud_location TEXT
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    async def initialize_redis(self):
        """Inicializar conexión Redis"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis not available: {e}, using memory cache")
            self.redis_client = None

    def generate_client_token(self, client_id: str, client_type: str) -> str:
        """Generar token JWT para cliente"""
        payload = {
            'client_id': client_id,
            'client_type': client_type,
            'issued_at': datetime.utcnow().timestamp(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=self.config['security']['jwt_expiration'])).timestamp()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def verify_client_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            if payload['expires_at'] < datetime.utcnow().timestamp():
                return None
            return payload
        except jwt.InvalidTokenError:
            return None

    async def register_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar nuevo cliente"""
        client_id = client_data.get('client_id')
        client_type = client_data.get('client_type')  # enterprise, industrial
        hostname = client_data.get('hostname')
        ip_address = client_data.get('ip_address')
        version = client_data.get('version', '1.0.0')

        if not all([client_id, client_type, hostname, ip_address]):
            raise ValueError("Missing required client information")

        client = Client(
            client_id=client_id,
            client_type=client_type,
            hostname=hostname,
            ip_address=ip_address,
            last_seen=datetime.utcnow().isoformat(),
            version=version
        )

        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO clients
            (client_id, client_type, hostname, ip_address, last_seen, version, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (client.client_id, client.client_type, client.hostname,
              client.ip_address, client.last_seen, client.version, client.status))
        conn.commit()
        conn.close()

        # Guardar en memoria
        self.clients[client_id] = client

        # Generar token
        token = self.generate_client_token(client_id, client_type)

        logger.info(f"Client registered: {client_id} ({client_type}) from {ip_address}")

        return {
            'status': 'registered',
            'client_id': client_id,
            'token': token,
            'expires_in': self.config['security']['jwt_expiration']
        }

    async def store_analysis(self, analysis_data: AnalysisData) -> str:
        """Almacenar análisis cifrado"""
        # Cifrar datos sensibles
        data_json = json.dumps(analysis_data.data)
        encrypted_data = self.fernet.encrypt(data_json.encode()).decode()

        # Generar ID único
        analysis_id = hashlib.sha256(
            f"{analysis_data.client_id}{analysis_data.timestamp}{data_json}".encode()
        ).hexdigest()[:16]

        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses
            (client_id, analysis_type, timestamp, data_encrypted, severity, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (analysis_data.client_id, analysis_data.analysis_type,
              analysis_data.timestamp, encrypted_data,
              analysis_data.severity, analysis_data.status))
        conn.commit()
        conn.close()

        # Cache en Redis si está disponible
        if self.redis_client:
            cache_key = f"analysis:{analysis_id}"
            await self.redis_client.setex(
                cache_key, 3600,
                json.dumps(asdict(analysis_data))
            )

        # Verificar si se debe crear incidente
        if analysis_data.severity in ['high', 'critical']:
            incident_id = await self.create_incident_from_analysis(analysis_data)
            analysis_data.incident_id = incident_id

        logger.info(f"Analysis stored: {analysis_id} from {analysis_data.client_id}")
        return analysis_id

    async def create_incident_from_analysis(self, analysis_data: AnalysisData) -> str:
        """Crear incidente automáticamente desde análisis"""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{len(self.incidents) + 1:04d}"

        # Determinar título y descripción basado en el análisis
        if analysis_data.analysis_type == 'enterprise':
            title = f"Security Alert - {analysis_data.severity.upper()}"
            description = "Enterprise security analysis detected critical issues"
        else:  # industrial
            title = f"Industrial System Alert - {analysis_data.severity.upper()}"
            description = "Industrial system analysis detected critical conditions"

        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=analysis_data.severity,
            status='open',
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            source_analysis=[analysis_data.client_id],
            metadata={'analysis_type': analysis_data.analysis_type}
        )

        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(incident.metadata or {})
        encrypted_metadata = self.fernet.encrypt(metadata_json.encode()).decode()

        cursor.execute('''
            INSERT INTO incidents
            (incident_id, title, description, severity, status, created_at, updated_at, metadata_encrypted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (incident.incident_id, incident.title, incident.description,
              incident.severity, incident.status, incident.created_at,
              incident.updated_at, encrypted_metadata))
        conn.commit()
        conn.close()

        self.incidents[incident_id] = incident

        # Notificar via WebSocket a clientes conectados
        await self.broadcast_incident_update(incident)

        logger.warning(f"Incident created: {incident_id} from analysis {analysis_data.client_id}")
        return incident_id

    async def broadcast_incident_update(self, incident: Incident):
        """Broadcast incident update to connected WebSocket clients"""
        if self.websocket_connections:
            message = {
                'type': 'incident_update',
                'incident': asdict(incident),
                'timestamp': datetime.utcnow().isoformat()
            }

            disconnected = set()
            for ws in self.websocket_connections:
                try:
                    await ws.send(json.dumps(message))
                except:
                    disconnected.add(ws)

            # Remove disconnected clients
            self.websocket_connections -= disconnected

    async def get_analysis_history(self, client_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener historial de análisis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT client_id, analysis_type, timestamp, data_encrypted, severity, status, incident_id
            FROM analyses
            WHERE client_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (client_id, limit))

        results = []
        for row in cursor.fetchall():
            try:
                # Desencriptar datos
                encrypted_data = row[3].encode()
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                data = json.loads(decrypted_data)

                results.append({
                    'client_id': row[0],
                    'analysis_type': row[1],
                    'timestamp': row[2],
                    'data': data,
                    'severity': row[4],
                    'status': row[5],
                    'incident_id': row[6]
                })
            except Exception as e:
                logger.error(f"Error decrypting analysis data: {e}")

        conn.close()
        return results

    async def backup_database(self) -> Dict[str, Any]:
        """Crear backup de la base de datos"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_id = f"backup_{timestamp}"

        # Configuración RAID
        raid_config = self.config.get('database', {}).get('raid_config', 'raid1')

        backup_info = {
            'backup_id': backup_id,
            'timestamp': timestamp,
            'raid_config': raid_config,
            'files': []
        }

        # Crear backup según configuración RAID
        if raid_config == 'raid0':
            # RAID 0 - Sin redundancia, solo velocidad
            backup_files = await self._create_raid0_backup(backup_id)
        elif raid_config == 'raid1':
            # RAID 1 - Mirror completo
            backup_files = await self._create_raid1_backup(backup_id)
        elif raid_config == 'raid5':
            # RAID 5 - Con paridad
            backup_files = await self._create_raid5_backup(backup_id)
        elif raid_config == 'raid10':
            # RAID 10 - Mirror + Stripe
            backup_files = await self._create_raid10_backup(backup_id)

        backup_info['files'] = backup_files

        # Subir a la nube si está configurado
        cloud_provider = self.config.get('cloud', {}).get('provider', 'local')
        if cloud_provider != 'local':
            cloud_locations = await self._upload_to_cloud(backup_files, cloud_provider)
            backup_info['cloud_locations'] = cloud_locations

        # Registrar backup en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for file_info in backup_files:
            cursor.execute('''
                INSERT INTO backups (backup_id, backup_type, file_path, size_bytes, checksum)
                VALUES (?, ?, ?, ?, ?)
            ''', (backup_id, raid_config, file_info['path'],
                  file_info['size'], file_info['checksum']))
        conn.commit()
        conn.close()

        logger.info(f"Database backup created: {backup_id} ({raid_config})")
        return backup_info

    async def _create_raid1_backup(self, backup_id: str) -> List[Dict[str, Any]]:
        """Crear backup RAID 1 (mirror)"""
        backup_dir = Path(f"backups/{backup_id}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Crear dos copias idénticas
        files = []
        for mirror in ['mirror1', 'mirror2']:
            mirror_path = backup_dir / mirror / f"smartcompute_{backup_id}.db"
            mirror_path.parent.mkdir(exist_ok=True)

            # Copiar base de datos
            import shutil
            shutil.copy2(self.db_path, mirror_path)

            # Calcular checksum
            with open(mirror_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            files.append({
                'path': str(mirror_path),
                'size': mirror_path.stat().st_size,
                'checksum': checksum,
                'mirror': mirror
            })

        return files

    async def _create_raid0_backup(self, backup_id: str) -> List[Dict[str, Any]]:
        """Crear backup RAID 0 (stripe)"""
        # Para simplicidad, crear archivo único (RAID 0 requiere múltiples discos)
        backup_dir = Path(f"backups/{backup_id}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"smartcompute_{backup_id}.db"

        import shutil
        shutil.copy2(self.db_path, backup_path)

        with open(backup_path, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        return [{
            'path': str(backup_path),
            'size': backup_path.stat().st_size,
            'checksum': checksum,
            'stripe': 'single'
        }]

    async def _create_raid5_backup(self, backup_id: str) -> List[Dict[str, Any]]:
        """Crear backup RAID 5 (con paridad)"""
        # Simulación de RAID 5 con archivos de paridad
        backup_dir = Path(f"backups/{backup_id}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        files = []

        # Crear archivo principal
        main_path = backup_dir / f"smartcompute_{backup_id}_main.db"
        import shutil
        shutil.copy2(self.db_path, main_path)

        # Crear archivo de paridad (simplificado)
        parity_path = backup_dir / f"smartcompute_{backup_id}_parity.db"
        shutil.copy2(self.db_path, parity_path)

        for path in [main_path, parity_path]:
            with open(path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            files.append({
                'path': str(path),
                'size': path.stat().st_size,
                'checksum': checksum,
                'type': 'main' if 'main' in path.name else 'parity'
            })

        return files

    async def _create_raid10_backup(self, backup_id: str) -> List[Dict[str, Any]]:
        """Crear backup RAID 10 (mirror + stripe)"""
        # Combinación de RAID 1 y RAID 0
        return await self._create_raid1_backup(backup_id)

    async def _upload_to_cloud(self, backup_files: List[Dict[str, Any]],
                              provider: str) -> List[Dict[str, Any]]:
        """Subir backups a la nube"""
        cloud_locations = []

        if provider == 'gcp':
            # Google Cloud Storage
            cloud_locations = await self._upload_to_gcs(backup_files)
        elif provider == 'aws':
            # Amazon S3
            cloud_locations = await self._upload_to_s3(backup_files)
        elif provider == 'azure':
            # Azure Blob Storage
            cloud_locations = await self._upload_to_azure(backup_files)

        return cloud_locations

    async def _upload_to_gcs(self, backup_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Subir a Google Cloud Storage"""
        # Implementar usando google-cloud-storage
        logger.info("Uploading to Google Cloud Storage")
        return [{'provider': 'gcs', 'location': 'gs://bucket/path'} for _ in backup_files]

    async def _upload_to_s3(self, backup_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Subir a Amazon S3"""
        # Implementar usando boto3
        logger.info("Uploading to Amazon S3")
        return [{'provider': 's3', 'location': 's3://bucket/path'} for _ in backup_files]

    async def _upload_to_azure(self, backup_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Subir a Azure Blob Storage"""
        # Implementar usando azure-storage-blob
        logger.info("Uploading to Azure Blob Storage")
        return [{'provider': 'azure', 'location': 'https://account.blob.core.windows.net/container/path'} for _ in backup_files]

    # Handlers HTTP
    async def handle_register(self, request):
        """Handler para registro de clientes"""
        try:
            data = await request.json()
            result = await self.register_client(data)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=400)

    async def handle_submit_analysis(self, request):
        """Handler para envío de análisis"""
        try:
            # Verificar token
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return web.json_response({'error': 'Invalid authorization'}, status=401)

            token = auth_header[7:]
            client_info = self.verify_client_token(token)
            if not client_info:
                return web.json_response({'error': 'Invalid token'}, status=401)

            data = await request.json()
            analysis = AnalysisData(
                client_id=client_info['client_id'],
                analysis_type=data['analysis_type'],
                timestamp=data['timestamp'],
                data=data['data'],
                severity=data.get('severity', 'medium')
            )

            analysis_id = await self.store_analysis(analysis)
            return web.json_response({
                'status': 'stored',
                'analysis_id': analysis_id,
                'incident_id': analysis.incident_id
            })

        except Exception as e:
            logger.error(f"Error submitting analysis: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_get_incidents(self, request):
        """Handler para obtener incidentes"""
        try:
            incidents_list = [asdict(incident) for incident in self.incidents.values()]
            return web.json_response({'incidents': incidents_list})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_websocket(self, request):
        """Handler para conexiones WebSocket"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websocket_connections.add(ws)
        logger.info("WebSocket client connected")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # Procesar mensajes del cliente
                    if data.get('type') == 'ping':
                        await ws.send(json.dumps({'type': 'pong'}))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.websocket_connections.discard(ws)
            logger.info("WebSocket client disconnected")

        return ws

    def create_app(self):
        """Crear aplicación web"""
        app = web.Application()

        # Rutas API
        app.router.add_post('/api/register', self.handle_register)
        app.router.add_post('/api/analysis', self.handle_submit_analysis)
        app.router.add_get('/api/incidents', self.handle_get_incidents)
        app.router.add_get('/ws', self.handle_websocket)

        # Servir archivos estáticos
        app.router.add_static('/', path='static', name='static')

        return app

    async def start_server(self):
        """Iniciar servidor"""
        await self.initialize_database()
        await self.initialize_redis()

        app = self.create_app()

        # Configuración SSL
        ssl_context = None
        if self.config['server']['ssl_enabled']:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(
                self.config['server']['ssl_cert'],
                self.config['server']['ssl_key']
            )

        # Iniciar servidores HTTP y HTTPS
        runner = web.AppRunner(app)
        await runner.setup()

        # Servidor HTTP
        site = web.TCPSite(runner,
                          self.config['server']['host'],
                          self.config['server']['port'])
        await site.start()
        logger.info(f"HTTP server started on {self.config['server']['host']}:{self.config['server']['port']}")

        # Servidor HTTPS si SSL está habilitado
        if ssl_context:
            ssl_site = web.TCPSite(runner,
                                  self.config['server']['host'],
                                  self.config['server']['ssl_port'],
                                  ssl_context=ssl_context)
            await ssl_site.start()
            logger.info(f"HTTPS server started on {self.config['server']['host']}:{self.config['server']['ssl_port']}")

        return runner

async def main():
    """Función principal"""
    server = SmartComputeCentralServer()
    runner = await server.start_server()

    logger.info("SmartCompute Central Server is running")
    logger.info("Press Ctrl+C to stop")

    try:
        # Mantener servidor ejecutándose
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())