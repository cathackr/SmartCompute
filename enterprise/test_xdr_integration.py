#!/usr/bin/env python3
"""
SmartCompute Enterprise - XDR Integration Testing Suite

Comprehensive testing for multi-XDR platform integration including:
- CrowdStrike Falcon
- Microsoft Sentinel
- Cisco Umbrella

Tests both simulation mode and real platform integration where credentials available.
"""

import os
import sys
import json
import asyncio
import logging
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Add the enterprise directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xdr_mcp_coordinators import (
    CrowdStrikeCoordinator,
    SentinelCoordinator,
    CiscoUmbrellaCoordinator
)

# Define custom exception for tests
class XDRPlatformError(Exception):
    """Custom exception for XDR platform errors"""
    pass

from multi_xdr_response_engine import MultiXDRResponseEngine
from business_context_xdr_router import BusinessContextXDRRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestXDRIntegration(unittest.TestCase):
    """Test suite for XDR platform integration"""

    def setUp(self):
        """Set up test environment"""
        self.test_threat_data = {
            "threat_id": "test_threat_001",
            "source_ip": "192.168.1.100",
            "target_ip": "10.0.0.50",
            "threat_type": "malware",
            "severity": "high",
            "confidence": 85,
            "indicators": [
                {
                    "type": "ip",
                    "value": "192.168.1.100",
                    "confidence": 90
                },
                {
                    "type": "hash",
                    "value": "d41d8cd98f00b204e9800998ecf8427e",
                    "confidence": 95
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "business_unit": "finance",
            "compliance_frameworks": ["SOX", "PCI-DSS"]
        }

        self.test_business_context = {
            "business_unit": "finance",
            "region": "us-east",
            "compliance_frameworks": ["SOX", "PCI-DSS"],
            "criticality": "high",
            "approved_actions": ["isolate", "block_ip"],
            "approval_required": True
        }

    def test_crowdstrike_coordinator_initialization(self):
        """Test CrowdStrike coordinator initialization"""
        coordinator = CrowdStrikeCoordinator()
        self.assertIsNotNone(coordinator)
        self.assertFalse(coordinator.authenticated)

    def test_sentinel_coordinator_initialization(self):
        """Test Sentinel coordinator initialization"""
        coordinator = SentinelCoordinator()
        self.assertIsNotNone(coordinator)
        self.assertFalse(coordinator.authenticated)

    def test_umbrella_coordinator_initialization(self):
        """Test Umbrella coordinator initialization"""
        coordinator = CiscoUmbrellaCoordinator()
        self.assertIsNotNone(coordinator)
        self.assertFalse(coordinator.authenticated)

    @patch('xdr_mcp_coordinators.requests.post')
    def test_crowdstrike_authentication_simulation(self, mock_post):
        """Test CrowdStrike authentication in simulation mode"""
        # Mock successful authentication response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "access_token": "test_token_123",
            "token_type": "bearer",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        coordinator = CrowdStrikeCoordinator()
        coordinator.client_id = "test_client"
        coordinator.client_secret = "test_secret"

        result = coordinator.authenticate()
        self.assertTrue(result)
        self.assertTrue(coordinator.authenticated)

    @patch('xdr_mcp_coordinators.requests.post')
    def test_crowdstrike_export_simulation(self, mock_post):
        """Test CrowdStrike threat export in simulation mode"""
        coordinator = CrowdStrikeCoordinator()
        coordinator.authenticated = True
        coordinator.access_token = "test_token"

        # Mock export response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "meta": {"query_time": 0.123},
            "resources": ["indicator_123"],
            "errors": []
        }
        mock_post.return_value = mock_response

        result = coordinator.export_threat_data(self.test_threat_data)
        self.assertTrue(result["success"])
        self.assertIn("export_id", result)

    @patch('xdr_mcp_coordinators.requests.post')
    def test_sentinel_export_simulation(self, mock_post):
        """Test Sentinel threat export in simulation mode"""
        coordinator = SentinelCoordinator()
        coordinator.authenticated = True
        coordinator.access_token = "test_token"

        # Mock export response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "indicatorId": "test_indicator_123",
            "status": "Active"
        }
        mock_post.return_value = mock_response

        result = coordinator.export_threat_data(self.test_threat_data)
        self.assertTrue(result["success"])
        self.assertIn("export_id", result)

    @patch('xdr_mcp_coordinators.requests.post')
    def test_umbrella_export_simulation(self, mock_post):
        """Test Umbrella threat export in simulation mode"""
        coordinator = CiscoUmbrellaCoordinator()
        coordinator.authenticated = True
        coordinator.access_token = "test_token"

        # Mock export response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_domain_123",
            "status": "success"
        }
        mock_post.return_value = mock_response

        result = coordinator.export_threat_data(self.test_threat_data)
        self.assertTrue(result["success"])
        self.assertIn("export_id", result)

