#!/usr/bin/env python3
"""
SmartCompute Security Integration
Integrates all security components into FastAPI services
"""

import os
import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .tls_manager import TLSManager, get_tls_manager
from .mutual_auth import ServiceAuthManager, SecurityMiddleware, create_auth_manager
from .rate_limiter import SmartRateLimiter, RateLimitMiddleware, create_rate_limiter
from .circuit_breaker import CircuitBreakerRegistry, get_circuit_breaker, CircuitBreakerConfig

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration for SmartCompute services"""
    
    def __init__(self):
        # TLS Configuration
        self.tls_enabled = os.getenv("TLS_ENABLED", "true").lower() == "true"
        self.mtls_required = os.getenv("MTLS_REQUIRED", "false").lower() == "true"
        self.certs_dir = os.getenv("CERTS_DIR", "/app/security/tls")
        
        # CORS Configuration
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
        
        # Trusted Hosts
        self.trusted_hosts = os.getenv("TRUSTED_HOSTS", "*").split(",")
        
        # Rate Limiting
        self.rate_limiting_enabled = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        
        # Circuit Breaker
        self.circuit_breaker_enabled = os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() == "true"
        self.circuit_breaker_failure_threshold = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
        self.circuit_breaker_recovery_timeout = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60"))
        
        # Security Headers
        self.security_headers_enabled = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
        
        # Service Authentication
        self.service_auth_enabled = os.getenv("SERVICE_AUTH_ENABLED", "true").lower() == "true"
        self.jwt_secret = os.getenv("JWT_SECRET")
        
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"


class SmartComputeSecurityManager:
    """Manages all security components for a SmartCompute service"""
    
    def __init__(self, service_name: str, config: SecurityConfig = None):
        self.service_name = service_name
        self.config = config or SecurityConfig()
        
        # Initialize components
        self.tls_manager: Optional[TLSManager] = None
        self.auth_manager: Optional[ServiceAuthManager] = None
        self.rate_limiter: Optional[SmartRateLimiter] = None
        self.circuit_registry = CircuitBreakerRegistry()
        
        # Middleware instances
        self.security_middleware: Optional[SecurityMiddleware] = None
        self.rate_limit_middleware: Optional[RateLimitMiddleware] = None
        
    async def initialize(self):
        """Initialize all security components"""
        logger.info(f"Initializing security for service: {self.service_name}")
        
        # Initialize TLS Manager
        if self.config.tls_enabled:
            self.tls_manager = TLSManager(self.config.certs_dir)
            logger.info("TLS manager initialized")
        
        # Initialize Authentication Manager
        if self.config.service_auth_enabled:
            self.auth_manager = create_auth_manager(self.service_name)
            self.security_middleware = SecurityMiddleware(self.auth_manager)
            logger.info("Authentication manager initialized")
        
        # Initialize Rate Limiter
        if self.config.rate_limiting_enabled:
            self.rate_limiter = create_rate_limiter(self.config.redis_url)
            await self.rate_limiter.initialize()
            self.rate_limit_middleware = RateLimitMiddleware(self.rate_limiter)
            logger.info("Rate limiter initialized")
        
        logger.info("Security initialization completed")
    
    def configure_fastapi_app(self, app: FastAPI) -> FastAPI:
        """Configure FastAPI app with security middleware and settings"""
        
        # Add security middleware in correct order (last added = first executed)
        
        # 1. Security headers middleware (outermost)
        if self.config.security_headers_enabled:
            app.add_middleware(SecurityHeadersMiddleware)
        
        # 2. CORS middleware
        if self.config.cors_origins:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_origins,
                allow_credentials=self.config.cors_allow_credentials,
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["*"],
            )
        
        # 3. Trusted host middleware
        if self.config.trusted_hosts and self.config.trusted_hosts != ["*"]:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=self.config.trusted_hosts
            )
        
        # 4. Compression middleware
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # 5. Rate limiting middleware
        if self.rate_limit_middleware:
            app.middleware("http")(self.rate_limit_middleware)
        
        # 6. Authentication middleware (innermost)
        if self.security_middleware:
            app.middleware("http")(self.security_middleware)
        
        # Add security endpoints
        self._add_security_endpoints(app)
        
        return app
    
    def _add_security_endpoints(self, app: FastAPI):
        """Add security-related endpoints"""
        
        @app.get("/security/status")
        async def security_status():
            """Get security status"""
            status = {
                "service": self.service_name,
                "security_enabled": True,
                "tls_enabled": self.config.tls_enabled,
                "mtls_required": self.config.mtls_required,
                "rate_limiting_enabled": self.config.rate_limiting_enabled,
                "circuit_breaker_enabled": self.config.circuit_breaker_enabled,
                "environment": self.config.environment
            }
            
            # Add TLS certificate status
            if self.tls_manager:
                try:
                    cert_status = await self.tls_manager.validate_all_certificates()
                    status["certificates"] = cert_status
                except Exception as e:
                    status["certificates_error"] = str(e)
            
            # Add circuit breaker status
            if self.config.circuit_breaker_enabled:
                status["circuit_breakers"] = self.circuit_registry.get_all_status()
            
            return status
        
        @app.get("/security/certificates")
        async def certificate_status():
            """Get certificate status"""
            if not self.tls_manager:
                return {"error": "TLS not enabled"}
            
            return await self.tls_manager.validate_all_certificates()
        
        @app.post("/security/circuit-breaker/{name}/reset")
        async def reset_circuit_breaker(name: str):
            """Reset specific circuit breaker"""
            if name in self.circuit_registry.circuits:
                await self.circuit_registry.circuits[name].reset()
                return {"message": f"Circuit breaker {name} reset"}
            return {"error": "Circuit breaker not found"}
    
    def create_external_client(self, service_name: str, base_url: str) -> 'HTTPClientWithCircuitBreaker':
        """Create HTTP client for external service with circuit breaker"""
        from .circuit_breaker import HTTPClientWithCircuitBreaker
        
        config = CircuitBreakerConfig(
            failure_threshold=self.config.circuit_breaker_failure_threshold,
            recovery_timeout=self.config.circuit_breaker_recovery_timeout,
            timeout=30.0
        )
        
        return HTTPClientWithCircuitBreaker(service_name, base_url, config)
    
    def create_internal_client(self, target_service: str) -> 'ServiceClient':
        """Create client for internal service communication"""
        from .mutual_auth import ServiceClient
        
        if not self.auth_manager:
            raise ValueError("Authentication manager not initialized")
        
        return ServiceClient(self.service_name, target_service, self.auth_manager)
    
    def get_ssl_context(self, require_client_cert: bool = None):
        """Get SSL context for the service"""
        if not self.tls_manager:
            return None
        
        if require_client_cert is None:
            require_client_cert = self.config.mtls_required
        
        return self.tls_manager.get_server_ssl_context(
            self.service_name, 
            require_client_cert=require_client_cert
        )


class SecurityHeadersMiddleware:
    """Middleware to add security headers"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add security headers
                security_headers = {
                    b"x-content-type-options": b"nosniff",
                    b"x-frame-options": b"DENY",
                    b"x-xss-protection": b"1; mode=block",
                    b"referrer-policy": b"strict-origin-when-cross-origin",
                    b"content-security-policy": b"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
                    b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                    b"permissions-policy": b"geolocation=(), microphone=(), camera=()"
                }
                
                # Update headers
                for name, value in security_headers.items():
                    if name not in headers:
                        headers[name] = value
                
                message["headers"] = list(headers.items())
            
            await send(message)
        
        await self.app(scope, receive, send_with_security_headers)


