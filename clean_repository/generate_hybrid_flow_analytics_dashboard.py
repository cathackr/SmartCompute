#!/usr/bin/env python3
"""
SmartCompute Industrial - Dashboard Híbrido con Flujo + Gráficos + MLE Star
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Dashboard que combina:
- Diagrama de flujo interactivo (reacción automática al click)
- Gráficos detallados como el dashboard empresarial
- Análisis MLE Star contextual por área seleccionada
"""

import json
import math
import random
import secrets
from datetime import datetime, timedelta
from pathlib import Path

def generate_comprehensive_industrial_data():
    """Generar datos industriales completos y realistas"""
    now = datetime.now()

    return {
        'timestamp': now,
        'system_health': {
            'overall_score': random.uniform(85, 98),
            'cpu_usage': random.uniform(2, 15),
            'memory_usage': random.uniform(45, 75),
            'temperature': random.uniform(35, 55),
            'uptime_hours': random.randint(720, 8760)
        },
        'process_flow': {
            'raw_materials': {
                'id': 'raw_materials',
                'name': 'Materias Primas',
                'type': 'input',
                'icon': 'fas fa-boxes',
                'status': 'operational',
                'alerts': random.randint(0, 2),
                'personnel': random.randint(3, 6),
                'throughput': random.uniform(85, 98),
                'connections': ['quality_control_in'],
                'position': {'x': 50, 'y': 100},
                'sensors': {
                    'weight_scales': [
                        {'id': 'WS-001', 'type': 'Báscula Industrial', 'value': random.uniform(2.5, 15.8), 'unit': 'Ton', 'status': 'NORMAL'},
                        {'id': 'WS-002', 'type': 'Báscula de Precisión', 'value': random.uniform(450, 2000), 'unit': 'kg', 'status': 'NORMAL'}
                    ],
                    'inventory': [
                        {'id': 'INV-001', 'material': 'Acero Inoxidable 316L', 'quantity': random.uniform(85, 95), 'unit': '%', 'status': 'NORMAL'},
                        {'id': 'INV-002', 'material': 'Polímero PET', 'quantity': random.uniform(60, 75), 'unit': '%', 'status': 'WARNING'}
                    ]
                },
                'network': {
                    'vlan': 'VLAN-100-RAW',
                    'subnet': '192.168.100.0/24',
                    'devices': 12,
                    'bandwidth_usage': random.uniform(15, 35),
                    'security_level': 'HIGH'
                },
                'metrics_data': {
                    'throughput_history': [random.uniform(80, 95) for _ in range(24)],
                    'inventory_levels': [random.uniform(70, 95) for _ in range(24)],
                    'quality_scores': [random.uniform(92, 99) for _ in range(24)]
                }
            },
            'quality_control_in': {
                'id': 'quality_control_in',
                'name': 'Control de Calidad Entrada',
                'type': 'process',
                'icon': 'fas fa-search',
                'status': 'operational',
                'alerts': random.randint(0, 1),
                'personnel': random.randint(2, 4),
                'throughput': random.uniform(90, 99),
                'connections': ['preparation'],
                'position': {'x': 200, 'y': 100},
                'sensors': {
                    'sampling': [
                        {'id': 'SAMP-001', 'type': 'Muestreador Automático', 'samples_hour': random.randint(15, 25), 'status': 'OPERATIONAL'},
                        {'id': 'SAMP-002', 'type': 'Analizador Espectral', 'accuracy': random.uniform(98.5, 99.9), 'unit': '%', 'status': 'OPERATIONAL'}
                    ],
                    'compliance': [
                        {'standard': 'ISO 9001:2015', 'compliance': random.uniform(95, 99.5), 'last_audit': '2025-09-15'},
                        {'standard': 'FDA 21 CFR 11', 'compliance': random.uniform(92, 98), 'incidents': random.randint(0, 2)}
                    ]
                },
                'network': {
                    'vlan': 'VLAN-110-QC',
                    'subnet': '192.168.110.0/24',
                    'devices': 18,
                    'bandwidth_usage': random.uniform(45, 65),
                    'security_level': 'CRITICAL'
                },
                'metrics_data': {
                    'sample_processing': [random.randint(18, 28) for _ in range(24)],
                    'compliance_scores': [random.uniform(94, 99.5) for _ in range(24)],
                    'rejection_rates': [random.uniform(0.1, 2.5) for _ in range(24)]
                }
            },
            'preparation': {
                'id': 'preparation',
                'name': 'Preparación y Mezclado',
                'type': 'process',
                'icon': 'fas fa-blender',
                'status': 'operational',
                'alerts': random.randint(1, 3),
                'personnel': random.randint(4, 8),
                'throughput': random.uniform(82, 95),
                'connections': ['thermal_treatment', 'quality_control_process'],
                'position': {'x': 350, 'y': 100},
                'sensors': {
                    'mixing_parameters': [
                        {'id': 'MIX-001', 'parameter': 'Velocidad de Mezclado', 'value': random.uniform(180, 220), 'unit': 'RPM', 'status': 'NORMAL'},
                        {'id': 'MIX-002', 'parameter': 'Presión de Mezclado', 'value': random.uniform(2.8, 3.5), 'unit': 'bar', 'status': 'NORMAL'},
                        {'id': 'MIX-003', 'parameter': 'Temperatura de Mezcla', 'value': random.uniform(65, 75), 'unit': '°C', 'status': 'WARNING'}
                    ]
                },
                'network': {
                    'vlan': 'VLAN-120-PREP',
                    'subnet': '192.168.120.0/24',
                    'devices': 25,
                    'bandwidth_usage': random.uniform(55, 75),
                    'security_level': 'HIGH'
                },
                'metrics_data': {
                    'mixing_efficiency': [random.uniform(85, 95) for _ in range(24)],
                    'temperature_profile': [random.uniform(68, 78) for _ in range(24)],
                    'pressure_stability': [random.uniform(2.5, 3.8) for _ in range(24)]
                }
            },
            'thermal_treatment': {
                'id': 'thermal_treatment',
                'name': 'Tratamiento Térmico',
                'type': 'process',
                'icon': 'fas fa-fire',
                'status': 'warning',
                'alerts': random.randint(2, 5),
                'personnel': random.randint(6, 12),
                'throughput': random.uniform(75, 88),
                'connections': ['cooling', 'energy_recovery'],
                'position': {'x': 500, 'y': 50},
                'sensors': {
                    'thermal_monitoring': [
                        {'id': 'TEMP-001', 'type': 'Horno Principal', 'value': random.uniform(850, 950), 'unit': '°C', 'status': 'NORMAL'},
                        {'id': 'TEMP-002', 'type': 'Cámara de Enfriamiento', 'value': random.uniform(180, 220), 'unit': '°C', 'status': 'WARNING'},
                        {'id': 'TEMP-003', 'type': 'Detector de Fugas Térmica', 'value': random.uniform(2.5, 8.2), 'unit': 'kW perdidos', 'status': 'WARNING'}
                    ],
                    'gas_monitoring': [
                        {'id': 'GAS-001', 'type': 'Detector CO', 'value': random.uniform(5, 15), 'unit': 'ppm', 'status': 'NORMAL'},
                        {'id': 'GAS-002', 'type': 'Detector NH3', 'value': random.uniform(2, 8), 'unit': 'ppm', 'status': 'CRITICAL'}
                    ]
                },
                'network': {
                    'vlan': 'VLAN-130-THERMAL',
                    'subnet': '192.168.130.0/24',
                    'devices': 32,
                    'bandwidth_usage': random.uniform(70, 90),
                    'security_level': 'CRITICAL'
                },
                'metrics_data': {
                    'furnace_temperature': [random.uniform(840, 960) for _ in range(24)],
                    'energy_consumption': [random.uniform(2800, 3200) for _ in range(24)],
                    'thermal_efficiency': [random.uniform(78, 88) for _ in range(24)]
                }
            },
            'power_distribution': {
                'id': 'power_distribution',
                'name': 'Distribución Eléctrica',
                'type': 'utility',
                'icon': 'fas fa-bolt',
                'status': 'operational',
                'alerts': random.randint(0, 2),
                'personnel': random.randint(3, 6),
                'throughput': random.uniform(92, 99),
                'connections': ['ups_systems'],
                'position': {'x': 800, 'y': 250},
                'sensors': {
                    'electrical_monitoring': [
                        {'id': 'POW-001', 'type': 'Línea Principal A', 'load': random.uniform(75, 90), 'unit': '%', 'status': 'NORMAL'},
                        {'id': 'POW-002', 'type': 'Línea Principal B', 'load': random.uniform(65, 85), 'unit': '%', 'status': 'NORMAL'},
                        {'id': 'POW-003', 'type': 'Línea de Emergencia', 'load': random.uniform(5, 15), 'unit': '%', 'status': 'STANDBY'}
                    ]
                },
                'network': {
                    'vlan': 'VLAN-200-POWER',
                    'subnet': '192.168.200.0/24',
                    'devices': 28,
                    'bandwidth_usage': random.uniform(35, 55),
                    'security_level': 'CRITICAL'
                },
                'metrics_data': {
                    'power_consumption': [random.uniform(2600, 3400) for _ in range(24)],
                    'power_factor': [random.uniform(0.88, 0.96) for _ in range(24)],
                    'harmonic_distortion': [random.uniform(2.1, 6.8) for _ in range(24)]
                }
            },
            'packaging': {
                'id': 'packaging',
                'name': 'Empaquetado',
                'type': 'process',
                'icon': 'fas fa-box',
                'status': 'operational',
                'alerts': random.randint(1, 3),
                'personnel': random.randint(8, 15),
                'throughput': random.uniform(85, 94),
                'connections': ['warehouse'],
                'position': {'x': 1100, 'y': 100},
                'sensors': {
                    'production_flow': [
                        {'id': 'FLOW-001', 'type': 'Contador de Productos', 'value': random.randint(1850, 2200), 'unit': 'unid/h', 'status': 'NORMAL'},
                        {'id': 'FLOW-002', 'type': 'Sensor de Atascos', 'events': random.randint(0, 3), 'unit': 'eventos/h', 'status': 'NORMAL'}
                    ]
                },
                'network': {
                    'vlan': 'VLAN-150-PACK',
                    'subnet': '192.168.150.0/24',
                    'devices': 38,
                    'bandwidth_usage': random.uniform(65, 85),
                    'security_level': 'HIGH'
                },
                'metrics_data': {
                    'packaging_speed': [random.uniform(1800, 2300) for _ in range(24)],
                    'defect_rate': [random.uniform(0.5, 2.8) for _ in range(24)],
                    'efficiency': [random.uniform(82, 96) for _ in range(24)]
                }
            }
        }
    }

