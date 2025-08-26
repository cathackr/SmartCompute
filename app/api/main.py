"""
SmartCompute FastAPI Application
Performance-based anomaly detection API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import time
import asyncio
import json
from contextlib import asynccontextmanager

from ..core.smart_compute import SmartComputeEngine
from ..core.portable_system import PortableSystemDetector
from ..services.monitoring import MonitoringService
from ..services.crypto_payments import (
    crypto_service, 
    CryptoPaymentRequest, 
    PaymentResponse
)


class SystemInfo(BaseModel):
    """System information response model"""
    os: str
    architecture: str
    cpu_model: str
    cpu_cores: int
    ram_gb: float
    gpu_type: str


class OptimizationRequest(BaseModel):
    """Optimization request parameters"""
    precision_needed: float = 0.95
    speed_priority: float = 0.5
    enable_verbose: bool = True


class AnomalyResponse(BaseModel):
    """Anomaly detection response"""
    anomaly_score: float
    severity: str
    cpu_current: float
    memory_current: float
    timestamp: str


class PerformanceReport(BaseModel):
    """Performance report model"""
    system_profile: Dict[str, Any]
    optimization_applied: Dict[str, Any]
    security_status: Dict[str, Any]
    recommendations: List[str]
    timestamp: str


# Global instances
smart_engine: Optional[SmartComputeEngine] = None
portable_detector: Optional[PortableSystemDetector] = None
monitoring_service: Optional[MonitoringService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global smart_engine, portable_detector, monitoring_service
    
    # Initialize services
    print("🚀 Initializing SmartCompute services...")
    smart_engine = SmartComputeEngine()
    portable_detector = PortableSystemDetector()
    monitoring_service = MonitoringService(portable_detector)
    
    print("✅ SmartCompute API ready!")
    yield
    
    # Cleanup
    print("🔧 Shutting down SmartCompute services...")
    if monitoring_service:
        await monitoring_service.stop()


app = FastAPI(
    title="SmartCompute API",
    description="Performance-based anomaly detection for security monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SmartCompute API - Performance-based anomaly detection",
        "version": "1.0.0",
        "author": "Gatux - Certified Ethical Hacker",
        "endpoints": {
            "system_info": "/system-info",
            "optimize": "/optimize",
            "anomaly_detection": "/detect-anomalies",
            "performance_report": "/performance-report",
            "monitoring": "/monitoring"
        }
    }


@app.get("/system-info", response_model=SystemInfo)
async def get_system_info():
    """Get current system information and capabilities"""
    if not portable_detector:
        raise HTTPException(status_code=500, detail="Portable detector not initialized")
    
    info = portable_detector.system_info
    return SystemInfo(
        os=info['os'],
        architecture=info['arch'],
        cpu_model=info['cpu_model'],
        cpu_cores=info['cpu_cores'],
        ram_gb=info['ram_gb'],
        gpu_type=info['gpu_type']
    )


@app.post("/optimize")
async def optimize_computation(request: OptimizationRequest):
    """Perform intelligent computation optimization"""
    if not smart_engine:
        raise HTTPException(status_code=500, detail="SmartCompute engine not initialized")
    
    # Create sample matrices for demonstration
    import numpy as np
    np.random.seed(42)
    matrix_a = np.random.rand(500, 500)
    matrix_b = np.random.rand(500, 500)
    
    try:
        result = smart_engine.smart_multiply(
            matrix_a, 
            matrix_b,
            precision_needed=request.precision_needed,
            speed_priority=request.speed_priority,
            verbose=request.enable_verbose
        )
        
        # Remove the actual result matrix for API response (too large)
        api_result = {
            "method": result["method"],
            "time": result["time"],
            "accuracy": result["accuracy"],
            "speedup": result["speedup"],
            "meets_precision": result["meets_precision"],
            "choice": result["choice"],
            "metrics": result["metrics"]
        }
        
        return api_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/detect-anomalies", response_model=AnomalyResponse)
async def detect_anomalies():
    """Detect performance anomalies in real-time"""
    if not portable_detector:
        raise HTTPException(status_code=500, detail="Portable detector not initialized")
    
    try:
        anomaly_result = portable_detector.detect_anomalies()
        
        if 'error' in anomaly_result:
            raise HTTPException(status_code=400, detail=anomaly_result['error'])
        
        return AnomalyResponse(
            anomaly_score=anomaly_result['anomaly_score'],
            severity=anomaly_result['severity'],
            cpu_current=anomaly_result['cpu_current'],
            memory_current=anomaly_result['memory_current'],
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@app.post("/establish-baseline")
async def establish_baseline(duration: int = 30):
    """Establish performance baseline for anomaly detection"""
    if not portable_detector:
        raise HTTPException(status_code=500, detail="Portable detector not initialized")
    
    if duration < 10 or duration > 300:
        raise HTTPException(status_code=400, detail="Duration must be between 10 and 300 seconds")
    
    try:
        baseline = portable_detector.run_performance_baseline(duration)
        return {
            "message": f"Baseline established over {duration} seconds",
            "baseline_metrics": baseline,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Baseline establishment failed: {str(e)}")


@app.get("/performance-report", response_model=PerformanceReport)
async def get_performance_report():
    """Generate comprehensive performance and security report"""
    if not portable_detector:
        raise HTTPException(status_code=500, detail="Portable detector not initialized")
    
    try:
        report = portable_detector.generate_report()
        return PerformanceReport(**report)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/performance-history")
async def get_performance_history():
    """Get performance optimization history"""
    if not smart_engine:
        raise HTTPException(status_code=500, detail="SmartCompute engine not initialized")
    
    try:
        summary = smart_engine.get_performance_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@app.post("/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start continuous monitoring service"""
    if not monitoring_service:
        raise HTTPException(status_code=500, detail="Monitoring service not initialized")
    
    try:
        success = await monitoring_service.start_monitoring()
        if success:
            return {"message": "Monitoring started successfully", "status": "active"}
        else:
            raise HTTPException(status_code=400, detail="Monitoring already active")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@app.post("/monitoring/stop")
