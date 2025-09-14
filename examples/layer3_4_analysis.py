#!/usr/bin/env python3
"""
Ejemplo: Análisis específico de Capas 3-4 (Red + Transporte)
Usando el template estandarizado SmartCompute
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smartcompute_dashboard_template import SmartComputeDashboard
import numpy as np

def create_network_transport_analysis():
    """Dashboard enfocado en análisis L3-L4"""

    dashboard = SmartComputeDashboard("SMARTCOMPUTE NETWORK-TRANSPORT LAYER ANALYSIS")
    gs = dashboard.create_base_layout()

    # Panel principal - Análisis L3-L4 detallado
    network_data = {
        'labels': ['IPv4 UNICAST', 'IPv6 TRAFFIC', 'ICMP PACKETS', 'ARP REQUESTS',
                   'TCP CONNECTIONS', 'UDP DATAGRAMS', 'TCP RETRANS', 'PORT SCANS'],
        'values': [92, 78, 45, 67, 89, 76, 12, 8],
        'colors': ['#1dd1a1', '#48dbfb', '#ffd700', '#ff9ff3', '#ff6b6b', '#feca57', '#ff4757', '#5352ed']
    }
    dashboard.create_main_analysis_panel(gs, network_data,
                                        'LAYER 3-4 NETWORK & TRANSPORT ANALYSIS',
                                        'ACTIVITY LEVEL (%)')

    # Métricas específicas L3-L4
    routing_data = {
        'labels': ['Routes\n24', 'Hops\n8', 'TTL\n64', 'MSS\n1460'],
        'values': [85, 45, 90, 78],
        'colors': ['#00ff88', '#ffd700', '#ff6b6b', '#48dbfb']
    }
    dashboard.create_metrics_panel(gs, routing_data, 'ROUTING METRICS')

    # Protocolos L4 específicos
    l4_protocols = {
        'labels': ['TCP-443', 'TCP-80', 'UDP-53', 'TCP-22', 'UDP-67'],
        'values': [156, 89, 67, 23, 12],
        'colors': ['#1dd1a1', '#feca57', '#48dbfb', '#ff6b6b', '#ff9ff3']
    }
    dashboard.create_bar_panel(gs, (1, 0), l4_protocols, 'L4 PROTOCOL DISTRIBUTION', 'CONNECTIONS')

    # Estados TCP
    tcp_states = {
        'labels': ['ESTABLISHED', 'TIME_WAIT', 'CLOSE_WAIT', 'SYN_SENT', 'LISTEN'],
        'values': [89, 45, 23, 12, 67],
        'colors': ['#00ff88', '#ffd700', '#ff6b6b', '#ff9ff3', '#48dbfb']
    }
    dashboard.create_bar_panel(gs, (1, 1), tcp_states, 'TCP CONNECTION STATES', 'COUNT')

    # Throughput por puerto
    port_traffic = {
        'labels': ['HTTPS:443', 'HTTP:80', 'SSH:22', 'DNS:53', 'DHCP:67'],
        'values': [2456, 1789, 456, 234, 123],
        'colors': ['#1dd1a1', '#feca57', '#ff6b6b', '#48dbfb', '#ff9ff3']
    }
    dashboard.create_horizontal_bar_panel(gs, (1, slice(2, 4)), port_traffic,
                                         'THROUGHPUT BY PORT', 'MB/S')

    # Latencia en tiempo real
    realtime_data = {
        'lines': [
            {
                'x': np.linspace(0, 30, 31),
                'y': 25 + 8 * np.sin(np.linspace(0, 30, 31)/4) + np.random.normal(0, 2, 31),
                'color': '#ff6b6b',
                'label': 'RTT LATENCY (MS)',
                'marker': 'o',
                'fill': True
            },
            {
                'x': np.linspace(0, 30, 31),
                'y': 45 + 12 * np.cos(np.linspace(0, 30, 31)/6) + np.random.normal(0, 3, 31),
                'color': '#ffd700',
                'label': 'PACKET LOSS (%)',
                'marker': '^',
                'fill': False
            },
            {
                'x': np.linspace(0, 30, 31),
                'y': 78 + 15 * np.sin(np.linspace(0, 30, 31)/3) + np.random.normal(0, 4, 31),
                'color': '#1dd1a1',
                'label': 'THROUGHPUT (MBPS)',
                'marker': 's',
                'fill': True
            }
        ],
        'xlabel': 'TIME (SECONDS)',
        'ylabel': 'NETWORK METRICS',
        'ylim': (0, 120)
    }
    dashboard.create_realtime_panel(gs, realtime_data, 'REAL-TIME NETWORK PERFORMANCE')

    # Información técnica L3-L4
    left_info = """LAYER 3 - NETWORK ANALYSIS:
├─ IPv4 ROUTES:         24 ACTIVE ROUTES
├─ DEFAULT GATEWAY:     192.168.0.1 (REACHABLE)
├─ DNS SERVERS:         8.8.8.8, 1.1.1.1 (RESPONSIVE)
├─ ARP TABLE:           12 ENTRIES CACHED
├─ ICMP RESPONSES:      98% SUCCESS RATE
└─ FRAGMENTATION:       0.2% PACKETS FRAGMENTED

ROUTING TABLE:
├─ 0.0.0.0/0           VIA 192.168.0.1
├─ 192.168.0.0/24      DIRECT INTERFACE
├─ 127.0.0.0/8         LOOPBACK
└─ MULTICAST ROUTES:    4 ACTIVE"""

    right_info = """LAYER 4 - TRANSPORT ANALYSIS:
├─ TCP CONNECTIONS:     89 ESTABLISHED
├─ UDP SOCKETS:         67 ACTIVE
├─ PORT USAGE:          156 PORTS IN USE
├─ CONNECTION POOLING:  78% EFFICIENCY
├─ RETRANSMISSIONS:     0.3% OF PACKETS
└─ WINDOW SCALING:      ENABLED ON ALL CONNECTIONS

PERFORMANCE METRICS:
├─ AVG RTT:             25ms
├─ MAX THROUGHPUT:      95 MBPS
├─ CONNECTION RATE:     12/SEC
├─ BANDWIDTH UTIL:      67%
├─ BUFFER OVERRUNS:     0 DETECTED
└─ QoS CLASSIFICATION:  DSCP MARKING ACTIVE"""

    dashboard.create_info_panel(gs, left_info, right_info)
    dashboard.add_footer("SmartCompute L3-L4 Analysis | Specialized Network Layer Monitoring")

    return dashboard.finalize('smartcompute_l3_l4_analysis.png')