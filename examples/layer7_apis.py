#!/usr/bin/env python3
"""
Ejemplo: Análisis Capa 7 - APIs, Lenguajes y Servicios
Usando el template estandarizado SmartCompute
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smartcompute_dashboard_template import SmartComputeDashboard
import numpy as np

def create_layer7_api_analysis():
    """Dashboard enfocado en análisis de Capa 7 - Aplicaciones"""

    dashboard = SmartComputeDashboard("SMARTCOMPUTE LAYER 7 - APPLICATION & API ANALYSIS")
    gs = dashboard.create_base_layout()

    # Panel principal - Análisis de aplicaciones L7
    l7_data = {
        'labels': ['REST APIs', 'GraphQL', 'WebSocket', 'gRPC', 'SOAP', 'HTTP/2', 'HTTP/3', 'WebRTC'],
        'values': [94, 78, 85, 67, 23, 89, 45, 34],
        'colors': ['#00b894', '#48dbfb', '#fdcb6e', '#e17055', '#636e72', '#a29bfe', '#fd79a8', '#e84393']
    }
    dashboard.create_main_analysis_panel(gs, l7_data,
                                        'LAYER 7 APPLICATION PROTOCOLS & APIs',
                                        'USAGE PERCENTAGE (%)')

    # Métricas de APIs
    api_metrics = {
        'labels': ['Req/s\n1,247', 'Latency\n45ms', 'Errors\n0.3%', 'Uptime\n99.9%'],
        'values': [85, 35, 3, 99],
        'colors': ['#00b894', '#fdcb6e', '#ff6b6b', '#00b894']
    }
    dashboard.create_metrics_panel(gs, api_metrics, 'API PERFORMANCE')

    # Lenguajes de programación detectados
    languages_data = {
        'labels': ['PYTHON', 'JAVASCRIPT', 'JAVA', 'GO', 'RUST'],
        'values': [156, 89, 67, 45, 23],
        'colors': ['#3776ab', '#f7df1e', '#ed8b00', '#00add8', '#ce422b']
    }
    dashboard.create_bar_panel(gs, (1, 0), languages_data, 'PROGRAMMING LANGUAGES', 'PROCESSES')

    # Status codes HTTP
    http_status = {
        'labels': ['2XX SUCCESS', '3XX REDIRECT', '4XX CLIENT', '5XX SERVER', 'TIMEOUT'],
        'values': [89, 8, 2, 0.8, 0.2],
        'colors': ['#00b894', '#fdcb6e', '#ff7675', '#ff6b6b', '#636e72']
    }
    dashboard.create_bar_panel(gs, (1, 1), http_status, 'HTTP RESPONSE CODES', 'PERCENTAGE')

    # Endpoints más utilizados
    endpoints_data = {
        'labels': ['/api/v1/users', '/api/v1/data', '/graphql', '/api/auth', '/websocket'],
        'values': [2847, 1956, 1234, 987, 456],
        'colors': ['#00b894', '#48dbfb', '#fdcb6e', '#e17055', '#a29bfe']
    }
    dashboard.create_horizontal_bar_panel(gs, (1, slice(2, 4)), endpoints_data,
                                         'TOP API ENDPOINTS', 'REQUESTS/MIN')

    # Métricas en tiempo real
    time_points = np.linspace(0, 30, 31)

    realtime_data = {
        'lines': [
            {
                'x': time_points,
                'y': 1200 + 300 * np.sin(time_points/5) + np.random.normal(0, 50, 31),
                'color': '#00b894',
                'label': 'API REQUESTS/MIN',
                'marker': 'o',
                'fill': True
            },
            {
                'x': time_points,
                'y': 45 + 15 * np.cos(time_points/7) + np.random.normal(0, 3, 31),
                'color': '#fdcb6e',
                'label': 'AVG LATENCY (MS)',
                'marker': 's',
                'fill': False
            },
            {
                'x': time_points,
                'y': 0.3 + 0.2 * np.sin(time_points/8) + np.random.normal(0, 0.05, 31),
                'color': '#ff6b6b',
                'label': 'ERROR RATE (%)',
                'marker': '^',
                'fill': True
            }
        ],
        'xlabel': 'TIME (SECONDS)',
        'ylabel': 'API METRICS',
        'ylim': (0, 1800)
    }
    dashboard.create_realtime_panel(gs, realtime_data, 'REAL-TIME API PERFORMANCE MONITORING')

    # Información técnica L7
    left_info = """API GATEWAY ANALYSIS:
├─ TOTAL ENDPOINTS:     47 ACTIVE
├─ AUTHENTICATION:      JWT + OAUTH2
├─ RATE LIMITING:       1000 REQ/MIN/IP
├─ LOAD BALANCER:       NGINX + 3 BACKENDS
├─ CDN CACHE HIT:       78% SUCCESS RATE
└─ API VERSIONS:        v1, v2, v3 SUPPORTED

MICROSERVICES:
├─ USER SERVICE:        3 INSTANCES (PYTHON)
├─ DATA SERVICE:        2 INSTANCES (GO)
├─ AUTH SERVICE:        2 INSTANCES (JAVA)
├─ NOTIFICATION:        1 INSTANCE (NODE.JS)
├─ FILE SERVICE:        2 INSTANCES (RUST)
└─ ANALYTICS:           1 INSTANCE (PYTHON)"""

    right_info = """APPLICATION FRAMEWORKS:
├─ FASTAPI:             USER + DATA SERVICES
├─ EXPRESS.JS:          NOTIFICATION SERVICE
├─ SPRING BOOT:         AUTHENTICATION
├─ ACTIX-WEB:           FILE PROCESSING
├─ GIN FRAMEWORK:       API GATEWAY
└─ REACT + NEXT.JS:     FRONTEND SPA

PERFORMANCE INSIGHTS:
├─ P50 LATENCY:         23ms
├─ P95 LATENCY:         87ms
├─ P99 LATENCY:         156ms
├─ CONCURRENT USERS:    1,247 ACTIVE
├─ DATABASE QUERIES:    2,456/MIN
└─ CACHE EFFICIENCY:    89% HIT RATE"""

    dashboard.create_info_panel(gs, left_info, right_info)
    dashboard.add_footer("SmartCompute L7 Analysis | API Gateway Monitoring | SLA: 99.9% Uptime, <100ms P95")

    return dashboard.finalize('smartcompute_layer7_apis.png')