def generate_mle_analysis_for_process(process_data):
    """Generar análisis MLE Star específico para el proceso seleccionado"""
    recommendations = []

    process_id = process_data['id']
    process_name = process_data['name']

    # Análisis específico por proceso
    if process_id == 'thermal_treatment':
        # Análisis térmico específico
        recommendations.append({
            'title': 'Optimización de Eficiencia Térmica',
            'description': f'Pérdidas térmicas detectadas en {process_name}',
            'severity': 'MEDIUM',
            'actions': [
                'Mejorar aislamiento en zonas críticas',
                'Implementar recuperadores de calor',
                'Optimizar perfiles de temperatura'
            ],
            'technical_details': {
                'current_efficiency': f"{random.uniform(75, 85):.1f}%",
                'target_efficiency': "90%+",
                'energy_loss': f"{random.uniform(5, 12):.1f} kW"
            }
        })
    elif process_id == 'preparation':
        # Análisis de mezclado
        recommendations.append({
            'title': 'Optimización de Parámetros de Mezclado',
            'description': f'Control reactivo detectado en {process_name}',
            'severity': 'HIGH',
            'actions': [
                'Implementar control predictivo',
                'Ajustar secuencia de mezclado',
                'Optimizar temperatura de proceso'
            ],
            'technical_details': {
                'current_variation': f"±{random.uniform(3, 8):.1f}°C",
                'target_variation': "±2°C",
                'efficiency_gain': f"{random.uniform(8, 15):.1f}%"
            }
        })
    elif process_id == 'power_distribution':
        # Análisis eléctrico
        recommendations.append({
            'title': 'Corrección de Calidad Eléctrica',
            'description': f'Distorsión armónica elevada en {process_name}',
            'severity': 'MEDIUM',
            'actions': [
                'Instalar filtros activos',
                'Balancear cargas por fase',
                'Mejorar factor de potencia'
            ],
            'technical_details': {
                'current_thd': f"{random.uniform(5.2, 9.8):.1f}%",
                'target_thd': "< 5%",
                'power_factor': f"{random.uniform(0.85, 0.92):.2f}"
            }
        })

    # Análisis general aplicable a todos los procesos
    if process_data['throughput'] < 90:
        recommendations.append({
            'title': 'Mejora de Rendimiento Global',
            'description': f'Rendimiento por debajo del óptimo en {process_name}',
            'severity': 'HIGH' if process_data['throughput'] < 80 else 'MEDIUM',
            'actions': [
                'Analizar cuellos de botella',
                'Optimizar programación de producción',
                'Implementar mantenimiento predictivo'
            ],
            'technical_details': {
                'current_throughput': f"{process_data['throughput']:.1f}%",
                'target_throughput': "95%+",
                'improvement_potential': f"{95 - process_data['throughput']:.1f}%"
            }
        })

    return recommendations

