"""
SmartCompute API Documentation Generator
Secure API documentation with access level considerations
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from datetime import datetime


@dataclass
class APIEndpoint:
    """API endpoint documentation structure"""
    path: str
    method: str
    summary: str
    description: str
    access_level: str  # starter, enterprise, industrial
    requires_auth: bool
    parameters: List[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    security_notes: List[str]
    examples: List[Dict[str, Any]]


@dataclass
class APISection:
    """API documentation section"""
    title: str
    description: str
    endpoints: List[APIEndpoint]
    security_overview: str


class SecureAPIDocumentationGenerator:
    """Generate secure API documentation with access level filtering"""
    
    def __init__(self):
        """Initialize documentation generator"""
        self.api_sections = self._define_api_structure()
    
    def _define_api_structure(self) -> List[APISection]:
        """Define complete API structure with security considerations"""
        
        # Core API Endpoints
        core_endpoints = [
            APIEndpoint(
                path="/",
                method="GET",
                summary="API Information",
                description="Get basic API information and available endpoints",
                access_level="starter",
                requires_auth=False,
                parameters=[],
                responses={
                    "200": {
                        "description": "API information",
                        "example": {
                            "message": "SmartCompute API - Performance-based anomaly detection",
                            "version": "1.0.0",
                            "author": "Gatux - Certified Ethical Hacker"
                        }
                    }
                },
                security_notes=[
                    "Public endpoint - no sensitive information exposed",
                    "Rate limiting applied in production"
                ],
                examples=[
                    {
                        "title": "Basic API Info",
                        "request": "GET /",
                        "response": {"status": 200, "data": "API info"}
                    }
                ]
            ),
            
            APIEndpoint(
                path="/health",
                method="GET",
                summary="Health Check",
                description="Service health status for monitoring systems",
                access_level="starter",
                requires_auth=False,
                parameters=[],
                responses={
                    "200": {
                        "description": "Service is healthy",
                        "example": {
                            "status": "healthy",
                            "timestamp": "2024-01-01T00:00:00",
                            "services": {
                                "smart_engine": True,
                                "portable_detector": True,
                                "monitoring_service": True
                            }
                        }
                    }
                },
                security_notes=[
                    "Used by load balancers and monitoring systems",
                    "Does not expose sensitive system information"
                ],
                examples=[
                    {
                        "title": "Health Check",
                        "request": "GET /health",
                        "response": {"status": 200, "data": "healthy"}
                    }
                ]
            ),
            
            APIEndpoint(
                path="/system-info",
                method="GET",
                summary="System Information",
                description="Get current system capabilities and hardware info",
                access_level="starter",
                requires_auth=False,
                parameters=[],
                responses={
                    "200": {
                        "description": "System information",
                        "example": {
                            "os": "Linux",
                            "architecture": "x86_64",
                            "cpu_model": "Intel Core i7",
                            "cpu_cores": 8,
                            "ram_gb": 16.0,
                            "gpu_type": "NVIDIA GTX 1080"
                        }
                    },
                    "500": {
                        "description": "System detection failed",
                        "example": {"detail": "Portable detector not initialized"}
                    }
                },
                security_notes=[
                    "Hardware information is generalized",
                    "No sensitive system paths exposed"
                ],
                examples=[
                    {
                        "title": "System Info Request",
                        "request": "GET /system-info",
                        "response": {"status": 200, "data": "system_info"}
                    }
                ]
            )
        ]
        
        # Performance & Optimization Endpoints
        performance_endpoints = [
            APIEndpoint(
                path="/optimize",
                method="POST",
                summary="Smart Computation Optimization",
                description="Perform intelligent matrix computation with automatic optimization",
                access_level="starter",
                requires_auth=False,
                parameters=[
                    {
                        "name": "precision_needed",
                        "type": "float",
                        "description": "Required precision (0.0-1.0)",
                        "default": 0.95
                    },
                    {
                        "name": "speed_priority",
                        "type": "float", 
                        "description": "Speed vs accuracy priority (0.0-1.0)",
                        "default": 0.5
                    },
                    {
                        "name": "enable_verbose",
                        "type": "boolean",
                        "description": "Enable detailed optimization logs",
                        "default": True
                    }
                ],
                responses={
                    "200": {
                        "description": "Optimization completed",
                        "example": {
                            "method": "numpy_standard",
                            "time": 0.123,
                            "accuracy": 0.98,
                            "speedup": 1.5,
                            "meets_precision": True
                        }
                    },
                    "500": {
                        "description": "Optimization failed",
                        "example": {"detail": "SmartCompute engine not initialized"}
                    }
                },
                security_notes=[
                    "Computation is performed on temporary matrices",
                    "No user data is stored or logged",
                    "Results include only performance metrics"
                ],
                examples=[
                    {
                        "title": "Basic Optimization",
                        "request": "POST /optimize",
                        "body": {"precision_needed": 0.95},
                        "response": {"status": 200, "speedup": 1.5}
                    }
                ]
            ),
            
            APIEndpoint(
                path="/detect-anomalies",
                method="GET",
                summary="Performance Anomaly Detection",
                description="Detect performance anomalies in real-time system metrics",
                access_level="starter",
                requires_auth=False,
                parameters=[],
                responses={
                    "200": {
                        "description": "Anomaly detection result",
                        "example": {
                            "anomaly_score": 0.15,
                            "severity": "low",
                            "cpu_current": 45.2,
                            "memory_current": 62.8,
                            "timestamp": "2024-01-01T00:00:00"
                        }
                    },
                    "400": {
                        "description": "No baseline established",
                        "example": {"detail": "No baseline established"}
                    }
                },
                security_notes=[
                    "Only aggregated performance metrics exposed",
                    "No detailed system internals revealed",
                    "Anomaly scoring uses safe thresholds"
                ],
                examples=[
                    {
                        "title": "Anomaly Detection",
                        "request": "GET /detect-anomalies",
                        "response": {"status": 200, "anomaly_score": 0.15}
                    }
                ]
            )
        ]
        
        # Business Metrics Endpoints (Enhanced Security)
        metrics_endpoints = [
            APIEndpoint(
                path="/metrics/business",
                method="GET",
                summary="Business Metrics Dashboard",
                description="Get KPI dashboard with business metrics (all versions)",
                access_level="starter",
                requires_auth=False,
                parameters=[],
                responses={
                    "200": {
                        "description": "Business metrics dashboard",
                        "example": {
                            "timestamp": "2024-01-01T00:00:00Z",
                            "kpis": {
                                "availability": {"value": 99.5, "status": "healthy"},
                                "performance": {"value": 95.2, "status": "healthy"}
                            }
                        }
                    }
                },
                security_notes=[
                    "Aggregated metrics only - no sensitive details",
                    "Historical data limited to prevent profiling",
                    "Rate limited to prevent excessive monitoring"
                ],
                examples=[
                    {
                        "title": "Business Dashboard",
                        "request": "GET /metrics/business",
                        "response": {"status": 200, "kpis": {}}
                    }
                ]
            ),
            
            APIEndpoint(
                path="/metrics/export",
                method="GET",
                summary="Secure Metrics Export",
                description="Export metrics with optional encryption (Enterprise/Industrial)",
                access_level="starter",
                requires_auth=False,
                parameters=[
                    {
                        "name": "format",
                        "type": "string",
                        "description": "Export format (json, csv)",
                        "default": "json"
                    },
                    {
                        "name": "access_level",
                        "type": "string",
                        "description": "Access level (starter, enterprise, industrial)",
                        "default": "starter"
                    },
                    {
                        "name": "encrypt",
                        "type": "boolean",
                        "description": "Enable encryption (Enterprise/Industrial only)",
                        "default": False
                    },
                    {
                        "name": "x-encryption-password",
                        "type": "string",
                        "in": "header",
                        "description": "Password for encryption (required if encrypt=true)",
                        "required": False
                    }
                ],
                responses={
                    "200": {
                        "description": "Metrics exported successfully",
                        "example": {
                            "data": "exported_metrics_data",
                            "format": "json",
                            "encrypted": False,
                            "access_level": "starter"
                        }
                    },
                    "403": {
                        "description": "Encryption not available in Starter",
                        "example": {"detail": "Encryption not available in Starter version"}
                    }
                },
                security_notes=[
                    "🔐 Enterprise/Industrial: AES-128 encryption with PBKDF2",
                    "🔑 Password-based encryption with unique salts",
                    "🚫 Starter version: Plain text only",
                    "📝 All export attempts are logged for audit",
                    "⏰ Rate limiting prevents bulk data extraction"
                ],
                examples=[
                    {
                        "title": "Encrypted Export (Enterprise)",
                        "request": "GET /metrics/export?encrypt=true&access_level=enterprise",
                        "headers": {"x-encryption-password": "secure_password"},
                        "response": {"status": 200, "encrypted": True}
                    }
                ]
            ),
            
            APIEndpoint(
                path="/metrics/secure-export",
                method="POST",
                summary="Secure Package Export",
                description="Create encrypted metrics package with download token (Enterprise/Industrial only)",
                access_level="enterprise",
                requires_auth=True,
                parameters=[
                    {
                        "name": "format",
                        "type": "string",
                        "description": "Export format (json, csv)",
                        "default": "json"
                    },
                    {
                        "name": "access_level",
                        "type": "string",
                        "description": "Access level (enterprise, industrial)",
                        "default": "enterprise"
                    },
                    {
                        "name": "x-encryption-password",
                        "type": "string",
                        "in": "header",
                        "description": "Password for encryption (required)",
                        "required": True
                    }
                ],
                responses={
                    "200": {
                        "description": "Secure package created",
                        "example": {
                            "success": True,
                            "download_token": "sc_enterprise_...",
                            "expires_in_hours": 2,
                            "encrypted_package": "{...}"
                        }
                    },
                    "403": {
                        "description": "Feature not available",
                        "example": {"detail": "Secure export only available for Enterprise and Industrial"}
                    }
                },
                security_notes=[
                    "🔒 Enterprise-grade AES encryption",
                    "🎫 Time-limited download tokens (2 hours)",
                    "📋 Full audit trail of secure exports",
                    "🚫 Blocked for Starter version",
                    "🔐 Requires strong password authentication"
                ],
                examples=[
                    {
                        "title": "Secure Package Creation",
                        "request": "POST /metrics/secure-export",
                        "headers": {"x-encryption-password": "strong_password"},
                        "response": {"status": 200, "download_token": "sc_enterprise_..."}
                    }
                ]
            )
        ]
        
        # Define sections
        return [
            APISection(
                title="Core API",
                description="Basic API endpoints available in all versions",
                endpoints=core_endpoints,
                security_overview="Public endpoints with basic rate limiting and no sensitive data exposure."
            ),
            APISection(
                title="Performance & Optimization",
                description="Smart computation and anomaly detection features",
                endpoints=performance_endpoints,
                security_overview="Performance analysis endpoints with temporary computation and no data persistence."
            ),
            APISection(
                title="Business Metrics & Analytics",
                description="Business metrics with enterprise encryption capabilities",
                endpoints=metrics_endpoints,
                security_overview="Tiered security model: Starter (plain text), Enterprise/Industrial (AES encryption)."
            )
        ]
    
    def generate_openapi_spec(self, access_level: str = "starter") -> Dict[str, Any]:
        """Generate OpenAPI specification filtered by access level"""
        
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "SmartCompute API",
                "version": "1.0.0",
                "description": f"Performance-based anomaly detection API - {access_level.title()} Version",
                "contact": {
                    "name": "SmartCompute Support",
                    "url": "https://github.com/cathackr/SmartCompute"
                },
                "license": {
                    "name": "Commercial License",
                    "url": "https://smartcompute.io/license"
                }
            },
            "servers": [
                {
                    "url": "https://api.smartcompute.io",
                    "description": "Production server"
                },
                {
                    "url": "http://localhost:8000",
                    "description": "Development server"
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    },
                    "PasswordHeader": {
                        "type": "apiKey",
                        "in": "header", 
                        "name": "x-encryption-password"
                    }
                }
            },
            "security": [],
            "tags": []
        }
        
        # Add sections and endpoints filtered by access level
        for section in self.api_sections:
            # Add tag
            spec["tags"].append({
                "name": section.title,
                "description": section.description,
                "externalDocs": {
                    "description": f"Security Overview: {section.security_overview}",
                    "url": "https://docs.smartcompute.io/security"
                }
            })
            
            # Add endpoints
            for endpoint in section.endpoints:
                # Filter by access level
                if self._endpoint_available_for_access_level(endpoint, access_level):
                    path = endpoint.path
                    method = endpoint.method.lower()
                    
                    if path not in spec["paths"]:
                        spec["paths"][path] = {}
                    
                    spec["paths"][path][method] = self._create_openapi_operation(endpoint, access_level)
        
        return spec
    
    def _endpoint_available_for_access_level(self, endpoint: APIEndpoint, access_level: str) -> bool:
        """Check if endpoint is available for given access level"""
        access_hierarchy = {
            "starter": 0,
            "enterprise": 1, 
            "industrial": 2
        }
        
        user_level = access_hierarchy.get(access_level, 0)
        endpoint_level = access_hierarchy.get(endpoint.access_level, 0)
        
        return user_level >= endpoint_level
    
    def _create_openapi_operation(self, endpoint: APIEndpoint, access_level: str) -> Dict[str, Any]:
        """Create OpenAPI operation object"""
        operation = {
            "summary": endpoint.summary,
            "description": self._create_description_with_security(endpoint, access_level),
            "responses": endpoint.responses,
            "tags": [self._get_section_for_endpoint(endpoint).title]
        }
        
        # Add parameters
        if endpoint.parameters:
            operation["parameters"] = []
            for param in endpoint.parameters:
                param_obj = {
                    "name": param["name"],
                    "in": param.get("in", "query"),
                    "description": param["description"],
                    "required": param.get("required", False),
                    "schema": {"type": param["type"]}
                }
                if "default" in param:
                    param_obj["schema"]["default"] = param["default"]
                
                operation["parameters"].append(param_obj)
        
        # Add security if required
        if endpoint.requires_auth:
            operation["security"] = [{"ApiKeyAuth": []}]
        
        # Add request body for POST endpoints
        if endpoint.method.upper() == "POST":
            operation["requestBody"] = {
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}
                    }
                }
            }
        
        return operation
    
    def _create_description_with_security(self, endpoint: APIEndpoint, access_level: str) -> str:
        """Create description including security notes"""
        description = endpoint.description
        
        if endpoint.security_notes:
            description += "\n\n**Security Notes:**\n"
            for note in endpoint.security_notes:
                description += f"- {note}\n"
        
        # Add access level info
        if endpoint.access_level != "starter":
            if access_level == "starter":
                description += f"\n⚠️ **Note:** This endpoint requires {endpoint.access_level.title()} version or higher."
            else:
                description += f"\n✅ **Available in:** {endpoint.access_level.title()}+ versions"
        
        return description
    
    def _get_section_for_endpoint(self, endpoint: APIEndpoint) -> APISection:
        """Get section that contains the endpoint"""
        for section in self.api_sections:
            if endpoint in section.endpoints:
                return section
        return self.api_sections[0]  # Fallback
    
    def generate_markdown_docs(self, access_level: str = "starter") -> str:
        """Generate comprehensive markdown documentation"""
        
        docs = f"""# SmartCompute API Documentation
