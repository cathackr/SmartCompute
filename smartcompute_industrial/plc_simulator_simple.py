#!/usr/bin/env python3
"""
SmartCompute Industrial - Simulador PLC Básico
Simulador simple de dispositivos industriales para testing
"""

import asyncio
import time
import random
import math
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PLCDevice:
    """Configuración de dispositivo PLC simulado"""
    name: str
    device_id: int
    ip_address: str = "127.0.0.1"
    port: int = 502
    simulation_type: str = "industrial_process"
    update_interval: float = 1.0

class IndustrialProcessSimulator:
    """Simulador de procesos industriales realistas"""
    
    def __init__(self, device_config: PLCDevice):
        self.config = device_config
        self.current_values = {}
        self.base_values = {}
        self.anomaly_mode = False
        self.anomaly_start_time = 0
        self.cycle_time = 0
        
        self.initialize_base_values()
        logger.info(f"🏭 Simulador inicializado para {device_config.name}")
    
    def initialize_base_values(self):
        """Inicializar valores base del proceso"""
        if self.config.simulation_type == "industrial_process":
            self.base_values = {
                "temperature": 85.0,  # °C
                "pressure": 2.5,      # bar
                "flow_rate": 150.0,   # L/min
                "vibration": 0.1,     # mm/s
                "power": 75.0,        # kW
                "speed": 1450.0,      # RPM
                "efficiency": 92.0,   # %
                "status": 1           # 1=Running, 0=Stopped
            }
        elif self.config.simulation_type == "motor_drive":
            self.base_values = {
                "temperature": 65.0,
                "pressure": 0.0,
                "flow_rate": 0.0,
                "vibration": 0.05,
                "power": 45.0,
                "speed": 1200.0,
                "efficiency": 94.0,
                "status": 1
            }
        elif self.config.simulation_type == "hvac_system":
            self.base_values = {
                "temperature": 22.0,  # °C ambiente
                "pressure": 1.2,      # bar
                "flow_rate": 300.0,   # m³/h
                "vibration": 0.02,
                "power": 25.0,
                "speed": 850.0,
                "efficiency": 88.0,
                "status": 1
            }
        
        self.current_values = self.base_values.copy()
    
    def update_values(self):
        """Actualizar valores simulados"""
        self.cycle_time += self.config.update_interval
        current_time = time.time()
        
        # Patrón cíclico base
        cycle_factor = math.sin(self.cycle_time * 0.1) * 0.1
        
        for param, base_value in self.base_values.items():
            # Variación cíclica normal
            cyclic_variation = base_value * cycle_factor
            
            # Ruido aleatorio pequeño
            noise = random.gauss(0, base_value * 0.02)
            
            # Aplicar anomalías si están activas
            anomaly_factor = self.get_anomaly_factor(param, current_time)
            
            # Calcular valor final
            new_value = base_value + cyclic_variation + noise + anomaly_factor
            
            # Aplicar límites realistas
            new_value = self.apply_realistic_limits(param, new_value)
            
            self.current_values[param] = round(new_value, 2)
        
        # Lógica de estado
        self.update_status_logic()
    
    def get_anomaly_factor(self, param: str, current_time: float) -> float:
        """Calcular factor de anomalía para parámetro"""
        if not self.anomaly_mode:
            return 0.0
        
        elapsed = current_time - self.anomaly_start_time
        base_value = self.base_values[param]
        
        # Diferentes tipos de anomalías según el parámetro
        if param == "temperature" and elapsed < 300:  # 5 minutos
            return base_value * 0.3 * math.exp(-elapsed / 100)
        elif param == "vibration" and elapsed < 180:  # 3 minutos
            return base_value * 2.0 * (1 + math.sin(elapsed * 2))
        elif param == "pressure" and elapsed < 240:  # 4 minutos
            return base_value * -0.2 * math.cos(elapsed / 30)
        elif param == "efficiency" and elapsed < 600:  # 10 minutos
            return -base_value * 0.15 * (elapsed / 600)
        
        return 0.0
    
    def apply_realistic_limits(self, param: str, value: float) -> float:
        """Aplicar límites realistas a los parámetros"""
        limits = {
            "temperature": (0, 150),
            "pressure": (0, 10),
            "flow_rate": (0, 500),
            "vibration": (0, 5),
            "power": (0, 200),
            "speed": (0, 3000),
            "efficiency": (0, 100),
            "status": (0, 1)
        }
        
        if param in limits:
            min_val, max_val = limits[param]
            return max(min_val, min(max_val, value))
        
        return value
    
    def update_status_logic(self):
        """Actualizar lógica de estado del dispositivo"""
        # Auto-parada por condiciones críticas
        if (self.current_values["temperature"] > 120 or 
            self.current_values["vibration"] > 2.0 or
            self.current_values["pressure"] < 0.5):
            self.current_values["status"] = 0
        elif self.current_values["status"] == 0 and random.random() < 0.01:
            # Reinicio automático aleatorio
            self.current_values["status"] = 1
    
    def trigger_anomaly(self, duration: float = 300):
        """Activar modo anomalía"""
        self.anomaly_mode = True
        self.anomaly_start_time = time.time()
        logger.warning(f"🚨 Anomalía activada en {self.config.name} por {duration}s")
        
        # Programar desactivación
        asyncio.create_task(self.deactivate_anomaly_after(duration))
    
    async def deactivate_anomaly_after(self, duration: float):
        """Desactivar anomalía después de duración especificada"""
        await asyncio.sleep(duration)
        self.anomaly_mode = False
        logger.info(f"✅ Anomalía desactivada en {self.config.name}")

