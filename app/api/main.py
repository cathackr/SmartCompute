"""
SmartCompute FastAPI Application
Performance-based anomaly detection API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Header, Response
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
from ..services.business_metrics import (
    metrics_collector,
    record_api_call,
    record_optimization_event,
    record_anomaly_detection
)
from ..core.performance_optimizer import get_performance_optimizer
from ..security.audit_system import SecurityAuditSystem, SecurityEventType


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
security_audit_system: Optional[SecurityAuditSystem] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global smart_engine, portable_detector, monitoring_service, security_audit_system
    
    # Initialize services
    print("🚀 Initializing SmartCompute services...")
    smart_engine = SmartComputeEngine()
    portable_detector = PortableSystemDetector()
    monitoring_service = MonitoringService(portable_detector)
    security_audit_system = SecurityAuditSystem()
    
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

# Security middleware for request monitoring
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security monitoring middleware"""
    start_time = time.time()
    
    # Get client information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    endpoint = str(request.url.path)
    
    # Log API access for security monitoring
    if security_audit_system:
        security_audit_system.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            source_ip=client_ip,
            user_agent=user_agent,
            endpoint=endpoint,
            details={"method": request.method}
        )
    
    response = await call_next(request)
    
    # Log response time and status for anomaly detection
    process_time = time.time() - start_time
    if security_audit_system and process_time > 5.0:  # Log slow requests
        security_audit_system.log_security_event(
            event_type=SecurityEventType.ANOMALY_DETECTED,
            source_ip=client_ip,
            endpoint=endpoint,
            details={"response_time": process_time, "status_code": response.status_code}
        )
    
    return response

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
            "monitoring": "/monitoring",
            "metrics_business": "/metrics/business",
            "metrics_export": "/metrics/export",
            "documentation": "/docs",
            "security_status": "/security/status",
            "security_events": "/security/events",
            "security_metrics": "/security/metrics"
        }
    }


@app.get("/system-info", response_model=SystemInfo)
async def get_system_info():
    """Get current system information and capabilities"""
    if not portable_detector:
        raise HTTPException(status_code=500, detail="Portable detector not initialized")
    
    info = portable_detector.system_info
    return SystemInfo(
        os=info.get('os', 'Unknown'),
        architecture=info.get('arch', 'Unknown'),
        cpu_model=info.get('cpu_model', 'Unknown'),
        cpu_cores=info.get('cpu_cores', 1),
        ram_gb=info.get('ram_gb', 1.0),
        gpu_type=info.get('gpu_type', 'None')
    )