## {access_level.title()} Version

**Version:** 1.0.0  
**Base URL:** `https://api.smartcompute.io`  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

SmartCompute is a performance-based anomaly detection API with intelligent computation optimization. The API offers three tiers:

- 🏠 **Starter**: Free version with basic monitoring
- 🏢 **Enterprise**: Advanced features with encrypted metrics export
- 🏭 **Industrial**: Full industrial monitoring with secure packages

## Authentication

Most endpoints are publicly accessible. Advanced features require:
- **API Key**: Include `X-API-Key` header for authenticated endpoints
- **Encryption Password**: Include `x-encryption-password` header for encrypted exports

## Security Model

SmartCompute implements a tiered security model:

"""
        
        # Add security overview for each access level
        if access_level == "starter":
            docs += """### Starter Security
- ✅ Basic rate limiting
- ✅ Input validation
- ❌ No data encryption
- ❌ Limited export capabilities

"""
        elif access_level == "enterprise":
            docs += """### Enterprise Security
- ✅ Advanced rate limiting
- ✅ AES-128 encryption for metrics
- ✅ Password-based key derivation
- ✅ Secure export tokens
- ✅ Audit logging

"""
        else:  # industrial
            docs += """### Industrial Security
- ✅ Enterprise security features
- ✅ Time-limited secure packages
- ✅ Enhanced audit trails
- ✅ Industrial-grade encryption
- ✅ Advanced threat detection