class PLCSimulator:
    """Simulador básico de PLCs sin dependencia de pymodbus"""
    
    def __init__(self, devices: List[PLCDevice]):
        self.devices = devices
        self.simulators = {}
        self.running = False
        
        # Crear simuladores para cada dispositivo
        for device in devices:
            self.simulators[device.device_id] = IndustrialProcessSimulator(device)
        
        logger.info(f"🔧 Simulador básico inicializado con {len(devices)} dispositivos")
    
    async def update_loop(self):
        """Loop de actualización continua"""
        while self.running:
            try:
                for simulator in self.simulators.values():
                    simulator.update_values()
                
                await asyncio.sleep(1.0)  # Actualizar cada segundo
                
            except Exception as e:
                logger.error(f"Error en loop de actualización: {e}")
                await asyncio.sleep(1.0)
    
    async def start_simulation(self):
        """Iniciar simulación"""
        logger.info("🚀 Iniciando simulación de PLCs...")
        self.running = True
        
        try:
            await self.update_loop()
        except KeyboardInterrupt:
            logger.info("⏹️ Simulación interrumpida por usuario")
        finally:
            self.running = False
    
    def stop_simulation(self):
        """Detener simulación"""
        logger.info("⏹️ Deteniendo simulación...")
        self.running = False
    
    def trigger_device_anomaly(self, device_id: int, duration: float = 300):
        """Activar anomalía en dispositivo específico"""
        if device_id in self.simulators:
            self.simulators[device_id].trigger_anomaly(duration)
        else:
            logger.warning(f"Dispositivo {device_id} no encontrado")
    
    def get_device_status(self) -> Dict[int, Dict]:
        """Obtener estado de todos los dispositivos"""
        status = {}
        for device_id, simulator in self.simulators.items():
            device_name = next(d.name for d in self.devices if d.device_id == device_id)
            status[device_id] = {
                "name": device_name,
                "values": simulator.current_values.copy(),
                "anomaly_active": simulator.anomaly_mode,
                "cycle_time": simulator.cycle_time,
                "simulation_type": simulator.config.simulation_type
            }
        return status
    
    def get_modbus_registers(self, device_id: int) -> Dict[int, int]:
        """Simular registros Modbus (para compatibilidad)"""
        if device_id not in self.simulators:
            return {}
        
        simulator = self.simulators[device_id]
        registers = {}
        base_addr = 40001 + (device_id - 1) * 10
        
        for i, (param, value) in enumerate(simulator.current_values.items()):
            if param == "temperature":
                registers[base_addr + i] = int(value * 10)  # 0.1°C resolución
            elif param == "pressure":
                registers[base_addr + i] = int(value * 100)  # 0.01 bar resolución
            elif param == "flow_rate":
                registers[base_addr + i] = int(value * 10)  # 0.1 L/min resolución
            elif param == "vibration":
                registers[base_addr + i] = int(value * 1000)  # 0.001 mm/s resolución
            elif param == "power":
                registers[base_addr + i] = int(value * 10)  # 0.1 kW resolución
            elif param == "speed":
                registers[base_addr + i] = int(value)  # 1 RPM resolución
            elif param == "efficiency":
                registers[base_addr + i] = int(value * 10)  # 0.1% resolución
            else:
                registers[base_addr + i] = int(value)
        
        return registers

def create_default_devices() -> List[PLCDevice]:
    """Crear dispositivos PLC por defecto"""
    return [
        PLCDevice(
            name="Bomba Principal",
            device_id=1,
            simulation_type="industrial_process"
        ),
        PLCDevice(
            name="Motor Compresor",
            device_id=2,
            simulation_type="motor_drive"
        ),
        PLCDevice(
            name="Sistema HVAC",
            device_id=3,
            simulation_type="hvac_system"
        )
    ]