@app.post("/optimize")
async def optimize_computation(request: OptimizationRequest):
    """Perform intelligent computation optimization with performance monitoring"""
    if not smart_engine:
        raise HTTPException(status_code=500, detail="SmartCompute engine not initialized")
    
    # Get performance optimizer (detect access level from request or default to starter)
    access_level = getattr(request, 'access_level', 'starter')
    optimizer = get_performance_optimizer(access_level)
    
    # Apply performance monitoring decorator
    @optimizer.performance_monitor("matrix_optimization")
    def perform_optimization():
        # Create sample matrices for demonstration
        import numpy as np
        np.random.seed(42)
        matrix_a = np.random.rand(500, 500)
        matrix_b = np.random.rand(500, 500)
        
        result = smart_engine.smart_multiply(
            matrix_a, 
            matrix_b,
            precision_needed=request.precision_needed,
            speed_priority=request.speed_priority,
            verbose=request.enable_verbose
        )
        return result
    
    try:
        # Execute with performance monitoring
        result = perform_optimization()
        
        # Record optimization metrics
        record_optimization_event(
            result["method"], 
            result["speedup"], 
            result["accuracy"]
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
        
        # Record anomaly detection metrics
        record_anomaly_detection(
            anomaly_result['anomaly_score'],
            anomaly_result['severity']
        )
        
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
    health_data = {
        "status": "healthy",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "services": {
            "smart_engine": smart_engine is not None,
            "portable_detector": portable_detector is not None,
            "monitoring_service": monitoring_service is not None
        }
    }
    
    # Record health check metric
    record_api_call("/health", 0.1, 200)
    
    return health_data


@app.get("/metrics/business")
async def get_business_metrics():
    """Get business metrics dashboard"""
    start_time = time.time()
    
    try:
        dashboard = metrics_collector.get_kpi_dashboard()
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/business", response_time, 200)
        return dashboard
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/business", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@app.get("/metrics/summary")
async def get_metrics_summary(hours: int = 24):
    """Get metrics summary for specified time period"""
    start_time = time.time()
    
    try:
        if hours < 1 or hours > 168:  # Max 1 week
            raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")
        
        summary = metrics_collector.get_metrics_summary(hours)
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/summary", response_time, 200)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/summary", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@app.get("/metrics/export")
async def export_metrics(
    format: str = "json",
    access_level: str = "starter",
    encrypt: bool = False,
    password: Optional[str] = Header(None, alias="x-encryption-password")
):
    """Export metrics in specified format with optional encryption"""
    start_time = time.time()
    
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be json or csv")
        
        if access_level not in ["starter", "enterprise", "industrial"]:
            raise HTTPException(status_code=400, detail="Access level must be starter, enterprise, or industrial")
        
        # Check encryption requirements
        if encrypt and access_level == "starter":
            raise HTTPException(
                status_code=403, 
                detail="Encryption not available in Starter version. Upgrade to Enterprise or Industrial."
            )
        
        if encrypt and not password:
            raise HTTPException(
                status_code=400,
                detail="Password required for encrypted export (use x-encryption-password header)"
            )
        
        exported_data = metrics_collector.export_metrics(
            format_type=format,
            access_level=access_level,
            password=password,
            encrypt=encrypt
        )
        
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/export", response_time, 200)
        
        # Record encryption usage for Enterprise/Industrial
        if encrypt and access_level in ["enterprise", "industrial"]:
            record_api_call(f"/metrics/export/encrypted_{access_level}", response_time, 200)
        
        if format == "csv" and not encrypt:
            return Response(
                content=exported_data,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=smartcompute_metrics.csv"}
            )
        else:
            return {
                "data": exported_data,
                "format": format,
                "encrypted": encrypt,
                "access_level": access_level,
                "export_info": {
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "size_bytes": len(exported_data.encode() if isinstance(exported_data, str) else str(exported_data).encode())
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/export", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/metrics/secure-export")
async def create_secure_metrics_export(
    format: str = "json",
    access_level: str = "enterprise",
    password: str = Header(None, alias="x-encryption-password")
):
    """Create secure encrypted metrics package (Enterprise/Industrial only)"""
    start_time = time.time()
    
    try:
        if access_level not in ["enterprise", "industrial"]:
            raise HTTPException(
                status_code=403,
                detail="Secure export only available for Enterprise and Industrial versions"
            )
        
        if not password:
            raise HTTPException(
                status_code=400,
                detail="Password required for secure export (use x-encryption-password header)"
            )
        
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be json or csv")
        
        # Create secure package
        download_token, encrypted_package = metrics_collector.export_secure_package(
            format_type=format,
            access_level=access_level,
            password=password
        )
        
        response_time = (time.time() - start_time) * 1000
        record_api_call(f"/metrics/secure-export/{access_level}", response_time, 200)
        
        return {
            "success": True,
            "download_token": download_token,
            "package_size_bytes": len(encrypted_package.encode()),
            "format": format,
            "access_level": access_level,
            "expires_in_hours": 2,
            "instructions": {
                "message": "Save the encrypted package securely. Use SmartCompute decryption tools with your password.",
                "security_notice": "This package contains encrypted business metrics. Handle according to your organization's security policies."
            },
            "encrypted_package": encrypted_package
        }
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/secure-export", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Secure export failed: {str(e)}")


@app.get("/metrics/encryption-info")
async def get_encryption_info(access_level: str = "starter"):
    """Get information about encryption capabilities for different access levels"""
    start_time = time.time()
    
    try:
        from ..services.metrics_encryption import get_encryption_service
        encryption_service = get_encryption_service(access_level)
        info = encryption_service.get_encryption_info()
        
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/encryption-info", response_time, 200)
        
        return info
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/metrics/encryption-info", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to get encryption info: {str(e)}")


