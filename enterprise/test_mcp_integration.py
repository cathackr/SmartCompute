#!/usr/bin/env python3
"""
Test Suite para MCP + HRM Integration
Suite completa de tests para validar la integración Enterprise
"""

import asyncio
import json
import pytest
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import websockets
from unittest.mock import Mock, patch

# Importar módulos a testear
from mcp_hrm_bridge import create_mcp_hrm_bridge, MCPRequest, MCPResponse
from mcp_enterprise_orchestrator import create_mcp_enterprise_orchestrator, ScalingAction
from mcp_server import MCPServer

# Configurar logging para tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMCPHRMBridge:
    """Tests para el puente MCP-HRM"""

    @pytest.fixture
    def bridge(self):
        """Fixture para crear bridge de prueba"""
        config = {
            "log_level": "DEBUG",
            "enterprise_mode": True
        }
        return create_mcp_hrm_bridge(config)

    @pytest.mark.asyncio
    async def test_health_check(self, bridge):
        """Test health check básico"""
        request = MCPRequest(
            method="smartcompute/health_check",
            params={}
        )

        response = await bridge.handle_mcp_request(request)

        assert response.error is None
        assert response.result is not None
        assert response.result["status"] == "healthy"
        assert "components" in response.result

    @pytest.mark.asyncio
    async def test_threat_analysis_basic(self, bridge):
        """Test análisis de amenaza básico"""
        test_event = {
            "event_id": "test_001",
            "timestamp": datetime.now().isoformat(),
            "event_type": "process_injection",
            "source_ip": "192.168.1.100",
            "target_process": "explorer.exe"
        }

        request = MCPRequest(
            method="smartcompute/analyze_threat",
            params={"event": test_event}
        )

        response = await bridge.handle_mcp_request(request)

        assert response.error is None
        assert response.result is not None
        assert "analysis_timestamp" in response.result
        assert "routing_recommendations" in response.result

    @pytest.mark.asyncio
    async def test_threat_analysis_with_business_context(self, bridge):
        """Test análisis con contexto empresarial"""
        test_event = {
            "event_id": "test_enterprise_001",
            "event_type": "advanced_persistent_threat",
            "severity": "high"
        }

        business_context = {
            "business_unit": "finance",
            "compliance_frameworks": ["SOX", "PCI-DSS"],
            "asset_criticality": "critical",
            "risk_tolerance": "low",
            "user_privileges": "admin"
        }

        request = MCPRequest(
            method="smartcompute/analyze_threat",
            params={
                "event": test_event,
                "business_context": business_context
            }
        )

        response = await bridge.handle_mcp_request(request)

        assert response.error is None
        assert response.result is not None
        assert "enterprise_actions" in response.result
        assert len(response.result["enterprise_actions"]) > 0

        # Verificar acciones específicas para contexto crítico
        actions = response.result["enterprise_actions"]
        action_types = [action["action"] for action in actions]
        assert "enhanced_logging" in action_types

    @pytest.mark.asyncio
    async def test_enterprise_context_analysis(self, bridge):
        """Test análisis de contexto empresarial"""
        request = MCPRequest(
            method="smartcompute/enterprise_context",
            params={
                "business_unit": "healthcare",
                "compliance_frameworks": ["HIPAA", "HITECH"],
                "risk_tolerance": "very_low",
                "asset_criticality": "critical"
            }
        )

        response = await bridge.handle_mcp_request(request)

        assert response.error is None
        assert response.result is not None
        assert "enterprise_context" in response.result
        assert "compliance_requirements" in response.result

    @pytest.mark.asyncio
    async def test_stream_events_processing(self, bridge):
        """Test procesamiento de eventos en stream"""
        test_events = [
            {"event_id": "stream_001", "event_type": "malware_detection"},
            {"event_id": "stream_002", "event_type": "network_intrusion"},
            {"event_id": "stream_003", "event_type": "data_exfiltration"}
        ]

        request = MCPRequest(
            method="smartcompute/stream_events",
            params={
                "events": test_events,
                "stream_config": {"batch_size": 10}
            }
        )

        response = await bridge.handle_mcp_request(request)

        assert response.error is None
        assert response.result is not None
        assert "processed_events" in response.result
        assert len(response.result["processed_events"]) == 3

    @pytest.mark.asyncio
    async def test_metrics_retrieval(self, bridge):
        """Test obtención de métricas"""
        # Generar algunas métricas primero
        await self.test_threat_analysis_basic(bridge)

        request = MCPRequest(
            method="smartcompute/get_metrics",
            params={}
        )

        response = await bridge.handle_mcp_request(request)

        assert response.error is None
        assert response.result is not None
        assert "bridge_metrics" in response.result
        assert response.result["bridge_metrics"]["requests_processed"] > 0

    @pytest.mark.asyncio
    async def test_invalid_method(self, bridge):
        """Test manejo de método inválido"""
        request = MCPRequest(
            method="invalid/method",
            params={}
        )

        response = await bridge.handle_mcp_request(request)

        assert response.error is not None
        assert response.error["code"] == -32603

