#!/usr/bin/env python3
"""
XDR MCP Coordinators
Coordinación MCP para exporters XDR existentes con inteligencia HRM
Extiende funcionalidad Enterprise existente con capacidades MCP
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import hashlib
import base64

class XDRPlatform(Enum):
    CROWDSTRIKE = "crowdstrike"
    SENTINEL = "sentinel"
    CISCO_UMBRELLA = "cisco_umbrella"
    WAZUH = "wazuh"

class ExportPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class XDRExportTask:
    """Tarea de exportación XDR"""
    task_id: str
    platform: XDRPlatform
    threat_data: Dict[str, Any]
    hrm_analysis: Dict[str, Any]
    business_context: Dict[str, Any]
    priority: ExportPriority
    export_format: str
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    status: str = "pending"

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class XDRResponse:
    """Respuesta de exportación XDR"""
    platform: XDRPlatform
    success: bool
    response_data: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_time_ms: float = 0
    export_id: Optional[str] = None

class CrowdStrikeCoordinator:
    """Coordinador MCP para CrowdStrike Falcon"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("CrowdStrikeCoordinator")
        self.api_base = config.get("api_base", "https://api.crowdstrike.com")
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.access_token = None
        self.token_expires_at = None

    async def authenticate(self) -> bool:
        """Autenticación OAuth2 con CrowdStrike"""
        try:
            auth_url = f"{self.api_base}/oauth2/token"

            # Simular autenticación (en producción usar credenciales reales)
            if not self.client_id or not self.client_secret:
                self.logger.warning("CrowdStrike credentials not configured - using simulation mode")
                self.access_token = "simulated_token_" + str(datetime.now().timestamp())
                self.token_expires_at = datetime.now() + timedelta(hours=1)
                return True

            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, data=auth_data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data["access_token"]
                        expires_in = token_data.get("expires_in", 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        return True
                    else:
                        self.logger.error(f"CrowdStrike authentication failed: {response.status}")
                        return False

        except Exception as e:
            self.logger.error(f"CrowdStrike authentication error: {str(e)}")
            return False

    async def export_threat_data(self, export_task: XDRExportTask) -> XDRResponse:
        """Exportar datos de amenaza a CrowdStrike"""
        start_time = datetime.now()

        try:
            # Verificar autenticación
            if not await self._ensure_authenticated():
                return XDRResponse(
                    platform=XDRPlatform.CROWDSTRIKE,
                    success=False,
                    error_message="Authentication failed"
                )

            # Transformar datos HRM a formato CrowdStrike
            crowdstrike_payload = self._transform_to_crowdstrike_format(
                export_task.threat_data,
                export_task.hrm_analysis,
                export_task.business_context
            )

            # Determinar endpoint según prioridad y contexto
            endpoint = self._determine_crowdstrike_endpoint(export_task)

            # Simular exportación (en producción usar API real)
            if self.access_token.startswith("simulated_"):
                self.logger.debug(f"Simulating CrowdStrike export to {endpoint}")

                response_data = {
                    "meta": {
                        "query_time": 0.045,
                        "powered_by": "crowdstrike-api-gateway",
                        "request_id": f"cs_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]}"
                    },
                    "resources": [
                        {
                            "id": f"cs_ioc_{hashlib.md5(export_task.task_id.encode()).hexdigest()[:16]}",
                            "type": "threat_intelligence",
                            "value": export_task.threat_data.get("indicator", "unknown"),
                            "source": "smartcompute_hrm",
                            "confidence": export_task.hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5),
                            "severity": self._map_severity_to_crowdstrike(
                                export_task.hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
                            ),
                            "created_on": start_time.isoformat()
                        }
                    ],
                    "errors": []
                }

                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                return XDRResponse(
                    platform=XDRPlatform.CROWDSTRIKE,
                    success=True,
                    response_data=response_data,
                    processing_time_ms=processing_time,
                    export_id=response_data["resources"][0]["id"]
                )

            # Producción: usar API real de CrowdStrike
            else:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{self.api_base}{endpoint}",
                                          json=crowdstrike_payload,
                                          headers=headers) as response:

                        processing_time = (datetime.now() - start_time).total_seconds() * 1000

                        if response.status == 200:
                            response_data = await response.json()
                            return XDRResponse(
                                platform=XDRPlatform.CROWDSTRIKE,
                                success=True,
                                response_data=response_data,
                                processing_time_ms=processing_time
                            )
                        else:
                            error_text = await response.text()
                            return XDRResponse(
                                platform=XDRPlatform.CROWDSTRIKE,
                                success=False,
                                error_message=f"HTTP {response.status}: {error_text}",
                                processing_time_ms=processing_time
                            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"CrowdStrike export error: {str(e)}")
            return XDRResponse(
                platform=XDRPlatform.CROWDSTRIKE,
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )

    def _transform_to_crowdstrike_format(self, threat_data: Dict, hrm_analysis: Dict, business_context: Dict) -> Dict:
        """Transformar datos SmartCompute a formato CrowdStrike Streaming API"""

        # Extraer información clave del análisis HRM
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)

        # Extraer indicadores de amenaza
        threat_intel = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {})

        # Formato CrowdStrike
        payload = {
            "resources": [
                {
                    "indicator_type": self._determine_indicator_type(threat_data),
                    "malicious_confidence": self._map_confidence_to_crowdstrike(confidence),
                    "publishedDate": datetime.now().isoformat(),
                    "source": "SmartCompute HRM Enterprise",
                    "threat_types": self._extract_threat_types(hrm_analysis),
                    "labels": self._generate_crowdstrike_labels(threat_data, business_context),
                    "relations": self._build_threat_relations(hrm_analysis),
                    "metadata": {
                        "smartcompute_analysis_id": threat_data.get("event_id"),
                        "hrm_threat_level": threat_level,
                        "business_unit": business_context.get("business_unit"),
                        "compliance_frameworks": business_context.get("compliance_frameworks", []),
                        "original_event": threat_data
                    }
                }
            ]
        }

        return payload

    def _determine_crowdstrike_endpoint(self, export_task: XDRExportTask) -> str:
        """Determinar endpoint CrowdStrike según contexto"""
        if export_task.priority == ExportPriority.EMERGENCY:
            return "/intel/entities/indicators/v1"  # Threat Intelligence
        elif export_task.business_context.get("asset_criticality") == "critical":
            return "/intel/combined/indicators/v1"  # Combined Intelligence
        else:
            return "/intel/entities/indicators/v1"  # Standard

    def _map_severity_to_crowdstrike(self, smartcompute_level: str) -> str:
        """Mapear niveles SmartCompute a CrowdStrike"""
        mapping = {
            "CRITICAL": "high",
            "HIGH": "medium",
            "MEDIUM": "low",
            "LOW": "informational"
        }
        return mapping.get(smartcompute_level, "low")

    def _map_confidence_to_crowdstrike(self, confidence: float) -> str:
        """Mapear confidence HRM a CrowdStrike"""
        if confidence >= 0.9:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        elif confidence >= 0.5:
            return "low"
        else:
            return "unverified"

    def _determine_indicator_type(self, threat_data: Dict) -> str:
        """Determinar tipo de indicador para CrowdStrike"""
        event_type = threat_data.get("event_type", "").lower()

        if "ip" in event_type or threat_data.get("source_ip"):
            return "ipv4"
        elif "domain" in event_type or threat_data.get("domain"):
            return "domain"
        elif "hash" in event_type or threat_data.get("file_hash"):
            return "sha256"
        elif "url" in event_type or threat_data.get("url"):
            return "url"
        else:
            return "unknown"

    def _extract_threat_types(self, hrm_analysis: Dict) -> List[str]:
        """Extraer tipos de amenaza del análisis HRM"""
        threat_intel = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {})
        category = threat_intel.get("category", "unknown")

        # Mapear categorías HRM a tipos CrowdStrike
        type_mapping = {
            "malware": ["Malware"],
            "apt": ["APT", "Targeted Attack"],
            "phishing": ["Phishing", "Social Engineering"],
            "botnet": ["Botnet", "Command and Control"],
            "ransomware": ["Ransomware", "Extortion"],
            "insider_threat": ["Insider Threat", "Data Theft"]
        }

        return type_mapping.get(category, ["Unknown"])

    def _generate_crowdstrike_labels(self, threat_data: Dict, business_context: Dict) -> List[str]:
        """Generar labels CrowdStrike basados en contexto"""
        labels = ["smartcompute_hrm"]

        # Labels de contexto empresarial
        business_unit = business_context.get("business_unit")
        if business_unit:
            labels.append(f"business_unit:{business_unit}")

        # Labels de compliance
        compliance = business_context.get("compliance_frameworks", [])
        for framework in compliance:
            labels.append(f"compliance:{framework.lower()}")

        # Labels de criticidad
        criticality = business_context.get("asset_criticality")
        if criticality:
            labels.append(f"criticality:{criticality}")

        return labels

    def _build_threat_relations(self, hrm_analysis: Dict) -> List[Dict]:
        """Construir relaciones de amenaza"""
        relations = []

        # Relación con análisis comportamental
        behavioral = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("behavioral_analysis", {})
        if behavioral:
            relations.append({
                "relation_type": "analyzed_by",
                "target": "smartcompute_behavioral_engine",
                "confidence": behavioral.get("confidence", 0.5)
            })

        return relations

    async def _ensure_authenticated(self) -> bool:
        """Asegurar que tenemos token válido"""
        if not self.access_token:
            return await self.authenticate()

        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            return await self.authenticate()

        return True