async def stop_monitoring():
    """Stop continuous monitoring service"""
    if not monitoring_service:
        raise HTTPException(status_code=500, detail="Monitoring service not initialized")
    
    try:
        success = await monitoring_service.stop_monitoring()
        return {"message": "Monitoring stopped successfully", "status": "inactive"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@app.get("/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring service status"""
    if not monitoring_service:
        raise HTTPException(status_code=500, detail="Monitoring service not initialized")
    
    return await monitoring_service.get_status()


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "services": {
            "smart_engine": smart_engine is not None,
            "portable_detector": portable_detector is not None,
            "monitoring_service": monitoring_service is not None
        }
    }


# === CRYPTO PAYMENT ENDPOINTS ===

@app.post("/api/v1/crypto/create-payment", response_model=PaymentResponse)
async def create_crypto_payment(request: CryptoPaymentRequest):
    """Create a new USDT payment request"""
    try:
        payment_response = crypto_service.create_payment(request)
        return payment_response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")


@app.get("/api/v1/crypto/verify/{payment_id}")
async def verify_payment(payment_id: str):
    """Verify payment status by payment ID"""
    try:
        payment_status = crypto_service.verify_payment(payment_id)
        return payment_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")


@app.post("/api/v1/crypto/webhook")
async def crypto_webhook(request: Request, x_signature: Optional[str] = Header(None)):
    """Handle crypto payment webhook notifications"""
    try:
        body = await request.body()
        payload_str = body.decode('utf-8')
        
        # Verify webhook signature if provided
        if x_signature and not crypto_service.verify_webhook_signature(payload_str, x_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        payload = json.loads(payload_str)
        result = crypto_service.process_webhook(payload)
        
        # Here you can add logic to handle the payment confirmation
        # For example: send email, update database, provision service, etc.
        if result.get('event') == 'payment_confirmed':
            # Payment confirmed - provision service
            print(f"💰 Payment confirmed for invoice {result['invoice_id']}")
            # TODO: Add service provisioning logic here
        
        return {"status": "webhook_processed", "result": result}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@app.get("/api/v1/crypto/rates")
async def get_crypto_rates():
    """Get current cryptocurrency rates for payments"""
    try:
        rates = crypto_service.get_payment_rates()
        return rates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rate check failed: {str(e)}")


@app.get("/api/v1/crypto/currencies")
async def get_available_currencies():
    """Get list of supported cryptocurrencies"""
    try:
        currencies = crypto_service.get_available_cryptocurrencies()
        return {
            "currencies": currencies,
            "recommended": ["BTC", "ETH", "USDT", "LTC"],
            "total_available": len(currencies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Currency check failed: {str(e)}")


@app.get("/api/v1/crypto/services")
async def get_crypto_services():
    """Get available services and pricing for crypto payments"""
    return {
        "services": [
            {
                "id": "audit",
                "name": "Performance Audit",
                "description": "3 hours comprehensive analysis + PDF report",
                "price_usd": 299.0,
                "crypto_price_usd": 284.05,  # 5% discount
                "discount_percent": 5
            },
            {
                "id": "installation", 
                "name": "SmartCompute PRO Installation",
                "description": "Full system installation + 60 days support",
                "price_usd": 199.0,
                "crypto_price_usd": 189.05,  # 5% discount
                "discount_percent": 5
            },
            {
                "id": "monitoring",
                "name": "Monthly Monitoring",
                "description": "24/7 automated monitoring + alerts",
                "price_usd": 150.0,
                "crypto_price_usd": 142.50,  # 5% discount
                "discount_percent": 5
            }
        ],
        "payment_methods": {
            "usdt_trc20": "USDT (TRC20) - Recommended",
            "usdt_erc20": "USDT (ERC20) - Higher fees"
        },
        "benefits": [
            "5% automatic discount on crypto payments",
            "Instant payment verification",
            "No chargebacks",
            "Global accessibility"
        ]
    }