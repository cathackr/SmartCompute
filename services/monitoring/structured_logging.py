#!/usr/bin/env python3
"""
SmartCompute Structured Logging
JSON structured logging with PII filtering and log rotation
"""

import json
import logging
import logging.handlers
import re
import os
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from pathlib import Path


class PIIFilter:
    """Filter to remove or mask PII from log messages"""
    
    # Patterns for common PII
    PII_PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
        'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
        'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
        'credit_card': re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'),
        'api_key': re.compile(r'\b[A-Za-z0-9]{24,}\b'),
        'jwt_token': re.compile(r'\beyJ[A-Za-z0-9_/+=-]+\.[A-Za-z0-9_/+=-]+\.[A-Za-z0-9_/+=-]*\b'),
        'password_field': re.compile(r'(password|passwd|pwd|secret|token|key)\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE),
        'bearer_token': re.compile(r'Bearer\s+[A-Za-z0-9_/+=-]+', re.IGNORECASE),
    }
    
    # Sensitive field names to mask completely
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api_key',
        'access_token', 'refresh_token', 'auth_token', 'session_token',
        'private_key', 'secret_key', 'webhook_secret', 'signing_key',
        'encryption_key', 'vault_token', 'db_password', 'redis_password',
        'jwt_secret', 'stripe_secret', 'payment_key'
    }
    
    @classmethod
    def mask_pii(cls, text: str) -> str:
        """Mask PII in text"""
        if not isinstance(text, str):
            return text
            
        masked_text = text
        
        # Mask patterns
        for pattern_name, pattern in cls.PII_PATTERNS.items():
            if pattern_name == 'password_field':
                # Special handling for password fields
                masked_text = pattern.sub(r'\1: ***MASKED***', masked_text)
            elif pattern_name in ['email', 'ip_address']:
                # Hash emails and IPs for correlation while preserving privacy
                def hash_match(match):
                    value = match.group(0)
                    hashed = hashlib.md5(value.encode()).hexdigest()[:8]
                    return f"***{pattern_name.upper()}-{hashed}***"
                masked_text = pattern.sub(hash_match, masked_text)
            else:
                # Completely mask other PII
                masked_text = pattern.sub(f"***{pattern_name.upper()}-MASKED***", masked_text)
        
        return masked_text
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary by masking sensitive fields"""
        if not isinstance(data, dict):
            return data
            
        sanitized = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Mask sensitive field values
            if any(sensitive in key_lower for sensitive in cls.SENSITIVE_FIELDS):
                sanitized[key] = "***MASKED***"
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_dict(item) if isinstance(item, dict)
                    else cls.mask_pii(str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                sanitized[key] = cls.mask_pii(value)
            else:
                sanitized[key] = value
                
        return sanitized


class JSONFormatter(logging.Formatter):
    """JSON formatter with PII filtering"""
    
    def __init__(self, service_name: str, environment: str = "production", mask_pii: bool = True):
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        self.mask_pii = mask_pii
        
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        # Base log structure
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "service": self.service_name,
            "environment": self.environment,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add trace ID if available (for distributed tracing)
        if hasattr(record, 'trace_id'):
            log_entry["trace_id"] = record.trace_id
        
        if hasattr(record, 'span_id'):
            log_entry["span_id"] = record.span_id
            
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_entry["correlation_id"] = record.correlation_id
        
        # Add user ID if available (but hash it for privacy)
        if hasattr(record, 'user_id'):
            user_id = str(record.user_id)
            log_entry["user_id_hash"] = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if self.mask_pii 
                           else PIIFilter.mask_pii(self.formatException(record.exc_info))
            }
        
        # Add extra fields from record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message',
                          'trace_id', 'span_id', 'correlation_id', 'user_id', 'request_id']:
                extra_fields[key] = value
        
        if extra_fields:
            if self.mask_pii:
                log_entry["extra"] = PIIFilter.sanitize_dict(extra_fields)
            else:
                log_entry["extra"] = extra_fields
        
        # Apply PII filtering to the entire log entry
        if self.mask_pii:
            log_entry["message"] = PIIFilter.mask_pii(log_entry["message"])
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    log_dir: str = "/var/log/smartcompute",
    environment: str = "production",
    max_bytes: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 5,
    mask_pii: bool = True,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup structured logging for SmartCompute service
    
    Args:
        service_name: Name of the service
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        environment: Environment name (development, production, etc.)
        max_bytes: Maximum size per log file
        backup_count: Number of backup files to keep
        mask_pii: Whether to mask PII in logs
        console_output: Whether to output to console
    """
    
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create JSON formatter
    formatter = JSONFormatter(service_name, environment, mask_pii)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{service_name}.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler (for errors and above)
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{service_name}-errors.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Console handler for development/debugging
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


