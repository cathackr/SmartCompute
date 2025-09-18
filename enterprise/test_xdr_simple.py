#!/usr/bin/env python3
"""
Simplified XDR Integration Test Suite
Tests XDR coordinators with proper config initialization
"""

import os
import sys
import json
import logging
import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add the enterprise directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestXDRCoordinatorsSimple(unittest.TestCase):
    """Simplified test suite for XDR coordinators"""

    def setUp(self):
        """Set up test environment with proper configs"""
        self.test_config = {
            "api_base": "https://api.test.com",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "simulation_mode": True
        }

        self.test_threat_data = {
            "threat_id": "test_threat_001",
            "source_ip": "192.168.1.100",
            "threat_type": "malware",
            "severity": "high",
            "indicators": [
                {"type": "ip", "value": "192.168.1.100"}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    def test_crowdstrike_coordinator_init(self):
        """Test CrowdStrike coordinator initialization with config"""
        try:
            from xdr_mcp_coordinators import CrowdStrikeCoordinator
            coordinator = CrowdStrikeCoordinator(self.test_config)
            self.assertIsNotNone(coordinator)
            self.assertEqual(coordinator.client_id, "test_client_id")
            logger.info("✅ CrowdStrike coordinator initialization successful")
        except Exception as e:
            logger.error(f"❌ CrowdStrike coordinator init failed: {e}")
            self.fail(f"CrowdStrike coordinator initialization failed: {e}")

    def test_sentinel_coordinator_init(self):
        """Test Sentinel coordinator initialization with config"""
        try:
            from xdr_mcp_coordinators import SentinelCoordinator
            coordinator = SentinelCoordinator(self.test_config)
            self.assertIsNotNone(coordinator)
            logger.info("✅ Sentinel coordinator initialization successful")
        except Exception as e:
            logger.error(f"❌ Sentinel coordinator init failed: {e}")
            self.fail(f"Sentinel coordinator initialization failed: {e}")

    def test_cisco_umbrella_coordinator_init(self):
        """Test Cisco Umbrella coordinator initialization with config"""
        try:
            from xdr_mcp_coordinators import CiscoUmbrellaCoordinator
            coordinator = CiscoUmbrellaCoordinator(self.test_config)
            self.assertIsNotNone(coordinator)
            logger.info("✅ Cisco Umbrella coordinator initialization successful")
        except Exception as e:
            logger.error(f"❌ Cisco Umbrella coordinator init failed: {e}")
            self.fail(f"Cisco Umbrella coordinator initialization failed: {e}")

    def test_multi_xdr_response_engine_init(self):
        """Test Multi XDR Response Engine initialization"""
        try:
            from multi_xdr_response_engine import MultiXDRResponseEngine
            engine = MultiXDRResponseEngine(self.test_config)
            self.assertIsNotNone(engine)
            logger.info("✅ Multi XDR Response Engine initialization successful")
        except Exception as e:
            logger.error(f"❌ Multi XDR Response Engine init failed: {e}")
            self.fail(f"Multi XDR Response Engine initialization failed: {e}")

    def test_business_context_router_init(self):
        """Test Business Context Router initialization"""
        try:
            from business_context_xdr_router import BusinessContextXDRRouter
            router = BusinessContextXDRRouter(self.test_config)
            self.assertIsNotNone(router)
            logger.info("✅ Business Context Router initialization successful")
        except Exception as e:
            logger.error(f"❌ Business Context Router init failed: {e}")
            self.fail(f"Business Context Router initialization failed: {e}")

class TestXDRSimulationMode(unittest.TestCase):
    """Test XDR coordinators in simulation mode"""

    def setUp(self):
        """Set up simulation mode config"""
        self.sim_config = {
            "simulation_mode": True,
            "api_base": "https://simulation.test.com"
        }

    def test_crowdstrike_simulation_auth(self):
        """Test CrowdStrike authentication in simulation mode"""
        try:
            from xdr_mcp_coordinators import CrowdStrikeCoordinator
            coordinator = CrowdStrikeCoordinator(self.sim_config)

            # Test async authentication in sync context
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(coordinator.authenticate())
                self.assertTrue(result)
                self.assertIsNotNone(coordinator.access_token)
                logger.info("✅ CrowdStrike simulation authentication successful")
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"❌ CrowdStrike simulation auth failed: {e}")
            self.fail(f"CrowdStrike simulation authentication failed: {e}")

    def test_threat_data_export_simulation(self):
        """Test threat data export in simulation mode"""
        try:
            from xdr_mcp_coordinators import CrowdStrikeCoordinator, XDRExportTask, XDRPlatform, ExportPriority
            coordinator = CrowdStrikeCoordinator(self.sim_config)

            # Create proper XDRExportTask
            export_task = XDRExportTask(
                task_id="sim_test_001",
                platform=XDRPlatform.CROWDSTRIKE,
                threat_data={"indicator": "10.0.0.1", "type": "ip"},
                hrm_analysis={"hrm_analysis": {"final_assessment": {"confidence": 0.85, "threat_level": "HIGH"}}},
                business_context={"unit": "test"},
                priority=ExportPriority.HIGH,
                export_format="stix"
            )

            # Simulate successful export
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # First authenticate
                auth_result = loop.run_until_complete(coordinator.authenticate())
                self.assertTrue(auth_result)

                # Then export with proper task object
                export_result = loop.run_until_complete(coordinator.export_threat_data(export_task))
                self.assertTrue(export_result.success)
                logger.info("✅ Threat data export simulation successful")
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"❌ Threat export simulation failed: {e}")
            self.fail(f"Threat export simulation failed: {e}")

class TestXDRCredentialCheck(unittest.TestCase):
    """Test XDR platform credential checking"""

    def test_credential_availability(self):
        """Check which XDR platform credentials are available"""
        credentials = {
            "CrowdStrike": {
                "available": bool(os.getenv('CROWDSTRIKE_CLIENT_ID')),
                "vars": ['CROWDSTRIKE_CLIENT_ID', 'CROWDSTRIKE_CLIENT_SECRET']
            },
            "Sentinel": {
                "available": bool(os.getenv('AZURE_CLIENT_ID')),
                "vars": ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID']
            },
            "Umbrella": {
                "available": bool(os.getenv('UMBRELLA_API_KEY')),
                "vars": ['UMBRELLA_API_KEY', 'UMBRELLA_API_SECRET']
            }
        }

        logger.info("🔐 XDR Platform Credential Status:")
        for platform, info in credentials.items():
            status = "✅ Available" if info["available"] else "❌ Not Available"
            logger.info(f"  {platform}: {status}")
            if not info["available"]:
                logger.info(f"    Required env vars: {', '.join(info['vars'])}")

        # At least simulation mode should work
        self.assertTrue(True, "Credential check completed")

def run_simple_xdr_tests():
    """Run simplified XDR integration test suite"""
    print("\n🧪 SmartCompute Enterprise - Simplified XDR Testing")
    print("=" * 55)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestXDRCoordinatorsSimple,
        TestXDRSimulationMode,
        TestXDRCredentialCheck
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
            print(f"  - {test}")

    if result.errors:
        print(f"\n⚠️ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n✅ Success Rate: {success_rate:.1f}%")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_simple_xdr_tests()
    sys.exit(0 if success else 1)