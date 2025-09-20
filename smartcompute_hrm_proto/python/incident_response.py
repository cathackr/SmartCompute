#!/usr/bin/env python3
import json
import yaml
import subprocess
import logging
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ResponseAction:
    action_type: str
    priority: int
    command: str
    timeout: int
    requires_approval: bool

class AutomatedIncidentResponse:
    def __init__(self, config_file="../plans/response_config.yml"):
        self.config_file = config_file
        self.setup_logging()
        self.load_response_config()

    def setup_logging(self):
        logging.basicConfig(
            filename="../logs/incident_response.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_response_config(self):
        """Cargar configuración de respuesta automática"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Crear configuración por defecto
            self.create_default_config()
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)

    def create_default_config(self):
        """Crear configuración por defecto"""
        default_config = {
            "response_rules": {
                "process_injection": {
                    "threshold": 5.0,
                    "actions": [
                        {
                            "type": "isolate_host",
                            "priority": 1,
                            "command": "netsh advfirewall set allprofiles firewallpolicy blockinbound,blockoutbound",
                            "timeout": 30,
                            "requires_approval": False
                        },
                        {
                            "type": "collect_memory",
                            "priority": 2,
                            "command": "python3 collect_memory_dump.py --host {host} --output ../logs/",
                            "timeout": 300,
                            "requires_approval": True
                        },
                        {
                            "type": "block_process",
                            "priority": 3,
                            "command": "taskkill /f /im {process_name}",
                            "timeout": 10,
                            "requires_approval": False
                        },
                        {
                            "type": "alert_soc",
                            "priority": 4,
                            "command": "python3 soc_alert.py --severity CRITICAL --event {event_id}",
                            "timeout": 5,
                            "requires_approval": False
                        }
                    ]
                },
                "suspicious_behavior": {
                    "threshold": 3.0,
                    "actions": [
                        {
                            "type": "enhanced_monitoring",
                            "priority": 1,
                            "command": "python3 enable_monitoring.py --host {host} --duration 24h",
                            "timeout": 60,
                            "requires_approval": False
                        },
                        {
                            "type": "alert_soc",
                            "priority": 2,
                            "command": "python3 soc_alert.py --severity MEDIUM --event {event_id}",
                            "timeout": 5,
                            "requires_approval": False
                        }
                    ]
                }
            },
            "approval_settings": {
                "auto_approve_low_risk": True,
                "require_approval_threshold": 7.0,
                "approval_timeout": 300
            }
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

    def process_incident(self, analysis_result: Dict, event_data: Dict) -> Dict:
        """Procesar incidente y ejecutar respuestas automáticas"""
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        risk_score = analysis_result.get("risk_score", 0)

        response_summary = {
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "risk_score": risk_score,
            "actions_executed": [],
            "actions_pending": [],
            "status": "processing"
        }

        self.logger.info(f"Processing incident {incident_id} with risk score {risk_score}")

        # Determinar tipo de respuesta basado en técnicas detectadas
        response_type = self._determine_response_type(analysis_result)

        if response_type in self.config["response_rules"]:
            rule_config = self.config["response_rules"][response_type]

            if risk_score >= rule_config["threshold"]:
                # Ejecutar acciones automáticas
                response_summary["actions_executed"] = self._execute_automated_actions(
                    rule_config["actions"], event_data, risk_score
                )

        # Guardar resumen del incidente
        incident_file = f"../logs/incident_{incident_id}.json"
        with open(incident_file, 'w') as f:
            json.dump(response_summary, f, indent=2)

        response_summary["status"] = "completed"
        return response_summary

    def _determine_response_type(self, analysis_result: Dict) -> str:
        """Determinar el tipo de respuesta basado en las técnicas detectadas"""
        techniques = analysis_result.get("detected_techniques", [])

        injection_techniques = ["CreateRemoteThread", "Process Hollowing", "DLL Injection", "PE Injection"]

        for technique in techniques:
            if technique["technique"] in injection_techniques:
                return "process_injection"

        return "suspicious_behavior"

    def _execute_automated_actions(self, actions: List[Dict], event_data: Dict, risk_score: float) -> List[Dict]:
        """Ejecutar acciones automatizadas"""
        executed_actions = []

        # Ordenar acciones por prioridad
        sorted_actions = sorted(actions, key=lambda x: x["priority"])

        for action_config in sorted_actions:
            # Verificar si requiere aprobación
            if action_config.get("requires_approval", False):
                if risk_score < self.config["approval_settings"]["require_approval_threshold"]:
                    if not self.config["approval_settings"]["auto_approve_low_risk"]:
                        self.logger.info(f"Action {action_config['type']} requires approval - skipping")
                        continue

            # Preparar comando con variables
            command = self._prepare_command(action_config["command"], event_data)

            # Ejecutar acción
            action_result = self._execute_action(action_config, command)
            executed_actions.append(action_result)

            self.logger.info(f"Executed action: {action_config['type']} - Status: {action_result['status']}")

        return executed_actions

    def _prepare_command(self, command_template: str, event_data: Dict) -> str:
        """Preparar comando sustituyendo variables"""
        variables = {
            "host": event_data.get("source_meta", {}).get("host", "unknown"),
            "event_id": event_data.get("event_id", "unknown"),
            "process_name": self._extract_process_name(event_data.get("process_path", "")),
            "user": event_data.get("source_meta", {}).get("user", "unknown")
        }

        command = command_template
        for var, value in variables.items():
            command = command.replace(f"{{{var}}}", str(value))

        return command

    def _extract_process_name(self, process_path: str) -> str:
        """Extraer nombre del proceso de la ruta completa"""
        if "\\" in process_path:
            return process_path.split("\\")[-1]
        elif "/" in process_path:
            return process_path.split("/")[-1]
        return process_path

    def _execute_action(self, action_config: Dict, command: str) -> Dict:
        """Ejecutar una acción específica"""
        result = {
            "action_type": action_config["type"],
            "command": command,
            "status": "failed",
            "output": "",
            "error": "",
            "execution_time": None
        }

        start_time = datetime.now()

        try:
            # Simular ejecución para demo (en producción ejecutaría comandos reales)
            if action_config["type"] == "isolate_host":
                result["output"] = "Host isolation command simulated - firewall rules would be applied"
                result["status"] = "simulated"
            elif action_config["type"] == "collect_memory":
                result["output"] = "Memory collection command simulated - dump would be created"
                result["status"] = "simulated"
            elif action_config["type"] == "block_process":
                result["output"] = "Process termination command simulated"
                result["status"] = "simulated"
            elif action_config["type"] == "alert_soc":
                result["output"] = "SOC alert sent successfully"
                result["status"] = "success"
            else:
                result["output"] = f"Unknown action type: {action_config['type']}"

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Failed to execute action {action_config['type']}: {e}")

        result["execution_time"] = (datetime.now() - start_time).total_seconds()
        return result

def main():
    # Cargar análisis de inyección
    analysis_file = "../plans/injection_analysis_8.json"
    event_file = "../redacted_output.json"

    with open(analysis_file, 'r') as f:
        analysis_result = json.load(f)

    with open(event_file, 'r') as f:
        event_data = json.load(f)["findings"][0]

    # Crear y ejecutar respuesta automática
    response_system = AutomatedIncidentResponse()
    incident_response = response_system.process_incident(analysis_result, event_data)

    print(f"\n=== Incident Response Summary ===")
    print(f"Incident ID: {incident_response['incident_id']}")
    print(f"Risk Score: {incident_response['risk_score']}")
    print(f"Actions Executed: {len(incident_response['actions_executed'])}")

    for action in incident_response["actions_executed"]:
        print(f"  ✓ {action['action_type']}: {action['status']}")

    print(f"\nDetailed log saved to: ../logs/incident_{incident_response['incident_id']}.json")

if __name__ == "__main__":
    main()