"""
        
        # Add sections
        for section in self.api_sections:
            docs += f"\n## {section.title}\n\n"
            docs += f"{section.description}\n\n"
            docs += f"**Security:** {section.security_overview}\n\n"
            
            # Add endpoints
            for endpoint in section.endpoints:
                if self._endpoint_available_for_access_level(endpoint, access_level):
                    docs += self._format_endpoint_markdown(endpoint, access_level)
        
        return docs
    
    def _format_endpoint_markdown(self, endpoint: APIEndpoint, access_level: str) -> str:
        """Format endpoint as markdown"""
        
        markdown = f"""### {endpoint.method.upper()} {endpoint.path}

**Summary:** {endpoint.summary}

{endpoint.description}

"""
        
        # Parameters
        if endpoint.parameters:
            markdown += "**Parameters:**\n\n"
            for param in endpoint.parameters:
                required = "✅" if param.get("required", False) else "❌"
                default = f" (default: `{param['default']}`)" if 'default' in param else ""
                markdown += f"- `{param['name']}` ({param['type']}) {required} - {param['description']}{default}\n"
            markdown += "\n"
        
        # Security notes
        if endpoint.security_notes:
            markdown += "**Security Notes:**\n\n"
            for note in endpoint.security_notes:
                markdown += f"- {note}\n"
            markdown += "\n"
        
        # Example
        if endpoint.examples:
            example = endpoint.examples[0]
            markdown += f"**Example:**\n\n```bash\n{example['request']}\n```\n\n"
        
        markdown += "---\n\n"
        return markdown


# Global documentation generator
doc_generator = SecureAPIDocumentationGenerator()