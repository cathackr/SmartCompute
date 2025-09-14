#!/usr/bin/env python3
"""
Ejemplo: Monitoreo IoT - Sensores de Temperatura y Humedad
Usando el template estandarizado SmartCompute
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smartcompute_dashboard_template import SmartComputeDashboard
import numpy as np

def create_iot_sensors_dashboard():
    """Dashboard para monitoreo de sensores IoT"""

    dashboard = SmartComputeDashboard("SMARTCOMPUTE IOT SENSOR MONITORING SYSTEM", "SENSORS ONLINE")
    gs = dashboard.create_base_layout()

    # Panel principal - Estado de sensores
    sensors_data = {
        'labels': ['TEMP SENSOR 01', 'TEMP SENSOR 02', 'HUMIDITY 01', 'HUMIDITY 02',
                   'PRESSURE 01', 'AIR QUALITY', 'MOTION DETECT', 'LIGHT SENSOR'],
        'values': [98, 95, 89, 92, 87, 78, 100, 94],
        'colors': ['#ff6b6b', '#ff4757', '#48dbfb', '#0984e3', '#00b894', '#fdcb6e', '#e17055', '#a29bfe']
    }
    dashboard.create_main_analysis_panel(gs, sensors_data,
                                        'IOT SENSORS - HEALTH & CONNECTIVITY STATUS',
                                        'SENSOR HEALTH (%)')

    # Métricas ambientales actuales
    env_metrics = {
        'labels': ['Temp\n23.5°C', 'Humid\n67%', 'Press\n1013hPa', 'AQI\n45'],
        'values': [75, 67, 85, 45],
        'colors': ['#ff6b6b', '#48dbfb', '#00b894', '#fdcb6e']
    }
    dashboard.create_metrics_panel(gs, env_metrics, 'CURRENT READINGS')

    # Distribución por ubicación
    location_data = {
        'labels': ['SALA A', 'SALA B', 'EXTERIOR', 'ALMACÉN', 'OFICINA'],
        'values': [8, 6, 4, 3, 5],
        'colors': ['#00b894', '#48dbfb', '#fdcb6e', '#e17055', '#a29bfe']
    }
    dashboard.create_bar_panel(gs, (1, 0), location_data, 'SENSORS BY LOCATION', 'SENSOR COUNT')

    # Alertas por tipo
    alerts_data = {
        'labels': ['NORMAL', 'WARNING', 'CRITICAL', 'OFFLINE', 'MAINTENANCE'],
        'values': [82, 12, 3, 2, 1],
        'colors': ['#00b894', '#fdcb6e', '#ff6b6b', '#636e72', '#a29bfe']
    }
    dashboard.create_bar_panel(gs, (1, 1), alerts_data, 'ALERT STATUS', 'PERCENTAGE')

    # Consumo energético
    power_data = {
        'labels': ['TEMP SENSORS', 'HUMIDITY', 'PRESSURE', 'AIR QUALITY', 'MOTION'],
        'values': [45, 38, 67, 89, 23],
        'colors': ['#ff6b6b', '#48dbfb', '#00b894', '#fdcb6e', '#e17055']
    }
    dashboard.create_horizontal_bar_panel(gs, (1, slice(2, 4)), power_data,
                                         'POWER CONSUMPTION', 'mW')

    # Lecturas en tiempo real - Temperatura y Humedad
    time_points = np.linspace(0, 30, 61)  # Más puntos para sensores
    temp_base = 23.5
    humid_base = 67

    realtime_data = {
        'lines': [
            {
                'x': time_points,
                'y': temp_base + 2 * np.sin(time_points/8) + 0.5 * np.cos(time_points/3) + np.random.normal(0, 0.3, 61),
                'color': '#ff6b6b',
                'label': 'TEMPERATURE (°C)',
                'marker': 'o',
                'fill': True
            },
            {
                'x': time_points,
                'y': humid_base + 8 * np.cos(time_points/10) + 2 * np.sin(time_points/4) + np.random.normal(0, 1, 61),
                'color': '#48dbfb',
                'label': 'HUMIDITY (%)',
                'marker': 's',
                'fill': True
            },
            {
                'x': time_points,
                'y': 1013 + 5 * np.sin(time_points/12) + np.random.normal(0, 1, 61) - 970,  # Normalizado para gráfico
                'color': '#00b894',
                'label': 'PRESSURE (hPa - 970)',
                'marker': '^',
                'fill': False
            }
        ],
        'xlabel': 'TIME (SECONDS)',
        'ylabel': 'SENSOR READINGS',
        'ylim': (0, 100)
    }
    dashboard.create_realtime_panel(gs, realtime_data, 'REAL-TIME ENVIRONMENTAL MONITORING')

    # Información detallada de sensores
    left_info = """SENSOR NETWORK STATUS:
├─ TOTAL SENSORS:       26 ACTIVE
├─ COMMUNICATION:       WIFI + ZIGBEE MESH
├─ DATA RATE:           1 READING/SEC
├─ NETWORK UPTIME:      99.8% (30 DAYS)
├─ BATTERY STATUS:      AVG 78% REMAINING
└─ SIGNAL STRENGTH:     -45dBm AVERAGE

TEMPERATURE MONITORING:
├─ SENSOR 01 (SALA A):  23.2°C (NORMAL)
├─ SENSOR 02 (SALA B):  24.1°C (NORMAL)
├─ OUTDOOR SENSOR:      18.7°C (NORMAL)
├─ THRESHOLD HIGH:      30°C
├─ THRESHOLD LOW:       15°C
└─ CALIBRATION:         LAST: 2024-09-01"""

    right_info = """ENVIRONMENTAL CONDITIONS:
├─ HUMIDITY LEVELS:     67% AVG (OPTIMAL)
├─ AIR PRESSURE:        1013 hPa (STABLE)
├─ AIR QUALITY INDEX:   45 (GOOD)
├─ LIGHT LEVELS:        850 LUX (ADEQUATE)
├─ MOTION DETECTED:     12 EVENTS/HOUR
└─ NOISE LEVELS:        42dB (QUIET)

SYSTEM HEALTH:
├─ CPU USAGE:           8% (IOT GATEWAY)
├─ MEMORY USAGE:        34% (512MB TOTAL)
├─ STORAGE USED:        67% (32GB SDCARD)
├─ DATA TRANSMITTED:    2.3GB (THIS MONTH)
├─ ALERTS SENT:         15 (LAST 24H)
└─ MAINTENANCE DUE:     NEXT: 2024-10-15"""

    dashboard.create_info_panel(gs, left_info, right_info)
    dashboard.add_footer("SmartCompute IoT | Industrial Sensor Monitoring | Alert Threshold: Temp >30°C, Humidity >80%")

    return dashboard.finalize('smartcompute_iot_sensors.png')