# === API DOCUMENTATION ENDPOINTS ===

@app.get("/docs/openapi.json")
async def get_openapi_spec(access_level: str = "starter"):
    """Get OpenAPI specification filtered by access level"""
    start_time = time.time()
    
    try:
        if access_level not in ["starter", "enterprise", "industrial"]:
            raise HTTPException(status_code=400, detail="Access level must be starter, enterprise, or industrial")
        
        from ..core.documentation import doc_generator
        openapi_spec = doc_generator.generate_openapi_spec(access_level)
        
        response_time = (time.time() - start_time) * 1000
        record_api_call("/docs/openapi.json", response_time, 200)
        
        return openapi_spec
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/docs/openapi.json", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to generate OpenAPI spec: {str(e)}")


@app.get("/docs")
async def get_api_documentation(
    access_level: str = "starter",
    format: str = "html"
):
    """Get API documentation in specified format"""
    start_time = time.time()
    
    try:
        if access_level not in ["starter", "enterprise", "industrial"]:
            raise HTTPException(status_code=400, detail="Access level must be starter, enterprise, or industrial")
        
        if format not in ["html", "markdown", "json"]:
            raise HTTPException(status_code=400, detail="Format must be html, markdown, or json")
        
        from ..core.documentation import doc_generator
        
        if format == "json":
            # Return OpenAPI spec
            docs = doc_generator.generate_openapi_spec(access_level)
            content_type = "application/json"
            content = json.dumps(docs, indent=2)
        elif format == "markdown":
            # Return markdown documentation
            docs = doc_generator.generate_markdown_docs(access_level)
            content_type = "text/markdown"
            content = docs
        else:  # html
            # Return HTML documentation
            docs = doc_generator.generate_markdown_docs(access_level)
            content_type = "text/html"
            content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute API Documentation - {access_level.title()}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #2980b9; background: #ecf0f1; padding: 10px; border-radius: 4px; }}
        code {{ background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: 'Monaco', 'Consolas', monospace; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        .security-note {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .access-level {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
        .starter {{ background: #d1ecf1; color: #0c5460; }}
        .enterprise {{ background: #d4edda; color: #155724; }}
        .industrial {{ background: #fff3cd; color: #856404; }}
        .endpoint {{ border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin: 20px 0; background: #fdfdfd; }}
        .method {{ display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; }}
        .get {{ background: #28a745; }}
        .post {{ background: #007bff; }}
        .put {{ background: #ffc107; color: #212529; }}
        .delete {{ background: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="security-note">
            <strong>🔒 Security Notice:</strong> This documentation is filtered for <span class="access-level {access_level}">{access_level.upper()}</span> access level. 
            Some endpoints may require higher access levels or authentication.
        </div>
        {_markdown_to_basic_html(docs)}
        <hr style="margin-top: 40px;">
        <p style="text-align: center; color: #6c757d; font-size: 0.9em;">
            Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | SmartCompute API Documentation
        </p>
    </div>
</body>
</html>"""
        
        response_time = (time.time() - start_time) * 1000
        record_api_call(f"/docs/{format}", response_time, 200)
        
        return Response(content=content, media_type=content_type)
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/docs", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to generate documentation: {str(e)}")


def _markdown_to_basic_html(markdown: str) -> str:
    """Convert basic markdown to HTML"""
    html = markdown
    
    # Headers
    html = html.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
    html = html.replace('<h1>', '</h1><h1>').replace('<h2>', '</h2><h2>').replace('<h3>', '</h3><h3>')
    
    # Code blocks
    import re
    html = re.sub(r'```bash\n(.*?)\n```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Lists
    html = re.sub(r'\n- (.*)', r'\n<li>\1</li>', html)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Paragraphs
    html = re.sub(r'\n\n', '\n<p></p>\n', html)
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    return html


@app.get("/docs/security")
async def get_security_documentation():
    """Get security-specific documentation"""
    start_time = time.time()
    
    try:
        security_docs = {
            "security_model": {
                "overview": "SmartCompute implements a tiered security model with three access levels",
                "levels": {
                    "starter": {
                        "features": ["Basic rate limiting", "Input validation", "No data persistence"],
                        "limitations": ["No encryption", "Limited export capabilities"],
                        "use_case": "Development and testing environments"
                    },
                    "enterprise": {
                        "features": [
                            "AES-128 encryption for metrics export",
                            "Password-based key derivation (PBKDF2)",
                            "Secure export tokens",
                            "Advanced rate limiting",
                            "Audit logging"
                        ],
                        "compliance": ["Enterprise data protection", "Encrypted data at rest"],
                        "use_case": "Business and corporate environments"
                    },
                    "industrial": {
                        "features": [
                            "All Enterprise features",
                            "Time-limited secure packages",
                            "Industrial-grade encryption",
                            "Enhanced audit trails",
                            "Advanced threat detection"
                        ],
                        "compliance": ["Industrial security standards", "Critical infrastructure protection"],
                        "use_case": "Manufacturing and critical infrastructure"
                    }
                }
            },
            "encryption_details": {
                "algorithm": "Fernet (AES 128-bit)",
                "key_derivation": "PBKDF2-HMAC-SHA256",
                "iterations": 100000,
                "salt_size": "128-bit random",
                "encoding": "Base64 for transport safety"
            },
            "best_practices": [
                "Use strong passwords for encryption (12+ characters)",
                "Rotate encryption passwords regularly",
                "Store secure packages in encrypted storage",
                "Monitor audit logs for unusual activity",
                "Use appropriate access level for your environment",
                "Implement additional authentication for sensitive operations"
            ],
            "compliance_notes": [
                "Encryption meets enterprise security standards",
                "Audit trails support compliance reporting",
                "Data minimization principles applied",
                "No sensitive data stored in logs",
                "Password-based encryption prevents unauthorized access"
            ]
        }
        
        response_time = (time.time() - start_time) * 1000
        record_api_call("/docs/security", response_time, 200)
        
        return security_docs
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/docs/security", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to get security documentation: {str(e)}")


# === PERFORMANCE OPTIMIZATION ENDPOINTS ===

@app.get("/performance/summary")
async def get_performance_summary(access_level: str = "starter"):
    """Get performance optimization summary"""
    start_time = time.time()
    
    try:
        if access_level not in ["starter", "enterprise", "industrial"]:
            raise HTTPException(status_code=400, detail="Access level must be starter, enterprise, or industrial")
        
        optimizer = get_performance_optimizer(access_level)
        summary = optimizer.get_performance_summary()
        
        response_time = (time.time() - start_time) * 1000
        record_api_call("/performance/summary", response_time, 200)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "performance_summary": summary,
            "response_time_ms": round(response_time, 2)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/performance/summary", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")


@app.get("/performance/cache-stats")
async def get_cache_statistics(access_level: str = "starter"):
    """Get performance cache statistics"""
    start_time = time.time()
    
    try:
        if access_level not in ["starter", "enterprise", "industrial"]:
            raise HTTPException(status_code=400, detail="Access level must be starter, enterprise, or industrial")
        
        optimizer = get_performance_optimizer(access_level)
        cache_stats = optimizer.cache.get_stats()
        
        response_time = (time.time() - start_time) * 1000
        record_api_call("/performance/cache-stats", response_time, 200)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "access_level": access_level,
            "cache_statistics": cache_stats,
            "optimization_enabled": optimizer._optimization_enabled,
            "cache_settings": {
                "max_size": optimizer.cache.max_size,
                "default_ttl": optimizer.cache.default_ttl
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/performance/cache-stats", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")


@app.post("/performance/clear-cache")
async def clear_performance_cache(access_level: str = "starter"):
    """Clear performance cache (Enterprise/Industrial feature)"""
    start_time = time.time()
    
    try:
        if access_level not in ["starter", "enterprise", "industrial"]:
            raise HTTPException(status_code=400, detail="Access level must be starter, enterprise, or industrial")
        
        if access_level == "starter":
            raise HTTPException(
                status_code=403,
                detail="Cache management not available in Starter version. Upgrade to Enterprise or Industrial."
            )
        
        optimizer = get_performance_optimizer(access_level)
        clear_result = optimizer.clear_performance_cache()
        
        response_time = (time.time() - start_time) * 1000
        record_api_call(f"/performance/clear-cache/{access_level}", response_time, 200)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cache_cleared": clear_result,
            "access_level": access_level,
            "message": "Performance cache cleared successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/performance/clear-cache", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@app.get("/performance/optimization-settings")
async def get_optimization_settings(access_level: str = "starter"):
    """Get performance optimization settings"""
    start_time = time.time()
    
    try:
        if access_level not in ["starter", "enterprise", "industrial"]:
            raise HTTPException(status_code=400, detail="Access level must be starter, enterprise, or industrial")
        
        optimizer = get_performance_optimizer(access_level)
        
        settings_info = {
            "access_level": access_level,
            "optimization_enabled": optimizer._optimization_enabled,
            "current_settings": optimizer.settings,
            "features_available": {
                "caching": optimizer.settings.get("cache_enabled", False),
                "gc_optimization": optimizer.settings.get("gc_optimization", False),
                "async_processing": optimizer.settings.get("async_processing", False),
                "memory_monitoring": optimizer.settings.get("memory_monitoring", False),
                "predictive_caching": optimizer.settings.get("predictive_caching", False),
                "resource_pooling": optimizer.settings.get("resource_pooling", False)
            },
            "upgrade_benefits": []
        }
        
        # Add upgrade information
        if access_level == "starter":
            settings_info["upgrade_benefits"] = [
                "Advanced caching with longer TTL",
                "Memory optimization and garbage collection",
                "Async processing capabilities",
                "Detailed performance monitoring",
                "Cache management controls"
            ]
        elif access_level == "enterprise":
            settings_info["upgrade_benefits"] = [
                "Predictive caching algorithms",
                "Resource pooling optimization",
                "Industrial-grade performance monitoring",
                "Extended cache lifetime",
                "Advanced memory management"
            ]
        
        response_time = (time.time() - start_time) * 1000
        record_api_call("/performance/optimization-settings", response_time, 200)
        
        return settings_info
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        record_api_call("/performance/optimization-settings", response_time, 500)
        raise HTTPException(status_code=500, detail=f"Failed to get optimization settings: {str(e)}")


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


# === SECURITY MONITORING ENDPOINTS ===

@app.get("/security/status")
async def get_security_status(
    request: Request,
    access_level: str = "starter",
    x_api_key: Optional[str] = Header(None)
):
    """Get current security system status (Enterprise/Industrial only)"""
    if access_level not in ["enterprise", "industrial"]:
        raise HTTPException(
            status_code=403, 
            detail="Security monitoring requires Enterprise or Industrial access"
        )
    
    if not security_audit_system:
        raise HTTPException(status_code=500, detail="Security system not initialized")
    
    try:
        # Log security access
        client_ip = request.client.host if request.client else "unknown"
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SECURITY_ACCESS,
            source_ip=client_ip,
            access_level=access_level,
            endpoint="/security/status"
        )
        
        status = security_audit_system.get_security_summary()
        
        # Filter data based on access level
        if access_level == "enterprise":
            # Remove industrial-only features from response
            filtered_status = {k: v for k, v in status.items() 
                             if k not in ["predictive_blocking", "industrial_metrics"]}
            return filtered_status
        else:  # industrial
            return status
            
    except Exception as e:
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SYSTEM_ERROR,
            source_ip=request.client.host if request.client else "unknown",
            details={"error": str(e), "endpoint": "/security/status"}
        )
        raise HTTPException(status_code=500, detail=f"Security status check failed: {str(e)}")


@app.get("/security/events")
async def get_security_events(
    request: Request,
    access_level: str = "enterprise",
    limit: int = 50,
    event_type: Optional[str] = None,
    since_hours: int = 24
):
    """Get recent security events (Enterprise/Industrial only)"""
    if access_level not in ["enterprise", "industrial"]:
        raise HTTPException(
            status_code=403,
            detail="Security event monitoring requires Enterprise or Industrial access"
        )
    
    if not security_audit_system:
        raise HTTPException(status_code=500, detail="Security system not initialized")
    
    try:
        # Log access to security events
        client_ip = request.client.host if request.client else "unknown"
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SECURITY_ACCESS,
            source_ip=client_ip,
            access_level=access_level,
            endpoint="/security/events",
            details={"requested_limit": limit, "since_hours": since_hours}
        )
        
        events = security_audit_system.get_recent_events(
            limit=limit, 
            event_type=SecurityEventType[event_type] if event_type else None,
            since_hours=since_hours
        )
        
        return {
            "total_events": len(events),
            "access_level": access_level,
            "time_range_hours": since_hours,
            "events": events
        }
        
    except Exception as e:
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SYSTEM_ERROR,
            source_ip=request.client.host if request.client else "unknown",
            details={"error": str(e), "endpoint": "/security/events"}
        )
        raise HTTPException(status_code=500, detail=f"Security events retrieval failed: {str(e)}")


@app.post("/security/block-ip")
async def block_ip_address(
    request: Request,
    ip_address: str,
    access_level: str = "enterprise",
    reason: str = "Manual block",
    duration_hours: int = 24
):
    """Manually block an IP address (Enterprise/Industrial only)"""
    if access_level not in ["enterprise", "industrial"]:
        raise HTTPException(
            status_code=403,
            detail="IP blocking requires Enterprise or Industrial access"
        )
    
    if not security_audit_system:
        raise HTTPException(status_code=500, detail="Security system not initialized")
    
    try:
        client_ip = request.client.host if request.client else "unknown"
        
        # Block the IP
        result = security_audit_system.block_ip(ip_address, reason, duration_hours)
        
        # Log the blocking action
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SECURITY_ACTION,
            source_ip=client_ip,
            access_level=access_level,
            endpoint="/security/block-ip",
            details={
                "blocked_ip": ip_address,
                "reason": reason,
                "duration_hours": duration_hours,
                "action_by": client_ip
            }
        )
        
        return result
        
    except Exception as e:
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SYSTEM_ERROR,
            source_ip=request.client.host if request.client else "unknown",
            details={"error": str(e), "endpoint": "/security/block-ip"}
        )
        raise HTTPException(status_code=500, detail=f"IP blocking failed: {str(e)}")


@app.get("/security/metrics")
async def get_security_metrics(
    request: Request,
    access_level: str = "industrial",
    period_hours: int = 24
):
    """Get detailed security metrics and analysis (Industrial only)"""
    if access_level != "industrial":
        raise HTTPException(
            status_code=403,
            detail="Advanced security metrics require Industrial access"
        )
    
    if not security_audit_system:
        raise HTTPException(status_code=500, detail="Security system not initialized")
    
    try:
        client_ip = request.client.host if request.client else "unknown"
        
        # Log access to advanced metrics
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SECURITY_ACCESS,
            source_ip=client_ip,
            access_level=access_level,
            endpoint="/security/metrics",
            details={"period_hours": period_hours}
        )
        
        metrics = security_audit_system.generate_security_report(period_hours)
        
        return {
            "security_metrics": metrics,
            "access_level": access_level,
            "period_hours": period_hours,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        
    except Exception as e:
        security_audit_system.log_security_event(
            event_type=SecurityEventType.SYSTEM_ERROR,
            source_ip=request.client.host if request.client else "unknown",
            details={"error": str(e), "endpoint": "/security/metrics"}
        )
        raise HTTPException(status_code=500, detail=f"Security metrics generation failed: {str(e)}")