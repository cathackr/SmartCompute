#!/usr/bin/env python3
"""
SmartCompute Industrial - Network Intelligence API
REST API for network monitoring and analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime, timedelta

from network_intelligence import (
    NetworkIntelligenceAnalyzer, SecurityDeviceIntegrator, LocalThreatAnalyzer,
    AlertSeverity, DeviceType, ProtocolType
)

app = FastAPI(
    title="SmartCompute Network Intelligence API",
    version="1.0.0",
    description="Advanced network monitoring and analysis for industrial environments"
)

# Global analyzer instance
network_analyzer = None


class SecurityDeviceConfig(BaseModel):
    ip: str
    vendor: str  # cisco, fortinet, paloalto, checkpoint, opengear
    username: str
    password: str
    api_key: Optional[str] = None


class CiscoConfig(BaseModel):
    xdr_api_key: Optional[str] = None
    umbrella_client_id: Optional[str] = None
    umbrella_client_secret: Optional[str] = None


class NetworkScanRequest(BaseModel):
    subnets: List[str]
    scan_ports: List[int] = [22, 23, 80, 443, 502, 44818, 4840, 161]


@app.on_event("startup")
async def startup_event():
    """Initialize network analyzer"""
    global network_analyzer
    
    try:
        network_analyzer = NetworkIntelligenceAnalyzer()
        
        # Start monitoring in background
        asyncio.create_task(network_analyzer.start_monitoring())
        
        logging.info("🚀 Network Intelligence API started")
        
    except Exception as e:
        logging.error(f"Failed to start network analyzer: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global network_analyzer
    
    if network_analyzer:
        await network_analyzer.stop_monitoring()
        logging.info("🛑 Network Intelligence API stopped")


# === DEVICE DISCOVERY ENDPOINTS ===

@app.get("/api/network/devices")
async def get_discovered_devices(
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    protocol: Optional[str] = Query(None, description="Filter by protocol"),
    subnet: Optional[str] = Query(None, description="Filter by subnet")
):
    """Get all discovered network devices"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    devices = []
    
    for ip, device in network_analyzer.discovered_devices.items():
        # Apply filters
        if device_type and device.device_type.value != device_type:
            continue
        if protocol and not any(p.value == protocol for p in device.protocols):
            continue
        if subnet and subnet not in device.subnet:
            continue
        
        device_info = {
            "ip_address": device.ip_address,
            "mac_address": device.mac_address,
            "hostname": device.hostname,
            "device_type": device.device_type.value,
            "vendor": device.vendor,
            "open_ports": device.open_ports,
            "protocols": [p.value for p in device.protocols],
            "response_time_ms": device.response_time,
            "subnet": device.subnet,
            "last_seen": device.last_seen.isoformat(),
            "vlan_id": device.vlan_id
        }
        
        devices.append(device_info)
    
    return {
        "devices": devices,
        "total_count": len(devices),
        "discovery_active": network_analyzer.monitoring_active
    }


@app.get("/api/network/topology")
async def get_network_topology():
    """Get network topology information"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    topology = network_analyzer.get_network_topology()
    return topology


@app.post("/api/network/scan")
async def trigger_network_scan(scan_request: NetworkScanRequest, background_tasks: BackgroundTasks):
    """Trigger manual network scan"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    async def perform_scan():
        for subnet in scan_request.subnets:
            await network_analyzer.scan_subnet(subnet)
    
    background_tasks.add_task(perform_scan)
    
    return {
        "message": "Network scan initiated",
        "subnets": scan_request.subnets,
        "scan_ports": scan_request.scan_ports
    }


# === PROTOCOL ANALYSIS ENDPOINTS ===