class ContextualLogger:
    """Logger with contextual information"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set contextual information"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context"""
        self.context.clear()
    
    def _log_with_context(self, level: int, msg: str, *args, **kwargs):
        """Log with context"""
        # Merge context with kwargs
        extra = kwargs.get('extra', {})
        extra.update(self.context)
        kwargs['extra'] = extra
        
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """Log exception with traceback"""
        kwargs['exc_info'] = True
        self.error(msg, *args, **kwargs)


def get_logger(service_name: str, **context) -> ContextualLogger:
    """Get contextual logger for service"""
    base_logger = logging.getLogger(service_name)
    contextual_logger = ContextualLogger(base_logger)
    
    if context:
        contextual_logger.set_context(**context)
    
    return contextual_logger


def log_performance_metrics(logger: ContextualLogger, operation: str, 
                          duration_ms: float, success: bool = True, **metadata):
    """Log performance metrics in structured format"""
    logger.info(
        f"Performance metric: {operation}",
        extra={
            "metric_type": "performance",
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            **metadata
        }
    )


def log_security_event(logger: ContextualLogger, event_type: str, severity: str,
                      source_ip: str = None, user_id: str = None, **details):
    """Log security events with proper masking"""
    logger.warning(
        f"Security event: {event_type}",
        extra={
            "event_type": "security",
            "security_event": event_type,
            "severity": severity,
            "source_ip": source_ip,  # Will be hashed by PII filter
            "user_id": user_id,      # Will be hashed by PII filter
            **details
        }
    )


def log_business_event(logger: ContextualLogger, event_type: str, 
                      event_data: Dict[str, Any], **metadata):
    """Log business events"""
    logger.info(
        f"Business event: {event_type}",
        extra={
            "event_type": "business",
            "business_event": event_type,
            "event_data": event_data,
            **metadata
        }
    )


if __name__ == "__main__":
    # Test structured logging
    import time
    
    # Setup logging
    logger = setup_logging(
        service_name="test-service",
        log_level="DEBUG",
        log_dir="./test_logs",
        environment="development",
        mask_pii=True,
        console_output=True
    )
    
    # Get contextual logger
    ctx_logger = get_logger("test-service", request_id="req-123", user_id="user-456")
    
    # Test various log types
    ctx_logger.info("Service started successfully")
    
    # Test PII masking
    ctx_logger.info("User login: email=user@example.com, ip=192.168.1.100")
    
    # Test performance logging
    log_performance_metrics(
        ctx_logger, 
        "database_query", 
        duration_ms=45.2, 
        query_type="SELECT", 
        table="users"
    )
    
    # Test security event
    log_security_event(
        ctx_logger,
        "failed_login",
        severity="medium",
        source_ip="192.168.1.100",
        user_id="user-456",
        attempts=3
    )
    
    # Test business event
    log_business_event(
        ctx_logger,
        "payment_processed",
        {"amount": 29.99, "currency": "USD", "payment_id": "pay_123"}
    )
    
    # Test error with PII
    try:
        raise ValueError("Database connection failed with password=secret123")
    except Exception:
        ctx_logger.exception("Database error occurred")
    
    print("Logging tests completed. Check ./test_logs/ directory for output.")