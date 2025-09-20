#!/usr/bin/env python3
"""
SmartCompute Industrial Variable Configurator - Configuración Manual Avanzada de Variables

Configuraciones Técnicas Especializadas:
- Sistemas Eléctricos: Baja/Media/Alta tensión, Trifásico/Monofásico, AC/DC
- Líneas de Alimentación: Principal, Emergencia, UPS, Backup, Red
- Temperaturas Críticas: Ambientes fríos, conservación, caducidad
- Especificaciones de Instalación: Ubicación física, acceso, seguridad
- Mantenimiento y Calibración: Programas, certificaciones, trazabilidad

Author: SmartCompute Team
Version: 2.0.0 Variable Configurator
Date: 2025-09-19
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

# Enumeraciones para configuración técnica

class ElectricalVoltageClass(Enum):
    """Clasificación de voltaje eléctrico"""
    EXTRA_LOW = "extra_low"      # < 50V AC / < 120V DC
    LOW = "low"                  # 50-1000V AC / 120-1500V DC
    MEDIUM = "medium"            # 1-35 kV
    HIGH = "high"               # 35-138 kV
    EXTRA_HIGH = "extra_high"   # > 138 kV

class ElectricalPhaseType(Enum):
    """Tipo de sistema eléctrico"""
    SINGLE_PHASE = "single_phase"
    THREE_PHASE_WYE = "three_phase_wye"
    THREE_PHASE_DELTA = "three_phase_delta"
    DC_POSITIVE = "dc_positive"
    DC_NEGATIVE = "dc_negative"
    DC_BIPOLAR = "dc_bipolar"

class PowerSupplyType(Enum):
    """Tipo de suministro eléctrico"""
    MAIN_GRID = "main_grid"
    EMERGENCY_GENERATOR = "emergency_generator"
    UPS_SYSTEM = "ups_system"
    BATTERY_BACKUP = "battery_backup"
    SOLAR_PANEL = "solar_panel"
    REDUNDANT_SUPPLY = "redundant_supply"

class TemperatureApplication(Enum):
    """Aplicación de temperatura"""
    AMBIENT_MONITORING = "ambient_monitoring"
    EQUIPMENT_PROTECTION = "equipment_protection"
    COLD_STORAGE = "cold_storage"
    FREEZER_STORAGE = "freezer_storage"
    PROCESS_CONTROL = "process_control"
    SAFETY_SHUTDOWN = "safety_shutdown"

class SafetyClassification(Enum):
    """Clasificación de seguridad industrial"""
    SIL_0 = "sil_0"    # No safety function
    SIL_1 = "sil_1"    # Low safety integrity
    SIL_2 = "sil_2"    # Medium safety integrity
    SIL_3 = "sil_3"    # High safety integrity
    SIL_4 = "sil_4"    # Very high safety integrity

class MaintenanceType(Enum):
    """Tipo de mantenimiento"""
    PREDICTIVE = "predictive"
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    CONDITION_BASED = "condition_based"

@dataclass
class ElectricalSpecification:
    """Especificaciones técnicas eléctricas"""
    voltage_class: ElectricalVoltageClass
    phase_type: ElectricalPhaseType
    supply_type: PowerSupplyType
    nominal_voltage: float
    nominal_current: float
    nominal_frequency: float
    power_factor: Optional[float] = None
    harmonic_distortion: Optional[float] = None
    insulation_class: Optional[str] = None
    protection_class: Optional[str] = None  # IP rating
    grounding_type: Optional[str] = None
    cable_specifications: Optional[Dict] = None
    switchgear_type: Optional[str] = None

@dataclass
class TemperatureSpecification:
    """Especificaciones técnicas de temperatura"""
    application: TemperatureApplication
    measurement_range: Dict[str, float]  # min, max
    accuracy_class: str
    response_time: float  # seconds
    storage_requirements: Optional[Dict] = None
    expiry_monitoring: Optional[Dict] = None
    environmental_conditions: Optional[Dict] = None
    sensor_type: Optional[str] = None
    calibration_medium: Optional[str] = None

@dataclass
class StorageRequirement:
    """Requisitos de almacenamiento para productos"""
    product_category: str
    min_temperature: float
    max_temperature: float
    humidity_range: Dict[str, float]
    max_storage_time: timedelta
    expiry_alert_advance: timedelta
    quality_degradation_rate: Optional[float] = None
    regulatory_compliance: Optional[List[str]] = None

@dataclass
class MaintenanceSchedule:
    """Programa de mantenimiento"""
    maintenance_type: MaintenanceType
    frequency_days: int
    estimated_duration_hours: float
    required_personnel: List[str]
    required_tools: List[str]
    safety_procedures: List[str]
    documentation_required: bool = True
    shutdown_required: bool = False

@dataclass
class CalibrationInfo:
    """Información de calibración"""
    calibration_interval_days: int
    last_calibration: Optional[datetime] = None
    next_calibration: Optional[datetime] = None
    calibration_standard: Optional[str] = None
    uncertainty: Optional[float] = None
    certificate_number: Optional[str] = None
    calibration_laboratory: Optional[str] = None
    traceability_chain: Optional[List[str]] = None

class IndustrialVariableConfigurator:
    """Configurador avanzado de variables industriales"""

    def __init__(self):
        self.electrical_templates = self._load_electrical_templates()
        self.temperature_templates = self._load_temperature_templates()
        self.storage_templates = self._load_storage_templates()

    def _load_electrical_templates(self) -> Dict:
        """Plantillas de configuración eléctrica"""
        return {
            "low_voltage_main_supply": ElectricalSpecification(
                voltage_class=ElectricalVoltageClass.LOW,
                phase_type=ElectricalPhaseType.THREE_PHASE_WYE,
                supply_type=PowerSupplyType.MAIN_GRID,
                nominal_voltage=400.0,  # V
                nominal_current=100.0,  # A
                nominal_frequency=50.0,  # Hz
                power_factor=0.92,
                harmonic_distortion=5.0,  # %
                insulation_class="F",
                protection_class="IP54",
                grounding_type="TN-S",
                cable_specifications={
                    "type": "XLPE",
                    "section": "95 mm²",
                    "cores": 4,
                    "armour": "SWA"
                },
                switchgear_type="Air Circuit Breaker"
            ),

            "low_voltage_ups_supply": ElectricalSpecification(
                voltage_class=ElectricalVoltageClass.LOW,
                phase_type=ElectricalPhaseType.THREE_PHASE_WYE,
                supply_type=PowerSupplyType.UPS_SYSTEM,
                nominal_voltage=400.0,
                nominal_current=50.0,
                nominal_frequency=50.0,
                power_factor=0.95,
                harmonic_distortion=3.0,
                insulation_class="F",
                protection_class="IP54",
                grounding_type="TN-S",
                cable_specifications={
                    "type": "LSZH",
                    "section": "50 mm²",
                    "cores": 4,
                    "fire_rating": "Eca"
                },
                switchgear_type="MCCB"
            ),

            "medium_voltage_main": ElectricalSpecification(
                voltage_class=ElectricalVoltageClass.MEDIUM,
                phase_type=ElectricalPhaseType.THREE_PHASE_WYE,
                supply_type=PowerSupplyType.MAIN_GRID,
                nominal_voltage=11000.0,  # V
                nominal_current=1000.0,   # A
                nominal_frequency=50.0,
                power_factor=0.85,
                harmonic_distortion=8.0,
                insulation_class="F",
                protection_class="IP65",
                grounding_type="Resistance Grounded",
                cable_specifications={
                    "type": "XLPE-HV",
                    "section": "300 mm²",
                    "cores": 3,
                    "screen": "Copper Tape",
                    "insulation_level": "12/20/24 kV"
                },
                switchgear_type="Vacuum Circuit Breaker"
            ),

            "dc_system_24v": ElectricalSpecification(
                voltage_class=ElectricalVoltageClass.EXTRA_LOW,
                phase_type=ElectricalPhaseType.DC_POSITIVE,
                supply_type=PowerSupplyType.BATTERY_BACKUP,
                nominal_voltage=24.0,
                nominal_current=10.0,
                nominal_frequency=0.0,  # DC
                power_factor=None,      # N/A for DC
                harmonic_distortion=None,
                insulation_class="Basic",
                protection_class="IP20",
                grounding_type="Floating",
                cable_specifications={
                    "type": "PVC",
                    "section": "2.5 mm²",
                    "cores": 2,
                    "voltage_rating": "300/500V"
                },
                switchgear_type="DC Fuse"
            )
        }

    def _load_temperature_templates(self) -> Dict:
        """Plantillas de configuración de temperatura"""
        return {
            "ambient_monitoring": TemperatureSpecification(
                application=TemperatureApplication.AMBIENT_MONITORING,
                measurement_range={"min": -20.0, "max": 60.0},
                accuracy_class="Class A ±0.15°C",
                response_time=30.0,  # seconds
                environmental_conditions={
                    "humidity_range": "10-90% RH",
                    "vibration_resistance": "2g",
                    "electromagnetic_immunity": "EN 61326"
                },
                sensor_type="PT100 RTD",
                calibration_medium="Dry-block calibrator"
            ),

            "cold_storage_monitoring": TemperatureSpecification(
                application=TemperatureApplication.COLD_STORAGE,
                measurement_range={"min": -30.0, "max": 10.0},
                accuracy_class="Class AA ±0.1°C",
                response_time=15.0,
                storage_requirements={
                    "products": ["dairy", "meat", "vegetables"],
                    "regulatory": ["HACCP", "FDA", "EU 852/2004"]
                },
                expiry_monitoring={
                    "enabled": True,
                    "alert_days_before": 7,
                    "quality_tracking": True
                },
                environmental_conditions={
                    "humidity_range": "85-95% RH",
                    "air_circulation": "Required",
                    "defrost_cycles": "4x daily"
                },
                sensor_type="PT1000 RTD",
                calibration_medium="Ice point + boiling point"
            ),

            "freezer_storage_monitoring": TemperatureSpecification(
                application=TemperatureApplication.FREEZER_STORAGE,
                measurement_range={"min": -40.0, "max": -10.0},
                accuracy_class="Class AA ±0.1°C",
                response_time=20.0,
                storage_requirements={
                    "products": ["frozen_food", "pharmaceuticals", "biological_samples"],
                    "regulatory": ["HACCP", "FDA CFR 21", "EU GMP"]
                },
                expiry_monitoring={
                    "enabled": True,
                    "alert_days_before": 30,
                    "temperature_abuse_tracking": True,
                    "quality_degradation_model": "Arrhenius"
                },
                environmental_conditions={
                    "humidity_range": "90-95% RH",
                    "temperature_stability": "±0.5°C",
                    "alarm_delay": "5 minutes"
                },
                sensor_type="Thermocouple Type T",
                calibration_medium="Cryogenic calibrator"
            ),

            "equipment_protection": TemperatureSpecification(
                application=TemperatureApplication.EQUIPMENT_PROTECTION,
                measurement_range={"min": -10.0, "max": 150.0},
                accuracy_class="Class B ±0.3°C",
                response_time=5.0,  # Fast response for protection
                environmental_conditions={
                    "vibration_resistance": "5g",
                    "shock_resistance": "30g",
                    "ingress_protection": "IP67"
                },
                sensor_type="Thermocouple Type K",
                calibration_medium="Dry-block calibrator"
            )
        }

    def _load_storage_templates(self) -> Dict:
        """Plantillas de requisitos de almacenamiento"""
        return {
            "dairy_products": StorageRequirement(
                product_category="Dairy Products",
                min_temperature=2.0,
                max_temperature=4.0,
                humidity_range={"min": 80.0, "max": 90.0},
                max_storage_time=timedelta(days=7),
                expiry_alert_advance=timedelta(days=2),
                quality_degradation_rate=0.15,  # %/day above 4°C
                regulatory_compliance=["HACCP", "FDA Grade A", "EU 853/2004"]
            ),

            "frozen_vegetables": StorageRequirement(
                product_category="Frozen Vegetables",
                min_temperature=-18.0,
                max_temperature=-15.0,
                humidity_range={"min": 90.0, "max": 95.0},
                max_storage_time=timedelta(days=365),
                expiry_alert_advance=timedelta(days=30),
                quality_degradation_rate=0.02,  # %/day above -15°C
                regulatory_compliance=["HACCP", "USDA", "BRC Global Standard"]
            ),

            "pharmaceuticals": StorageRequirement(
                product_category="Pharmaceuticals",
                min_temperature=2.0,
                max_temperature=8.0,
                humidity_range={"min": 45.0, "max": 65.0},
                max_storage_time=timedelta(days=730),  # 2 years
                expiry_alert_advance=timedelta(days=90),
                quality_degradation_rate=0.05,  # %/day deviation
                regulatory_compliance=["FDA CFR 21", "EU GMP", "ICH Q1A", "WHO TRS"]
            ),

            "biological_samples": StorageRequirement(
                product_category="Biological Samples",
                min_temperature=-80.0,
                max_temperature=-70.0,
                humidity_range={"min": 10.0, "max": 30.0},
                max_storage_time=timedelta(days=1825),  # 5 years
                expiry_alert_advance=timedelta(days=180),
                quality_degradation_rate=1.0,   # Critical - any deviation
                regulatory_compliance=["FDA CFR 21", "ISO 20387", "CLIA"]
            )
        }

    def create_electrical_variable(self, base_config: dict, electrical_spec_name: str) -> dict:
        """Crear variable eléctrica con especificaciones técnicas"""
        if electrical_spec_name not in self.electrical_templates:
            raise ValueError(f"Electrical specification '{electrical_spec_name}' not found")

        electrical_spec = self.electrical_templates[electrical_spec_name]

        # Configuración técnica completa
        technical_specs = {
            "electrical": asdict(electrical_spec),
            "measurement_parameters": {
                "sampling_rate": 1000,  # Hz
                "filtering": "Anti-aliasing + Digital",
                "measurement_method": "True RMS",
                "accuracy_class": "0.2S",
                "burden": "< 0.1 VA"
            },
            "communication": {
                "protocol": "Modbus RTU",
                "baud_rate": 19200,
                "parity": "Even",
                "stop_bits": 1,
                "slave_address": 1
            }
        }

        # Especificaciones de instalación
        installation_details = {
            "location_type": self._get_location_type(electrical_spec),
            "mounting": "DIN Rail" if electrical_spec.voltage_class == ElectricalVoltageClass.LOW else "Panel Mount",
            "cable_routing": "Cable Tray" if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM else "Conduit",
            "earthing_requirements": electrical_spec.grounding_type,
            "safety_distances": self._get_safety_distances(electrical_spec),
            "access_level": "Authorized Personnel Only" if electrical_spec.voltage_class != ElectricalVoltageClass.EXTRA_LOW else "General Access"
        }

        # Programa de mantenimiento
        maintenance_schedule = MaintenanceSchedule(
            maintenance_type=MaintenanceType.PREVENTIVE,
            frequency_days=90 if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM else 180,
            estimated_duration_hours=2.0 if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM else 1.0,
            required_personnel=["Electrical Engineer", "Safety Officer"] if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM else ["Electrician"],
            required_tools=["Insulation Tester", "Multimeter", "Oscilloscope", "PPE"],
            safety_procedures=[
                "LOTO Procedure",
                "Electrical Safety Permit",
                "Arc Flash PPE" if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM else "Basic PPE"
            ],
            shutdown_required=electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM
        )

        # Información de calibración
        calibration_info = CalibrationInfo(
            calibration_interval_days=365,  # Anual
            calibration_standard="IEC 61557",
            uncertainty=0.2,  # %
            certificate_number=f"CAL-{electrical_spec_name.upper()}-{datetime.now().year}",
            calibration_laboratory="Accredited Electrical Calibration Lab",
            traceability_chain=["National Standards", "Primary Standards", "Working Standards"]
        )

        # Completar configuración base
        enhanced_config = base_config.copy()
        enhanced_config.update({
            "technical_specs": technical_specs,
            "safety_classification": self._get_safety_classification(electrical_spec).value,
            "maintenance_schedule": asdict(maintenance_schedule),
            "calibration_info": asdict(calibration_info),
            "installation_details": installation_details
        })

        return enhanced_config

    def create_temperature_variable(self, base_config: dict, temperature_spec_name: str, storage_spec_name: Optional[str] = None) -> dict:
        """Crear variable de temperatura con especificaciones técnicas"""
        if temperature_spec_name not in self.temperature_templates:
            raise ValueError(f"Temperature specification '{temperature_spec_name}' not found")

        temperature_spec = self.temperature_templates[temperature_spec_name]

        # Configuración técnica completa
        technical_specs = {
            "temperature": asdict(temperature_spec),
            "measurement_parameters": {
                "resolution": "0.01°C",
                "stability": "±0.02°C/year",
                "self_heating": "< 0.1°C",
                "time_constant": f"{temperature_spec.response_time}s"
            },
            "communication": {
                "protocol": "4-20mA + HART",
                "update_rate": "1 second",
                "diagnostic_capability": "Enhanced",
                "configuration_tool": "HART Communicator"
            }
        }

        # Requisitos de almacenamiento si aplica
        if storage_spec_name and storage_spec_name in self.storage_templates:
            storage_req = self.storage_templates[storage_spec_name]
            technical_specs["storage_requirements"] = asdict(storage_req)

        # Especificaciones de instalación para temperatura
        installation_details = {
            "location_type": "Process Area" if temperature_spec.application == TemperatureApplication.PROCESS_CONTROL else "Storage Area",
            "mounting": "Thermowell" if temperature_spec.sensor_type and "thermocouple" in temperature_spec.sensor_type.lower() else "Direct Immersion",
            "protection_tube": "316L Stainless Steel",
            "insertion_length": "150mm",
            "thread_connection": "1/2\" NPT",
            "environmental_rating": temperature_spec.environmental_conditions.get("ingress_protection", "IP65") if temperature_spec.environmental_conditions else "IP65"
        }

        # Programa de mantenimiento para temperatura
        maintenance_schedule = MaintenanceSchedule(
            maintenance_type=MaintenanceType.CONDITION_BASED,
            frequency_days=180 if temperature_spec.application == TemperatureApplication.COLD_STORAGE else 90,
            estimated_duration_hours=0.5,
            required_personnel=["Instrument Technician"],
            required_tools=["Temperature Calibrator", "Precision Thermometer", "Insulation Tester"],
            safety_procedures=[
                "Process Isolation",
                "Temperature Calibrator Safety",
                "Cold Storage PPE" if temperature_spec.application == TemperatureApplication.COLD_STORAGE else "Standard PPE"
            ],
            shutdown_required=False
        )

        # Información de calibración para temperatura
        calibration_info = CalibrationInfo(
            calibration_interval_days=180,  # Semestral para temperaturas críticas
            calibration_standard="ITS-90",
            uncertainty=float(temperature_spec.accuracy_class.split('±')[1].replace('°C', '')) if '±' in temperature_spec.accuracy_class else 0.1,
            certificate_number=f"TEMP-CAL-{temperature_spec_name.upper()}-{datetime.now().year}",
            calibration_laboratory="NIST Traceable Temperature Lab",
            traceability_chain=["ITS-90", "NIST Standards", "Working Standards"]
        )

        # Completar configuración base
        enhanced_config = base_config.copy()
        enhanced_config.update({
            "technical_specs": technical_specs,
            "safety_classification": SafetyClassification.SIL_2.value if temperature_spec.application == TemperatureApplication.SAFETY_SHUTDOWN else SafetyClassification.SIL_1.value,
            "maintenance_schedule": asdict(maintenance_schedule),
            "calibration_info": asdict(calibration_info),
            "installation_details": installation_details
        })

        return enhanced_config

    def _get_location_type(self, electrical_spec: ElectricalSpecification) -> str:
        """Determinar tipo de ubicación según especificaciones eléctricas"""
        if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM:
            return "Electrical Substation"
        elif electrical_spec.supply_type == PowerSupplyType.UPS_SYSTEM:
            return "UPS Room"
        elif electrical_spec.supply_type == PowerSupplyType.EMERGENCY_GENERATOR:
            return "Generator Room"
        else:
            return "Electrical Room"

    def _get_safety_distances(self, electrical_spec: ElectricalSpecification) -> Dict[str, str]:
        """Obtener distancias de seguridad según voltaje"""
        if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM:
            return {
                "minimum_approach": "1.0 m",
                "working_distance": "1.5 m",
                "arc_flash_boundary": "2.5 m",
                "confined_space": "Not Applicable"
            }
        elif electrical_spec.voltage_class == ElectricalVoltageClass.LOW:
            return {
                "minimum_approach": "0.3 m",
                "working_distance": "0.5 m",
                "arc_flash_boundary": "1.2 m",
                "confined_space": "0.6 m"
            }
        else:
            return {
                "minimum_approach": "0.1 m",
                "working_distance": "0.3 m",
                "arc_flash_boundary": "N/A",
                "confined_space": "0.3 m"
            }

    def _get_safety_classification(self, electrical_spec: ElectricalSpecification) -> SafetyClassification:
        """Determinar clasificación de seguridad"""
        if electrical_spec.voltage_class == ElectricalVoltageClass.MEDIUM:
            return SafetyClassification.SIL_3
        elif electrical_spec.supply_type == PowerSupplyType.EMERGENCY_GENERATOR:
            return SafetyClassification.SIL_2
        else:
            return SafetyClassification.SIL_1

    def create_configuration_examples(self) -> Dict:
        """Crear ejemplos de configuración completa"""
        examples = {}

        # Ejemplo 1: Línea principal trifásica 400V
        examples["main_power_line_400v"] = self.create_electrical_variable(
            base_config={
                "id": "voltage_main_l1_l2",
                "name": "Main Power Line L1-L2 Voltage",
                "description": "Voltage between Line 1 and Line 2 on main 400V supply",
                "variable_type": "electrical",
                "unit": "V",
                "min_value": 0.0,
                "max_value": 500.0,
                "nominal_value": 400.0,
                "warning_low": 380.0,
                "warning_high": 420.0,
                "alarm_low": 360.0,
                "alarm_high": 440.0,
                "location": "Main Electrical Room - Panel A1",
                "plc_address": "40001",
                "update_rate_ms": 1000
            },
            electrical_spec_name="low_voltage_main_supply"
        )

        # Ejemplo 2: Sistema UPS crítico
        examples["ups_critical_supply"] = self.create_electrical_variable(
            base_config={
                "id": "voltage_ups_critical",
                "name": "UPS Critical Load Voltage",
                "description": "UPS system voltage for critical loads",
                "variable_type": "electrical",
                "unit": "V",
                "min_value": 0.0,
                "max_value": 450.0,
                "nominal_value": 400.0,
                "warning_low": 390.0,
                "warning_high": 410.0,
                "alarm_low": 380.0,
                "alarm_high": 420.0,
                "location": "UPS Room - Critical Panel",
                "plc_address": "40101",
                "update_rate_ms": 500  # Más rápido para críticos
            },
            electrical_spec_name="low_voltage_ups_supply"
        )

        # Ejemplo 3: Temperatura de cámara frigorífica
        examples["cold_storage_temperature"] = self.create_temperature_variable(
            base_config={
                "id": "temp_cold_storage_zone_a",
                "name": "Cold Storage Zone A Temperature",
                "description": "Temperature monitoring for dairy products storage",
                "variable_type": "thermal",
                "unit": "°C",
                "min_value": -5.0,
                "max_value": 15.0,
                "nominal_value": 3.0,
                "warning_low": 1.0,
                "warning_high": 5.0,
                "alarm_low": -1.0,
                "alarm_high": 7.0,
                "location": "Cold Storage Zone A - Dairy Section",
                "plc_address": "40201",
                "update_rate_ms": 5000  # Cada 5 segundos
            },
            temperature_spec_name="cold_storage_monitoring",
            storage_spec_name="dairy_products"
        )

        # Ejemplo 4: Temperatura de congelador farmacéutico
        examples["pharma_freezer_temperature"] = self.create_temperature_variable(
            base_config={
                "id": "temp_pharma_freezer_main",
                "name": "Pharmaceutical Freezer Main Temperature",
                "description": "Critical temperature monitoring for pharmaceutical storage",
                "variable_type": "thermal",
                "unit": "°C",
                "min_value": -25.0,
                "max_value": -10.0,
                "nominal_value": -18.0,
                "warning_low": -20.0,
                "warning_high": -16.0,
                "alarm_low": -22.0,
                "alarm_high": -14.0,
                "location": "Pharmaceutical Storage - Freezer Unit 1",
                "plc_address": "40301",
                "update_rate_ms": 2000  # Cada 2 segundos - crítico
            },
            temperature_spec_name="freezer_storage_monitoring",
            storage_spec_name="pharmaceuticals"
        )

        # Ejemplo 5: Sistema DC 24V para control
        examples["control_system_24vdc"] = self.create_electrical_variable(
            base_config={
                "id": "voltage_control_24vdc",
                "name": "Control System 24VDC Supply",
                "description": "24VDC power supply for control instrumentation",
                "variable_type": "electrical",
                "unit": "V",
                "min_value": 0.0,
                "max_value": 30.0,
                "nominal_value": 24.0,
                "warning_low": 22.0,
                "warning_high": 26.0,
                "alarm_low": 20.0,
                "alarm_high": 28.0,
                "location": "Control Room - DC Panel",
                "plc_address": "40401",
                "update_rate_ms": 2000
            },
            electrical_spec_name="dc_system_24v"
        )

        return examples

    def save_configuration_templates(self, file_path: str):
        """Guardar plantillas de configuración"""
        templates = {
            "electrical_templates": {name: asdict(spec) for name, spec in self.electrical_templates.items()},
            "temperature_templates": {name: asdict(spec) for name, spec in self.temperature_templates.items()},
            "storage_templates": {name: asdict(spec) for name, spec in self.storage_templates.items()},
            "configuration_examples": self.create_configuration_examples()
        }

        with open(file_path, 'w') as f:
            json.dump(templates, f, indent=2, default=str)

        print(f"📝 Configuration templates saved to: {file_path}")

def main():
    """Función principal para generar configuraciones"""
    print("🔧 SmartCompute Industrial Variable Configurator")
    print("=" * 60)

    configurator = IndustrialVariableConfigurator()

    # Generar ejemplos de configuración
    examples = configurator.create_configuration_examples()

    print(f"✅ Generated {len(examples)} configuration examples:")
    for name, config in examples.items():
        print(f"  • {name}: {config['name']}")

    # Mostrar ejemplo detallado
    print("\n📋 Example Configuration - Main Power Line 400V:")
    main_power = examples["main_power_line_400v"]
    print(f"  Name: {main_power['name']}")
    print(f"  Location: {main_power['location']}")
    print(f"  Voltage Class: {main_power['technical_specs']['electrical']['voltage_class']}")
    print(f"  Phase Type: {main_power['technical_specs']['electrical']['phase_type']}")
    print(f"  Supply Type: {main_power['technical_specs']['electrical']['supply_type']}")
    print(f"  Safety Classification: {main_power['safety_classification']}")

    print("\n📋 Example Configuration - Cold Storage Temperature:")
    cold_storage = examples["cold_storage_temperature"]
    print(f"  Name: {cold_storage['name']}")
    print(f"  Location: {cold_storage['location']}")
    print(f"  Range: {cold_storage['min_value']}°C to {cold_storage['max_value']}°C")
    print(f"  Application: {cold_storage['technical_specs']['temperature']['application']}")
    print(f"  Sensor Type: {cold_storage['technical_specs']['temperature']['sensor_type']}")
    if 'storage_requirements' in cold_storage['technical_specs']:
        storage = cold_storage['technical_specs']['storage_requirements']
        print(f"  Product Category: {storage['product_category']}")
        print(f"  Max Storage Time: {storage['max_storage_time']}")

    # Guardar plantillas
    configurator.save_configuration_templates("industrial_configuration_templates.json")

if __name__ == "__main__":
    main()