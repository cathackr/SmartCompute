#!/usr/bin/env python3
"""
SmartCompute Enterprise - Real-time Local Analysis
=================================================

Ejecuta análisis completo en tiempo real del sistema SmartCompute Enterprise
incluyendo todos los nuevos módulos de seguridad implementados.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import psutil
import subprocess

# Importar monitor de procesos y motor de recomendaciones
from process_monitor import SmartComputeProcessMonitor
from security_recommendations_engine import SmartComputeSecurityRecommendationsEngine

# Agregar directorio enterprise al path
sys.path.append(str(Path(__file__).parent / "enterprise"))

# Importar módulos individualmente para mejor debugging
MODULES_AVAILABLE = {}

try:
    from smartcompute_hrm_learning_framework import SmartComputeHRMLearning, LearningContext, SecurityDomain
    MODULES_AVAILABLE['hrm_learning'] = True
except ImportError as e:
    print(f"⚠️  Error importing HRM Learning: {e}")
    MODULES_AVAILABLE['hrm_learning'] = False

try:
    from smartcompute_mitre_experimenter import SmartComputeMitreExperimenter
    MODULES_AVAILABLE['mitre_experimenter'] = True
except ImportError as e:
    print(f"⚠️  Error importing MITRE Experimenter: {e}")
    MODULES_AVAILABLE['mitre_experimenter'] = False

try:
    from smartcompute_nodejs_sandbox import SmartComputeNodeJSSandbox
    MODULES_AVAILABLE['nodejs_sandbox'] = True
except ImportError as e:
    print(f"⚠️  Error importing Node.js Sandbox: {e}")
    MODULES_AVAILABLE['nodejs_sandbox'] = False

try:
    from smartcompute_admin_authorization import SmartComputeAdminAuthorization, ChangeType, RiskLevel
    MODULES_AVAILABLE['admin_authorization'] = True
except ImportError as e:
    print(f"⚠️  Error importing Admin Authorization: {e}")
    MODULES_AVAILABLE['admin_authorization'] = False

try:
    from smartcompute_secret_manager import SmartComputeSecretManager, SecretType
    MODULES_AVAILABLE['secret_manager'] = True
except ImportError as e:
    print(f"⚠️  Error importing Secret Manager: {e}")
    MODULES_AVAILABLE['secret_manager'] = False

print(f"📦 Módulos disponibles: {sum(MODULES_AVAILABLE.values())}/{len(MODULES_AVAILABLE)}")


class SmartComputeEnterpriseAnalyzer:
    """Analizador Enterprise en tiempo real"""

    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "system": {},
            "security": {},
            "enterprise_modules": {},
            "analysis_duration": 0
        }

        # Configurar logging para mostrar en tiempo real
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def run_comprehensive_analysis(self):
        """Ejecuta análisis completo en tiempo real"""

        print("🔍 SmartCompute Enterprise - Análisis en Tiempo Real")
        print("=" * 60)
        print(f"🕐 Iniciado: {self.start_time.strftime('%H:%M:%S')}")
        print()

        try:
            # 1. Análisis del sistema base
            await self._analyze_system_health()

            # 2. Análisis de módulos enterprise
            await self._analyze_enterprise_modules()

            # 3. Test de framework HRM
            await self._test_hrm_learning()

            # 4. Test de experimentación MITRE
            await self._test_mitre_experimenter()

            # 5. Test de sandbox Node.js
            await self._test_nodejs_sandbox()

            # 6. Test de autorización admin
            await self._test_admin_authorization()

            # 7. Test de gestión de secretos
            await self._test_secret_manager()

            # 8. Generar recomendaciones de seguridad
            await self._generate_security_recommendations()

            # 9. Generar reporte final
            await self._generate_final_report()

        except Exception as e:
            self.logger.error(f"Error en análisis: {e}")

        finally:
            self.metrics["analysis_duration"] = (datetime.now() - self.start_time).total_seconds()

    async def _analyze_system_health(self):
        """Analiza salud del sistema"""
        print("📊 1. Análisis de Salud del Sistema")
        print("-" * 40)

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"   CPU: {cpu_percent}%")

        # Memoria
        memory = psutil.virtual_memory()
        print(f"   Memoria: {memory.percent}% ({memory.used // 1024 // 1024} MB / {memory.total // 1024 // 1024} MB)")

        # Disco
        disk = psutil.disk_usage('/')
        print(f"   Disco: {disk.percent}% ({disk.used // 1024 // 1024 // 1024} GB / {disk.total // 1024 // 1024 // 1024} GB)")

        # Inicializar monitor de procesos detallado
        process_monitor = SmartComputeProcessMonitor()

        # Obtener información detallada de procesos
        print("   🔍 Analizando procesos detallados...")
        filter_keywords = ['smartcompute', 'python', 'node', 'nginx', 'apache', 'mysql', 'chrome', 'firefox']
        detailed_processes = await process_monitor.get_detailed_process_info(filter_keywords)

        # Obtener conexiones de red
        network_connections = await process_monitor.get_network_overview()

        # Obtener conexiones directas de Capa 1/2
        print("   🔗 Analizando conexiones directas Capa 1/2...")
        layer12_connections = await process_monitor.get_layer12_connections()

        print(f"   Procesos monitorizados: {len(detailed_processes)}")
        print(f"   Conexiones de red: {len(network_connections)}")
        print(f"   Conexiones Capa 1/2: {len(layer12_connections)}")

        # Top procesos por CPU y memoria
        if detailed_processes:
            top_cpu = sorted(detailed_processes, key=lambda p: p.cpu_percent, reverse=True)[:3]
            top_memory = sorted(detailed_processes, key=lambda p: p.memory_mb, reverse=True)[:3]

            print("   📈 Top CPU:")
            for i, proc in enumerate(top_cpu, 1):
                print(f"      {i}. {proc.name} (PID {proc.pid}) - {proc.cpu_percent:.1f}% CPU, {proc.memory_mb:.1f} MB")

            print("   🧠 Top Memoria:")
            for i, proc in enumerate(top_memory, 1):
                print(f"      {i}. {proc.name} (PID {proc.pid}) - {proc.memory_mb:.1f} MB, {proc.cpu_percent:.1f}% CPU")

        # Puertos en escucha
        listening_ports = [conn for conn in network_connections
                          if conn.status == 'LISTEN' and conn.local_port > 0]

        if listening_ports:
            print(f"   🔌 Puertos en escucha: {len(listening_ports)}")
            for port in listening_ports[:5]:  # Mostrar primeros 5
                print(f"      {port.local_port} ({port.protocol}) - {port.process_name} (PID {port.pid})")

        self.metrics["system"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "monitored_processes": len(detailed_processes),
            "network_connections": len(network_connections),
            "listening_ports": len(listening_ports),
            "layer12_connections": len(layer12_connections),
            "process_details": [
                {
                    "pid": p.pid,
                    "name": p.name,
                    "cpu_percent": p.cpu_percent,
                    "memory_mb": p.memory_mb,
                    "cwd": p.cwd,
                    "connections": len(p.connections),
                    "open_files": len(p.open_files)
                } for p in detailed_processes
            ],
            "network_details": [
                {
                    "pid": conn.pid,
                    "process_name": conn.process_name,
                    "local_address": conn.local_address,
                    "local_port": conn.local_port,
                    "remote_address": conn.remote_address,
                    "remote_port": conn.remote_port,
                    "protocol": conn.protocol,
                    "status": conn.status,
                    "network_adapter": conn.network_adapter,
                    "channel": conn.channel,
                    "frequency": conn.frequency,
                    "connection_time": conn.connection_time,
                    "physical_port": conn.physical_port,
                    "encryption_type": conn.encryption_type,
                    "transmission_speed": conn.transmission_speed,
                    "bytes_sent": conn.bytes_sent,
                    "bytes_received": conn.bytes_received,
                    "interface_name": conn.interface_name
                } for conn in network_connections
            ],
            "layer12_details": [
                {
                    "mac_address": l12.mac_address,
                    "manufacturer": l12.manufacturer,
                    "firmware_version": l12.firmware_version,
                    "ip_requested": l12.ip_requested,
                    "dhcp_active": l12.dhcp_active,
                    "vlan_id": l12.vlan_id,
                    "vxlan_vni": l12.vxlan_vni,
                    "link_type": l12.link_type,
                    "cable_category": l12.cable_category,
                    "interface_name": l12.interface_name,
                    "port_speed": l12.port_speed,
                    "duplex_mode": l12.duplex_mode,
                    "mtu_size": l12.mtu_size,
                    "link_state": l12.link_state,
                    "last_seen": l12.last_seen,
                    "packet_count": l12.packet_count,
                    "byte_count": l12.byte_count
                } for l12 in layer12_connections
            ]
        }

        # Evaluación de salud
        health_score = 100
        if cpu_percent > 80: health_score -= 20
        if memory.percent > 85: health_score -= 20
        if disk.percent > 90: health_score -= 30

        status = "🟢 EXCELENTE" if health_score >= 90 else "🟡 BUENO" if health_score >= 70 else "🔴 CRÍTICO"
        print(f"   Estado General: {status} ({health_score}/100)")
        print()

    async def _analyze_enterprise_modules(self):
        """Analiza módulos enterprise"""
        print("🏢 2. Análisis de Módulos Enterprise")
        print("-" * 40)

        enterprise_path = Path(__file__).parent / "enterprise"
        modules = list(enterprise_path.glob("smartcompute_*.py"))

        print(f"   Módulos encontrados: {len(modules)}")

        module_status = {}
        for module in modules:
            try:
                # Verificar sintaxis básica
                with open(module, 'r') as f:
                    content = f.read()

                # Verificar imports y estructura
                has_class = "class " in content
                has_async = "async def" in content
                has_logging = "logging" in content

                status = "✅ OK"
                if not has_class: status = "⚠️  Sin clases"
                if len(content) < 1000: status = "⚠️  Muy pequeño"

                module_status[module.name] = {
                    "status": status,
                    "size_kb": len(content) // 1024,
                    "has_async": has_async,
                    "has_logging": has_logging
                }

                print(f"   {module.name}: {status}")

            except Exception as e:
                module_status[module.name] = {"status": f"❌ Error: {e}"}
                print(f"   {module.name}: ❌ Error")

        self.metrics["enterprise_modules"] = module_status
        print()

    async def _test_hrm_learning(self):
        """Test del framework HRM"""
        print("🧠 3. Test Framework HRM Learning")
        print("-" * 40)

        if not MODULES_AVAILABLE.get('hrm_learning', False):
            print("   ❌ Módulo HRM Learning no disponible")
            self.metrics["security"]["hrm_learning"] = {"error": "Module not available"}
            print()
            return

        try:
            # Crear instancia en directorio local
            local_path = str(Path.home() / "smartcompute" / "hrm_test")
            hrm = SmartComputeHRMLearning(local_path)

            print("   ✅ Framework HRM inicializado")

            # Crear contexto de prueba
            context = LearningContext(
                context_id="test_context",
                trigger_event="security_test",
                environment_data={"env": "test"},
                threat_landscape={"level": "medium"},
                business_constraints={"downtime": "minimal"},
                compliance_requirements=["SOX"],
                available_resources={"compute": "high"}
            )

            print("   ✅ Contexto de aprendizaje creado")

            # Test de aprendizaje
            implementation_data = {
                "name": "Test Security Solution",
                "description": "Test implementation for analysis",
                "domain": "threat_detection",
                "mitre_techniques": ["T1110"],
                "complexity": 5,
                "risk_level": 2,
                "success_metrics": {"effectiveness": 0.9},
                "validation_criteria": ["Test validation"],
                "rollback_plan": "Test rollback"
            }

            solution = await hrm.learn_from_successful_implementation(implementation_data, context)
            print(f"   ✅ Solución aprendida: {solution.name}")

            # Test de análisis de brecha
            threat_data = {
                "mitre_techniques": ["T1110"],
                "domain": "authentication"
            }

            solutions = await hrm.analyze_security_gap(threat_data, context)
            print(f"   ✅ Análisis de brecha: {len(solutions)} soluciones propuestas")

            self.metrics["security"]["hrm_learning"] = {
                "initialized": True,
                "solutions_learned": len(hrm.learned_solutions),
                "test_successful": True
            }

        except Exception as e:
            print(f"   ❌ Error en HRM Learning: {e}")
            self.metrics["security"]["hrm_learning"] = {"error": str(e)}

        print()

    async def _test_mitre_experimenter(self):
        """Test del experimentador MITRE"""
        print("🎯 4. Test Experimentador MITRE")
        print("-" * 40)

        if not MODULES_AVAILABLE.get('mitre_experimenter', False):
            print("   ❌ Módulo MITRE Experimenter no disponible")
            self.metrics["security"]["mitre_experimenter"] = {"error": "Module not available"}
            print()
            return

        try:
            # Crear instancia en directorio local
            local_path = str(Path.home() / "smartcompute" / "mitre_test")
            experimenter = SmartComputeMitreExperimenter(local_path)

            print("   ✅ Experimentador MITRE inicializado")
            print(f"   📚 Base de conocimiento: {len(experimenter.mitre_kb)} técnicas")

            # Crear experimento de prueba
            security_solution = {
                "rate_limit": 5,
                "window_seconds": 60,
                "block_dangerous_chars": True,
                "rollback_plan": "Test rollback available"
            }

            experiment = await experimenter.create_mitre_experiment(
                technique_id="T1110",
                security_solution=security_solution,
                environment="sandbox"
            )

            print(f"   ✅ Experimento creado: {experiment.name}")
            print(f"   🔬 Técnica MITRE: {experiment.mitre_technique_id}")
            print(f"   ⚖️  Nivel de riesgo: {experiment.security_solution}")

            # Listar experimentos
            experiments = experimenter.list_experiments()
            print(f"   📊 Total experimentos: {len(experiments)}")

            self.metrics["security"]["mitre_experimenter"] = {
                "initialized": True,
                "knowledge_base_size": len(experimenter.mitre_kb),
                "experiments_created": len(experiments),
                "test_successful": True
            }

        except Exception as e:
            print(f"   ❌ Error en MITRE Experimenter: {e}")
            self.metrics["security"]["mitre_experimenter"] = {"error": str(e)}

        print()

    async def _test_nodejs_sandbox(self):
        """Test del sandbox Node.js"""
        print("🟢 5. Test Sandbox Node.js")
        print("-" * 40)

        if not MODULES_AVAILABLE.get('nodejs_sandbox', False):
            print("   ❌ Módulo Node.js Sandbox no disponible")
            self.metrics["security"]["nodejs_sandbox"] = {"error": "Module not available"}
            print()
            return

        try:
            # Crear sandbox en directorio local
            local_path = str(Path.home() / "smartcompute" / "nodejs_test")
            sandbox = SmartComputeNodeJSSandbox(local_path)

            print("   ✅ Sandbox Node.js inicializado")

            # Verificar estado del sandbox
            info = sandbox.get_sandbox_info()
            print(f"   📁 Directorio: {Path(info['sandbox_path']).name}")
            print(f"   🔧 Estado: {'Listo' if info['is_ready'] else 'No listo'}")
            print(f"   ⚙️  Configuraciones: {len(info['available_configs'])}")

            # Verificar Node.js
            try:
                node_result = subprocess.run(['node', '--version'],
                                           capture_output=True, text=True, timeout=5)
                if node_result.returncode == 0:
                    print(f"   🟢 Node.js: {node_result.stdout.strip()}")
                    node_available = True
                else:
                    print("   🔴 Node.js: No disponible")
                    node_available = False
            except:
                print("   🔴 Node.js: No disponible")
                node_available = False

            # Test básico si está listo
            if info['is_ready'] and node_available:
                print("   🧪 Ejecutando test de seguridad básico...")

                # Configuración de test simple
                test_config = {
                    "testBruteForce": True,
                    "testInputValidation": True,
                    "testAuthentication": False,  # Simplificado para test rápido
                    "bruteForce": {
                        "maxAttempts": 3,
                        "testAttempts": 5
                    }
                }

                try:
                    result = await sandbox.run_security_test(test_config, "enterprise_analysis_test")
                    print(f"   ✅ Test completado: Score {result.security_score:.1f}%")
                    print(f"   🔍 Vulnerabilidades: {len(result.vulnerabilities_found)}")

                    test_successful = True
                except Exception as test_error:
                    print(f"   ⚠️  Test falló: {test_error}")
                    test_successful = False
            else:
                print("   ⚠️  Test de seguridad omitido (Node.js no disponible o sandbox no listo)")
                test_successful = False

            self.metrics["security"]["nodejs_sandbox"] = {
                "initialized": True,
                "ready": info['is_ready'],
                "node_available": node_available,
                "test_successful": test_successful,
                "configs_available": len(info['available_configs'])
            }

        except Exception as e:
            print(f"   ❌ Error en Node.js Sandbox: {e}")
            self.metrics["security"]["nodejs_sandbox"] = {"error": str(e)}

        print()

    async def _test_admin_authorization(self):
        """Test del sistema de autorización"""
        print("🔐 6. Test Sistema Autorización Admin")
        print("-" * 40)

        if not MODULES_AVAILABLE.get('admin_authorization', False):
            print("   ❌ Módulo Admin Authorization no disponible")
            self.metrics["security"]["admin_authorization"] = {"error": "Module not available"}
            print()
            return

        try:
            # Crear sistema en directorio local
            local_config = str(Path.home() / "smartcompute" / "admin_auth_test.yaml")
            auth_system = SmartComputeAdminAuthorization(local_config)

            print("   ✅ Sistema de autorización inicializado")
            print(f"   👥 Administradores: {len(auth_system.admins)}")

            # Registrar admin de prueba
            admin_id = auth_system.register_admin(
                username="test_admin",
                email="test@localhost",
                role="test_administrator",
                authorization_level=4
            )

            print(f"   ✅ Admin de prueba registrado: {admin_id[:8]}...")

            # Crear solicitud de prueba (solo si los enums están disponibles)
            if MODULES_AVAILABLE.get('admin_authorization', False):
                request_id = await auth_system.submit_approval_request(
                    title="Test Security Implementation",
                    description="Test implementation for enterprise analysis",
                    change_type=ChangeType.SECURITY_SOLUTION,
                    risk_level=RiskLevel.MEDIUM,
                    requested_by="enterprise_analyzer",
                    technical_details={"test": True},
                    affected_systems=["test_system"],
                    rollback_plan="Test rollback available"
                )
            else:
                # Fallback para testing básico
                print("   ⚠️  Usando valores básicos para test")
                return

            print(f"   ✅ Solicitud creada: {request_id[:8]}...")

            # Verificar estado
            status = auth_system.get_request_status(request_id)
            print(f"   📋 Estado: {status['status']}")
            print(f"   ⏳ Aprobaciones necesarias: {status['approvals_required']}")

            # Simular aprobación
            approved = await auth_system.approve_request(
                request_id=request_id,
                admin_id=admin_id,
                justification="Approved for enterprise analysis test"
            )

            if approved:
                final_status = auth_system.get_request_status(request_id)
                print(f"   ✅ Aprobación: Exitosa")
                print(f"   🎯 Estado final: {final_status['status']}")
            else:
                print("   ❌ Aprobación falló")

            self.metrics["security"]["admin_authorization"] = {
                "initialized": True,
                "admins_count": len(auth_system.admins),
                "test_approval_successful": approved,
                "requests_processed": len(auth_system.requests)
            }

        except Exception as e:
            print(f"   ❌ Error en Autorización Admin: {e}")
            self.metrics["security"]["admin_authorization"] = {"error": str(e)}

        print()

    async def _test_secret_manager(self):
        """Test del gestor de secretos"""
        print("🔑 7. Test Gestor de Secretos")
        print("-" * 40)

        if not MODULES_AVAILABLE.get('secret_manager', False):
            print("   ❌ Módulo Secret Manager no disponible")
            self.metrics["security"]["secret_manager"] = {"error": "Module not available"}
            print()
            return

        try:
            # Crear gestor en directorio local
            local_vault = str(Path.home() / "smartcompute" / "vault_test")
            secret_manager = SmartComputeSecretManager(local_vault)

            print("   ✅ Gestor de secretos inicializado")
            print(f"   🔐 Vault: {Path(local_vault).name}")

            # Almacenar secreto de prueba
            secret_id = await secret_manager.store_secret(
                name="test_api_key",
                secret_data="test_secret_value_12345",
                secret_type=SecretType.API_KEY,
                user_id="enterprise_analyzer",
                tags=["test", "analysis"]
            )

            print(f"   ✅ Secreto almacenado: {secret_id[:8]}...")

            # Recuperar secreto
            retrieved = await secret_manager.get_secret(secret_id, "enterprise_analyzer")
            if retrieved == "test_secret_value_12345":
                print("   ✅ Secreto recuperado correctamente")
                retrieval_successful = True
            else:
                print("   ❌ Error en recuperación de secreto")
                retrieval_successful = False

            # Listar secretos
            secrets_list = await secret_manager.list_secrets("enterprise_analyzer")
            print(f"   📊 Secretos totales: {len(secrets_list)}")

            # Obtener logs de acceso
            access_logs = await secret_manager.get_access_logs()
            print(f"   📝 Logs de acceso: {len(access_logs)}")

            self.metrics["security"]["secret_manager"] = {
                "initialized": True,
                "secrets_stored": len(secrets_list),
                "retrieval_successful": retrieval_successful,
                "access_logs": len(access_logs)
            }

        except Exception as e:
            print(f"   ❌ Error en Gestor de Secretos: {e}")
            self.metrics["security"]["secret_manager"] = {"error": str(e)}

        print()

    async def _generate_security_recommendations(self):
        """Genera recomendaciones de seguridad basadas en OWASP, NIST e ISO 27001"""
        print("🛡️ 8. Análisis de Recomendaciones de Seguridad")
        print("-" * 40)

        try:
            # Inicializar motor de recomendaciones
            recommendations_engine = SmartComputeSecurityRecommendationsEngine()
            print("   ✅ Motor de recomendaciones inicializado")

            # Generar recomendaciones basadas en métricas del sistema
            recommendations = recommendations_engine.analyze_system_security(self.metrics)
            print(f"   📋 Recomendaciones generadas: {len(recommendations)}")

            # Generar resumen de seguridad
            security_summary = recommendations_engine.generate_security_summary(recommendations)
            print(f"   🎯 Nivel de seguridad: {security_summary.get('security_level', 'N/A')}")
            print(f"   📊 Prioridad promedio: {security_summary.get('average_priority', 0)}")

            # Mostrar top 3 recomendaciones
            top_recommendations = security_summary.get('top_priority_recommendations', [])[:3]
            if top_recommendations:
                print("   🏆 Top 3 Recomendaciones:")
                for i, rec in enumerate(top_recommendations, 1):
                    print(f"      {i}. [{rec.framework.value}] {rec.title}")
                    print(f"         Riesgo: {rec.risk_level.value} | Prioridad: {rec.priority_score}")

            # Mostrar distribución por frameworks
            framework_dist = security_summary.get('framework_distribution', {})
            print("   📈 Distribución por Framework:")
            for framework, count in framework_dist.items():
                if count > 0:
                    print(f"      {framework}: {count} recomendaciones")

            # Almacenar en métricas para el reporte
            self.metrics["security_recommendations"] = {
                "recommendations": [
                    {
                        "id": rec.id,
                        "title": rec.title,
                        "description": rec.description,
                        "framework": rec.framework.value,
                        "category": rec.category.value,
                        "risk_level": rec.risk_level.value,
                        "impact": rec.impact,
                        "implementation_effort": rec.implementation_effort,
                        "compliance_references": rec.compliance_references,
                        "technical_details": rec.technical_details,
                        "remediation_steps": rec.remediation_steps,
                        "priority_score": rec.priority_score,
                        "affected_assets": rec.affected_assets
                    } for rec in recommendations
                ],
                "summary": security_summary
            }

        except Exception as e:
            print(f"   ❌ Error generando recomendaciones: {e}")
            self.metrics["security_recommendations"] = {
                "error": str(e),
                "recommendations": [],
                "summary": {}
            }

        print()

    async def _generate_final_report(self):
        """Genera reporte final del análisis"""
        print("📋 9. Reporte Final del Análisis")
        print("-" * 40)

        analysis_duration = (datetime.now() - self.start_time).total_seconds()

        # Calcular score general
        total_tests = 0
        successful_tests = 0

        for category, data in self.metrics["security"].items():
            if isinstance(data, dict):
                total_tests += 1
                if data.get("test_successful") or data.get("initialized"):
                    successful_tests += 1

        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"   🕐 Duración total: {analysis_duration:.1f} segundos")
        print(f"   📊 Tests ejecutados: {total_tests}")
        print(f"   ✅ Tests exitosos: {successful_tests}")
        print(f"   📈 Tasa de éxito: {success_rate:.1f}%")

        # Estado del sistema
        system_health = "🟢 EXCELENTE"
        if self.metrics["system"]["cpu_percent"] > 80:
            system_health = "🟡 MODERADO"
        if self.metrics["system"]["memory_percent"] > 85:
            system_health = "🔴 CRÍTICO"

        print(f"   🏥 Salud del sistema: {system_health}")

        # Estado de seguridad
        security_modules_ok = sum(1 for data in self.metrics["security"].values()
                                if isinstance(data, dict) and not data.get("error"))
        security_score = (security_modules_ok / len(self.metrics["security"]) * 100) if self.metrics["security"] else 0

        security_status = "🟢 SEGURO" if security_score >= 80 else "🟡 ACEPTABLE" if security_score >= 60 else "🔴 CRÍTICO"
        print(f"   🛡️  Estado de seguridad: {security_status} ({security_score:.1f}%)")

        # Módulos enterprise
        enterprise_modules_ok = sum(1 for data in self.metrics["enterprise_modules"].values()
                                  if "✅" in str(data.get("status", "")))
        enterprise_score = (enterprise_modules_ok / len(self.metrics["enterprise_modules"]) * 100) if self.metrics["enterprise_modules"] else 0

        print(f"   🏢 Módulos Enterprise: {enterprise_modules_ok}/{len(self.metrics['enterprise_modules'])} ({enterprise_score:.1f}%)")

        # Guardar reporte detallado
        report_path = Path.home() / "smartcompute" / f"enterprise_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)

        detailed_report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": analysis_duration,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "system_health": system_health,
                "security_status": security_status,
                "security_score": security_score,
                "enterprise_score": enterprise_score
            },
            "metrics": self.metrics
        }

        with open(report_path, 'w') as f:
            json.dump(detailed_report, f, indent=2, default=str)

        print(f"   💾 Reporte guardado: {report_path.name}")
        print()

        # Actualizar estado en claude_inc
        await self._update_claude_inc(detailed_report)

    async def _update_claude_inc(self, report: Dict[str, Any]):
        """Actualiza el archivo claude_inc con resultados del análisis"""
        try:
            claude_inc_path = Path(__file__).parent / "claude_inc"

            if claude_inc_path.exists():
                with open(claude_inc_path, 'r') as f:
                    content = f.read()

                # Agregar sección de último análisis
                analysis_section = f"""