@app.get("/api/network/protocols")
async def get_protocol_summary():
    """Get summary of detected protocols"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    protocol_stats = {}
    device_count_by_protocol = {}
    
    for device in network_analyzer.discovered_devices.values():
        for protocol in device.protocols:
            protocol_name = protocol.value
            if protocol_name not in protocol_stats:
                protocol_stats[protocol_name] = {
                    "device_count": 0,
                    "devices": []
                }
            
            protocol_stats[protocol_name]["device_count"] += 1
            protocol_stats[protocol_name]["devices"].append({
                "ip": device.ip_address,
                "hostname": device.hostname,
                "device_type": device.device_type.value
            })
    
    return {
        "protocols": protocol_stats,
        "total_protocols": len(protocol_stats),
        "industrial_protocols": [p for p in protocol_stats.keys() 
                               if p in ["modbus_tcp", "profinet", "ethernet_ip", "opcua"]]
    }


@app.get("/api/network/protocols/{protocol}/devices")
async def get_devices_by_protocol(protocol: str):
    """Get devices using specific protocol"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    try:
        protocol_enum = ProtocolType(protocol)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown protocol: {protocol}")
    
    devices = []
    for device in network_analyzer.discovered_devices.values():
        if protocol_enum in device.protocols:
            devices.append({
                "ip_address": device.ip_address,
                "hostname": device.hostname,
                "device_type": device.device_type.value,
                "response_time_ms": device.response_time,
                "open_ports": device.open_ports
            })
    
    return {
        "protocol": protocol,
        "devices": devices,
        "count": len(devices)
    }


# === PERFORMANCE MONITORING ENDPOINTS ===

@app.get("/api/network/performance")
async def get_performance_metrics(
    device_ip: Optional[str] = Query(None, description="Filter by device IP"),
    hours: int = Query(24, description="Hours of history to return")
):
    """Get network performance metrics"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    metrics = []
    for metric in network_analyzer.performance_metrics:
        if metric.timestamp < cutoff_time:
            continue
        if device_ip and metric.device_ip != device_ip:
            continue
        
        metrics.append({
            "timestamp": metric.timestamp.isoformat(),
            "device_ip": metric.device_ip,
            "latency_ms": metric.latency_ms,
            "packet_loss_pct": metric.packet_loss_pct,
            "bandwidth_utilization_pct": metric.bandwidth_utilization_pct,
            "connection_count": metric.connection_count,
            "error_count": metric.error_count,
            "retransmission_count": metric.retransmission_count
        })
    
    return {
        "metrics": metrics,
        "count": len(metrics),
        "time_range_hours": hours
    }


@app.get("/api/network/performance/summary")
async def get_performance_summary():
    """Get network performance summary"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    if not network_analyzer.performance_metrics:
        return {"message": "No performance data available"}
    
    recent_metrics = [m for m in network_analyzer.performance_metrics 
                     if m.timestamp > datetime.now() - timedelta(hours=1)]
    
    if not recent_metrics:
        return {"message": "No recent performance data"}
    
    avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
    max_latency = max(m.latency_ms for m in recent_metrics)
    avg_bandwidth = sum(m.bandwidth_utilization_pct for m in recent_metrics) / len(recent_metrics)
    
    high_latency_devices = [m.device_ip for m in recent_metrics if m.latency_ms > 100]
    high_bandwidth_devices = [m.device_ip for m in recent_metrics if m.bandwidth_utilization_pct > 80]
    
    return {
        "summary_period_hours": 1,
        "total_devices_monitored": len(set(m.device_ip for m in recent_metrics)),
        "average_latency_ms": round(avg_latency, 2),
        "maximum_latency_ms": round(max_latency, 2),
        "average_bandwidth_utilization_pct": round(avg_bandwidth, 2),
        "high_latency_devices": list(set(high_latency_devices)),
        "high_bandwidth_devices": list(set(high_bandwidth_devices)),
        "performance_issues": len(set(high_latency_devices + high_bandwidth_devices))
    }


# === SECURITY AND ALERTS ENDPOINTS ===