def create_secure_app(
    service_name: str,
    title: str = None,
    description: str = None,
    version: str = "1.0.0",
    config: SecurityConfig = None
) -> tuple[FastAPI, SmartComputeSecurityManager]:
    """Create FastAPI app with integrated security"""
    
    security_manager = SmartComputeSecurityManager(service_name, config)
    
    # Create FastAPI app
    app = FastAPI(
        title=title or f"SmartCompute {service_name.title()}",
        description=description or f"SmartCompute {service_name} service with integrated security",
        version=version,
        docs_url="/docs" if config and config.debug else None,
        redoc_url="/redoc" if config and config.debug else None
    )
    
    # Configure security
    app = security_manager.configure_fastapi_app(app)
    
    # Add startup event to initialize security
    @app.on_event("startup")
    async def initialize_security():
        await security_manager.initialize()
    
    return app, security_manager


# Example service configurations
def get_api_service_config() -> SecurityConfig:
    """Security configuration for public API service"""
    config = SecurityConfig()
    config.cors_origins = ["https://dashboard.smartcompute.com", "https://api.smartcompute.com"]
    config.cors_allow_credentials = True
    config.trusted_hosts = ["api.smartcompute.com", "smartcompute-api"]
    config.mtls_required = False  # Public API doesn't require client certs
    config.rate_limiting_enabled = True
    return config


def get_core_service_config() -> SecurityConfig:
    """Security configuration for internal core service"""
    config = SecurityConfig()
    config.cors_origins = []  # No CORS for internal service
    config.trusted_hosts = ["smartcompute-core", "localhost", "127.0.0.1"]
    config.mtls_required = True  # Internal service requires mTLS
    config.rate_limiting_enabled = True
    return config


def get_payment_service_config() -> SecurityConfig:
    """Security configuration for payment service (most restrictive)"""
    config = SecurityConfig()
    config.cors_origins = []  # No CORS
    config.trusted_hosts = ["smartcompute-payment", "localhost"]
    config.mtls_required = True  # Strict mTLS requirement
    config.rate_limiting_enabled = True
    config.circuit_breaker_failure_threshold = 3  # More aggressive circuit breaker
    config.circuit_breaker_recovery_timeout = 120  # Longer recovery time
    return config


if __name__ == "__main__":
    import asyncio
    import uvicorn
    
    async def test_security_integration():
        """Test security integration"""
        
        # Create secure app
        app, security_manager = create_secure_app(
            service_name="test-service",
            title="Test Service",
            description="Test service for security integration"
        )
        
        # Add a test endpoint
        @app.get("/test")
        async def test_endpoint():
            return {"message": "Hello from secure service!"}
        
        # Add a protected endpoint
        from .mutual_auth import require_permissions
        
        @app.get("/protected")
        @require_permissions("read:data")
        async def protected_endpoint():
            return {"message": "This is a protected endpoint"}
        
        print("✅ Secure FastAPI app created successfully")
        
        # Test external client creation
        external_client = security_manager.create_external_client(
            "external-api",
            "https://api.external-service.com"
        )
        
        print(f"✅ External client created: {external_client.service_name}")
        
        # Check security status
        status = {
            "service": security_manager.service_name,
            "tls_enabled": security_manager.config.tls_enabled,
            "auth_enabled": security_manager.config.service_auth_enabled,
            "rate_limiting": security_manager.config.rate_limiting_enabled
        }
        
        print(f"✅ Security status: {status}")
        
        print("\n🎉 Security integration test completed successfully!")
        print("\nTo run the service:")
        print("uvicorn security_integration:app --host 0.0.0.0 --port 8000")
    
    # Run test
    asyncio.run(test_security_integration())
    
    # If run directly, start the test service
    if os.getenv("RUN_TEST_SERVICE"):
        app, _ = create_secure_app("test-service")
        uvicorn.run(app, host="0.0.0.0", port=8000)