def print_status_table(simulator: PLCSimulator):
    """Imprimir tabla de estado de dispositivos"""
    status = simulator.get_device_status()
    
    print("\n" + "="*80)
    print(f"📊 ESTADO DE DISPOSITIVOS SIMULADOS - {datetime.now().strftime('%H:%M:%S')}")
    print("="*80)
    
    for device_id, device_status in status.items():
        anomaly_indicator = "🚨 ANOMALÍA" if device_status["anomaly_active"] else "✅ NORMAL"
        print(f"\n🔧 {device_status['name']} (ID: {device_id}) - {anomaly_indicator}")
        print("-" * 40)
        
        for param, value in device_status["values"].items():
            if param == "status":
                display_value = "🟢 ACTIVO" if value > 0 else "🔴 PARADO"
            elif param == "temperature":
                display_value = f"{value}°C"
            elif param == "pressure":
                display_value = f"{value} bar"
            elif param == "flow_rate":
                display_value = f"{value} L/min"
            elif param == "vibration":
                display_value = f"{value} mm/s"
            elif param == "power":
                display_value = f"{value} kW"
            elif param == "speed":
                display_value = f"{value} RPM"
            elif param == "efficiency":
                display_value = f"{value}%"
            else:
                display_value = str(value)
            
            param_name = param.replace("_", " ").title()
            print(f"   {param_name:15}: {display_value}")
        
        print(f"   {'Tiempo Ciclo':15}: {device_status['cycle_time']:.1f}s")
        print(f"   {'Tipo':15}: {device_status['simulation_type']}")

async def run_interactive_simulator():
    """Ejecutar simulador en modo interactivo"""
    devices = create_default_devices()
    simulator = PLCSimulator(devices)
    
    print("🏭 SmartCompute Industrial - Simulador PLC")
    print("="*60)
    print(f"📊 Dispositivos configurados: {len(devices)}")
    for device in devices:
        print(f"   • ID {device.device_id}: {device.name} ({device.simulation_type})")
    
    print("\n🎮 Comandos interactivos:")
    print("   • 's' - Mostrar estado actual")
    print("   • 'a<ID>' - Activar anomalía en dispositivo (ej: a1)")
    print("   • 'q' - Salir")
    print("   • Enter - Actualizar automáticamente")
    print("="*60)
    
    # Iniciar simulación en background
    simulation_task = asyncio.create_task(simulator.start_simulation())
    
    try:
        last_status_time = 0
        while True:
            # Mostrar estado cada 10 segundos automáticamente
            current_time = time.time()
            if current_time - last_status_time > 10:
                print_status_table(simulator)
                last_status_time = current_time
            
            # Procesar entrada del usuario (no bloqueante)
            try:
                # Simular input no bloqueante con timeout corto
                await asyncio.sleep(0.1)
                
                # En producción usar aioconsole o similar para input async
                # Por ahora solo auto-actualización
                
            except KeyboardInterrupt:
                break
    
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo simulador...")
    finally:
        simulator.stop_simulation()
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass

async def run_data_export_mode(output_file: str = "plc_simulation_data.json"):
    """Ejecutar simulador y exportar datos a archivo"""
    devices = create_default_devices()
    simulator = PLCSimulator(devices)
    
    print(f"📊 Modo exportación de datos - guardando en {output_file}")
    
    data_log = []
    simulator.running = True
    
    try:
        for i in range(100):  # Generar 100 puntos de datos
            # Actualizar simuladores
            for sim in simulator.simulators.values():
                sim.update_values()
            
            # Capturar estado
            timestamp = datetime.now().isoformat()
            status = simulator.get_device_status()
            
            data_point = {
                "timestamp": timestamp,
                "devices": status
            }
            data_log.append(data_point)
            
            # Activar algunas anomalías para variedad
            if i == 30:
                simulator.trigger_device_anomaly(1, 60)
            elif i == 60:
                simulator.trigger_device_anomaly(2, 90)
            
            print(f"   Generando datos... {i+1}/100", end="\r")
            await asyncio.sleep(0.5)
        
        # Guardar datos
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_log, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Datos exportados: {output_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Exportación interrumpida")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SmartCompute Industrial PLC Simulator")
    parser.add_argument("--mode", choices=["interactive", "export"], default="interactive", 
                       help="Modo de operación")
    parser.add_argument("--output", default="plc_simulation_data.json", 
                       help="Archivo de salida para modo export")
    parser.add_argument("--devices", type=int, default=3, 
                       help="Número de dispositivos a simular")
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        if args.mode == "interactive":
            print("🎮 Iniciando modo interactivo...")
            asyncio.run(run_interactive_simulator())
        elif args.mode == "export":
            print("📊 Iniciando modo exportación...")
            asyncio.run(run_data_export_mode(args.output))
    except KeyboardInterrupt:
        print("\n👋 Simulador terminado")

if __name__ == "__main__":
    main()