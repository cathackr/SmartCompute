"""
SmartCompute Security Configuration
Production-grade security settings based on post-audit recommendations
"""

import os
import secrets
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from dataclasses import dataclass, field


@dataclass
class SecurityConfig:
    """Security configuration for SmartCompute production deployment"""
    
    # TLS/SSL Configuration
    TLS_CERT_PATH: str = os.getenv("TLS_CERT_PATH", "/certs/cert.pem")
    TLS_KEY_PATH: str = os.getenv("TLS_KEY_PATH", "/certs/key.pem")
    TLS_REQUIRED: bool = os.getenv("TLS_REQUIRED", "true").lower() == "true"
    TLS_MIN_VERSION: str = os.getenv("TLS_MIN_VERSION", "1.2")
    
    # Database Security
    DB_ENCRYPTION_KEY: Optional[str] = None
    DB_CONNECTION_TIMEOUT: int = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))
    DB_MAX_CONNECTIONS: int = int(os.getenv("DB_MAX_CONNECTIONS", "20"))
    DB_SSL_REQUIRED: bool = os.getenv("DB_SSL_REQUIRED", "true").lower() == "true"
    
    # Authentication & Authorization
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "1"))
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "12"))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "20"))
    
    # API Security
    API_KEY_LENGTH: int = int(os.getenv("API_KEY_LENGTH", "32"))
    CORS_ORIGINS: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [])
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = field(default_factory=lambda: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    })
    
    # Audit & Logging
    AUDIT_LOG_ENABLED: bool = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
    AUDIT_LOG_PATH: str = os.getenv("AUDIT_LOG_PATH", "/app/logs/audit.log")
    SECURITY_LOG_PATH: str = os.getenv("SECURITY_LOG_PATH", "/app/logs/security.log")
    LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", "90"))
    
    # Threat Detection Settings
    MAX_FAILED_LOGINS: int = int(os.getenv("MAX_FAILED_LOGINS", "5"))
    LOCKOUT_DURATION: int = int(os.getenv("LOCKOUT_DURATION", "900"))  # 15 minutes
    SUSPICIOUS_IP_THRESHOLD: int = int(os.getenv("SUSPICIOUS_IP_THRESHOLD", "10"))
    
    # Data Protection
    DATA_ENCRYPTION_AT_REST: bool = os.getenv("DATA_ENCRYPTION_AT_REST", "true").lower() == "true"
    BACKUP_ENCRYPTION: bool = os.getenv("BACKUP_ENCRYPTION", "true").lower() == "true"
    PII_SCRUBBING: bool = os.getenv("PII_SCRUBBING", "true").lower() == "true"
    
    def __post_init__(self):
        """Initialize security configuration after dataclass creation"""
        self._load_secrets()
        self._validate_config()
    
    def _load_secrets(self):
        """Load secrets from files or environment variables"""
        # Load JWT secret
        jwt_secret_file = os.getenv("JWT_SECRET_FILE")
        if jwt_secret_file and Path(jwt_secret_file).exists():
            self.JWT_SECRET = Path(jwt_secret_file).read_text().strip()
        else:
            self.JWT_SECRET = os.getenv("JWT_SECRET")
            
        if not self.JWT_SECRET:
            self.JWT_SECRET = secrets.token_urlsafe(32)
            print("⚠️  Generated random JWT secret - not suitable for production")
        
        # Load DB encryption key
        db_key_file = os.getenv("DB_ENCRYPTION_KEY_FILE")
        if db_key_file and Path(db_key_file).exists():
            self.DB_ENCRYPTION_KEY = Path(db_key_file).read_text().strip()
        else:
            self.DB_ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")
            
        if not self.DB_ENCRYPTION_KEY:
            self.DB_ENCRYPTION_KEY = Fernet.generate_key().decode()
            print("⚠️  Generated random DB encryption key - not suitable for production")
    
    def _validate_config(self):
        """Validate security configuration"""
        errors = []
        
        # Validate TLS configuration
        if self.TLS_REQUIRED:
            if not Path(self.TLS_CERT_PATH).exists():
                errors.append(f"TLS certificate not found: {self.TLS_CERT_PATH}")
            if not Path(self.TLS_KEY_PATH).exists():
                errors.append(f"TLS private key not found: {self.TLS_KEY_PATH}")
        
        # Validate JWT secret strength
        if len(self.JWT_SECRET) < 32:
            errors.append("JWT secret too short (minimum 32 characters)")
        
        # Validate rate limiting
        if self.RATE_LIMIT_REQUESTS <= 0:
            errors.append("Rate limit requests must be positive")
        
        # Validate password policy
        if self.PASSWORD_MIN_LENGTH < 8:
            errors.append("Password minimum length too short (minimum 8)")
        
        if errors:
            raise ValueError(f"Security configuration errors: {'; '.join(errors)}")
    
    def get_encryption_key(self) -> bytes:
        """Get database encryption key as bytes"""
        return self.DB_ENCRYPTION_KEY.encode() if isinstance(self.DB_ENCRYPTION_KEY, str) else self.DB_ENCRYPTION_KEY
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    def get_cors_origins(self) -> list:
        """Get CORS origins as list"""
        if not self.CORS_ORIGINS or self.CORS_ORIGINS == [""]:
            return ["http://localhost:3000"] if not self.is_production() else []
        return self.CORS_ORIGINS
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        headers = self.SECURITY_HEADERS.copy()
        
        if self.is_production():
            # Stricter CSP for production
            headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none';"
            )
        
        return headers


