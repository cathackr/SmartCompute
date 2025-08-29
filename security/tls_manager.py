#!/usr/bin/env python3
"""
SmartCompute TLS Manager
Handles TLS configuration and certificate management for microservices
"""

import os
import ssl
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import aiofiles
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

logger = logging.getLogger(__name__)


class TLSManager:
    """Manages TLS certificates and SSL contexts for SmartCompute services"""
    
    def __init__(self, certs_dir: str = None):
        self.certs_dir = Path(certs_dir or "/app/security/tls")
        self.ca_cert_path = self.certs_dir / "ca" / "ca-cert.pem"
        self.ca_key_path = self.certs_dir / "ca" / "ca-key.pem"
        self.server_certs_dir = self.certs_dir / "server"
        self.client_certs_dir = self.certs_dir / "client"
        
        # Cache for SSL contexts
        self._ssl_contexts: Dict[str, ssl.SSLContext] = {}
        self._cert_cache: Dict[str, x509.Certificate] = {}
        
    def _load_certificate(self, cert_path: Path) -> Optional[x509.Certificate]:
        """Load and cache X.509 certificate"""
        if cert_path in self._cert_cache:
            return self._cert_cache[cert_path]
            
        try:
            if not cert_path.exists():
                logger.warning(f"Certificate not found: {cert_path}")
                return None
                
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
                cert = x509.load_pem_x509_certificate(cert_data)
                self._cert_cache[cert_path] = cert
                return cert
                
        except Exception as e:
            logger.error(f"Failed to load certificate {cert_path}: {e}")
            return None
    
    def _verify_certificate_chain(self, cert_path: Path) -> bool:
        """Verify certificate chain against CA"""
        try:
            cert = self._load_certificate(cert_path)
            ca_cert = self._load_certificate(self.ca_cert_path)
            
            if not cert or not ca_cert:
                return False
            
            # Basic chain validation
            # In production, use proper certificate chain validation
            issuer = cert.issuer
            ca_subject = ca_cert.subject
            
            return issuer == ca_subject
            
        except Exception as e:
            logger.error(f"Certificate chain verification failed: {e}")
            return False
    
    def check_certificate_expiry(self, cert_path: Path, days_warning: int = 30) -> Dict[str, Any]:
        """Check certificate expiry status"""
        cert = self._load_certificate(cert_path)
        if not cert:
            return {"status": "error", "message": "Certificate not found or invalid"}
        
        now = datetime.utcnow()
        expiry = cert.not_valid_after
        days_until_expiry = (expiry - now).days
        
        status = "valid"
        if days_until_expiry <= 0:
            status = "expired"
        elif days_until_expiry <= days_warning:
            status = "expiring_soon"
        
        return {
            "status": status,
            "expires_at": expiry.isoformat(),
            "days_until_expiry": days_until_expiry,
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "serial_number": str(cert.serial_number)
        }
    
    def get_server_ssl_context(self, service_name: str, require_client_cert: bool = False) -> Optional[ssl.SSLContext]:
        """Create SSL context for server with optional client certificate verification"""
        cache_key = f"server_{service_name}_{require_client_cert}"
        
        if cache_key in self._ssl_contexts:
            return self._ssl_contexts[cache_key]
        
        try:
            cert_path = self.server_certs_dir / f"{service_name}-cert.pem"
            key_path = self.server_certs_dir / f"{service_name}-key.pem"
            
            if not cert_path.exists() or not key_path.exists():
                logger.error(f"Server certificate files not found for {service_name}")
                return None
            
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(str(cert_path), str(key_path))
            
            # Configure security settings
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
            # Enable client certificate verification if required
            if require_client_cert:
                context.verify_mode = ssl.CERT_REQUIRED
                context.load_verify_locations(str(self.ca_cert_path))
                logger.info(f"Client certificate verification enabled for {service_name}")
            else:
                context.verify_mode = ssl.CERT_NONE
            
            # Verify our own certificate chain
            if not self._verify_certificate_chain(cert_path):
                logger.warning(f"Certificate chain verification failed for {service_name}")
            
            self._ssl_contexts[cache_key] = context
            logger.info(f"SSL context created for server {service_name}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create SSL context for {service_name}: {e}")
            return None
    
    def get_client_ssl_context(self, client_name: str, verify_server: bool = True) -> Optional[ssl.SSLContext]:
        """Create SSL context for client with optional server verification"""
        cache_key = f"client_{client_name}_{verify_server}"
        
        if cache_key in self._ssl_contexts:
            return self._ssl_contexts[cache_key]
        
        try:
            cert_path = self.client_certs_dir / f"{client_name}-cert.pem"
            key_path = self.client_certs_dir / f"{client_name}-key.pem"
            
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            
            # Load client certificate if available
            if cert_path.exists() and key_path.exists():
                context.load_cert_chain(str(cert_path), str(key_path))
                logger.info(f"Client certificate loaded for {client_name}")
            
            # Configure security settings
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
            # Configure server verification
            if verify_server:
                context.check_hostname = True
                context.verify_mode = ssl.CERT_REQUIRED
                context.load_verify_locations(str(self.ca_cert_path))
            else:
                context.check_hostname = False  
                context.verify_mode = ssl.CERT_NONE
                logger.warning(f"Server certificate verification disabled for {client_name}")
            
            self._ssl_contexts[cache_key] = context
            logger.info(f"SSL context created for client {client_name}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create client SSL context for {client_name}: {e}")
            return None
    
    async def validate_all_certificates(self) -> Dict[str, Dict[str, Any]]:
        """Validate all certificates and return status report"""
        results = {}
        
        # Check CA certificate
        if self.ca_cert_path.exists():
            results["ca"] = self.check_certificate_expiry(self.ca_cert_path)
        
        # Check server certificates
        if self.server_certs_dir.exists():
            for cert_file in self.server_certs_dir.glob("*-cert.pem"):
                service_name = cert_file.stem.replace("-cert", "")
                results[f"server_{service_name}"] = self.check_certificate_expiry(cert_file)
        
        # Check client certificates
        if self.client_certs_dir.exists():
            for cert_file in self.client_certs_dir.glob("*-cert.pem"):
                client_name = cert_file.stem.replace("-cert", "")
                results[f"client_{client_name}"] = self.check_certificate_expiry(cert_file)
        
        return results
    
    def get_certificate_info(self, service_name: str, cert_type: str = "server") -> Optional[Dict[str, Any]]:
        """Get detailed certificate information"""
        if cert_type == "server":
            cert_path = self.server_certs_dir / f"{service_name}-cert.pem"
        elif cert_type == "client":
            cert_path = self.client_certs_dir / f"{service_name}-cert.pem"
        else:
            return None
        
        cert = self._load_certificate(cert_path)
        if not cert:
            return None
        
        # Extract SAN (Subject Alternative Names)
        san_extension = None
        try:
            san_extension = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_names = [name.value for name in san_extension.value]
        except x509.ExtensionNotFound:
            san_names = []
        
        # Extract key usage
        key_usage = []
        try:
            key_usage_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE)
            ku = key_usage_ext.value
            if ku.digital_signature: key_usage.append("digital_signature")
            if ku.key_encipherment: key_usage.append("key_encipherment")
            if ku.data_encipherment: key_usage.append("data_encipherment")
        except x509.ExtensionNotFound:
            pass
        
        return {
            "subject": {attr.oid._name: attr.value for attr in cert.subject},
            "issuer": {attr.oid._name: attr.value for attr in cert.issuer},
            "serial_number": str(cert.serial_number),
            "not_valid_before": cert.not_valid_before.isoformat(),
            "not_valid_after": cert.not_valid_after.isoformat(),
            "signature_algorithm": cert.signature_algorithm_oid._name,
            "public_key_size": cert.public_key().key_size if hasattr(cert.public_key(), 'key_size') else None,
            "subject_alternative_names": san_names,
            "key_usage": key_usage,
            "is_ca": self._is_ca_certificate(cert),
            "fingerprint_sha256": cert.fingerprint(hashes.SHA256()).hex()
        }
    
    def _is_ca_certificate(self, cert: x509.Certificate) -> bool:
        """Check if certificate is a CA certificate"""
        try:
            basic_constraints = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.BASIC_CONSTRAINTS)
            return basic_constraints.value.ca
        except x509.ExtensionNotFound:
            return False
    
    def clear_ssl_context_cache(self):
        """Clear SSL context cache (useful after certificate rotation)"""
        self._ssl_contexts.clear()
        self._cert_cache.clear()
        logger.info("SSL context cache cleared")
    
    async def monitor_certificate_expiry(self, callback=None, check_interval: int = 3600):
        """Monitor certificate expiry and call callback for expiring certificates"""
        while True:
            try:
                cert_status = await self.validate_all_certificates()
                
                for cert_name, status in cert_status.items():
                    if status["status"] in ["expired", "expiring_soon"]:
                        logger.warning(f"Certificate {cert_name} status: {status['status']} "
                                     f"(expires: {status['expires_at']})")
                        
                        if callback:
                            await callback(cert_name, status)
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Certificate monitoring error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error


