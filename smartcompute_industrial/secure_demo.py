#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security import secure_sensor_data, save_secure_json
from plc_simulator_simple import PLCSimulator, create_default_devices

def get_secure_plc_data():
    devices = create_default_devices()
    simulator = PLCSimulator(devices)
    
    # Actualizar una vez los valores
    for sim in simulator.simulators.values():
        sim.update_values()
    
    raw_data = simulator.get_device_status()
    hash_keys = ["name"]
    encrypt_keys = ["simulation_type"]
    secured_data = secure_sensor_data(
        raw_data,
        hash_keys=hash_keys,
        encrypt_keys=encrypt_keys
    )
    save_secure_json(secured_data, "secured_sensors.json")
    return secured_data

async def monitor_secure_data():
    while True:
        data = get_secure_plc_data()
        print("🔹 Datos seguros PLC:", data)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_secure_data())
