"""
SmartCompute Core Engine - Internal Service
Isolated core detection and analysis logic
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import logging
import os
import json
import sys
import time
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from services.secrets.secret_manager import secret_manager
    from services.monitoring.prometheus_metrics import get_metrics, prometheus_middleware
    from services.monitoring.structured_logging import setup_logging, get_logger
except ImportError as e:
    # Fallback if modules not available
    secret_manager = None
    get_metrics = lambda x: None
    prometheus_middleware = lambda x: None
    setup_logging = None
    get_logger = lambda x: None
    print(f"Warning: Some monitoring modules not available: {e}")

# Initialize structured logging
if setup_logging:
    setup_logging(
        service_name="smartcompute-core",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        environment=os.getenv("ENVIRONMENT", "production"),
        console_output=os.getenv("LOG_LEVEL") == "DEBUG"
    )
    logger = get_logger("smartcompute-core")
else:
    # Fallback logging
    logging.basicConfig(
        level=logging.INFO,
        format='{"service": "smartcompute-core", "level": "%(levelname)s", "message": "%(message)s", "timestamp": "%(asctime)s"}'
    )
    logger = logging.getLogger(__name__)

# Initialize metrics
metrics = get_metrics("smartcompute-core") if get_metrics else None

app = FastAPI(
    title="SmartCompute Core Engine",
    description="Internal core detection and analysis service",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None
)

# Add Prometheus metrics middleware
if prometheus_middleware and metrics:
    app.middleware("http")(prometheus_middleware(metrics))


class AnalysisRequest(BaseModel):
    """Analysis request model"""
    id: str
    type: str  # threat_analysis, performance_optimization, anomaly_detection
    data: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, critical
    metadata: Optional[Dict[str, Any]] = None


class AnalysisResult(BaseModel):
    """Analysis result model"""
    request_id: str
    type: str
    status: str  # completed, failed, processing
    result: Dict[str, Any]
    processing_time_ms: float
    timestamp: str
    confidence: float


# In-memory job queue (replace with Redis/RabbitMQ in production)
analysis_queue: List[AnalysisRequest] = []
processing_jobs: Dict[str, AnalysisResult] = {}


async def process_threat_analysis(request: AnalysisRequest) -> Dict[str, Any]:
    """Process threat detection analysis"""
    start_time = asyncio.get_event_loop().time()
    
    # Simulate core detection logic
    await asyncio.sleep(0.01)  # Simulate processing time
    
    data = request.data
    threat_score = 0.0
    indicators = []
    
    # Mock threat analysis logic
    if data.get("src_ip", "").startswith("192.168"):
        threat_score += 0.1
    if data.get("dst_port") in [22, 23, 445, 135]:
        threat_score += 0.4
        indicators.append("suspicious_port")
    if data.get("payload", "").lower().find("exploit") >= 0:
        threat_score += 0.8
        indicators.append("exploit_payload")
    
    processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
    
    return {
        "threat_detected": threat_score > 0.5,
        "threat_score": min(threat_score, 1.0),
        "indicators": indicators,
        "analysis_type": "threat_detection",
        "processing_time_ms": processing_time
    }


async def process_performance_optimization(request: AnalysisRequest) -> Dict[str, Any]:
    """Process performance optimization analysis"""
    start_time = asyncio.get_event_loop().time()
    
    # Simulate optimization logic
    await asyncio.sleep(0.005)  # Simulate processing time
    
    data = request.data
    precision = data.get("precision_needed", 0.95)
    speed_priority = data.get("speed_priority", 0.5)
    
    # Mock optimization results
    if speed_priority > 0.7:
        method = "fast_approximation"
        speedup = 3.2
        accuracy = precision * 0.98
    elif precision > 0.98:
        method = "high_precision"
        speedup = 1.1
        accuracy = precision * 0.999
    else:
        method = "balanced"
        speedup = 1.8
        accuracy = precision * 0.995
    
    processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
    
    return {
        "method": method,
        "speedup": speedup,
        "accuracy": accuracy,
        "optimization_applied": True,
        "processing_time_ms": processing_time
    }


async def process_analysis_request(request: AnalysisRequest) -> AnalysisResult:
    """Process analysis request based on type"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        if request.type == "threat_analysis":
            result_data = await process_threat_analysis(request)
        elif request.type == "performance_optimization":
            result_data = await process_performance_optimization(request)
        else:
            raise ValueError(f"Unknown analysis type: {request.type}")
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        result = AnalysisResult(
            request_id=request.id,
            type=request.type,
            status="completed",
            result=result_data,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat(),
            confidence=result_data.get("threat_score", 0.95)
        )
        
        # Track metrics
        if metrics:
            metrics.track_analysis(request.type, processing_time / 1000, "completed")
            if request.type == "threat_analysis" and result_data.get("threat_detected"):
                metrics.track_threat_detection(
                    "high" if result_data.get("threat_score", 0) > 0.7 else "medium",
                    "detected"
                )
            elif request.type == "performance_optimization":
                metrics.track_optimization(
                    "matrix_multiply",
                    result_data.get("speedup", 1.0),
                    result_data.get("accuracy", 0.95)
                )
        
        logger.info(
            "Analysis completed",
            extra={
                "request_id": request.id,
                "analysis_type": request.type,
                "processing_time_ms": processing_time,
                "confidence": result_data.get("threat_score", 0.95)
            }
        )
        
        return result
        
    except Exception as e:
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Track error metrics
        if metrics:
            metrics.track_analysis(request.type, processing_time / 1000, "failed")
            metrics.track_error("analysis_processing_error", "error")
        
        logger.error(
            "Analysis failed",
            extra={
                "request_id": request.id,
                "analysis_type": request.type,
                "processing_time_ms": processing_time,
                "error": str(e)
            },
            exc_info=True
        )
        
        return AnalysisResult(
            request_id=request.id,
            type=request.type,
            status="failed",
            result={"error": str(e)},
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat(),
            confidence=0.0
        )


