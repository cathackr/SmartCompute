#!/usr/bin/env python3
"""
SmartCompute SIEM Integration Manager
Orquesta el envío de eventos a múltiples SIEMs basado en configuración
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List

import requests

from .splunk_connector import SplunkConnector
from .cef_formatter import SmartComputeCEFFormatter
from .wazuh_connector import WazuhConnector


class SIEMManager:
    """Gestor centralizado para integraciones SIEM"""

    def __init__(self, config_path: str = "siem_config.yaml"):
        """
        Initialize SIEM Manager with configuration

        Args:
            config_path: Path to SIEM configuration YAML file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.connectors = {}
        self.cef_formatter = SmartComputeCEFFormatter()

        # Setup logging
        self._setup_logging()

        # Initialize enabled connectors
        self._initialize_connectors()

        self.logger.info("SIEMManager initialized with connectors: %s", list(self.connectors.keys()))

    def _load_config(self) -> Dict[str, Any]:
        """Load SIEM configuration from YAML file"""
        try:
            if self.config_path.exists():
                try:
                    import yaml
                except ImportError as exc:
                    raise ImportError(
                        "Leer la configuración SIEM requiere PyYAML: pip install smartcompute[siem]"
                    ) from exc
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return config
            else:
                # Return default config if file doesn't exist
                return {
                    'siem_settings': {
                        'enabled': True,
                        'default_format': 'cef',
                        'min_risk_score': 0.3
                    },
                    'splunk': {'enabled': False},
                    'wazuh': {'enabled': False},
                    'qradar': {'enabled': False},
                    'sentinel': {'enabled': False}
                }
        except ImportError:
            raise
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return {'siem_settings': {'enabled': False}}

    def _setup_logging(self):
        """Configure logging based on config settings"""
        log_level = self.config.get('debug', {}).get('log_level', 'INFO')

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_connectors(self):
        """Initialize enabled SIEM connectors based on configuration"""

        # Initialize Splunk connector
        if self.config.get('splunk', {}).get('enabled', False):
            try:
                splunk_config = self.config['splunk']
                self.connectors['splunk'] = SplunkConnector(
                    splunk_host=splunk_config.get('host', 'localhost'),
                    hec_token=splunk_config.get('hec_token', ''),
                    index=splunk_config.get('index', 'smartcompute'),
                    source=splunk_config.get('source', 'smartcompute'),
                    sourcetype=splunk_config.get('sourcetype_anomaly', 'smartcompute:cef'),
                    use_ssl=splunk_config.get('use_ssl', True),
                    verify_ssl=splunk_config.get('verify_ssl', True),
                    hec_port=splunk_config.get('hec_port', 8088)
                )
                self.logger.info("Splunk connector initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Splunk connector: {e}")

        # Initialize Wazuh connector
        if self.config.get('wazuh', {}).get('enabled', False):
            try:
                wc = self.config['wazuh']
                self.connectors['wazuh'] = WazuhConnector(
                    host=wc.get('host', 'localhost'),
                    port=wc.get('port', 514),
                    protocol=wc.get('protocol', 'udp'),
                    tag=wc.get('tag', 'smartcompute'),
                )
                self.logger.info("Wazuh connector initialized → %s:%s", wc.get('host'), wc.get('port'))
            except Exception as e:
                self.logger.error(f"Failed to initialize Wazuh connector: {e}")

        # Add other SIEM connectors here (QRadar, Sentinel, etc.)

    def send_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Send anomaly event to all configured SIEMs

        Args:
            anomaly_data: Anomaly data from SmartCompute detection

        Returns:
            Dict with results from each SIEM connector
        """
        # Check if event meets minimum risk score threshold
        risk_score = anomaly_data.get('risk_score', 0)
        min_risk_score = self.config.get('siem_settings', {}).get('min_risk_score', 0.3)

        if risk_score < min_risk_score:
            self.logger.debug(f"Event risk score {risk_score} below threshold {min_risk_score}, skipping")
            return {"skipped": [{"reason": "below_threshold", "risk_score": risk_score}]}

        results = {}

        # Send to each configured SIEM
        for siem_name, connector in self.connectors.items():
            try:
                if siem_name == 'splunk':
                    result = connector.send_anomaly_event(anomaly_data, use_cef=True)
                    results[siem_name] = [result]

                    if risk_score >= 0.9 and self.config.get('notifications', {}).get('slack', {}).get('enabled', False):
                        self._send_slack_alert(anomaly_data)

                elif siem_name == 'wazuh':
                    result = connector.send_anomaly_event(anomaly_data, use_cef=True)
                    results[siem_name] = [result]

                # Add other SIEM integrations here

            except Exception as e:
                self.logger.error(f"Error sending to {siem_name}: {e}")
                results[siem_name] = [{"status": "error", "message": str(e)}]

        return results

    def send_performance_baseline(self, perf_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Send performance baseline data to configured SIEMs"""
        results = {}

        for siem_name, connector in self.connectors.items():
            try:
                if siem_name == 'splunk':
                    result = connector.send_performance_event(perf_data)
                    results[siem_name] = [result]

            except Exception as e:
                self.logger.error(f"Error sending performance data to {siem_name}: {e}")
                results[siem_name] = [{"status": "error", "message": str(e)}]

        return results

    def send_batch_events(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Send multiple events in batch for better performance"""
        results = {}

        # Filter events by risk score threshold
        min_risk_score = self.config.get('siem_settings', {}).get('min_risk_score', 0.3)
        filtered_events = [
            event for event in events
            if event.get('risk_score', 0) >= min_risk_score
        ]

        if not filtered_events:
            return {"filtered_out": [{"reason": "all_below_threshold", "count": len(events)}]}

        for siem_name, connector in self.connectors.items():
            try:
                if siem_name == 'splunk':
                    result = connector.send_batch_events(filtered_events)
                    results[siem_name] = [result]

            except Exception as e:
                self.logger.error(f"Error sending batch to {siem_name}: {e}")
                results[siem_name] = [{"status": "error", "message": str(e)}]

        return results

    def test_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Test connectivity to all configured SIEMs"""
        results = {}

        for siem_name, connector in self.connectors.items():
            try:
                if hasattr(connector, 'test_connection'):
                    result = connector.test_connection()
                    results[siem_name] = result
                else:
                    results[siem_name] = {"status": "unsupported", "message": "Test not available"}

            except Exception as e:
                results[siem_name] = {"status": "error", "message": str(e)}

        return results

    def _send_slack_alert(self, anomaly_data: Dict[str, Any]):
        """Send critical alert to Slack"""
        try:
            slack_config = self.config.get('notifications', {}).get('slack', {})
            webhook_url = slack_config.get('webhook_url')

            if not webhook_url:
                return

            risk_score = anomaly_data.get('risk_score', 0)
            anomaly_type = anomaly_data.get('anomaly_type', 'Unknown')
            source_host = anomaly_data.get('source_host', 'Unknown')

            slack_message = {
                "text": f"🚨 Critical SmartCompute Alert",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {
                                "title": "Anomaly Type",
                                "value": anomaly_type,
                                "short": True
                            },
                            {
                                "title": "Risk Score",
                                "value": f"{risk_score:.1%}",
                                "short": True
                            },
                            {
                                "title": "Source Host",
                                "value": source_host,
                                "short": True
                            },
                            {
                                "title": "Description",
                                "value": anomaly_data.get('description', 'No description available'),
                                "short": False
                            }
                        ]
                    }
                ]
            }

            response = requests.post(webhook_url, json=slack_message, timeout=10)

            if response.status_code == 200:
                self.logger.info("Slack alert sent successfully")
            else:
                self.logger.warning(f"Slack alert failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of SIEM Manager"""
        return {
            "enabled_connectors": list(self.connectors.keys()),
            "config_loaded": bool(self.config),
            "min_risk_score": self.config.get('siem_settings', {}).get('min_risk_score', 0.3),
            "default_format": self.config.get('siem_settings', {}).get('default_format', 'cef'),
            "notifications_enabled": {
                "slack": self.config.get('notifications', {}).get('slack', {}).get('enabled', False)
            }
        }