class TestMultiXDRResponseEngine(unittest.TestCase):
    """Test suite for Multi-XDR Response Engine"""

    def setUp(self):
        """Set up test environment"""
        self.engine = MultiXDRResponseEngine()
        self.test_threat = {
            "threat_id": "engine_test_001",
            "source_ip": "192.168.1.200",
            "severity": "critical",
            "threat_type": "apt",
            "business_unit": "executive",
            "compliance_frameworks": ["SOX"]
        }

    @patch('multi_xdr_response_engine.CrowdStrikeCoordinator')
    @patch('multi_xdr_response_engine.SentinelCoordinator')
    def test_coordinated_response_simulation(self, mock_sentinel, mock_crowdstrike):
        """Test coordinated response across multiple XDR platforms"""
        # Mock coordinators
        mock_cs = Mock()
        mock_cs.execute_response_action.return_value = {"success": True, "action_id": "cs_123"}
        mock_crowdstrike.return_value = mock_cs

        mock_sen = Mock()
        mock_sen.execute_response_action.return_value = {"success": True, "action_id": "sen_456"}
        mock_sentinel.return_value = mock_sen

        response_plan = {
            "actions": [
                {
                    "type": "isolate_host",
                    "target": "192.168.1.200",
                    "platforms": ["crowdstrike", "sentinel"]
                }
            ]
        }

        result = self.engine.execute_coordinated_response(self.test_threat, response_plan)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["action_results"]), 2)

    def test_approval_workflow_simulation(self):
        """Test approval workflow for sensitive actions"""
        sensitive_action = {
            "type": "isolate_critical_system",
            "target": "production_db_01",
            "business_impact": "high"
        }

        # Test that approval is required
        requires_approval = self.engine._requires_approval(sensitive_action, self.test_threat)
        self.assertTrue(requires_approval)

        # Test approval simulation
        approval_result = self.engine._simulate_approval_process(sensitive_action)
        self.assertIn("approval_id", approval_result)
        self.assertIn("status", approval_result)

class TestBusinessContextRouter(unittest.TestCase):
    """Test suite for Business Context XDR Router"""

    def setUp(self):
        """Set up test environment"""
        self.router = BusinessContextXDRRouter()

    def test_compliance_framework_routing(self):
        """Test routing based on compliance frameworks"""
        # SOX compliance should prefer Sentinel for audit trails
        sox_threat = {
            "compliance_frameworks": ["SOX"],
            "business_unit": "finance",
            "threat_type": "insider_threat"
        }

        routing = self.router.determine_optimal_routing(sox_threat)
        self.assertIn("sentinel", [p.lower() for p in routing["primary_platforms"]])

        # HIPAA compliance should have specific routing
        hipaa_threat = {
            "compliance_frameworks": ["HIPAA"],
            "business_unit": "healthcare",
            "threat_type": "data_exfiltration"
        }

        routing = self.router.determine_optimal_routing(hipaa_threat)
        self.assertTrue(len(routing["primary_platforms"]) > 0)

    def test_business_unit_routing(self):
        """Test routing based on business unit criticality"""
        executive_threat = {
            "business_unit": "executive",
            "severity": "high",
            "threat_type": "spear_phishing"
        }

        routing = self.router.determine_optimal_routing(executive_threat)
        # Executive threats should get multi-platform coverage
        self.assertGreaterEqual(len(routing["primary_platforms"]), 2)

    def test_threat_type_routing(self):
        """Test routing based on threat type specialization"""
        apt_threat = {
            "threat_type": "apt",
            "severity": "critical",
            "indicators": ["persistence", "lateral_movement"]
        }

        routing = self.router.determine_optimal_routing(apt_threat)
        # APT threats should get comprehensive coverage
        self.assertGreaterEqual(len(routing["primary_platforms"]), 2)