async def background_processor():
    """Background task processor for analysis queue"""
    while True:
        if analysis_queue:
            # Update queue size metric
            if metrics:
                metrics.set_queue_size(len(analysis_queue))
            
            request = analysis_queue.pop(0)
            result = await process_analysis_request(request)
            processing_jobs[request.id] = result
        else:
            if metrics:
                metrics.set_queue_size(0)
            await asyncio.sleep(0.1)


# Start background processor on startup
@app.on_event("startup")
async def startup_event():
    """Initialize background services"""
    logger.info("SmartCompute Core Engine starting up...")
    
    # Set service status and app info
    if metrics:
        metrics.set_service_status("starting")
        metrics.set_app_info(
            version="1.0.0", 
            build_date=datetime.utcnow().isoformat(),
            git_commit=os.getenv("GIT_COMMIT", "unknown")
        )
    
    # Initialize credentials from secret manager
    if secret_manager:
        try:
            db_creds = await secret_manager.get_database_credentials()
            service_creds = await secret_manager.get_service_credentials()
            logger.info("Loaded credentials from secret manager")
        except Exception as e:
            logger.warning("Failed to load credentials from secret manager", extra={"error": str(e)})
    
    asyncio.create_task(background_processor())
    
    # Set service as healthy
    if metrics:
        metrics.set_service_status("healthy")
    
    logger.info("SmartCompute Core Engine startup completed")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "smartcompute-core",
        "version": "1.0.0",
        "queue_size": len(analysis_queue),
        "processing_jobs": len(processing_jobs),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/analyze", response_model=Dict[str, str])
async def submit_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Submit analysis request to processing queue"""
    logger.info(f"Analysis request received: {request.id}, type: {request.type}")
    
    # Add to queue
    analysis_queue.append(request)
    
    return {
        "request_id": request.id,
        "status": "queued",
        "message": f"Analysis request {request.id} queued for processing"
    }


@app.get("/status/{request_id}", response_model=AnalysisResult)
async def get_analysis_status(request_id: str):
    """Get analysis result by request ID"""
    if request_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Analysis request not found")
    
    return processing_jobs[request_id]


@app.get("/queue/status")
async def get_queue_status():
    """Get current queue status"""
    return {
        "queue_size": len(analysis_queue),
        "processing_jobs": len(processing_jobs),
        "next_jobs": [{"id": job.id, "type": job.type} for job in analysis_queue[:5]]
    }


@app.delete("/jobs/{request_id}")
async def delete_job_result(request_id: str):
    """Delete completed job result"""
    if request_id in processing_jobs:
        del processing_jobs[request_id]
        return {"message": f"Job result {request_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Job result not found")


@app.get("/metrics")
async def get_prometheus_metrics():
    """Prometheus metrics endpoint"""
    if metrics:
        from prometheus_client import CONTENT_TYPE_LATEST
        return Response(
            content=metrics.get_metrics(),
            media_type=CONTENT_TYPE_LATEST
        )
    else:
        raise HTTPException(status_code=503, detail="Metrics not available")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)