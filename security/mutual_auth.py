#!/usr/bin/env python3
"""
SmartCompute Mutual Authentication
Implements mTLS and JWT-based authentication between microservices
"""

import jwt
import uuid
import logging
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from fastapi import HTTPException, Depends, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

from .tls_manager import TLSManager, get_tls_manager

logger = logging.getLogger(__name__)


class ServiceAuthManager:
    """Manages authentication and authorization between microservices"""
    
    def __init__(self, service_name: str, tls_manager: TLSManager = None):
        self.service_name = service_name
        self.tls_manager = tls_manager or get_tls_manager()
        
        # Service registry with access permissions
        self.service_registry = {
            "smartcompute-api": {
                "type": "public",
                "permissions": ["read:analysis", "write:analysis", "read:reports"],
                "allowed_clients": ["dashboard", "external"],
                "mtls_required": False
            },
            "smartcompute-core": {
                "type": "internal", 
                "permissions": ["execute:analysis", "read:models", "write:results"],
                "allowed_clients": ["smartcompute-api", "monitoring"],
                "mtls_required": True
            },
            "smartcompute-payment": {
                "type": "sensitive",
                "permissions": ["process:payment", "read:payment", "write:payment"],
                "allowed_clients": ["smartcompute-api"],
                "mtls_required": True
            },
            "smartcompute-monitoring": {
                "type": "internal",
                "permissions": ["read:metrics", "read:logs", "write:alerts"],
                "allowed_clients": ["prometheus", "grafana", "alertmanager"],
                "mtls_required": False
            }
        }
        
        # JWT configuration
        self.jwt_secret = self._get_jwt_secret()
        self.jwt_algorithm = "HS256"
        self.jwt_expiry = timedelta(hours=1)
        
        # API key management
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        
        # Request signature verification
        self.signature_keys: Dict[str, str] = {}
        
    def _get_jwt_secret(self) -> str:
        """Get JWT secret from secure storage"""
        # In production, get from Vault or secure environment
        import os
        return os.getenv("JWT_SECRET", "your-secure-jwt-secret-change-in-production")
    
    def generate_service_token(self, client_service: str, permissions: List[str] = None) -> str:
        """Generate JWT token for service-to-service communication"""
        now = datetime.utcnow()
        
        payload = {
            "iss": self.service_name,  # Issuer
            "sub": client_service,      # Subject (client service)
            "aud": self.service_name,   # Audience (this service)
            "iat": now,                 # Issued at
            "exp": now + self.jwt_expiry,  # Expires
            "jti": str(uuid.uuid4()),   # JWT ID
            "service_type": "microservice",
            "permissions": permissions or [],
            "client_cert_required": self._requires_mtls(client_service)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        logger.info(f"Generated service token for {client_service}")
        return token
    
    def verify_service_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode service JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm],
                audience=self.service_name
            )
            
            # Additional validation
            if payload.get("service_type") != "microservice":
                raise ValueError("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    def _requires_mtls(self, client_service: str) -> bool:
        """Check if client service requires mTLS"""
        # Services accessing sensitive endpoints require mTLS
        sensitive_services = {"smartcompute-payment", "smartcompute-vault"}
        return self.service_name in sensitive_services or client_service in sensitive_services
    
    def generate_api_key(self, client_name: str, permissions: List[str], expires_days: int = 365) -> Dict[str, str]:
        """Generate API key for external clients"""
        api_key = f"sc_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        self.api_keys[key_hash] = {
            "client_name": client_name,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "active": True
        }
        
        logger.info(f"Generated API key for {client_name}")
        return {
            "api_key": api_key,
            "key_id": key_hash[:16],
            "expires_at": expires_at.isoformat()
        }
    
    def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Verify API key and return client info"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash not in self.api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        key_info = self.api_keys[key_hash]
        
        if not key_info["active"]:
            raise HTTPException(status_code=401, detail="API key disabled")
        
        expires_at = datetime.fromisoformat(key_info["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(status_code=401, detail="API key expired")
        
        return key_info
    
    def verify_request_signature(self, request_body: bytes, signature: str, client_service: str) -> bool:
        """Verify HMAC signature of request body"""
        if client_service not in self.signature_keys:
            logger.error(f"No signature key found for {client_service}")
            return False
        
        expected_signature = hmac.new(
            self.signature_keys[client_service].encode(),
            request_body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def create_client_certificate_validator(self) -> Callable:
        """Create certificate validator for client authentication"""
        def validate_client_certificate(request: Request) -> Dict[str, Any]:
            """Validate client certificate from mTLS connection"""
            # Extract client certificate from TLS connection
            # Note: This requires proper TLS termination setup
            
            client_cert_header = request.headers.get("X-SSL-Client-Cert")
            client_subject = request.headers.get("X-SSL-Client-Subject")
            client_verified = request.headers.get("X-SSL-Client-Verified")
            
            if not client_cert_header or client_verified != "SUCCESS":
                raise HTTPException(
                    status_code=401, 
                    detail="Valid client certificate required"
                )
            
            # Parse client certificate info
            # In production, implement full certificate validation
            client_info = {
                "certificate_verified": True,
                "subject": client_subject,
                "client_service": self._extract_service_name_from_cert(client_subject)
            }
            
            return client_info
        
        return validate_client_certificate
    
    def _extract_service_name_from_cert(self, cert_subject: str) -> Optional[str]:
        """Extract service name from certificate subject"""
        # Parse certificate subject to extract service name
        # Example: CN=smartcompute-api,O=SmartCompute -> smartcompute-api
        if "CN=" in cert_subject:
            cn_part = [part for part in cert_subject.split(",") if part.strip().startswith("CN=")]
            if cn_part:
                return cn_part[0].split("=", 1)[1].strip()
        return None


class SecurityMiddleware:
    """FastAPI middleware for service authentication and authorization"""
    
    def __init__(self, auth_manager: ServiceAuthManager):
        self.auth_manager = auth_manager
        self.bearer_scheme = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request, call_next):
        """Process request through security middleware"""
        
        # Skip authentication for health checks and metrics
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        try:
            # Extract authentication information
            auth_info = await self._authenticate_request(request)
            
            # Add authentication info to request state
            request.state.auth = auth_info
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Service-Auth"] = auth_info["type"]
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise HTTPException(status_code=500, detail="Authentication error")
    
    async def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate incoming request"""
        
        # Try JWT token authentication (service-to-service)
        authorization = request.headers.get("authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ", 1)[1]
            payload = self.auth_manager.verify_service_token(token)
            
            # Verify client certificate if required
            if payload.get("client_cert_required"):
                cert_validator = self.auth_manager.create_client_certificate_validator()
                cert_info = cert_validator(request)
                payload["client_certificate"] = cert_info
            
            return {
                "type": "service_token",
                "service": payload["sub"],
                "permissions": payload.get("permissions", []),
                "payload": payload
            }
        
        # Try API key authentication (external clients)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            key_info = self.auth_manager.verify_api_key(api_key)
            return {
                "type": "api_key",
                "client": key_info["client_name"],
                "permissions": key_info["permissions"],
                "key_info": key_info
            }
        
        # Try request signature authentication
        signature = request.headers.get("X-Request-Signature")
        client_service = request.headers.get("X-Client-Service")
        
        if signature and client_service:
            body = await request.body()
            if self.auth_manager.verify_request_signature(body, signature, client_service):
                return {
                    "type": "signed_request",
                    "service": client_service,
                    "permissions": ["basic"],
                    "signature_verified": True
                }
        
        # Check if mTLS certificate is present
        if request.headers.get("X-SSL-Client-Verified") == "SUCCESS":
            cert_validator = self.auth_manager.create_client_certificate_validator()
            cert_info = cert_validator(request)
            
            service_name = cert_info.get("client_service")
            service_config = self.auth_manager.service_registry.get(service_name, {})
            
            return {
                "type": "mtls_certificate",
                "service": service_name,
                "permissions": service_config.get("permissions", []),
                "certificate": cert_info
            }
        
        # No valid authentication found
        raise HTTPException(status_code=401, detail="Authentication required")


class ServiceClient:
    """HTTP client with automatic service authentication"""
    
    def __init__(self, client_service: str, target_service: str, auth_manager: ServiceAuthManager):
        self.client_service = client_service
        self.target_service = target_service
        self.auth_manager = auth_manager
        self.tls_manager = auth_manager.tls_manager
        
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to target service"""
        
        # Generate service token
        permissions = kwargs.pop("permissions", ["read", "write"])
        token = self.auth_manager.generate_service_token(self.client_service, permissions)
        
        # Setup headers
        headers = kwargs.get("headers", {})
        headers.update({
            "Authorization": f"Bearer {token}",
            "X-Client-Service": self.client_service,
            "Content-Type": "application/json"
        })
        
        # Add request signature if configured
        if "json" in kwargs:
            import json
            body = json.dumps(kwargs["json"]).encode()
            if self.client_service in self.auth_manager.signature_keys:
                signature = hmac.new(
                    self.auth_manager.signature_keys[self.client_service].encode(),
                    body,
                    hashlib.sha256
                ).hexdigest()
                headers["X-Request-Signature"] = signature
        
        kwargs["headers"] = headers
        
        # Determine if mTLS is required
        requires_mtls = self.auth_manager._requires_mtls(self.client_service)
        
        # Create SSL context
        ssl_context = None
        if requires_mtls:
            ssl_context = self.tls_manager.get_client_ssl_context(
                f"{self.client_service}-client",
                verify_server=True
            )
        
        # Make request
        async with httpx.AsyncClient(verify=ssl_context) as client:
            response = await client.request(method, endpoint, **kwargs)
            
            # Handle response
            if response.status_code >= 400:
                logger.error(f"Service request failed: {response.status_code} {response.text}")
                response.raise_for_status()
            
            return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text


def require_permissions(*required_permissions: str):
    """Decorator to require specific permissions for endpoint access"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from function arguments
            request = None
            for arg in args:
                if hasattr(arg, "state"):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, "auth"):
                raise HTTPException(status_code=401, detail="Authentication required")
            
            auth_info = request.state.auth
            user_permissions = auth_info.get("permissions", [])
            
            # Check if user has required permissions
            for permission in required_permissions:
                if permission not in user_permissions:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Permission '{permission}' required"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_service_auth(allowed_services: List[str] = None):
    """Decorator to require service-level authentication"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not hasattr(request.state, "auth"):
                raise HTTPException(status_code=401, detail="Service authentication required")
            
            auth_info = request.state.auth
            
            if allowed_services:
                service_name = auth_info.get("service")
                if service_name not in allowed_services:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Service '{service_name}' not authorized"
                    )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# Example usage and factory functions
def create_auth_manager(service_name: str) -> ServiceAuthManager:
    """Factory function to create auth manager for service"""
    return ServiceAuthManager(service_name)


def create_security_middleware(service_name: str) -> SecurityMiddleware:
    """Factory function to create security middleware"""
    auth_manager = create_auth_manager(service_name)
    return SecurityMiddleware(auth_manager)


if __name__ == "__main__":
    import asyncio
    
    async def test_mutual_auth():
        """Test mutual authentication functionality"""
        
        # Create auth manager for API service
        auth_manager = ServiceAuthManager("smartcompute-api")
        
        # Generate service token for core service
        token = auth_manager.generate_service_token(
            "smartcompute-core", 
            ["execute:analysis", "read:models"]
        )
        print(f"Generated token: {token[:50]}...")
        
        # Verify the token
        try:
            payload = auth_manager.verify_service_token(token)
            print(f"Token verified: {payload}")
        except Exception as e:
            print(f"Token verification failed: {e}")
        
        # Generate API key for external client
        api_info = auth_manager.generate_api_key(
            "external-dashboard",
            ["read:analysis", "read:reports"]
        )
        print(f"Generated API key: {api_info}")
        
        # Test API key verification
        try:
            key_info = auth_manager.verify_api_key(api_info["api_key"])
            print(f"API key verified: {key_info}")
        except Exception as e:
            print(f"API key verification failed: {e}")
        
        print("✅ Mutual authentication test completed")
    
    asyncio.run(test_mutual_auth())