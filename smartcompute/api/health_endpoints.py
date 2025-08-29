#!/usr/bin/env python3
"""
Health and Monitoring Endpoints for SmartCompute API
Provides /health, /metrics, and observability endpoints
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi import FastAPI, Response, HTTPException, Depends
    from fastapi.responses import PlainTextResponse, JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from flask import Flask, jsonify, request, make_response
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from smartcompute.observability.health_monitor import HealthMonitor, create_health_endpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None

def get_health_monitor() -> HealthMonitor:
    """Get or create global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor(
            check_interval=30.0,
            metrics_retention_minutes=60
        )
        
        # Add custom metrics for SmartCompute
        _health_monitor.register_custom_metric('api_requests_total', lambda: 0)  # TODO: implement counter
        _health_monitor.register_custom_metric('active_computations', lambda: 0)  # TODO: implement
        
        # Start background monitoring
        _health_monitor.start_monitoring()
        logger.info("Health monitor initialized and started")
    
    return _health_monitor

# FastAPI implementation
if FASTAPI_AVAILABLE:
    def setup_fastapi_health_endpoints(app: FastAPI) -> None:
        """Setup health endpoints for FastAPI application"""
        
        monitor = get_health_monitor()
        health_check, metrics_endpoint = create_health_endpoint(monitor)
        
        @app.get("/health", tags=["Health"], summary="Health Check")
        async def health():
            """
            Health check endpoint
            Returns the current health status of the SmartCompute service
            """
            try:
                result, status_code = health_check()
                return JSONResponse(content=result, status_code=status_code)
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    content={
                        "status": "unknown",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    status_code=500
                )
        
        @app.get("/health/detailed", tags=["Health"], summary="Detailed Health Check")
        async def detailed_health():
            """
            Detailed health check with full diagnostic information
            """
            try:
                health_status = monitor.run_health_checks()
                return JSONResponse(content={
                    "status": health_status.status,
                    "timestamp": health_status.timestamp,
                    "uptime_seconds": health_status.uptime_seconds,
                    "checks": health_status.checks,
                    "metrics": health_status.metrics,
                    "errors": health_status.errors,
                    "warnings": health_status.warnings,
                    "summary": monitor.get_health_summary(last_minutes=10)
                })
            except Exception as e:
                logger.error(f"Detailed health check failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/metrics", tags=["Monitoring"], summary="Prometheus Metrics")
        async def prometheus_metrics():
            """
            Prometheus metrics endpoint
            Returns metrics in Prometheus format
            """
            try:
                metrics_data, status_code, headers = metrics_endpoint('prometheus')
                return PlainTextResponse(
                    content=metrics_data,
                    status_code=status_code,
                    headers=headers
                )
            except Exception as e:
                logger.error(f"Metrics export failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/metrics/json", tags=["Monitoring"], summary="JSON Metrics")
        async def json_metrics():
            """
            JSON metrics endpoint
            Returns detailed metrics and history in JSON format
            """
            try:
                metrics_data, status_code, headers = metrics_endpoint('json')
                return JSONResponse(
                    content=json.loads(metrics_data),
                    status_code=status_code
                )
            except Exception as e:
                logger.error(f"JSON metrics export failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/ping", tags=["Health"], summary="Simple Ping")
        async def ping():
            """
            Simple ping endpoint for basic connectivity checks
            """
            return JSONResponse(content={
                "message": "pong",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "SmartCompute",
                "version": "1.0.0"  # TODO: get from package
            })
        
        @app.get("/readiness", tags=["Health"], summary="Readiness Check")
        async def readiness():
            """
            Kubernetes-style readiness check
            Returns 200 if service is ready to accept traffic
            """
            try:
                health_status = monitor.run_health_checks()
                
                # Service is ready if not critical
                if health_status.status in ['healthy', 'warning']:
                    return JSONResponse(content={
                        "ready": True,
                        "status": health_status.status,
                        "timestamp": health_status.timestamp
                    })
                else:
                    return JSONResponse(
                        content={
                            "ready": False,
                            "status": health_status.status,
                            "errors": health_status.errors,
                            "timestamp": health_status.timestamp
                        },
                        status_code=503
                    )
            except Exception as e:
                logger.error(f"Readiness check failed: {e}")
                return JSONResponse(
                    content={
                        "ready": False,
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    status_code=503
                )
        
        @app.get("/liveness", tags=["Health"], summary="Liveness Check")
        async def liveness():
            """
            Kubernetes-style liveness check
            Returns 200 if service is alive (even if degraded)
            """
            return JSONResponse(content={
                "alive": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": time.time() - monitor.start_time
            })
        
        logger.info("FastAPI health endpoints configured")

# Flask implementation
if FLASK_AVAILABLE:
    def setup_flask_health_endpoints(app: Flask) -> None:
        """Setup health endpoints for Flask application"""
        
        monitor = get_health_monitor()
        health_check, metrics_endpoint = create_health_endpoint(monitor)
        
        @app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            try:
                result, status_code = health_check()
                return jsonify(result), status_code
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    "status": "unknown",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }), 500
        
        @app.route('/health/detailed', methods=['GET'])
        def detailed_health():
            """Detailed health check"""
            try:
                health_status = monitor.run_health_checks()
                return jsonify({
                    "status": health_status.status,
                    "timestamp": health_status.timestamp,
                    "uptime_seconds": health_status.uptime_seconds,
                    "checks": health_status.checks,
                    "metrics": health_status.metrics,
                    "errors": health_status.errors,
                    "warnings": health_status.warnings,
                    "summary": monitor.get_health_summary(last_minutes=10)
                })
            except Exception as e:
                logger.error(f"Detailed health check failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @app.route('/metrics', methods=['GET'])
        def prometheus_metrics():
            """Prometheus metrics endpoint"""
            try:
                metrics_data, status_code, headers = metrics_endpoint('prometheus')
                response = make_response(metrics_data, status_code)
                for key, value in headers.items():
                    response.headers[key] = value
                return response
            except Exception as e:
                logger.error(f"Metrics export failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @app.route('/metrics/json', methods=['GET'])
        def json_metrics():
            """JSON metrics endpoint"""
            try:
                metrics_data, status_code, headers = metrics_endpoint('json')
                return json.loads(metrics_data), status_code
            except Exception as e:
                logger.error(f"JSON metrics export failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @app.route('/ping', methods=['GET'])
        def ping():
            """Simple ping endpoint"""
            return jsonify({
                "message": "pong",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "SmartCompute",
                "version": "1.0.0"
            })
        
        @app.route('/readiness', methods=['GET'])
        def readiness():
            """Readiness check"""
            try:
                health_status = monitor.run_health_checks()
                
                if health_status.status in ['healthy', 'warning']:
                    return jsonify({
                        "ready": True,
                        "status": health_status.status,
                        "timestamp": health_status.timestamp
                    })
                else:
                    return jsonify({
                        "ready": False,
                        "status": health_status.status,
                        "errors": health_status.errors,
                        "timestamp": health_status.timestamp
                    }), 503
            except Exception as e:
                logger.error(f"Readiness check failed: {e}")
                return jsonify({
                    "ready": False,
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }), 503
        
        @app.route('/liveness', methods=['GET'])
        def liveness():
            """Liveness check"""
            return jsonify({
                "alive": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": time.time() - monitor.start_time
            })
        
        logger.info("Flask health endpoints configured")

# Standalone health server (for testing or simple deployments)
def create_standalone_health_server(port: int = 8080) -> None:
    """Create a standalone health monitoring server"""
    
    if FASTAPI_AVAILABLE:
        from fastapi import FastAPI
        import uvicorn
        
        app = FastAPI(
            title="SmartCompute Health Monitor",
            description="Health monitoring and metrics for SmartCompute",
            version="1.0.0"
        )
        
        setup_fastapi_health_endpoints(app)
        
        print(f"Starting standalone health server on port {port}")
        print(f"Health endpoint: http://localhost:{port}/health")
        print(f"Metrics endpoint: http://localhost:{port}/metrics")
        
        uvicorn.run(app, host="0.0.0.0", port=port)
    
    elif FLASK_AVAILABLE:
        from flask import Flask
        
        app = Flask(__name__)
        setup_flask_health_endpoints(app)
        
        print(f"Starting standalone health server on port {port}")
        print(f"Health endpoint: http://localhost:{port}/health")
        print(f"Metrics endpoint: http://localhost:{port}/metrics")
        
        app.run(host="0.0.0.0", port=port, debug=False)
    
    else:
        raise RuntimeError("Neither FastAPI nor Flask is available")

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartCompute Health Monitor')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--test', action='store_true', help='Run health test')
    
    args = parser.parse_args()
    
    if args.test:
        # Run health test
        monitor = get_health_monitor()
        health_status = monitor.run_health_checks()
        
        print("Health Status:")
        print(json.dumps({
            "status": health_status.status,
            "timestamp": health_status.timestamp,
            "uptime_seconds": health_status.uptime_seconds,
            "errors": health_status.errors,
            "warnings": health_status.warnings
        }, indent=2))
        
        print("\nMetrics (Prometheus format):")
        print(monitor.export_metrics(format='prometheus'))
        
        monitor.stop_monitoring()
    else:
        create_standalone_health_server(port=args.port)

if __name__ == "__main__":
    main()