@app.get("/api/network/alerts")
async def get_network_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    hours: int = Query(24, description="Hours of history to return"),
    resolved: bool = Query(False, description="Include resolved alerts")
):
    """Get network alerts"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    alerts = []
    for alert in network_analyzer.alerts:
        if alert.timestamp < cutoff_time:
            continue
        if severity and alert.severity.value != severity:
            continue
        if not resolved and alert.resolved:
            continue
        
        alerts.append({
            "timestamp": alert.timestamp.isoformat(),
            "severity": alert.severity.value,
            "alert_type": alert.alert_type,
            "device_ip": alert.device_ip,
            "message": alert.message,
            "details": alert.details,
            "resolved": alert.resolved
        })
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "time_range_hours": hours
    }


@app.get("/api/network/security/summary")
async def get_security_summary():
    """Get network security summary"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    summary = network_analyzer.get_security_summary()
    return summary


@app.post("/api/network/security/devices")
async def add_security_device(device_config: SecurityDeviceConfig):
    """Add security device for monitoring"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    credentials = {
        "username": device_config.username,
        "password": device_config.password
    }
    
    if device_config.api_key:
        credentials["api_key"] = device_config.api_key
    
    network_analyzer.security_integrator.add_security_device(
        device_config.ip, 
        device_config.vendor, 
        credentials
    )
    
    return {
        "message": f"Added {device_config.vendor} security device",
        "device_ip": device_config.ip
    }


@app.get("/api/network/recommendations")
async def get_network_recommendations():
    """Get intelligent network recommendations (no automated actions)"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    # Generate local recommendations based on observed patterns
    recommendations = []
    
    # Analyze current network state
    for device in network_analyzer.discovered_devices.values():
        if device.response_time > 100:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "device_ip": device.ip_address,
                "issue": f"High latency detected ({device.response_time:.1f}ms)",
                "suggestion": "Administrator should check network path to device",
                "automated_action": "none - monitoring only",
                "requires_admin": True
            })
    
    return {
        "recommendations": recommendations,
        "total_count": len(recommendations),
        "note": "SmartCompute provides recommendations only. All actions require administrator approval."
    }


# === CONFLICT DETECTION ENDPOINTS ===

@app.get("/api/network/conflicts")
async def get_network_conflicts():
    """Get detected network conflicts"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    # Get conflict-related alerts
    conflict_alerts = [
        alert for alert in network_analyzer.alerts
        if alert.alert_type in ["ip_conflict", "mac_conflict", "vlan_conflict"]
        and not alert.resolved
    ]
    
    conflicts = []
    for alert in conflict_alerts:
        conflicts.append({
            "timestamp": alert.timestamp.isoformat(),
            "conflict_type": alert.alert_type,
            "severity": alert.severity.value,
            "message": alert.message,
            "details": alert.details,
            "affected_devices": alert.details.get("ip_addresses", [alert.device_ip])
        })
    
    return {
        "conflicts": conflicts,
        "total_conflicts": len(conflicts),
        "conflict_types": list(set(c["conflict_type"] for c in conflicts))
    }


@app.post("/api/network/conflicts/{conflict_id}/resolve")
async def resolve_network_conflict(conflict_id: int):
    """Mark network conflict as resolved"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    if conflict_id < 0 or conflict_id >= len(network_analyzer.alerts):
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    alert = network_analyzer.alerts[conflict_id]
    if alert.alert_type not in ["ip_conflict", "mac_conflict", "vlan_conflict"]:
        raise HTTPException(status_code=400, detail="Not a conflict alert")
    
    alert.resolved = True
    
    return {
        "message": "Conflict marked as resolved",
        "conflict_type": alert.alert_type,
        "device_ip": alert.device_ip
    }


# === THREAT INTELLIGENCE ENDPOINTS ===