## 🔬 Último Análisis Enterprise (Tiempo Real)
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duración**: {report['analysis_duration_seconds']:.1f}s
**Estado General**: {report['summary']['security_status']}

### Resultados:
- ✅ Tests exitosos: {report['summary']['successful_tests']}/{report['summary']['total_tests']} ({report['summary']['success_rate']:.1f}%)
- 🏥 Salud del sistema: {report['summary']['system_health']}
- 🛡️  Score de seguridad: {report['summary']['security_score']:.1f}%
- 🏢 Módulos Enterprise: {report['summary']['enterprise_score']:.1f}%

### Módulos Probados:
"""

                for module, status in report['metrics']['security'].items():
                    if isinstance(status, dict):
                        icon = "✅" if not status.get("error") else "❌"
                        analysis_section += f"- {icon} {module.replace('_', ' ').title()}\n"

                # Remover sección anterior si existe
                if "## 🔬 Último Análisis Enterprise" in content:
                    content = content.split("## 🔬 Último Análisis Enterprise")[0]

                # Agregar nueva sección
                content += analysis_section

                with open(claude_inc_path, 'w') as f:
                    f.write(content)

                print(f"   📝 claude_inc actualizado con resultados")

        except Exception as e:
            print(f"   ⚠️  Error actualizando claude_inc: {e}")

        # Generar reportes HTML automáticamente y abrir en navegador
        await self._generate_html_reports()

    async def _generate_html_reports(self):
        """Genera reportes HTML automáticamente"""
        try:
            from generate_html_reports import SmartComputeHTMLReportGenerator

            # Buscar el último reporte JSON
            reports_dir = Path.home() / "smartcompute"
            json_reports = list(reports_dir.glob("enterprise_analysis_*.json"))

            if json_reports:
                latest_report = max(json_reports, key=lambda p: p.stat().st_mtime)

                html_generator = SmartComputeHTMLReportGenerator()

                # Generar y abrir reporte principal automáticamente
                html_path = html_generator.generate_enterprise_analysis_html(str(latest_report), auto_open=True)
                print(f"   🌐 Reporte HTML generado y abierto: {Path(html_path).name}")

                # Generar HTML del reporte de seguridad (sin abrir automáticamente)
                security_report = Path(__file__).parent / "REPORTE_SEGURIDAD_SMARTCOMPUTE.md"
                if security_report.exists():
                    security_html = html_generator.generate_security_report_html(str(security_report), auto_open=False)
                    if security_html:
                        print(f"   🔒 Reporte seguridad HTML: {Path(security_html).name}")

        except Exception as e:
            print(f"   ⚠️  Error generando HTML: {e}")


async def main():
    """Función principal"""
    print("🚀 Iniciando SmartCompute Enterprise Analysis...")
    print()

    analyzer = SmartComputeEnterpriseAnalyzer()
    await analyzer.run_comprehensive_analysis()

    print("🎉 Análisis SmartCompute Enterprise Completado!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())