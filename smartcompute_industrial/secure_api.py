#!/usr/bin/env python3
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from secure_demo import get_secure_plc_data

app = FastAPI(title="SmartCompute Industrial Secure API", version="1.0.0", description="Secure API for industrial PLC data monitoring")

# Permitir acceso desde cualquier origen (para pruebas; en producción, limitar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key para acceso seguro
API_KEY = "mi_clave_secreta_123"

@app.get("/")
async def root():
    return {"message": "SmartCompute Industrial Secure API", "version": "1.0.0", "status": "active"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "smartcompute-industrial"}

@app.get("/api/sensors")
async def read_sensors(x_api_key: str = Header(...)):
    """
    Obtener datos seguros de sensores PLC
    
    Requiere header X-API-Key para autenticación
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    
    try:
        # Obtener datos seguros de PLC
        data = get_secure_plc_data()
        return {
            "success": True,
            "timestamp": "2025-08-28T09:40:00Z",
            "data": data,
            "device_count": len(data) if isinstance(data, dict) else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/sensors/status")
async def sensors_status(x_api_key: str = Header(...)):
    """
    Obtener estado de conectividad de sensores
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    
    try:
        data = get_secure_plc_data()
        device_statuses = {}
        
        if isinstance(data, dict):
            for device_id, values in data.items():
                if isinstance(values, dict) and 'status' in values:
                    device_statuses[f"device_{device_id}"] = {
                        "online": values['status'] > 0,
                        "status_value": values['status'],
                        "temperature": values.get('temperature', 0),
                        "efficiency": values.get('efficiency', 0)
                    }
        
        return {
            "success": True,
            "device_statuses": device_statuses,
            "total_devices": len(device_statuses),
            "online_devices": sum(1 for status in device_statuses.values() if status["online"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sensor status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SmartCompute Industrial Secure API...")
    print("📡 API will be available at: http://127.0.0.1:8000")
    print("📋 Documentation at: http://127.0.0.1:8000/docs")
    print("🔑 Use X-API-Key header with value: mi_clave_secreta_123")
    uvicorn.run(app, host="127.0.0.1", port=8000)