class SecurityAuditLogger:
    """Security event audit logger"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup security audit logging"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory
        log_dir = Path(self.config.AUDIT_LOG_PATH).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup audit logger
        self.audit_logger = logging.getLogger("smartcompute.security.audit")
        handler = RotatingFileHandler(
            self.config.AUDIT_LOG_PATH,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def log_auth_attempt(self, username: str, ip: str, success: bool):
        """Log authentication attempt"""
        status = "SUCCESS" if success else "FAILED"
        self.audit_logger.info(f"AUTH_{status} - User: {username}, IP: {ip}")
    
    def log_api_access(self, endpoint: str, ip: str, user_id: Optional[str] = None):
        """Log API access"""
        user_info = f"User: {user_id}" if user_id else "Anonymous"
        self.audit_logger.info(f"API_ACCESS - Endpoint: {endpoint}, IP: {ip}, {user_info}")
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """Log general security event"""
        self.audit_logger.log(
            getattr(logging, severity.upper()),
            f"SECURITY_EVENT - Type: {event_type}, Details: {details}"
        )


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._requests = {}  # {key: [(timestamp, count), ...]}
        self._lock = __import__('threading').Lock()
    
    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Check if request is allowed for given key"""
        import time
        
        with self._lock:
            current_time = time.time()
            window_start = current_time - self.config.RATE_LIMIT_WINDOW
            
            # Clean old entries
            if key in self._requests:
                self._requests[key] = [
                    (ts, count) for ts, count in self._requests[key]
                    if ts > window_start
                ]
            else:
                self._requests[key] = []
            
            # Count requests in window
            total_requests = sum(count for _, count in self._requests[key])
            
            if total_requests >= self.config.RATE_LIMIT_REQUESTS:
                return False, total_requests
            
            # Add current request
            self._requests[key].append((current_time, 1))
            return True, total_requests + 1


def generate_api_key() -> str:
    """Generate secure API key"""
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """Encrypt sensitive data"""
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt sensitive data"""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode()


# Global security config instance - only initialize if not in testing mode
security_config = None

def get_security_config():
    """Get security config instance - lazy initialization"""
    global security_config
    if security_config is None:
        # Don't validate config in test mode
        is_test_mode = os.getenv("PYTEST_CURRENT_TEST") is not None
        if is_test_mode:
            # Create minimal config for testing
            import tempfile
            test_config = SecurityConfig()
            test_config.TLS_REQUIRED = False
            test_config.JWT_SECRET = "test_secret" * 4  # 44 characters
            return test_config
        else:
            security_config = SecurityConfig()
    return security_config