def generate_hybrid_dashboard():
    """Generar dashboard híbrido completo"""
    data = generate_comprehensive_industrial_data()

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Industrial - Dashboard Híbrido Avanzado</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #2980b9 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .glass-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        .process-flow-map {{
            position: relative;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #2c3e50 100%);
            border-radius: 15px;
            height: 500px;
            overflow: auto;
            padding: 20px;
        }}
        .process-node {{
            position: absolute;
            width: 120px;
            height: 80px;
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.1);
            color: white;
            padding: 8px;
            font-size: 0.7rem;
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(5px);
        }}
        .process-node:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
            z-index: 10;
        }}
        .process-node.selected {{
            border-color: #FFD700;
            background: rgba(255, 215, 0, 0.3);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        }}
        .process-node.input {{
            background: rgba(76, 175, 80, 0.3);
            border-color: #4CAF50;
        }}
        .process-node.process {{
            background: rgba(33, 150, 243, 0.3);
            border-color: #2196F3;
        }}
        .process-node.utility {{
            background: rgba(156, 39, 176, 0.3);
            border-color: #9C27B0;
        }}
        .connection-line {{
            position: absolute;
            height: 4px;
            background: linear-gradient(90deg, rgba(52,152,219,0.4), rgba(52,152,219,0.9), rgba(52,152,219,0.4));
            border-radius: 2px;
            transform-origin: left center;
            animation: flow 3s infinite;
            z-index: 1;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}
        .connection-arrow {{
            position: absolute;
            width: 0;
            height: 0;
            border-left: 10px solid rgba(52,152,219,0.9);
            border-top: 7px solid transparent;
            border-bottom: 7px solid transparent;
            z-index: 2;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
        }}
        .chart-container {{
            position: relative;
            height: 350px;
            margin: 15px 0;
        }}
        .metric-card {{
            transition: transform 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        .mle-recommendation {{
            background: rgba(255, 193, 7, 0.1);
            border-left: 4px solid #FFC107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }}
        .severity-high {{ border-left-color: #dc3545; }}
        .severity-medium {{ border-left-color: #ffc107; }}
        .severity-low {{ border-left-color: #28a745; }}
        @keyframes flow {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4 text-center">
                    <h1 class="text-white display-4 mb-3">
                        <i class="fas fa-industry me-3"></i>
                        SmartCompute Industrial - Dashboard Híbrido
                    </h1>
                    <h2 class="text-white mb-3">
                        Diagrama de Flujo + Analytics + MLE Star
                    </h2>
                    <div class="row text-white">
                        <div class="col-md-4">
                            <i class="fas fa-clock me-2"></i>
                            <strong>Actualizado:</strong> {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-mouse-pointer me-2"></i>
                            <strong>Click en proceso</strong> para análisis detallado
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-robot me-2"></i>
                            <strong>MLE Star</strong> analiza cada área
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Process Flow Map -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-project-diagram me-2"></i>
                        Diagrama de Flujo de Procesos Industriales
                        <span class="badge bg-info ms-2" id="selectedProcessBadge">Seleccione un proceso</span>
                    </h5>
                    <div class="process-flow-map" id="processFlowMap">"""

    # Generar nodos del flujo de procesos
    for process_id, process in data['process_flow'].items():
        status_class = process['status']
        if process['alerts'] > 2:
            status_class = 'critical'
        elif process['alerts'] > 0:
            status_class = 'warning'

        html_content += f"""
                        <div class="process-node {process['type']} {status_class}"
                             style="left: {process['position']['x']}px; top: {process['position']['y']}px;"
                             onclick="selectProcess('{process_id}')"
                             data-node-id="{process_id}"
                             id="node_{process_id}">
                            <div class="node-icon">
                                <i class="{process['icon']}"></i>
                            </div>
                            <div class="node-name">{process['name']}</div>
                            <div class="node-status">{process['alerts']} alertas</div>
                            <div class="throughput-bar">
                                <div class="throughput-fill" style="width: {process['throughput']:.0f}%"></div>
                            </div>
                        </div>"""

    # Generar conexiones (simplificado para este ejemplo)
    def calculate_connection_line(from_pos, to_pos):
        node_width, node_height = 120, 80
        from_center_x = from_pos['x'] + node_width // 2
        from_center_y = from_pos['y'] + node_height // 2
        to_center_x = to_pos['x'] + node_width // 2
        to_center_y = to_pos['y'] + node_height // 2

        dx = to_center_x - from_center_x
        dy = to_center_y - from_center_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return None

        unit_x = dx / distance
        unit_y = dy / distance

        if abs(unit_x) > abs(unit_y):
            if unit_x > 0:
                from_x = from_pos['x'] + node_width
                from_y = from_center_y
                to_x = to_pos['x']
                to_y = to_center_y
            else:
                from_x = from_pos['x']
                from_y = from_center_y
                to_x = to_pos['x'] + node_width
                to_y = to_center_y
        else:
            if unit_y > 0:
                from_x = from_center_x
                from_y = from_pos['y'] + node_height
                to_x = to_center_x
                to_y = to_pos['y']
            else:
                from_x = from_center_x
                from_y = from_pos['y']
                to_x = to_center_x
                to_y = to_pos['y'] + node_height

        line_dx = to_x - from_x
        line_dy = to_y - from_y
        length = math.sqrt(line_dx * line_dx + line_dy * line_dy)
        angle = math.degrees(math.atan2(line_dy, line_dx))

        arrow_offset = 12
        arrow_x = to_x - (arrow_offset * math.cos(math.radians(angle)))
        arrow_y = to_y - (arrow_offset * math.sin(math.radians(angle)))

        return {
            'x': from_x,
            'y': from_y - 1.5,
            'length': length - arrow_offset,
            'angle': angle,
            'arrow_x': arrow_x - 6,
            'arrow_y': arrow_y - 6
        }

    # Agregar conexiones
    for process_id, process in data['process_flow'].items():
        for connection_id in process['connections']:
            if connection_id in data['process_flow']:
                from_pos = process['position']
                to_pos = data['process_flow'][connection_id]['position']
                line_data = calculate_connection_line(from_pos, to_pos)

                if line_data:
                    html_content += f"""
                        <div class="connection-line"
                             style="left: {line_data['x']}px;
                                    top: {line_data['y']}px;
                                    width: {line_data['length']}px;
                                    transform: rotate({line_data['angle']}deg);">
                        </div>
                        <div class="connection-arrow"
                             style="left: {line_data['arrow_x']}px;
                                    top: {line_data['arrow_y']}px;
                                    transform: rotate({line_data['angle']}deg);">
                        </div>"""

    html_content += f"""
                    </div>
                </div>
            </div>
        </div>

        <!-- Analytics Section (Initially Hidden) -->
        <div class="row mb-4" id="analyticsSection" style="display: none;">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3" id="analyticsTitle">
                        <i class="fas fa-chart-line me-2"></i>
                        Análisis Detallado del Proceso
                    </h5>

                    <!-- Process KPIs -->
                    <div class="row mb-4" id="processKPIs">
                        <!-- Will be populated by JavaScript -->
                    </div>

                    <!-- Charts Row -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="glass-card p-4">
                                <h6 class="text-white mb-3">
                                    <i class="fas fa-chart-area me-2"></i>
                                    Tendencias de Rendimiento (24h)
                                </h6>
                                <div class="chart-container">
                                    <canvas id="performanceChart"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="glass-card p-4">
                                <h6 class="text-white mb-3">
                                    <i class="fas fa-tachometer-alt me-2"></i>
                                    Métricas en Tiempo Real
                                </h6>
                                <div class="chart-container">
                                    <canvas id="realtimeChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Network and Sensors Details -->
                    <div class="row mb-4" id="technicalDetails">
                        <!-- Will be populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>

        <!-- MLE Star Analysis Section -->
        <div class="row mb-4" id="mleSection" style="display: none;">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-robot me-2"></i>
                        Análisis MLE Star - Recomendaciones Específicas
                        <button class="btn btn-sm btn-outline-success ms-2" onclick="runMLEAnalysis()">
                            <i class="fas fa-play"></i> Ejecutar Análisis
                        </button>
                    </h5>
                    <div id="mleRecommendations">
                        <!-- Will be populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="row">
            <div class="col-12">
                <div class="glass-card p-3 text-center">
                    <small class="text-white">
                        SmartCompute Industrial - Dashboard Híbrido |
                        <a href="mailto:ggwre04p0@mozmail.com" class="text-info">ggwre04p0@mozmail.com</a> |
                        <a href="https://www.linkedin.com/in/martín-iribarne-swtf/" class="text-info" target="_blank">LinkedIn</a>
                    </small>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Datos del sistema
        const systemData = {json.dumps(data, indent=8, default=str)};
        let selectedProcess = null;
        let performanceChart = null;
        let realtimeChart = null;

        // Configuración global de gráficos
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.color = '#ffffff';

        // Función principal para seleccionar proceso
        function selectProcess(processId) {{
            // Limpiar selección anterior
            document.querySelectorAll('.process-node').forEach(node => {{
                node.classList.remove('selected');
            }});

            // Seleccionar nuevo proceso
            selectedProcess = processId;
            const node = document.getElementById('node_' + processId);
            node.classList.add('selected');

            const processData = systemData.process_flow[processId];

            // Actualizar badge
            document.getElementById('selectedProcessBadge').textContent = processData.name;

            // Mostrar secciones de análisis
            showAnalyticsSection(processData);
            showMLESection(processData);
        }}

        // Mostrar sección de analytics
        function showAnalyticsSection(processData) {{
            document.getElementById('analyticsTitle').innerHTML = `
                <i class="fas fa-chart-line me-2"></i>
                Análisis Detallado: ${{processData.name}}
            `;

            // Generar KPIs del proceso
            generateProcessKPIs(processData);

            // Generar detalles técnicos
            generateTechnicalDetails(processData);

            // Crear gráficos
            createPerformanceChart(processData);
            createRealtimeChart(processData);

            // Mostrar sección
            document.getElementById('analyticsSection').style.display = 'block';
        }}

        // Generar KPIs del proceso
        function generateProcessKPIs(processData) {{
            const kpisHtml = `
                <div class="col-md-3">
                    <div class="glass-card p-4 text-center metric-card">
                        <div class="display-4 mb-2">
                            <i class="fas fa-tachometer-alt text-info"></i>
                        </div>
                        <h5 class="text-white">Rendimiento</h5>
                        <h3 class="text-info">${{processData.throughput.toFixed(1)}}%</h3>
                        <small class="text-light">Eficiencia actual</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="glass-card p-4 text-center metric-card">
                        <div class="display-4 mb-2">
                            <i class="fas fa-exclamation-triangle text-warning"></i>
                        </div>
                        <h5 class="text-white">Alertas</h5>
                        <h3 class="text-warning">${{processData.alerts}}</h3>
                        <small class="text-light">Alertas activas</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="glass-card p-4 text-center metric-card">
                        <div class="display-4 mb-2">
                            <i class="fas fa-users text-success"></i>
                        </div>
                        <h5 class="text-white">Personal</h5>
                        <h3 class="text-success">${{processData.personnel}}</h3>
                        <small class="text-light">Operadores</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="glass-card p-4 text-center metric-card">
                        <div class="display-4 mb-2">
                            <i class="fas fa-network-wired text-purple"></i>
                        </div>
                        <h5 class="text-white">Red</h5>
                        <h3 class="text-purple">${{processData.network.devices}}</h3>
                        <small class="text-light">Dispositivos</small>
                    </div>
                </div>
            `;
            document.getElementById('processKPIs').innerHTML = kpisHtml;
        }}

        // Generar detalles técnicos
        function generateTechnicalDetails(processData) {{
            let sensorsHtml = '';
            if (processData.sensors) {{
                Object.keys(processData.sensors).forEach(category => {{
                    const sensors = processData.sensors[category];
                    const categoryTitle = category.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());

                    sensorsHtml += `
                        <div class="col-md-6 mb-3">
                            <div class="glass-card p-3">
                                <h6 class="text-warning mb-2">${{categoryTitle}}</h6>`;

                    sensors.forEach(sensor => {{
                        const statusClass = sensor.status === 'NORMAL' || sensor.status === 'OPERATIONAL' ? 'success' : 'warning';
                        sensorsHtml += `
                            <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-dark rounded">
                                <div>
                                    <strong class="text-white">${{sensor.id || sensor.type || sensor.parameter}}</strong><br>
                                    <small class="text-light">${{sensor.type || sensor.parameter || 'Sensor'}}</small>
                                </div>
                                <div class="text-end">
                                    <span class="text-white">${{sensor.value || sensor.samples_hour || sensor.accuracy || 'N/A'}} ${{sensor.unit || ''}}</span><br>
                                    <span class="badge bg-${{statusClass}}">${{sensor.status}}</span>
                                </div>
                            </div>`;
                    }});

                    sensorsHtml += '</div></div>';
                }});
            }}

            // Información de red
            const networkHtml = `
                <div class="col-md-6 mb-3">
                    <div class="glass-card p-3">
                        <h6 class="text-info mb-2">Información de Red</h6>
                        <div class="row">
                            <div class="col-6">
                                <div class="p-2 bg-dark rounded text-center">
                                    <strong class="text-info">VLAN</strong><br>
                                    <span class="text-white">${{processData.network.vlan}}</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="p-2 bg-dark rounded text-center">
                                    <strong class="text-info">Dispositivos</strong><br>
                                    <span class="text-white">${{processData.network.devices}}</span>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <div class="p-2 bg-dark rounded text-center">
                                    <strong class="text-info">Subred</strong><br>
                                    <span class="text-white">${{processData.network.subnet}}</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="p-2 bg-dark rounded text-center">
                                    <strong class="text-info">Uso BW</strong><br>
                                    <span class="text-white">${{processData.network.bandwidth_usage.toFixed(1)}}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('technicalDetails').innerHTML = sensorsHtml + networkHtml;
        }}

        // Crear gráfico de rendimiento
        function createPerformanceChart(processData) {{
            if (performanceChart) {{
                performanceChart.destroy();
            }}

            const ctx = document.getElementById('performanceChart').getContext('2d');
            const hours = Array.from({{length: 24}}, (_, i) => `${{i}}:00`);

            let data1, data2, data3;
            if (processData.metrics_data) {{
                const metrics = Object.values(processData.metrics_data);
                data1 = metrics[0] || Array.from({{length: 24}}, () => Math.random() * 20 + 80);
                data2 = metrics[1] || Array.from({{length: 24}}, () => Math.random() * 20 + 80);
                data3 = metrics[2] || Array.from({{length: 24}}, () => Math.random() * 20 + 80);
            }} else {{
                data1 = Array.from({{length: 24}}, () => Math.random() * 20 + 80);
                data2 = Array.from({{length: 24}}, () => Math.random() * 20 + 80);
                data3 = Array.from({{length: 24}}, () => Math.random() * 20 + 80);
            }}

            performanceChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: hours,
                    datasets: [{{
                        label: 'Métrica 1',
                        data: data1,
                        borderColor: '#4ECDC4',
                        backgroundColor: 'rgba(78, 205, 196, 0.2)',
                        fill: true,
                        tension: 0.4
                    }}, {{
                        label: 'Métrica 2',
                        data: data2,
                        borderColor: '#FF6B6B',
                        backgroundColor: 'rgba(255, 107, 107, 0.2)',
                        fill: true,
                        tension: 0.4
                    }}, {{
                        label: 'Métrica 3',
                        data: data3,
                        borderColor: '#FFA726',
                        backgroundColor: 'rgba(255, 167, 38, 0.2)',
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#ffffff'
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#ffffff'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            ticks: {{
                                color: '#ffffff'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Crear gráfico en tiempo real
        function createRealtimeChart(processData) {{
            if (realtimeChart) {{
                realtimeChart.destroy();
            }}

            const ctx = document.getElementById('realtimeChart').getContext('2d');

            realtimeChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Rendimiento', 'Disponible'],
                    datasets: [{{
                        data: [processData.throughput, 100 - processData.throughput],
                        backgroundColor: [
                            '#4ECDC4',
                            'rgba(255, 255, 255, 0.1)'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                color: '#ffffff'
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Mostrar sección MLE
        function showMLESection(processData) {{
            document.getElementById('mleSection').style.display = 'block';

            // Placeholder para recomendaciones
            document.getElementById('mleRecommendations').innerHTML = `
                <div class="text-center text-light p-4">
                    <i class="fas fa-robot fa-3x mb-3 text-info"></i>
                    <h6>MLE Star listo para analizar: ${{processData.name}}</h6>
                    <p>Haga click en "Ejecutar Análisis" para obtener recomendaciones específicas</p>
                </div>
            `;
        }}

        // Ejecutar análisis MLE
        function runMLEAnalysis() {{
            if (!selectedProcess) return;

            const processData = systemData.process_flow[selectedProcess];

            // Simular análisis (en producción vendría del backend)
            const recommendations = generateMLERecommendations(processData);

            let html = '';
            recommendations.forEach((rec, index) => {{
                html += `
                    <div class="mle-recommendation severity-${{rec.severity.toLowerCase()}}">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="text-white">${{rec.title}}</h6>
                            <span class="badge bg-${{rec.severity.toLowerCase()}}">${{rec.severity}}</span>
                        </div>
                        <p class="text-light mb-3">${{rec.description}}</p>

                        <h6 class="text-warning mb-2">Acciones Recomendadas:</h6>
                        <ul class="text-light">`;

                rec.actions.forEach(action => {{
                    html += `<li>${{action}}</li>`;
                }});

                html += `</ul>

                        <div class="row mt-3">
                            <div class="col-md-6">
                                <h6 class="text-info mb-2">Detalles Técnicos:</h6>`;

                Object.keys(rec.technical_details).forEach(key => {{
                    html += `<small class="text-light d-block">${{key.replace('_', ' ')}}: <strong>${{rec.technical_details[key]}}</strong></small>`;
                }});

                html += `
                            </div>
                            <div class="col-md-6 text-end">
                                <button class="btn btn-success btn-sm me-2" onclick="implementRecommendation(${{index}})">
                                    <i class="fas fa-play me-1"></i>Implementar
                                </button>
                                <button class="btn btn-info btn-sm" onclick="scheduleRecommendation(${{index}})">
                                    <i class="fas fa-calendar me-1"></i>Programar
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }});

            document.getElementById('mleRecommendations').innerHTML = html;
        }}

        // Generar recomendaciones MLE (simplificado)
        function generateMLERecommendations(processData) {{
            const recommendations = [];

            if (processData.throughput < 90) {{
                recommendations.push({{
                    title: 'Optimización de Rendimiento',
                    description: `Rendimiento actual de ${{processData.throughput.toFixed(1)}}% está por debajo del objetivo`,
                    severity: processData.throughput < 80 ? 'HIGH' : 'MEDIUM',
                    actions: [
                        'Analizar cuellos de botella en el proceso',
                        'Implementar control predictivo avanzado',
                        'Optimizar parámetros de operación'
                    ],
                    technical_details: {{
                        'rendimiento_actual': processData.throughput.toFixed(1) + '%',
                        'objetivo': '95%+',
                        'mejora_potencial': (95 - processData.throughput).toFixed(1) + '%'
                    }}
                }});
            }}

            if (processData.alerts > 2) {{
                recommendations.push({{
                    title: 'Reducción de Alertas',
                    description: `${{processData.alerts}} alertas activas requieren atención`,
                    severity: 'HIGH',
                    actions: [
                        'Investigar causas raíz de alertas recurrentes',
                        'Ajustar umbrales de alarma',
                        'Implementar mantenimiento preventivo'
                    ],
                    technical_details: {{
                        'alertas_actuales': processData.alerts,
                        'objetivo': '< 2',
                        'reduccion_requerida': Math.max(0, processData.alerts - 2)
                    }}
                }});
            }}

            if (processData.network.bandwidth_usage > 70) {{
                recommendations.push({{
                    title: 'Optimización de Red',
                    description: `Uso de ancho de banda del ${{processData.network.bandwidth_usage.toFixed(1)}}% es elevado`,
                    severity: 'MEDIUM',
                    actions: [
                        'Implementar Quality of Service (QoS)',
                        'Optimizar protocolos de comunicación',
                        'Revisar tráfico no esencial'
                    ],
                    technical_details: {{
                        'uso_actual': processData.network.bandwidth_usage.toFixed(1) + '%',
                        'objetivo': '< 70%',
                        'dispositivos': processData.network.devices
                    }}
                }});
            }}

            return recommendations;
        }}

        // Funciones de acción
        function implementRecommendation(index) {{
            alert(`✅ Implementando recomendación #${{index + 1}}\\n\\nSe creará ticket de trabajo automáticamente.`);
        }}

        function scheduleRecommendation(index) {{
            const date = prompt('Ingrese fecha para programar (YYYY-MM-DD):');
            if (date) {{
                alert(`📅 Recomendación #${{index + 1}} programada para ${{date}}`);
            }}
        }}

        console.log('🚀 SmartCompute Dashboard Híbrido iniciado');
        console.log('📊 Procesos disponibles:', Object.keys(systemData.process_flow).length);
    </script>
</body>
</html>"""

    return html_content

def main():
    """Función principal"""
    try:
        print("=== SmartCompute Industrial - Dashboard Híbrido Avanzado ===")
        print("Desarrollado por: ggwre04p0@mozmail.com")
        print("LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
        print()

        # Crear directorio de reportes si no existe
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Generar dashboard híbrido
        html_content = generate_hybrid_dashboard()

        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/smartcompute_hybrid_flow_analytics_{timestamp}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Dashboard híbrido generado exitosamente:")
        print(f"📄 Archivo: {Path.cwd()}/{filename}")
        print(f"🌐 Para visualizar: file://{Path.cwd()}/{filename}")
        print()
        print("🎯 Características del Dashboard Híbrido:")
        print("  ✅ Diagrama de flujo interactivo (reacción automática al click)")
        print("  ✅ Gráficos detallados estilo dashboard empresarial")
        print("  ✅ KPIs específicos por proceso seleccionado")
        print("  ✅ Análisis MLE Star contextual por área")
        print("  ✅ Recomendaciones técnicas específicas")
        print("  ✅ Detalles de sensores y red por proceso")
        print("  ✅ Acciones de implementación directas")
        print()
        print("🎮 Instrucciones:")
        print("  1. Haga click en cualquier proceso del diagrama")
        print("  2. Se mostrará automáticamente el análisis detallado")
        print("  3. Use 'Ejecutar Análisis' para obtener recomendaciones MLE Star")
        print("  4. Implemente o programe las mejoras sugeridas")

    except Exception as e:
        print(f"❌ Error generando dashboard híbrido: {e}")
        return False

    return True

if __name__ == "__main__":
    main()