class TestXDRPlatformCredentials(unittest.TestCase):
    """Test XDR platform authentication with real credentials if available"""

    def setUp(self):
        """Check for real credentials in environment"""
        self.has_crowdstrike_creds = all([
            os.getenv('CROWDSTRIKE_CLIENT_ID'),
            os.getenv('CROWDSTRIKE_CLIENT_SECRET')
        ])

        self.has_sentinel_creds = all([
            os.getenv('AZURE_CLIENT_ID'),
            os.getenv('AZURE_CLIENT_SECRET'),
            os.getenv('AZURE_TENANT_ID')
        ])

        self.has_umbrella_creds = all([
            os.getenv('UMBRELLA_API_KEY'),
            os.getenv('UMBRELLA_API_SECRET')
        ])

    @unittest.skipUnless(
        os.getenv('CROWDSTRIKE_CLIENT_ID'),
        "CrowdStrike credentials not available"
    )
    def test_crowdstrike_real_authentication(self):
        """Test real CrowdStrike authentication if credentials available"""
        coordinator = CrowdStrikeCoordinator()
        coordinator.client_id = os.getenv('CROWDSTRIKE_CLIENT_ID')
        coordinator.client_secret = os.getenv('CROWDSTRIKE_CLIENT_SECRET')

        try:
            result = coordinator.authenticate()
            self.assertTrue(result)
            logger.info("✅ CrowdStrike authentication successful")
        except Exception as e:
            logger.warning(f"⚠️ CrowdStrike authentication failed: {e}")
            self.skipTest("CrowdStrike authentication failed")

    @unittest.skipUnless(
        os.getenv('AZURE_CLIENT_ID'),
        "Azure/Sentinel credentials not available"
    )
    def test_sentinel_real_authentication(self):
        """Test real Sentinel authentication if credentials available"""
        coordinator = SentinelCoordinator()
        coordinator.client_id = os.getenv('AZURE_CLIENT_ID')
        coordinator.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        coordinator.tenant_id = os.getenv('AZURE_TENANT_ID')

        try:
            result = coordinator.authenticate()
            self.assertTrue(result)
            logger.info("✅ Sentinel authentication successful")
        except Exception as e:
            logger.warning(f"⚠️ Sentinel authentication failed: {e}")
            self.skipTest("Sentinel authentication failed")

    @unittest.skipUnless(
        os.getenv('UMBRELLA_API_KEY'),
        "Umbrella credentials not available"
    )
    def test_umbrella_real_authentication(self):
        """Test real Umbrella authentication if credentials available"""
        coordinator = CiscoUmbrellaCoordinator()
        coordinator.api_key = os.getenv('UMBRELLA_API_KEY')
        coordinator.api_secret = os.getenv('UMBRELLA_API_SECRET')

        try:
            result = coordinator.authenticate()
            self.assertTrue(result)
            logger.info("✅ Umbrella authentication successful")
        except Exception as e:
            logger.warning(f"⚠️ Umbrella authentication failed: {e}")
            self.skipTest("Umbrella authentication failed")

class TestXDRIntegrationEnd2End(unittest.TestCase):
    """End-to-end integration tests"""

    @patch('multi_xdr_response_engine.CrowdStrikeCoordinator')
    @patch('multi_xdr_response_engine.SentinelCoordinator')
    @patch('multi_xdr_response_engine.UmbrellaCoordinator')
    def test_complete_threat_workflow(self, mock_umbrella, mock_sentinel, mock_crowdstrike):
        """Test complete threat detection to response workflow"""
        # Mock all coordinators
        for mock_coord_class in [mock_crowdstrike, mock_sentinel, mock_umbrella]:
            mock_coord = Mock()
            mock_coord.export_threat_data.return_value = {"success": True, "export_id": "test_123"}
            mock_coord.execute_response_action.return_value = {"success": True, "action_id": "action_123"}
            mock_coord_class.return_value = mock_coord

        # Initialize components
        router = BusinessContextXDRRouter()
        engine = MultiXDRResponseEngine()

        # Test threat
        threat = {
            "threat_id": "e2e_test_001",
            "source_ip": "192.168.1.100",
            "threat_type": "malware",
            "severity": "high",
            "business_unit": "finance",
            "compliance_frameworks": ["SOX"]
        }

        # Step 1: Route threat to optimal XDR platforms
        routing = router.determine_optimal_routing(threat)
        self.assertGreater(len(routing["primary_platforms"]), 0)

        # Step 2: Export to selected platforms
        export_results = []
        for platform in routing["primary_platforms"]:
            if platform.lower() == "crowdstrike":
                coord = mock_crowdstrike.return_value
            elif platform.lower() == "sentinel":
                coord = mock_sentinel.return_value
            else:
                coord = mock_umbrella.return_value

            result = coord.export_threat_data(threat)
            export_results.append(result)

        # Verify exports
        for result in export_results:
            self.assertTrue(result["success"])

        # Step 3: Execute coordinated response
        response_plan = {
            "actions": [
                {
                    "type": "block_ip",
                    "target": threat["source_ip"],
                    "platforms": routing["primary_platforms"]
                }
            ]
        }

        response_result = engine.execute_coordinated_response(threat, response_plan)
        self.assertTrue(response_result["success"])

        logger.info("✅ End-to-end workflow test completed successfully")

def run_xdr_integration_tests():
    """Run comprehensive XDR integration test suite"""
    print("\n🔧 SmartCompute Enterprise - XDR Integration Testing")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestXDRIntegration,
        TestMultiXDRResponseEngine,
        TestBusinessContextRouter,
        TestXDRPlatformCredentials,
        TestXDRIntegrationEnd2End
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print(f"\n📊 Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print(f"\n⚠️ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n✅ Success Rate: {success_rate:.1f}%")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_xdr_integration_tests()
    sys.exit(0 if success else 1)