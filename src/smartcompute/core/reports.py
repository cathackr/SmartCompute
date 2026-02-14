#!/usr/bin/env python3
"""
SmartCompute Enterprise - HTML Report Generator
===============================================

Genera reportes HTML gráficos e interactivos además de los reportes .md
para análisis de SmartCompute Enterprise en tiempo real.
"""

import json
import os
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import base64


class SmartComputeHTMLReportGenerator:
    """Generador de reportes HTML para SmartCompute Enterprise"""

    def __init__(self):
        self.output_dir = Path.home() / "smartcompute" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_enterprise_analysis_html(self, json_report_path: str, auto_open: bool = True) -> str:
        """Genera reporte HTML del análisis enterprise"""

        with open(json_report_path, 'r') as f:
            data = json.load(f)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_path = self.output_dir / f"smartcompute_enterprise_analysis_{timestamp}.html"

        html_content = self._create_enterprise_analysis_html(data)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Abrir automáticamente en el navegador
        if auto_open:
            self._open_in_browser(str(html_path))

        return str(html_path)

    def _create_enterprise_analysis_html(self, data: Dict[str, Any]) -> str:
        """Crea contenido HTML del análisis enterprise"""

        summary = data.get('summary', {})
        metrics = data.get('metrics', {})
        system_metrics = metrics.get('system', {})
        security_metrics = metrics.get('security', {})
        enterprise_modules = metrics.get('enterprise_modules', {})

        # Calcular colores basados en scores
        def get_status_color(score):
            if score >= 80: return '#28a745'  # Verde
            elif score >= 60: return '#ffc107'  # Amarillo
            else: return '#dc3545'  # Rojo

        def get_status_badge(score):
            if score >= 80: return 'success'
            elif score >= 60: return 'warning'
            else: return 'danger'

        # Obtener recomendaciones de seguridad
        security_recommendations = metrics.get('security_recommendations', {})
        recommendations_list = security_recommendations.get('recommendations', [])
        security_summary = security_recommendations.get('summary', {})

        # Generar gráficos de datos
        system_chart_data = [
            system_metrics.get('cpu_percent', 0),
            system_metrics.get('memory_percent', 0),
            system_metrics.get('disk_percent', 0)
        ]

        security_modules_data = []
        security_labels = []
        for module, status in security_metrics.items():
            security_labels.append(module.replace('_', ' ').title())
            if isinstance(status, dict) and not status.get('error'):
                security_modules_data.append(100)
            else:
                security_modules_data.append(0)

        html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Enterprise - Análisis en Tiempo Real</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        .metric-card {{
            transition: transform 0.3s ease;
            cursor: pointer;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        .status-excellent {{ color: #28a745; }}
        .status-good {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .header-title {{
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
        }}
        .pulse {{
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        .real-time-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #28a745;
            border-radius: 50%;
            animation: blink 1s infinite;
            margin-right: 8px;
        }}
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0.3; }}
        }}
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4 text-center">
                    <h1 class="header-title display-4 mb-3">
                        <i class="fas fa-shield-alt me-3"></i>
                        SmartCompute Enterprise
                    </h1>
                    <h2 class="text-white mb-3">
                        <span class="real-time-indicator"></span>
                        Análisis en Tiempo Real
                    </h2>
                    <div class="row text-white">
                        <div class="col-md-4">
                            <i class="fas fa-clock me-2"></i>
                            <strong>Ejecutado:</strong> {data.get('timestamp', 'N/A')}
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-stopwatch me-2"></i>
                            <strong>Duración:</strong> {data.get('analysis_duration_seconds', 0):.1f}s
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-chart-line me-2"></i>
                            <strong>Tests:</strong> {summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- KPIs Row -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-heartbeat status-{get_status_badge(100 - system_metrics.get('cpu_percent', 0))}"></i>
                    </div>
                    <h5 class="text-white">Salud del Sistema</h5>
                    <h3 class="text-white">{summary.get('system_health', 'N/A')}</h3>
                    <small class="text-light">CPU: {system_metrics.get('cpu_percent', 0)}%</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-shield-alt" style="color: {get_status_color(summary.get('security_score', 0))}"></i>
                    </div>
                    <h5 class="text-white">Score de Seguridad</h5>
                    <h3 class="text-white">{summary.get('security_score', 0):.1f}%</h3>
                    <small class="text-light">{summary.get('security_status', 'N/A')}</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-building" style="color: {get_status_color(summary.get('enterprise_score', 0))}"></i>
                    </div>
                    <h5 class="text-white">Módulos Enterprise</h5>
                    <h3 class="text-white">{summary.get('enterprise_score', 0):.1f}%</h3>
                    <small class="text-light">{len(enterprise_modules)} módulos</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-check-circle" style="color: {get_status_color(summary.get('success_rate', 0))}"></i>
                    </div>
                    <h5 class="text-white">Tasa de Éxito</h5>
                    <h3 class="text-white">{summary.get('success_rate', 0):.1f}%</h3>
                    <small class="text-light">Tests ejecutados</small>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-server me-2"></i>
                        Métricas del Sistema
                    </h5>
                    <div class="chart-container">
                        <canvas id="systemChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-cogs me-2"></i>
                        Módulos de Seguridad
                    </h5>
                    <div class="chart-container">
                        <canvas id="securityChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Process Monitoring Row -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-microchip me-2"></i>
                        Monitor de Procesos Detallado
                        <span class="badge bg-success ms-2">
                            {system_metrics.get('monitored_processes', 0)} procesos
                        </span>
                    </h5>

                    <!-- Process Summary Cards -->
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <div class="card bg-dark border-light">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-warning">
                                        <i class="fas fa-list me-1"></i>
                                        Procesos
                                    </h6>
                                    <h4 class="text-white">{system_metrics.get('monitored_processes', 0)}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-light">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-info">
                                        <i class="fas fa-network-wired me-1"></i>
                                        Red L3/L4
                                    </h6>
                                    <h4 class="text-white">{system_metrics.get('network_connections', 0)}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-light">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-primary">
                                        <i class="fas fa-ethernet me-1"></i>
                                        Capa L1/L2
                                    </h6>
                                    <h4 class="text-white">{system_metrics.get('layer12_connections', 0)}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-light">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-success">
                                        <i class="fas fa-plug me-1"></i>
                                        Puertos
                                    </h6>
                                    <h4 class="text-white">{system_metrics.get('listening_ports', 0)}</h4>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Process Details Table -->
                    <div class="table-responsive">
                        <table class="table table-dark table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>PID</th>
                                    <th>Proceso</th>
                                    <th>CPU %</th>
                                    <th>Memoria MB</th>
                                    <th>Directorio</th>
                                    <th>Conexiones</th>
                                    <th>Archivos</th>
                                </tr>
                            </thead>
                            <tbody id="processTable">
                            </tbody>
                        </table>
                    </div>

                    <!-- Network Connections Table -->
                    <h6 class="text-white mt-4 mb-3">
                        <i class="fas fa-globe me-2"></i>
                        Conexiones de Red Avanzadas
                    </h6>
                    <div class="table-responsive">
                        <table class="table table-dark table-striped table-hover table-sm">
                            <thead>
                                <tr>
                                    <th>PID</th>
                                    <th>Proceso</th>
                                    <th>Adaptador</th>
                                    <th>Puerto Físico</th>
                                    <th>Protocolo</th>
                                    <th>Local:Puerto</th>
                                    <th>Remoto:Puerto</th>
                                    <th>Canal</th>
                                    <th>Frecuencia</th>
                                    <th>Cifrado</th>
                                    <th>Velocidad</th>
                                    <th>Tiempo</th>
                                    <th>TX/RX</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody id="networkTable">
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Layer 1/2 Direct Connections Row -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-sitemap me-2"></i>
                        Conexiones Directas Capa 1/2 (Físicas)
                        <span class="badge bg-primary ms-2">
                            {system_metrics.get('layer12_connections', 0)} interfaces
                        </span>
                    </h5>

                    <!-- Layer 1/2 Summary Cards -->
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <div class="card bg-dark border-primary">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-primary">
                                        <i class="fas fa-microchip me-1"></i>
                                        MACs Detectadas
                                    </h6>
                                    <h4 class="text-white" id="macCount">0</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-success">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-success">
                                        <i class="fas fa-wifi me-1"></i>
                                        DHCP Activo
                                    </h6>
                                    <h4 class="text-white" id="dhcpCount">0</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-warning">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-warning">
                                        <i class="fas fa-tags me-1"></i>
                                        VLANs
                                    </h6>
                                    <h4 class="text-white" id="vlanCount">0</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-info">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-info">
                                        <i class="fas fa-link me-1"></i>
                                        Trunk Links
                                    </h6>
                                    <h4 class="text-white" id="trunkCount">0</h4>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Layer 1/2 Details Table -->
                    <div class="table-responsive">
                        <table class="table table-dark table-striped table-hover table-sm">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>MAC Address</th>
                                    <th>Fabricante</th>
                                    <th>Firmware</th>
                                    <th>IP Solicitada</th>
                                    <th>DHCP</th>
                                    <th>VLAN</th>
                                    <th>VXLAN</th>
                                    <th>Tipo Enlace</th>
                                    <th>Cat. Cable</th>
                                    <th>Velocidad</th>
                                    <th>Duplex</th>
                                    <th>MTU</th>
                                    <th>Estado</th>
                                    <th>Interfaz</th>
                                </tr>
                            </thead>
                            <tbody id="layer12Table">
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Security Recommendations Panel -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-shield-alt me-2"></i>
                        Recomendaciones de Seguridad (OWASP, NIST, ISO 27001)
                        <span class="badge {security_summary.get('security_color', 'secondary')} ms-2">
                            {len(recommendations_list)} recomendaciones
                        </span>
                    </h5>

                    <!-- Security Summary Cards -->
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <div class="card bg-dark border-danger">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-danger">
                                        <i class="fas fa-exclamation-triangle me-1"></i>
                                        Nivel de Riesgo
                                    </h6>
                                    <h5 class="text-white">{security_summary.get('security_level', 'N/A').split(' - ')[0]}</h5>
                                    <small class="text-muted">{security_summary.get('average_priority', 0):.1f}/100</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-info">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-info">
                                        <i class="fas fa-book me-1"></i>
                                        OWASP
                                    </h6>
                                    <h4 class="text-white" id="owaspCount">0</h4>
                                    <small class="text-muted">recomendaciones</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-warning">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-warning">
                                        <i class="fas fa-cog me-1"></i>
                                        NIST
                                    </h6>
                                    <h4 class="text-white" id="nistCount">0</h4>
                                    <small class="text-muted">recomendaciones</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-dark border-success">
                                <div class="card-body text-center">
                                    <h6 class="card-title text-success">
                                        <i class="fas fa-certificate me-1"></i>
                                        ISO 27001
                                    </h6>
                                    <h4 class="text-white" id="isoCount">0</h4>
                                    <small class="text-muted">recomendaciones</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Security Recommendations Table -->
                    <div class="table-responsive">
                        <table class="table table-dark table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>Prioridad</th>
                                    <th>Framework</th>
                                    <th>Recomendación</th>
                                    <th>Categoría</th>
                                    <th>Riesgo</th>
                                    <th>Esfuerzo</th>
                                    <th>Impacto</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody id="recommendationsTable">
                            </tbody>
                        </table>
                    </div>

                    <!-- Expandable Details -->
                    <div class="accordion mt-3" id="recommendationsAccordion">
                    </div>
                </div>
            </div>
        </div>

        <!-- Detailed Results -->
        <div class="row">
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-list-check me-2"></i>
                        Estado de Módulos Enterprise
                    </h5>
                    <div class="table-responsive">
                        <table class="table table-dark table-striped">
                            <thead>
                                <tr>
                                    <th>Módulo</th>
                                    <th>Estado</th>
                                    <th>Tamaño</th>
                                </tr>
                            </thead>
                            <tbody>"""

        # Agregar filas de módulos enterprise
        for module, info in enterprise_modules.items():
            status_icon = "✅" if "✅" in str(info.get('status', '')) else "❌"
            size_kb = info.get('size_kb', 0) if isinstance(info, dict) else 0

            html_template += f"""
                                <tr>
                                    <td>{module.replace('smartcompute_', '').replace('.py', '').replace('_', ' ').title()}</td>
                                    <td>{status_icon} {info.get('status', 'Unknown') if isinstance(info, dict) else 'Error'}</td>
                                    <td>{size_kb} KB</td>
                                </tr>"""

        html_template += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-bug me-2"></i>
                        Estado de Tests de Seguridad
                    </h5>
                    <div class="list-group list-group-flush">"""

        # Agregar estado de tests de seguridad
        for module, status in security_metrics.items():
            if isinstance(status, dict):
                icon = "fas fa-check-circle text-success" if not status.get('error') else "fas fa-times-circle text-danger"
                status_text = "Exitoso" if not status.get('error') else f"Error: {status.get('error', 'Unknown')}"

                html_template += f"""
                        <div class="list-group-item bg-transparent border-secondary text-white">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">
                                    <i class="{icon} me-2"></i>
                                    {module.replace('_', ' ').title()}
                                </h6>
                            </div>
                            <p class="mb-1">{status_text}</p>
                        </div>"""

        html_template += f"""
                    </div>
                </div>
            </div>
        </div>

        <!-- Real-time Updates -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-chart-area me-2"></i>
                        Métricas en Tiempo Real
                    </h5>
                    <div class="row">
                        <div class="col-md-3 text-center">
                            <div class="pulse">
                                <div class="display-6 text-info">
                                    <i class="fas fa-microchip"></i>
                                </div>
                                <h6 class="text-white">CPU</h6>
                                <h4 class="text-info">{system_metrics.get('cpu_percent', 0)}%</h4>
                            </div>
                        </div>
                        <div class="col-md-3 text-center">
                            <div class="pulse">
                                <div class="display-6 text-warning">
                                    <i class="fas fa-memory"></i>
                                </div>
                                <h6 class="text-white">Memoria</h6>
                                <h4 class="text-warning">{system_metrics.get('memory_percent', 0)}%</h4>
                            </div>
                        </div>
                        <div class="col-md-3 text-center">
                            <div class="pulse">
                                <div class="display-6 text-success">
                                    <i class="fas fa-hdd"></i>
                                </div>
                                <h6 class="text-white">Disco</h6>
                                <h4 class="text-success">{system_metrics.get('disk_percent', 0)}%</h4>
                            </div>
                        </div>
                        <div class="col-md-3 text-center">
                            <div class="pulse">
                                <div class="display-6 text-primary">
                                    <i class="fas fa-cogs"></i>
                                </div>
                                <h6 class="text-white">Procesos SC</h6>
                                <h4 class="text-primary">{system_metrics.get('smartcompute_processes', 0)}</h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="glass-card p-3 text-center">
                    <p class="text-white mb-0">
                        <i class="fas fa-robot me-2"></i>
                        Generado por SmartCompute Enterprise Analysis Engine
                        <span class="ms-3">
                            <i class="fas fa-clock me-1"></i>
                            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // System Chart
        const systemCtx = document.getElementById('systemChart').getContext('2d');
        new Chart(systemCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['CPU', 'Memoria', 'Disco'],
                datasets: [{{
                    data: {system_chart_data},
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: 'white'
                        }}
                    }}
                }}
            }}
        }});

        // Populate Process Details Table
        const processData = {json.dumps(system_metrics.get('process_details', []))};
        const processTableBody = document.getElementById('processTable');

        processData.slice(0, 15).forEach(process => {{
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-info">${{process.pid}}</span></td>
                <td><strong>${{process.name}}</strong></td>
                <td><span class="badge bg-warning">${{process.cpu_percent.toFixed(1)}}%</span></td>
                <td><span class="badge bg-primary">${{process.memory_mb.toFixed(1)}} MB</span></td>
                <td><small class="text-muted">${{process.cwd.length > 30 ? process.cwd.substring(0, 30) + '...' : process.cwd}}</small></td>
                <td><span class="badge bg-success">${{process.connections}}</span></td>
                <td><span class="badge bg-secondary">${{process.open_files}}</span></td>
            `;
            processTableBody.appendChild(row);
        }});

        // Populate Network Connections Table
        const networkData = {json.dumps(system_metrics.get('network_details', []))};
        const networkTableBody = document.getElementById('networkTable');

        networkData.slice(0, 15).forEach(conn => {{
            const row = document.createElement('tr');
            const statusBadge = conn.status === 'LISTEN' ? 'bg-success' : 'bg-secondary';

            // Formatear tiempo de conexión
            let connectionTimeStr = 'N/A';
            if (conn.connection_time) {{
                const hours = Math.floor(conn.connection_time / 3600);
                const minutes = Math.floor((conn.connection_time % 3600) / 60);
                const seconds = Math.floor(conn.connection_time % 60);
                connectionTimeStr = hours > 0 ? `${{hours}}h ${{minutes}}m` :
                                  minutes > 0 ? `${{minutes}}m ${{seconds}}s` : `${{seconds}}s`;
            }}

            // Formatear datos TX/RX
            const txRxStr = `↑${{(conn.bytes_sent/1024).toFixed(1)}}MB / ↓${{(conn.bytes_received/1024).toFixed(1)}}MB`;

            // Determinar badge del adaptador
            let adapterBadge = 'bg-secondary';
            if (conn.network_adapter.includes('Ethernet')) adapterBadge = 'bg-success';
            else if (conn.network_adapter.includes('WiFi')) adapterBadge = 'bg-info';
            else if (conn.network_adapter.includes('Loopback')) adapterBadge = 'bg-warning';

            // Determinar badge de cifrado
            let encryptionBadge = 'bg-secondary';
            if (conn.encryption_type.includes('WPA')) encryptionBadge = 'bg-success';
            else if (conn.encryption_type.includes('WEP')) encryptionBadge = 'bg-warning';
            else if (conn.encryption_type === 'Open') encryptionBadge = 'bg-danger';

            row.innerHTML = `
                <td><span class="badge bg-info">${{conn.pid || '0'}}</span></td>
                <td><strong>${{conn.process_name}}</strong></td>
                <td><span class="badge ${{adapterBadge}}">${{conn.network_adapter}}</span></td>
                <td><small class="text-muted">${{conn.physical_port}}</small></td>
                <td><span class="badge bg-primary">${{conn.protocol}}</span></td>
                <td>${{conn.local_address}}:${{conn.local_port}}</td>
                <td>${{conn.remote_address}}:${{conn.remote_port}}</td>
                <td><span class="badge bg-info">${{conn.channel || 'N/A'}}</span></td>
                <td><small class="text-info">${{conn.frequency || 'N/A'}}</small></td>
                <td><span class="badge ${{encryptionBadge}}">${{conn.encryption_type}}</span></td>
                <td><span class="badge bg-warning">${{conn.transmission_speed}}</span></td>
                <td><small class="text-muted">${{connectionTimeStr}}</small></td>
                <td><small class="text-success">${{txRxStr}}</small></td>
                <td><span class="badge ${{statusBadge}}">${{conn.status}}</span></td>
            `;
            networkTableBody.appendChild(row);
        }});

        // Populate Layer 1/2 Connections Table
        const layer12Data = {json.dumps(system_metrics.get('layer12_details', []))};
        const layer12TableBody = document.getElementById('layer12Table');

        let macCount = 0;
        let dhcpCount = 0;
        let vlanCount = 0;
        let trunkCount = 0;

        layer12Data.forEach((conn, index) => {{
            const row = document.createElement('tr');

            // Contar estadísticas
            macCount++;
            if (conn.dhcp_active) dhcpCount++;
            if (conn.vlan_id) vlanCount++;
            if (conn.link_type === 'trunk') trunkCount++;

            // Determinar badges
            const dhcpBadge = conn.dhcp_active ? 'bg-success' : 'bg-secondary';
            const dhcpText = conn.dhcp_active ? 'SÍ' : 'NO';

            const linkTypeBadge = conn.link_type === 'trunk' ? 'bg-warning' :
                                 conn.link_type === 'access' ? 'bg-info' : 'bg-secondary';

            const stateBadge = conn.link_state === 'UP' ? 'bg-success' :
                              conn.link_state === 'DOWN' ? 'bg-danger' : 'bg-info';

            // Determinar badge de categoría de cable
            let cableBadge = 'bg-secondary';
            if (conn.cable_category.includes('Cat 6A') || conn.cable_category.includes('Cat 7')) {{
                cableBadge = 'bg-success';
            }} else if (conn.cable_category.includes('Cat 5e') || conn.cable_category.includes('Cat 6')) {{
                cableBadge = 'bg-info';
            }} else if (conn.cable_category.includes('Cat 5')) {{
                cableBadge = 'bg-warning';
            }} else if (conn.cable_category.includes('Wireless')) {{
                cableBadge = 'bg-primary';
            }}

            row.innerHTML = `
                <td><span class="badge bg-dark">${{index + 1}}</span></td>
                <td><code class="text-info">${{conn.mac_address}}</code></td>
                <td><strong>${{conn.manufacturer}}</strong></td>
                <td><small class="text-muted">${{conn.firmware_version}}</small></td>
                <td><span class="text-warning">${{conn.ip_requested}}</span></td>
                <td><span class="badge ${{dhcpBadge}}">${{dhcpText}}</span></td>
                <td><span class="badge bg-warning">${{conn.vlan_id || 'N/A'}}</span></td>
                <td><span class="badge bg-info">${{conn.vxlan_vni || 'N/A'}}</span></td>
                <td><span class="badge ${{linkTypeBadge}}">${{conn.link_type.toUpperCase()}}</span></td>
                <td><span class="badge ${{cableBadge}}">${{conn.cable_category}}</span></td>
                <td><small class="text-success">${{conn.port_speed}}</small></td>
                <td><span class="badge bg-secondary">${{conn.duplex_mode.toUpperCase()}}</span></td>
                <td><small class="text-muted">${{conn.mtu_size}}</small></td>
                <td><span class="badge ${{stateBadge}}">${{conn.link_state}}</span></td>
                <td><code class="text-primary">${{conn.interface_name}}</code></td>
            `;
            layer12TableBody.appendChild(row);
        }});

        // Update summary counts
        document.getElementById('macCount').textContent = macCount;
        document.getElementById('dhcpCount').textContent = dhcpCount;
        document.getElementById('vlanCount').textContent = vlanCount;
        document.getElementById('trunkCount').textContent = trunkCount;

        // Populate Security Recommendations
        const recommendationsData = {json.dumps(recommendations_list)};
        const recommendationsTableBody = document.getElementById('recommendationsTable');
        const recommendationsAccordion = document.getElementById('recommendationsAccordion');

        let owaspCount = 0;
        let nistCount = 0;
        let isoCount = 0;

        recommendationsData.forEach((rec, index) => {{
            // Count by framework
            if (rec.framework === 'OWASP') owaspCount++;
            else if (rec.framework === 'NIST') nistCount++;
            else if (rec.framework === 'ISO 27001') isoCount++;

            // Determine badges and colors
            const riskBadge = rec.risk_level === 'Critical' ? 'bg-danger' :
                             rec.risk_level === 'High' ? 'bg-warning' :
                             rec.risk_level === 'Medium' ? 'bg-info' : 'bg-success';

            const frameworkBadge = rec.framework === 'OWASP' ? 'bg-info' :
                                  rec.framework === 'NIST' ? 'bg-warning' : 'bg-success';

            const effortBadge = rec.implementation_effort === 'High' ? 'bg-danger' :
                               rec.implementation_effort === 'Medium' ? 'bg-warning' : 'bg-success';

            // Create table row
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-primary">${{rec.priority_score}}</span></td>
                <td><span class="badge ${{frameworkBadge}}">${{rec.framework}}</span></td>
                <td><strong>${{rec.title}}</strong><br>
                    <small class="text-muted">${{rec.description.substring(0, 80)}}...</small></td>
                <td><span class="badge bg-secondary">${{rec.category}}</span></td>
                <td><span class="badge ${{riskBadge}}">${{rec.risk_level}}</span></td>
                <td><span class="badge ${{effortBadge}}">${{rec.implementation_effort}}</span></td>
                <td><small class="text-success">${{rec.impact.substring(0, 50)}}...</small></td>
                <td>
                    <button class="btn btn-sm btn-outline-info" data-bs-toggle="collapse"
                            data-bs-target="#details${{index}}" aria-expanded="false">
                        <i class="fas fa-info-circle"></i> Detalles
                    </button>
                </td>
            `;
            recommendationsTableBody.appendChild(row);

            // Create accordion item for details
            const accordionItem = document.createElement('div');
            accordionItem.className = 'accordion-item bg-dark border-secondary';
            accordionItem.innerHTML = `
                <div class="collapse" id="details${{index}}" data-bs-parent="#recommendationsAccordion">
                    <div class="accordion-body bg-dark text-white">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="text-warning">📋 Detalles Técnicos:</h6>
                                <p class="small">${{rec.technical_details}}</p>

                                <h6 class="text-info">🎯 Activos Afectados:</h6>
                                <ul class="small">
                                    ${{rec.affected_assets.map(asset => `<li>${{asset}}</li>`).join('')}}
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-success">🔧 Pasos de Remediación:</h6>
                                <ol class="small">
                                    ${{rec.remediation_steps.map(step => `<li>${{step}}</li>`).join('')}}
                                </ol>

                                <h6 class="text-primary">📚 Referencias de Cumplimiento:</h6>
                                <ul class="small">
                                    ${{rec.compliance_references.map(ref => `<li><code>${{ref}}</code></li>`).join('')}}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            recommendationsAccordion.appendChild(accordionItem);
        }});

        // Update framework counts
        document.getElementById('owaspCount').textContent = owaspCount;
        document.getElementById('nistCount').textContent = nistCount;
        document.getElementById('isoCount').textContent = isoCount;

        // Security Chart
        const securityCtx = document.getElementById('securityChart').getContext('2d');
        new Chart(securityCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(security_labels)},
                datasets: [{{
                    label: 'Estado (%)',
                    data: {security_modules_data},
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            color: 'white'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            color: 'white',
                            maxRotation: 45
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{
                            color: 'white'
                        }}
                    }}
                }}
            }}
        }});

        // Auto-refresh simulation (en implementación real, conectaría a WebSocket)
        setInterval(() => {{
            // Simular actualización de datos en tiempo real
            const indicators = document.querySelectorAll('.real-time-indicator');
            indicators.forEach(indicator => {{
                indicator.style.backgroundColor = indicator.style.backgroundColor === 'rgb(40, 167, 69)' ? '#ffc107' : '#28a745';
            }});
        }}, 2000);
    </script>
</body>
</html>"""

        return html_template

    def generate_security_report_html(self, security_report_path: str, auto_open: bool = False) -> str:
        """Genera reporte HTML del análisis de seguridad"""

        if not Path(security_report_path).exists():
            return None

        with open(security_report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_path = self.output_dir / f"smartcompute_security_report_{timestamp}.html"

        # Convertir Markdown a HTML con estilos mejorados
        html_content = self._markdown_to_html(content, "Reporte de Seguridad SmartCompute")

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Abrir automáticamente en el navegador si se solicita
        if auto_open:
            self._open_in_browser(str(html_path))

        return str(html_path)

    def _markdown_to_html(self, markdown_content: str, title: str) -> str:
        """Convierte contenido Markdown a HTML con estilos"""

        # Conversión básica de Markdown a HTML
        html_content = markdown_content

        # Headers
        html_content = html_content.replace('# ', '<h1 class="display-4 text-primary mb-4">')
        html_content = html_content.replace('## ', '<h2 class="h3 text-info mb-3 mt-4">')
        html_content = html_content.replace('### ', '<h3 class="h4 text-success mb-2 mt-3">')
        html_content = html_content.replace('\n', '</h1>\n').replace('</h1>\n<h1', '</h1>\n<h1')

        # Listas
        lines = html_content.split('\n')
        in_list = False
        processed_lines = []

        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    processed_lines.append('<ul class="list-group list-group-flush mb-3">')
                    in_list = True
                item_content = line.strip()[2:]
                # Aplicar estilos a diferentes tipos de items
                if '✅' in item_content:
                    processed_lines.append(f'<li class="list-group-item bg-success bg-opacity-10 border-success">{item_content}</li>')
                elif '❌' in item_content:
                    processed_lines.append(f'<li class="list-group-item bg-danger bg-opacity-10 border-danger">{item_content}</li>')
                elif '⚠️' in item_content:
                    processed_lines.append(f'<li class="list-group-item bg-warning bg-opacity-10 border-warning">{item_content}</li>')
                else:
                    processed_lines.append(f'<li class="list-group-item">{item_content}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                processed_lines.append(line)

        if in_list:
            processed_lines.append('</ul>')

        html_content = '\n'.join(processed_lines)

        # Códigos y bloques
        html_content = html_content.replace('```python', '<pre class="bg-dark text-light p-3 rounded"><code class="language-python">')
        html_content = html_content.replace('```bash', '<pre class="bg-dark text-light p-3 rounded"><code class="language-bash">')
        html_content = html_content.replace('```', '</code></pre>')

        # Bold y cursiva
        html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
        html_content = html_content.replace('*', '<em>').replace('*', '</em>')

        # Párrafos
        html_content = html_content.replace('\n\n', '</p>\n<p class="mb-3">')
        html_content = f'<p class="mb-3">{html_content}</p>'

        # Template HTML completo
        full_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-dark.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #2C3E50 0%, #3498DB 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .report-container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin: 20px auto;
            max-width: 1200px;
        }}
        .header-section {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-radius: 15px 15px 0 0;
            padding: 30px;
        }}
        .toc {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 20px 0;
        }}
        .metric-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 2px;
        }}
        .score-excellent {{ background: #d4edda; color: #155724; }}
        .score-good {{ background: #fff3cd; color: #856404; }}
        .score-warning {{ background: #f8d7da; color: #721c24; }}
        pre {{
            font-size: 0.9em;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="report-container">
            <div class="header-section text-center">
                <h1 class="display-4 mb-3">
                    <i class="fas fa-shield-alt me-3"></i>
                    {title}
                </h1>
                <p class="lead">
                    <i class="fas fa-calendar me-2"></i>
                    Generado: {datetime.now().strftime('%d de %B de %Y, %H:%M:%S')}
                </p>
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="metric-badge score-excellent">
                            <i class="fas fa-check-circle me-1"></i> Análisis Completo
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-badge score-good">
                            <i class="fas fa-cogs me-1"></i> Enterprise Ready
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-badge score-excellent">
                            <i class="fas fa-lock me-1"></i> Seguridad Validada
                        </div>
                    </div>
                </div>
            </div>

            <div class="p-4">
                <div class="toc">
                    <h5><i class="fas fa-list me-2"></i>Tabla de Contenidos</h5>
                    <ul class="list-unstyled mb-0">
                        <li><a href="#resumen-ejecutivo" class="text-decoration-none">📊 Resumen Ejecutivo</a></li>
                        <li><a href="#arquitectura" class="text-decoration-none">🏗️ Arquitectura del Sistema</a></li>
                        <li><a href="#analisis-seguridad" class="text-decoration-none">🔍 Análisis de Seguridad</a></li>
                        <li><a href="#vulnerabilidades" class="text-decoration-none">⚠️ Vulnerabilidades y Recomendaciones</a></li>
                        <li><a href="#componentes-industriales" class="text-decoration-none">🏭 Componentes Industriales</a></li>
                        <li><a href="#plan-accion" class="text-decoration-none">🎯 Plan de Acción</a></li>
                    </ul>
                </div>

                <div class="content-section">
                    {html_content}
                </div>
            </div>

            <div class="text-center p-3 bg-light border-top">
                <small class="text-muted">
                    <i class="fas fa-robot me-1"></i>
                    Generado automáticamente por SmartCompute Enterprise Security Analysis Engine
                </small>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
</body>
</html>"""

        return full_html

    def update_analysis_script(self):
        """Actualiza el script de análisis para generar HTML automáticamente"""

        script_path = Path(__file__).parent / "run_enterprise_analysis.py"

        # Agregar función de generación HTML al final del script
        html_generation_code = '''
    # Generar reporte HTML adicional
    try:
        from generate_html_reports import SmartComputeHTMLReportGenerator

        # Buscar el último reporte JSON
        reports_dir = Path.home() / "smartcompute"
        json_reports = list(reports_dir.glob("enterprise_analysis_*.json"))

        if json_reports:
            latest_report = max(json_reports, key=lambda p: p.stat().st_mtime)

            html_generator = SmartComputeHTMLReportGenerator()
            html_path = html_generator.generate_enterprise_analysis_html(str(latest_report))

            print(f"   🌐 Reporte HTML generado: {Path(html_path).name}")

            # Generar HTML del reporte de seguridad si existe
            security_report = Path(__file__).parent / "REPORTE_SEGURIDAD_SMARTCOMPUTE.md"
            if security_report.exists():
                security_html = html_generator.generate_security_report_html(str(security_report))
                if security_html:
                    print(f"   🔒 Reporte seguridad HTML: {Path(security_html).name}")

    except Exception as e:
        print(f"   ⚠️  Error generando HTML: {e}")'''

        return html_generation_code

    def _open_in_browser(self, html_path: str):
        """Abre el reporte HTML en el navegador por defecto"""
        try:
            # Convertir a file:// URL para mejor compatibilidad
            file_url = f"file://{os.path.abspath(html_path)}"

            # Intentar diferentes métodos según el sistema operativo
            try:
                # Método 1: webbrowser (más universal)
                webbrowser.open(file_url)
                print(f"   🌐 Abriendo en navegador: {Path(html_path).name}")
                return True
            except Exception:
                pass

            # Método 2: xdg-open (Linux)
            try:
                subprocess.run(['xdg-open', html_path], check=True, timeout=5,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   🌐 Abriendo con xdg-open: {Path(html_path).name}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass

            # Método 3: gnome-open (GNOME)
            try:
                subprocess.run(['gnome-open', html_path], check=True, timeout=5,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   🌐 Abriendo con gnome-open: {Path(html_path).name}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass

            # Método 4: firefox directo (fallback)
            try:
                subprocess.run(['firefox', html_path], check=True, timeout=5,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   🌐 Abriendo con Firefox: {Path(html_path).name}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass

            # Método 5: chrome/chromium (fallback)
            for browser in ['google-chrome', 'chromium-browser', 'chromium']:
                try:
                    subprocess.run([browser, html_path], check=True, timeout=5,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"   🌐 Abriendo con {browser}: {Path(html_path).name}")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue

            # Si todo falla, mostrar instrucciones manuales
            print(f"   ⚠️  No se pudo abrir automáticamente. Abrir manualmente:")
            print(f"   📁 {html_path}")
            return False

        except Exception as e:
            print(f"   ❌ Error abriendo navegador: {e}")
            print(f"   📁 Abrir manualmente: {html_path}")
            return False

    def open_latest_reports(self):
        """Abre los últimos reportes generados"""
        try:
            # Buscar reportes más recientes
            analysis_reports = list(self.output_dir.glob("smartcompute_enterprise_analysis_*.html"))
            security_reports = list(self.output_dir.glob("smartcompute_security_report_*.html"))

            if analysis_reports:
                latest_analysis = max(analysis_reports, key=lambda p: p.stat().st_mtime)
                self._open_in_browser(str(latest_analysis))

            if security_reports:
                latest_security = max(security_reports, key=lambda p: p.stat().st_mtime)
                print(f"   📋 Reporte de seguridad disponible: {latest_security.name}")
                # No abrir automáticamente el reporte de seguridad para evitar múltiples pestañas

        except Exception as e:
            print(f"   ⚠️  Error abriendo reportes: {e}")


def main():
    """Función principal para probar el generador"""

    print("🌐 SmartCompute HTML Report Generator")
    print("=" * 50)

    generator = SmartComputeHTMLReportGenerator()

    # Buscar último reporte JSON
    reports_dir = Path.home() / "smartcompute"
    json_reports = list(reports_dir.glob("enterprise_analysis_*.json"))

    if json_reports:
        latest_report = max(json_reports, key=lambda p: p.stat().st_mtime)
        print(f"📊 Procesando: {latest_report.name}")

        # Generar HTML del análisis enterprise
        html_path = generator.generate_enterprise_analysis_html(str(latest_report))
        print(f"✅ HTML generado: {html_path}")

        # Generar HTML del reporte de seguridad
        security_report = Path(__file__).parent / "REPORTE_SEGURIDAD_SMARTCOMPUTE.md"
        if security_report.exists():
            security_html = generator.generate_security_report_html(str(security_report))
            if security_html:
                print(f"✅ Seguridad HTML: {security_html}")
    else:
        print("❌ No se encontraron reportes JSON")


if __name__ == "__main__":
    main()