class TestMCPEnterpriseOrchestrator:
    """Tests para el orquestador Enterprise"""

    @pytest.fixture
    def orchestrator_config(self):
        """Configuración de prueba para orquestador"""
        return {
            "regions": {
                "us-east-1": {"primary": True, "capacity": 5},
                "eu-west-1": {"primary": False, "capacity": 3}
            },
            "node_types": {
                "standard": {"min_instances": 1, "max_instances": 3},
                "threat_analysis": {"min_instances": 1, "max_instances": 2}
            },
            "scaling_thresholds": {
                "cpu_threshold": 70.0,
                "threat_queue_threshold": 10
            }
        }

    @pytest.fixture
    def orchestrator(self, orchestrator_config):
        """Fixture para crear orquestador de prueba"""
        return create_mcp_enterprise_orchestrator(orchestrator_config)

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test inicialización del orquestador"""
        assert orchestrator is not None
        assert len(orchestrator.enterprise_nodes) == 2  # 2 regiones
        assert "us-east-1" in orchestrator.enterprise_nodes
        assert "eu-west-1" in orchestrator.enterprise_nodes

    @pytest.mark.asyncio
    async def test_orchestrator_start_stop(self, orchestrator):
        """Test inicio y parada del orquestador"""
        await orchestrator.start_orchestration()
        assert orchestrator.is_running is True

        await orchestrator.stop_orchestration()
        assert orchestrator.is_running is False

    @pytest.mark.asyncio
    async def test_enterprise_threat_processing(self, orchestrator):
        """Test procesamiento completo de amenaza empresarial"""
        await orchestrator.start_orchestration()

        threat_event = {
            "event_id": "orch_test_001",
            "event_type": "advanced_persistent_threat",
            "severity": "critical",
            "target_system": "financial_server"
        }

        business_context = {
            "business_unit": "finance",
            "compliance_frameworks": ["SOX"],
            "asset_criticality": "critical",
            "risk_tolerance": "very_low"
        }

        result = await orchestrator.process_enterprise_threat(
            threat_event, business_context
        )

        assert result is not None
        assert "orchestration_id" in result
        assert "threat_analysis" in result
        assert "routing_decision" in result
        assert "scaling_decision" in result
        assert "business_impact_assessment" in result

        await orchestrator.stop_orchestration()

    @pytest.mark.asyncio
    async def test_scaling_decision_critical_threat(self, orchestrator):
        """Test decisión de escalado para amenaza crítica"""
        await orchestrator.start_orchestration()

        # Simular análisis HRM con amenaza crítica
        mock_hrm_analysis = {
            "hrm_analysis": {
                "final_assessment": {
                    "threat_level": "CRITICAL",
                    "confidence": 0.90
                },
                "analysis_modules": {
                    "ml_false_positive": {"score": 0.1}
                }
            }
        }

        business_context = {
            "business_unit": "finance",
            "asset_criticality": "critical"
        }

        scaling_decision = await orchestrator._make_scaling_decision(
            mock_hrm_analysis, business_context
        )

        assert scaling_decision.action == ScalingAction.EMERGENCY_SCALE
        assert scaling_decision.target_instances > 0
        assert scaling_decision.execution_priority <= 2

        await orchestrator.stop_orchestration()

    @pytest.mark.asyncio
    async def test_intelligent_routing(self, orchestrator):
        """Test enrutamiento inteligente"""
        await orchestrator.start_orchestration()

        mock_hrm_analysis = {
            "hrm_analysis": {
                "final_assessment": {"threat_level": "HIGH"},
                "analysis_modules": {
                    "threat_intelligence": {"category": "apt"}
                }
            }
        }

        business_context = {"business_unit": "finance"}

        routing_decision = await orchestrator._make_intelligent_routing_decision(
            mock_hrm_analysis, business_context
        )

        assert routing_decision is not None
        assert routing_decision.target_node is not None
        assert len(routing_decision.fallback_nodes) > 0

        await orchestrator.stop_orchestration()

    @pytest.mark.asyncio
    async def test_orchestrator_status(self, orchestrator):
        """Test obtención de estado del orquestador"""
        await orchestrator.start_orchestration()

        status = await orchestrator.get_orchestrator_status()

        assert status is not None
        assert "orchestrator_status" in status
        assert "regions" in status
        assert "performance_metrics" in status
        assert status["orchestrator_status"] == "running"

        await orchestrator.stop_orchestration()

class TestMCPServer:
    """Tests para el servidor MCP"""

    @pytest.fixture
    def server_config(self):
        """Configuración de prueba para servidor"""
        return {
            "host": "localhost",
            "port": 8081,  # Puerto diferente para tests
            "max_connections": 10,
            "enable_orchestrator": False,  # Deshabilitado para tests rápidos
            "log_level": "DEBUG"
        }

    @pytest.fixture
    def server(self, server_config):
        """Fixture para crear servidor de prueba"""
        return MCPServer(server_config)

    def test_server_initialization(self, server):
        """Test inicialización del servidor"""
        assert server is not None
        assert server.config["port"] == 8081
        assert "smartcompute_extensions" in server.server_info["capabilities"]

    @pytest.mark.asyncio
    async def test_mcp_message_validation(self, server):
        """Test validación de mensajes MCP"""
        # Mensaje válido
        valid_message = {
            "jsonrpc": "2.0",
            "method": "test",
            "id": "1"
        }
        assert server._validate_mcp_message(valid_message) is True

        # Mensaje inválido - sin jsonrpc
        invalid_message = {"method": "test"}
        assert server._validate_mcp_message(invalid_message) is False

        # Mensaje inválido - jsonrpc incorrecto
        invalid_message = {"jsonrpc": "1.0", "method": "test"}
        assert server._validate_mcp_message(invalid_message) is False

    @pytest.mark.asyncio
    async def test_initialize_method(self, server):
        """Test método de inicialización MCP"""
        params = {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "Test Client",
                "version": "1.0.0"
            }
        }

        response = await server._handle_initialize(params, "test-id")

        assert response.error is None
        assert response.result is not None
        assert response.result["protocolVersion"] == "2024-11-05"
        assert "capabilities" in response.result

class TestIntegrationEnd2End:
    """Tests de integración end-to-end"""

    @pytest.mark.asyncio
    async def test_full_enterprise_workflow(self):
        """Test workflow completo Enterprise"""
        # 1. Crear componentes
        bridge = create_mcp_hrm_bridge()
        orchestrator = create_mcp_enterprise_orchestrator({
            "regions": {"us-east-1": {"primary": True, "capacity": 3}},
            "enable_orchestrator": True
        })

        await orchestrator.start_orchestration()

        # 2. Simular amenaza empresarial completa
        threat_event = {
            "event_id": "e2e_test_001",
            "timestamp": datetime.now().isoformat(),
            "event_type": "data_breach_attempt",
            "severity": "critical",
            "affected_systems": ["customer_db", "payment_processor"],
            "attack_vector": "sql_injection",
            "source_ip": "10.0.0.50"
        }

        business_context = {
            "business_unit": "finance",
            "compliance_frameworks": ["SOX", "PCI-DSS"],
            "asset_criticality": "critical",
            "risk_tolerance": "zero",
            "user_privileges": "admin",
            "business_hours": "active"
        }

        # 3. Procesamiento completo
        start_time = time.time()

        # Análisis HRM via bridge
        analysis_request = MCPRequest(
            method="smartcompute/analyze_threat",
            params={
                "event": threat_event,
                "business_context": business_context
            }
        )

        bridge_response = await bridge.handle_mcp_request(analysis_request)
        assert bridge_response.error is None

        # Orquestación completa
        orchestration_result = await orchestrator.process_enterprise_threat(
            threat_event, business_context
        )

        processing_time = time.time() - start_time

        # 4. Validaciones end-to-end
        assert orchestration_result is not None
        assert "orchestration_id" in orchestration_result
        assert processing_time < 5.0  # Debe completarse en menos de 5 segundos

        # Validar decisiones tomadas
        scaling_decision = orchestration_result["scaling_decision"]
        assert scaling_decision["action"] in ["emergency_scale", "scale_up"]

        routing_decision = orchestration_result["routing_decision"]
        assert routing_decision["target_node"] is not None

        business_impact = orchestration_result["business_impact_assessment"]
        assert business_impact["impact_level"] in ["CRITICAL", "HIGH"]

        await orchestrator.stop_orchestration()

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance bajo carga"""
        bridge = create_mcp_hrm_bridge()

        # Generar múltiples requests concurrentes
        concurrent_requests = 20
        requests = []

        for i in range(concurrent_requests):
            request = MCPRequest(
                method="smartcompute/analyze_threat",
                params={
                    "event": {
                        "event_id": f"load_test_{i}",
                        "event_type": "malware_detection"
                    }
                }
            )
            requests.append(bridge.handle_mcp_request(request))

        start_time = time.time()
        responses = await asyncio.gather(*requests)
        total_time = time.time() - start_time

        # Validaciones de performance
        assert len(responses) == concurrent_requests
        assert all(response.error is None for response in responses)
        assert total_time < 10.0  # Todos los requests en menos de 10 segundos

        # Verificar métricas
        metrics_request = MCPRequest(method="smartcompute/get_metrics")
        metrics_response = await bridge.handle_mcp_request(metrics_request)

        metrics = metrics_response.result["bridge_metrics"]
        assert metrics["requests_processed"] >= concurrent_requests
        assert metrics["average_response_time"] < 1.0  # Menos de 1 segundo promedio