class HTTPSClientSession:
    """HTTPS client with TLS configuration and certificate validation"""
    
    def __init__(self, tls_manager: TLSManager, client_name: str, verify_server: bool = True):
        self.tls_manager = tls_manager
        self.client_name = client_name
        self.verify_server = verify_server
        self._session = None
    
    async def __aenter__(self):
        import aiohttp
        
        ssl_context = self.tls_manager.get_client_ssl_context(
            self.client_name, 
            verify_server=self.verify_server
        )
        
        connector = aiohttp.TCPConnector(
            ssl_context=ssl_context,
            limit=100,
            limit_per_host=30,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': f'SmartCompute-{self.client_name}/1.0',
                'X-Client-Name': self.client_name
            }
        )
        
        return self._session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()


# Global TLS manager instance
tls_manager = TLSManager()


async def setup_tls_monitoring(callback=None):
    """Setup certificate expiry monitoring"""
    await tls_manager.monitor_certificate_expiry(callback)


def get_tls_manager() -> TLSManager:
    """Get global TLS manager instance"""
    return tls_manager


if __name__ == "__main__":
    import asyncio
    
    async def expiry_callback(cert_name: str, status: Dict[str, Any]):
        """Example callback for certificate expiry notifications"""
        print(f"⚠️  Certificate {cert_name} {status['status']}: "
              f"expires {status['expires_at']} ({status['days_until_expiry']} days)")
    
    async def main():
        """Test TLS manager functionality"""
        tls_mgr = TLSManager()
        
        # Validate all certificates
        print("📋 Certificate validation report:")
        cert_status = await tls_mgr.validate_all_certificates()
        
        for cert_name, status in cert_status.items():
            status_icon = {
                "valid": "✅",
                "expiring_soon": "⚠️ ",
                "expired": "❌",
                "error": "💥"
            }.get(status.get("status", "error"), "❓")
            
            print(f"{status_icon} {cert_name}: {status}")
        
        # Test SSL context creation
        print("\n🔐 Testing SSL context creation:")
        server_ctx = tls_mgr.get_server_ssl_context("smartcompute-api", require_client_cert=True)
        print(f"Server context for smartcompute-api: {'✅' if server_ctx else '❌'}")
        
        client_ctx = tls_mgr.get_client_ssl_context("api-client", verify_server=True)
        print(f"Client context for api-client: {'✅' if client_ctx else '❌'}")
        
        # Get certificate details
        print("\n📄 Certificate details:")
        cert_info = tls_mgr.get_certificate_info("smartcompute-api", "server")
        if cert_info:
            print(f"Subject: {cert_info['subject']}")
            print(f"SAN: {cert_info['subject_alternative_names']}")
            print(f"Expires: {cert_info['not_valid_after']}")
        
        print("\n🎉 TLS manager test completed")
    
    asyncio.run(main())