class SentinelCoordinator:
    """Coordinador MCP para Microsoft Sentinel"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("SentinelCoordinator")
        self.workspace_id = config.get("workspace_id")
        self.tenant_id = config.get("tenant_id")
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.access_token = None
        self.token_expires_at = None

    async def export_threat_data(self, export_task: XDRExportTask) -> XDRResponse:
        """Exportar datos de amenaza a Microsoft Sentinel"""
        start_time = datetime.now()

        try:
            # Simular autenticación
            if not await self._ensure_authenticated():
                return XDRResponse(
                    platform=XDRPlatform.SENTINEL,
                    success=False,
                    error_message="Authentication failed"
                )

            # Transformar a formato STIX 2.1 para Sentinel
            stix_payload = self._transform_to_stix_format(
                export_task.threat_data,
                export_task.hrm_analysis,
                export_task.business_context
            )

            # Simular exportación
            self.logger.debug("Simulating Sentinel STIX export")

            response_data = {
                "id": f"sentinel_{hashlib.md5(export_task.task_id.encode()).hexdigest()[:16]}",
                "type": "indicator",
                "spec_version": "2.1",
                "created": start_time.isoformat() + "Z",
                "modified": start_time.isoformat() + "Z",
                "pattern": self._generate_stix_pattern(export_task.threat_data),
                "labels": self._generate_sentinel_labels(export_task.hrm_analysis),
                "confidence": int(export_task.hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5) * 100),
                "external_references": [
                    {
                        "source_name": "SmartCompute HRM",
                        "description": "Enterprise threat analysis",
                        "external_id": export_task.threat_data.get("event_id")
                    }
                ]
            }

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return XDRResponse(
                platform=XDRPlatform.SENTINEL,
                success=True,
                response_data=response_data,
                processing_time_ms=processing_time,
                export_id=response_data["id"]
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Sentinel export error: {str(e)}")
            return XDRResponse(
                platform=XDRPlatform.SENTINEL,
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )

    def _transform_to_stix_format(self, threat_data: Dict, hrm_analysis: Dict, business_context: Dict) -> Dict:
        """Transformar datos a formato STIX 2.1"""
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)

        stix_object = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{hashlib.md5(threat_data.get('event_id', '').encode()).hexdigest()}",
            "created": datetime.now().isoformat() + "Z",
            "modified": datetime.now().isoformat() + "Z",
            "pattern": self._generate_stix_pattern(threat_data),
            "labels": self._generate_sentinel_labels(hrm_analysis),
            "confidence": int(confidence * 100),
            "lang": "en",
            "external_references": [
                {
                    "source_name": "SmartCompute HRM Enterprise",
                    "description": f"Threat level: {threat_level}, Confidence: {confidence:.2f}",
                    "external_id": threat_data.get("event_id")
                }
            ],
            "object_marking_refs": ["marking-definition--f88d31f6-486f-44da-b317-01333bde0b82"],  # TLP:WHITE
            "granular_markings": [
                {
                    "marking_ref": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82",
                    "selectors": ["pattern"]
                }
            ]
        }

        return stix_object

    def _generate_stix_pattern(self, threat_data: Dict) -> str:
        """Generar patrón STIX desde datos de amenaza"""
        source_ip = threat_data.get("source_ip")
        target_process = threat_data.get("target_process")
        event_type = threat_data.get("event_type")

        if source_ip:
            return f"[ipv4-addr:value = '{source_ip}']"
        elif target_process:
            return f"[process:name = '{target_process}']"
        elif event_type:
            return f"[x-smartcompute:event_type = '{event_type}']"
        else:
            return "[x-smartcompute:unknown = 'true']"

    def _generate_sentinel_labels(self, hrm_analysis: Dict) -> List[str]:
        """Generar labels Sentinel desde análisis HRM"""
        labels = ["smartcompute-hrm"]

        threat_intel = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {})
        category = threat_intel.get("category", "unknown")

        label_mapping = {
            "malware": "malicious-activity",
            "apt": "malicious-activity",
            "phishing": "malicious-activity",
            "botnet": "malicious-activity",
            "ransomware": "malicious-activity",
            "insider_threat": "anomalous-activity"
        }

        sentinel_label = label_mapping.get(category, "anomalous-activity")
        labels.append(sentinel_label)

        return labels

    async def _ensure_authenticated(self) -> bool:
        """Simular autenticación con Sentinel"""
        if not self.access_token:
            self.access_token = f"sentinel_token_{datetime.now().timestamp()}"
            self.token_expires_at = datetime.now() + timedelta(hours=1)

        return True

class CiscoUmbrellaCoordinator:
    """Coordinador MCP para Cisco Umbrella"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("CiscoUmbrellaCoordinator")
        self.api_key = config.get("api_key")
        self.api_secret = config.get("api_secret")

    async def export_threat_data(self, export_task: XDRExportTask) -> XDRResponse:
        """Exportar datos de amenaza a Cisco Umbrella"""
        start_time = datetime.now()

        try:
            # Transformar a formato Cisco Umbrella Enforcement API
            umbrella_payload = self._transform_to_umbrella_format(
                export_task.threat_data,
                export_task.hrm_analysis,
                export_task.business_context
            )

            # Simular exportación
            self.logger.debug("Simulating Cisco Umbrella export")

            response_data = {
                "id": f"umbrella_{hashlib.md5(export_task.task_id.encode()).hexdigest()[:16]}",
                "customerId": self.config.get("customer_id", "simulated_customer"),
                "domainName": umbrella_payload.get("domain", "unknown.domain"),
                "status": "success",
                "dstUrl": f"https://s-platform.api.opendns.com/1.0/domains/{umbrella_payload.get('domain', 'unknown')}/categorization",
                "lastSeen": start_time.isoformat(),
                "categories": umbrella_payload.get("categories", []),
                "securityCategories": umbrella_payload.get("security_categories", [])
            }

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return XDRResponse(
                platform=XDRPlatform.CISCO_UMBRELLA,
                success=True,
                response_data=response_data,
                processing_time_ms=processing_time,
                export_id=response_data["id"]
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Cisco Umbrella export error: {str(e)}")
            return XDRResponse(
                platform=XDRPlatform.CISCO_UMBRELLA,
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )

    def _transform_to_umbrella_format(self, threat_data: Dict, hrm_analysis: Dict, business_context: Dict) -> Dict:
        """Transformar datos a formato Cisco Umbrella"""
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")

        # Extraer dominio/IP del evento
        domain = threat_data.get("domain") or threat_data.get("source_ip", "unknown.domain")

        umbrella_data = {
            "domain": domain,
            "categories": self._map_to_umbrella_categories(hrm_analysis),
            "security_categories": self._map_to_security_categories(threat_level),
            "threat_types": self._extract_umbrella_threat_types(hrm_analysis),
            "confidence_score": int(hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5) * 100),
            "source": "SmartCompute HRM Enterprise",
            "business_context": {
                "unit": business_context.get("business_unit"),
                "criticality": business_context.get("asset_criticality")
            }
        }

        return umbrella_data

    def _map_to_umbrella_categories(self, hrm_analysis: Dict) -> List[str]:
        """Mapear análisis HRM a categorías Umbrella"""
        threat_intel = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {})
        category = threat_intel.get("category", "unknown")

        category_mapping = {
            "malware": ["Malware"],
            "phishing": ["Phishing", "Suspicious"],
            "botnet": ["Botnet", "Command and Control"],
            "apt": ["APT", "Suspicious"],
            "ransomware": ["Malware", "Cryptomining"]
        }

        return category_mapping.get(category, ["Suspicious"])

    def _map_to_security_categories(self, threat_level: str) -> List[str]:
        """Mapear nivel de amenaza a categorías de seguridad"""
        if threat_level == "CRITICAL":
            return ["Malware", "Command and Control"]
        elif threat_level == "HIGH":
            return ["Suspicious", "Potentially Harmful"]
        elif threat_level == "MEDIUM":
            return ["Suspicious"]
        else:
            return ["Unverified"]

    def _extract_umbrella_threat_types(self, hrm_analysis: Dict) -> List[str]:
        """Extraer tipos de amenaza para Umbrella"""
        behavioral = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("behavioral_analysis", {})

        threat_types = ["Unknown"]

        if behavioral:
            behavior_patterns = behavioral.get("behavior_patterns", [])
            for pattern in behavior_patterns:
                if "network" in pattern.lower():
                    threat_types.append("Network-based")
                elif "process" in pattern.lower():
                    threat_types.append("Process-based")
                elif "file" in pattern.lower():
                    threat_types.append("File-based")

        return list(set(threat_types))