class TestErrorHandling:
    """Tests para manejo de errores"""

    @pytest.mark.asyncio
    async def test_invalid_threat_data(self):
        """Test manejo de datos de amenaza inválidos"""
        bridge = create_mcp_hrm_bridge()

        # Datos inválidos
        request = MCPRequest(
            method="smartcompute/analyze_threat",
            params={"event": None}  # Evento nulo
        )

        response = await bridge.handle_mcp_request(request)
        # Debe manejar gracefully, no fallar
        assert response is not None

    @pytest.mark.asyncio
    async def test_orchestrator_resilience(self):
        """Test resistencia del orquestador ante fallos"""
        orchestrator = create_mcp_enterprise_orchestrator()
        await orchestrator.start_orchestration()

        # Simular múltiples fallos
        try:
            # Threat event malformado
            result1 = await orchestrator.process_enterprise_threat(
                {}, {}  # Datos vacíos
            )
            assert result1 is not None  # Debe manejar gracefully

            # Business context inválido
            result2 = await orchestrator.process_enterprise_threat(
                {"event_id": "test"},
                {"invalid_field": "invalid_value"}
            )
            assert result2 is not None

        finally:
            await orchestrator.stop_orchestration()

def run_manual_tests():
    """Ejecutar tests manuales básicos"""
    print("🧪 Ejecutando tests manuales...")

    async def manual_test():
        # Test 1: Bridge básico
        print("1. Testing MCP-HRM Bridge...")
        bridge = create_mcp_hrm_bridge()

        request = MCPRequest(
            method="smartcompute/health_check",
            params={}
        )
        response = await bridge.handle_mcp_request(request)
        print(f"   Health Check: {'✅ OK' if response.error is None else '❌ FAIL'}")

        # Test 2: Orchestrator básico
        print("2. Testing Enterprise Orchestrator...")
        orchestrator = create_mcp_enterprise_orchestrator()
        await orchestrator.start_orchestration()

        status = await orchestrator.get_orchestrator_status()
        print(f"   Orchestrator Status: {'✅ OK' if status else '❌ FAIL'}")

        await orchestrator.stop_orchestration()

        # Test 3: Workflow completo
        print("3. Testing Complete Workflow...")
        test_threat = {
            "event_id": "manual_test",
            "event_type": "test_threat"
        }
        test_context = {
            "business_unit": "test"
        }

        await orchestrator.start_orchestration()
        result = await orchestrator.process_enterprise_threat(test_threat, test_context)
        print(f"   Complete Workflow: {'✅ OK' if result else '❌ FAIL'}")
        await orchestrator.stop_orchestration()

        print("✅ Tests manuales completados")

    asyncio.run(manual_test())

if __name__ == "__main__":
    # Ejecutar tests manuales si se ejecuta directamente
    run_manual_tests()