@app.get("/api/network/threats")
async def get_threat_intelligence(device_ip: Optional[str] = Query(None)):
    """Get threat intelligence from security devices"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    threat_data = {}
    
    # Get threat intelligence from security devices
    for ip, device_config in network_analyzer.security_integrator.device_configs.items():
        if device_ip and device_ip != ip:
            continue
        
        device_threats = await network_analyzer.security_integrator.get_threat_intelligence(ip)
        threat_data[ip] = device_threats
    
    return {
        "threat_intelligence": threat_data,
        "devices_queried": len(threat_data)
    }


@app.post("/api/network/threats/analyze")
async def analyze_threat_locally(
    threat_type: str,
    device_ip: str,
    severity: str = "medium",
    details: Dict[str, Any] = None
):
    """Analyze threat pattern locally (no external sharing)"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    threat_data = {
        "threat_type": threat_type,
        "device_ip": device_ip,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    # Analyze locally for patterns
    analysis = network_analyzer.threat_analyzer.analyze_local_patterns(threat_data)
    
    # Learn from the pattern (local only)
    network_analyzer.threat_analyzer.learn_from_patterns(threat_data)
    
    return {
        "message": "Threat analyzed locally",
        "analysis": analysis,
        "threat_data": threat_data,
        "external_sharing": "disabled - local analysis only",
        "admin_action_required": True
    }


# === UTILITY ENDPOINTS ===

@app.get("/api/network/health")
async def get_network_health():
    """Get network analyzer health status"""
    if not network_analyzer:
        return {"status": "unavailable", "message": "Network analyzer not initialized"}
    
    return {
        "status": "healthy" if network_analyzer.monitoring_active else "inactive",
        "monitoring_active": network_analyzer.monitoring_active,
        "discovered_devices": len(network_analyzer.discovered_devices),
        "active_alerts": len([a for a in network_analyzer.alerts if not a.resolved]),
        "performance_metrics_count": len(network_analyzer.performance_metrics),
        "uptime_minutes": 0  # Would track actual uptime
    }


@app.get("/api/network/stats")
async def get_network_statistics():
    """Get comprehensive network statistics"""
    if not network_analyzer:
        raise HTTPException(status_code=503, detail="Network analyzer not initialized")
    
    devices_by_type = {}
    devices_by_vendor = {}
    protocols_in_use = set()
    
    for device in network_analyzer.discovered_devices.values():
        # Count by type
        device_type = device.device_type.value
        devices_by_type[device_type] = devices_by_type.get(device_type, 0) + 1
        
        # Count by vendor
        if device.vendor:
            devices_by_vendor[device.vendor] = devices_by_vendor.get(device.vendor, 0) + 1
        
        # Collect protocols
        for protocol in device.protocols:
            protocols_in_use.add(protocol.value)
    
    return {
        "discovery_statistics": {
            "total_devices": len(network_analyzer.discovered_devices),
            "devices_by_type": devices_by_type,
            "devices_by_vendor": devices_by_vendor,
            "protocols_in_use": list(protocols_in_use),
            "industrial_devices": devices_by_type.get("plc", 0) + devices_by_type.get("hmi", 0)
        },
        "security_statistics": {
            "total_alerts": len(network_analyzer.alerts),
            "unresolved_alerts": len([a for a in network_analyzer.alerts if not a.resolved]),
            "critical_alerts": len([a for a in network_analyzer.alerts 
                                  if a.severity == AlertSeverity.CRITICAL and not a.resolved]),
            "security_devices_configured": len(network_analyzer.security_integrator.device_configs)
        },
        "performance_statistics": {
            "metrics_collected": len(network_analyzer.performance_metrics),
            "devices_monitored": len(set(m.device_ip for m in network_analyzer.performance_metrics))
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting SmartCompute Network Intelligence API...")
    print("🌐 Network discovery and monitoring at: http://127.0.0.1:8002")
    print("📋 API Documentation at: http://127.0.0.1:8002/docs")
    print("🔧 Network topology at: http://127.0.0.1:8002/api/network/topology")
    
    uvicorn.run(app, host="127.0.0.1", port=8002)