class XDRMCPCoordinator:
    """Coordinador principal MCP para todos los sistemas XDR"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("XDRMCPCoordinator")

        # Inicializar coordinadores individuales
        self.coordinators = {}

        if config.get("crowdstrike", {}).get("enabled", False):
            self.coordinators[XDRPlatform.CROWDSTRIKE] = CrowdStrikeCoordinator(
                config["crowdstrike"]
            )

        if config.get("sentinel", {}).get("enabled", False):
            self.coordinators[XDRPlatform.SENTINEL] = SentinelCoordinator(
                config["sentinel"]
            )

        if config.get("cisco_umbrella", {}).get("enabled", False):
            self.coordinators[XDRPlatform.CISCO_UMBRELLA] = CiscoUmbrellaCoordinator(
                config["cisco_umbrella"]
            )

        # Cola de tareas de exportación
        self.export_queue = asyncio.Queue()
        self.active_tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []

        # Estado del coordinador
        self.is_running = False
        self.worker_tasks = []

    async def start_coordination(self):
        """Iniciar coordinación XDR"""
        self.logger.info("Starting XDR MCP Coordination")
        self.is_running = True

        # Iniciar workers para procesamiento paralelo
        num_workers = self.config.get("num_workers", 3)
        for i in range(num_workers):
            worker = asyncio.create_task(self._export_worker(f"worker-{i}"))
            self.worker_tasks.append(worker)

        self.logger.info(f"Started {num_workers} XDR export workers")

    async def stop_coordination(self):
        """Detener coordinación XDR"""
        self.logger.info("Stopping XDR MCP Coordination")
        self.is_running = False

        # Cancelar workers
        for task in self.worker_tasks:
            task.cancel()

        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.logger.info("XDR MCP Coordination stopped")

    async def coordinate_export(self, threat_data: Dict, hrm_analysis: Dict, business_context: Dict) -> List[XDRResponse]:
        """Coordinar exportación a múltiples XDR basado en contexto HRM"""

        # Determinar plataformas objetivo basado en contexto empresarial
        target_platforms = self._determine_target_platforms(
            hrm_analysis, business_context
        )

        # Determinar prioridad basado en análisis HRM
        priority = self._determine_export_priority(hrm_analysis, business_context)

        # Crear tareas de exportación
        export_tasks = []
        for platform in target_platforms:
            if platform in self.coordinators:
                task = XDRExportTask(
                    task_id=f"export_{datetime.now().timestamp()}_{platform.value}",
                    platform=platform,
                    threat_data=threat_data,
                    hrm_analysis=hrm_analysis,
                    business_context=business_context,
                    priority=priority,
                    export_format=self._determine_export_format(platform, business_context)
                )
                export_tasks.append(task)

        # Encolar tareas según prioridad
        for task in sorted(export_tasks, key=lambda t: t.priority.value, reverse=True):
            await self.export_queue.put(task)
            self.active_tasks[task.task_id] = task

        self.logger.info(f"Queued {len(export_tasks)} XDR export tasks with priority {priority.name}")

        # Esperar completar tareas (con timeout)
        timeout = self.config.get("export_timeout", 30)
        responses = await self._wait_for_completion(
            [task.task_id for task in export_tasks],
            timeout
        )

        return responses

    def _determine_target_platforms(self, hrm_analysis: Dict, business_context: Dict) -> List[XDRPlatform]:
        """Determinar plataformas XDR objetivo basado en contexto"""
        platforms = []

        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        business_unit = business_context.get("business_unit", "unknown")
        compliance_frameworks = business_context.get("compliance_frameworks", [])
        asset_criticality = business_context.get("asset_criticality", "medium")

        # Lógica de selección inteligente
        if threat_level == "CRITICAL" or asset_criticality == "critical":
            # Amenazas críticas van a todas las plataformas disponibles
            platforms.extend(self.coordinators.keys())

        elif threat_level == "HIGH":
            # Amenazas altas van a CrowdStrike y Sentinel
            if XDRPlatform.CROWDSTRIKE in self.coordinators:
                platforms.append(XDRPlatform.CROWDSTRIKE)
            if XDRPlatform.SENTINEL in self.coordinators:
                platforms.append(XDRPlatform.SENTINEL)

        elif business_unit in ["finance", "healthcare"]:
            # Unidades de negocio críticas siempre incluyen Sentinel (compliance)
            if XDRPlatform.SENTINEL in self.coordinators:
                platforms.append(XDRPlatform.SENTINEL)
            if XDRPlatform.CROWDSTRIKE in self.coordinators:
                platforms.append(XDRPlatform.CROWDSTRIKE)

        elif "SOX" in compliance_frameworks or "HIPAA" in compliance_frameworks:
            # Compliance específico requiere Sentinel
            if XDRPlatform.SENTINEL in self.coordinators:
                platforms.append(XDRPlatform.SENTINEL)

        else:
            # Por defecto, usar CrowdStrike si está disponible
            if XDRPlatform.CROWDSTRIKE in self.coordinators:
                platforms.append(XDRPlatform.CROWDSTRIKE)

        # Siempre incluir Cisco Umbrella para amenazas de red
        threat_intel = hrm_analysis.get("hrm_analysis", {}).get("analysis_modules", {}).get("threat_intelligence", {})
        if (threat_intel.get("category") in ["botnet", "phishing", "command_control"] and
            XDRPlatform.CISCO_UMBRELLA in self.coordinators):
            platforms.append(XDRPlatform.CISCO_UMBRELLA)

        return list(set(platforms))  # Eliminar duplicados

    def _determine_export_priority(self, hrm_analysis: Dict, business_context: Dict) -> ExportPriority:
        """Determinar prioridad de exportación"""
        threat_level = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("threat_level", "MEDIUM")
        confidence = hrm_analysis.get("hrm_analysis", {}).get("final_assessment", {}).get("confidence", 0.5)
        asset_criticality = business_context.get("asset_criticality", "medium")

        # Lógica de priorización
        if threat_level == "CRITICAL" and confidence > 0.9:
            return ExportPriority.EMERGENCY
        elif threat_level == "CRITICAL" or (threat_level == "HIGH" and confidence > 0.8):
            return ExportPriority.CRITICAL
        elif threat_level == "HIGH" or asset_criticality == "critical":
            return ExportPriority.HIGH
        elif threat_level == "MEDIUM" or asset_criticality == "high":
            return ExportPriority.MEDIUM
        else:
            return ExportPriority.LOW

    def _determine_export_format(self, platform: XDRPlatform, business_context: Dict) -> str:
        """Determinar formato de exportación por plataforma"""
        format_map = {
            XDRPlatform.CROWDSTRIKE: "streaming_api",
            XDRPlatform.SENTINEL: "stix_2.1",
            XDRPlatform.CISCO_UMBRELLA: "enforcement_api"
        }

        base_format = format_map.get(platform, "json")

        # Modificar formato basado en contexto
        compliance = business_context.get("compliance_frameworks", [])
        if "SOX" in compliance:
            return f"{base_format}_compliance_enhanced"
        elif business_context.get("asset_criticality") == "critical":
            return f"{base_format}_detailed"

        return base_format

    async def _export_worker(self, worker_name: str):
        """Worker para procesar exportaciones XDR"""
        self.logger.debug(f"Starting export worker: {worker_name}")

        while self.is_running:
            try:
                # Obtener tarea de la cola
                task = await asyncio.wait_for(self.export_queue.get(), timeout=1.0)

                self.logger.debug(f"{worker_name} processing task: {task.task_id}")
                task.status = "processing"

                # Ejecutar exportación
                coordinator = self.coordinators[task.platform]
                response = await coordinator.export_threat_data(task)

                # Actualizar estado de tarea
                task.completed_at = datetime.now()
                if response.success:
                    task.status = "completed"
                    self.completed_tasks.append((task, response))
                    self.logger.info(f"Export completed: {task.task_id} -> {task.platform.value}")
                else:
                    task.status = "failed"
                    task.retry_count += 1

                    # Reintentar si no se han agotado los intentos
                    if task.retry_count < task.max_retries:
                        self.logger.warning(f"Export failed, retrying: {task.task_id} (attempt {task.retry_count})")
                        await asyncio.sleep(2 ** task.retry_count)  # Backoff exponencial
                        await self.export_queue.put(task)
                    else:
                        self.failed_tasks.append((task, response))
                        self.logger.error(f"Export failed permanently: {task.task_id}")

                # Limpiar de tareas activas
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]

            except asyncio.TimeoutError:
                # Timeout normal de la cola
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {str(e)}")
                await asyncio.sleep(1)

        self.logger.debug(f"Export worker stopped: {worker_name}")

    async def _wait_for_completion(self, task_ids: List[str], timeout: int) -> List[XDRResponse]:
        """Esperar completar tareas específicas"""
        responses = []
        start_time = datetime.now()

        while task_ids and (datetime.now() - start_time).total_seconds() < timeout:
            # Verificar tareas completadas
            for completed_task, response in self.completed_tasks[-10:]:  # Últimas 10
                if completed_task.task_id in task_ids:
                    responses.append(response)
                    task_ids.remove(completed_task.task_id)

            # Verificar tareas fallidas
            for failed_task, response in self.failed_tasks[-10:]:  # Últimas 10
                if failed_task.task_id in task_ids:
                    responses.append(response)
                    task_ids.remove(failed_task.task_id)

            if not task_ids:
                break

            await asyncio.sleep(0.1)

        # Tareas que no completaron en tiempo
        for remaining_task_id in task_ids:
            responses.append(XDRResponse(
                platform=XDRPlatform.CROWDSTRIKE,  # Default
                success=False,
                error_message="Export timeout"
            ))

        return responses

    async def get_coordination_status(self) -> Dict:
        """Obtener estado de coordinación XDR"""
        return {
            "coordinator_status": "running" if self.is_running else "stopped",
            "available_platforms": [platform.value for platform in self.coordinators.keys()],
            "active_workers": len(self.worker_tasks),
            "queue_size": self.export_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "recent_completions": [
                {
                    "task_id": task.task_id,
                    "platform": task.platform.value,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "processing_time_ms": response.processing_time_ms,
                    "success": response.success
                }
                for task, response in self.completed_tasks[-5:]  # Últimas 5
            ]
        }

# Factory function
def create_xdr_mcp_coordinator(config: Optional[Dict] = None) -> XDRMCPCoordinator:
    """Factory para crear coordinador XDR MCP"""
    if config is None:
        config = {
            "crowdstrike": {
                "enabled": True,
                "client_id": "demo_client_id",
                "client_secret": "demo_client_secret"
            },
            "sentinel": {
                "enabled": True,
                "workspace_id": "demo_workspace",
                "tenant_id": "demo_tenant"
            },
            "cisco_umbrella": {
                "enabled": True,
                "api_key": "demo_api_key",
                "customer_id": "demo_customer"
            },
            "num_workers": 3,
            "export_timeout": 30
        }

    return XDRMCPCoordinator(config)

# Ejemplo de uso
if __name__ == "__main__":
    async def test_xdr_coordination():
        # Crear coordinador
        coordinator = create_xdr_mcp_coordinator()
        await coordinator.start_coordination()

        # Datos de prueba
        test_threat = {
            "event_id": "xdr_test_001",
            "event_type": "advanced_persistent_threat",
            "source_ip": "192.168.1.50",
            "target_process": "svchost.exe",
            "severity": "critical"
        }

        test_hrm_analysis = {
            "hrm_analysis": {
                "final_assessment": {
                    "threat_level": "CRITICAL",
                    "confidence": 0.92
                },
                "analysis_modules": {
                    "threat_intelligence": {"category": "apt"},
                    "behavioral_analysis": {"confidence": 0.85}
                }
            }
        }

        test_business_context = {
            "business_unit": "finance",
            "compliance_frameworks": ["SOX", "PCI-DSS"],
            "asset_criticality": "critical",
            "risk_tolerance": "very_low"
        }

        # Ejecutar coordinación
        responses = await coordinator.coordinate_export(
            test_threat, test_hrm_analysis, test_business_context
        )

        print("XDR Coordination Results:")
        for response in responses:
            print(f"- {response.platform.value}: {'✅ Success' if response.success else '❌ Failed'}")
            if response.export_id:
                print(f"  Export ID: {response.export_id}")
            print(f"  Processing time: {response.processing_time_ms:.2f}ms")

        # Estado del coordinador
        status = await coordinator.get_coordination_status()
        print(f"\nCoordination Status:")
        print(json.dumps(status, indent=2))

        await coordinator.stop_coordination()

    # Ejecutar test
    asyncio.run(test_xdr_coordination())