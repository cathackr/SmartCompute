"""
SmartCompute SIEM Integrations.

Conectores para reenviar eventos de SmartCompute a SIEMs:
- Splunk (HTTP Event Collector, formato CEF o JSON)
- Wazuh (JSON sobre syslog RFC-3164, decodificado con JSON_Decoder)
- Formateador CEF genérico (compatible con QRadar, ArcSight, LogRhythm)

La configuración se lee de un YAML (ver siem_config.example.yaml en este
directorio). Leer el YAML requiere PyYAML: pip install smartcompute[siem]
"""

from .cef_formatter import SmartComputeCEFFormatter, CEFSeverity
from .splunk_connector import SplunkConnector
from .wazuh_connector import WazuhConnector
from .siem_manager import SIEMManager

__all__ = [
    'SmartComputeCEFFormatter',
    'CEFSeverity',
    'SplunkConnector',
    'WazuhConnector',
    'SIEMManager',
]
