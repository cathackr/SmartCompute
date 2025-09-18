#!/usr/bin/env python3
"""
SmartCompute Industrial - Generador de Reportes HTML
==================================================

Genera reportes HTML detallados para sistemas industriales incluyendo:
- Protocolos industriales detectados
- Estado de PLCs y especificaciones
- Monitoreo de sensores en tiempo real
- Estados de interruptores manuales
- Logs de SCADA
- Recomendaciones ISA/IEC
"""

import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class SmartComputeIndustrialHTMLGenerator:
    """Generador de reportes HTML para SmartCompute Industrial"""

    def __init__(self):
        self.output_dir = Path.home() / "smartcompute" / "industrial_reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_industrial_report(self, json_report_path: str, auto_open: bool = True) -> str:
        """Genera reporte HTML completo del análisis industrial"""

        with open(json_report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_path = self.output_dir / f"smartcompute_industrial_report_{timestamp}.html"

        html_content = self._create_industrial_html(data)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Abrir automáticamente en el navegador
        if auto_open:
            webbrowser.open(f'file://{html_path.absolute()}')

        print(f"📊 Reporte HTML generado: {html_path}")
        return str(html_path)

    def _create_industrial_html(self, data: Dict[str, Any]) -> str:
        """Crear contenido HTML completo del reporte industrial"""

        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Industrial - Reporte de Análisis</title>
    <style>
        {self._get_industrial_css()}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        {self._create_header(data)}
        {self._create_overview_section(data)}
        {self._create_protocols_section(data)}
        {self._create_plcs_section(data)}
        {self._create_sensors_section(data)}
        {self._create_switches_section(data)}
        {self._create_scada_section(data)}
        {self._create_alerts_section(data)}
        {self._create_recommendations_section(data)}
        {self._create_footer()}
    </div>

    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""

        return html

    def _get_industrial_css(self) -> str:
        """CSS específico para reportes industriales"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;
        }

        .header h1 {
            color: #1e3c72;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header .subtitle {
            color: #666;
            font-size: 1.2em;
            margin-bottom: 20px;
        }

        .header .timestamp {
            background: #f8f9fa;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            color: #495057;
            font-weight: 500;
        }

        .section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }

        .section-title {
            font-size: 1.8em;
            color: #1e3c72;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #e9ecef;
            display: flex;
            align-items: center;
        }

        .section-title .icon {
            margin-right: 15px;
            font-size: 1.2em;
        }

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .metric-card h3 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .metric-card p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .protocols-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .protocol-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            position: relative;
        }

        .protocol-card.detected {
            border-color: #28a745;
            background: #d4edda;
        }

        .protocol-card.not-detected {
            border-color: #dc3545;
            background: #f8d7da;
        }

        .protocol-status {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .status-online {
            background: #28a745;
        }

        .status-offline {
            background: #dc3545;
        }

        .plc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }

        .plc-card {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        }

        .plc-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }

        .plc-status {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }

        .plc-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 0.9em;
        }

        .sensors-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }

        .sensor-card {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            position: relative;
        }

        .sensor-card.normal {
            border-left: 4px solid #28a745;
        }

        .sensor-card.warning {
            border-left: 4px solid #ffc107;
        }

        .sensor-card.critical {
            border-left: 4px solid #dc3545;
        }

        .sensor-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }

        .sensor-value.normal {
            color: #28a745;
        }

        .sensor-value.warning {
            color: #ffc107;
        }

        .sensor-value.critical {
            color: #dc3545;
        }

        .switches-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .switch-card {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }

        .switch-card.emergency {
            border-color: #dc3545;
            background: #fff5f5;
        }

        .switch-icon {
            font-size: 3em;
            margin-bottom: 10px;
        }

        .switch-state {
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin: 10px 0;
        }

        .state-on {
            background: #d4edda;
            color: #155724;
        }

        .state-off {
            background: #f8d7da;
            color: #721c24;
        }

        .state-pressed {
            background: #dc3545;
            color: white;
        }

        .scada-messages {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e9ecef;
            border-radius: 8px;
        }

        .message-item {
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
        }

        .message-item:last-child {
            border-bottom: none;
        }

        .message-priority {
            width: 8px;
            height: 40px;
            border-radius: 4px;
            margin-right: 15px;
        }

        .priority-low {
            background: #28a745;
        }

        .priority-medium {
            background: #ffc107;
        }

        .priority-high {
            background: #fd7e14;
        }

        .priority-critical {
            background: #dc3545;
        }

        .alerts-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .alert-item {
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid;
            display: flex;
            align-items: center;
        }

        .alert-item.high {
            background: #fff5f5;
            border-color: #dc3545;
        }

        .alert-item.medium {
            background: #fff8e1;
            border-color: #ffc107;
        }

        .alert-item.low {
            background: #f3f4f6;
            border-color: #6c757d;
        }

        .recommendations-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .recommendation-card {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }

        .recommendation-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .recommendation-content {
            padding: 20px;
            display: none;
        }

        .recommendation-content.active {
            display: block;
        }

        .standard-badge {
            background: #007bff;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }

        .priority-badge {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }

        .priority-critical {
            background: #dc3545;
            color: white;
        }

        .priority-high {
            background: #fd7e14;
            color: white;
        }

        .priority-medium {
            background: #ffc107;
            color: #212529;
        }

        .technical-details {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }

        .recommendation-list {
            list-style: none;
            padding-left: 0;
        }

        .recommendation-list li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }

        .recommendation-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
        }

        .chart-container {
            margin: 20px 0;
            height: 300px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            .overview-grid {
                grid-template-columns: 1fr;
            }

            .protocols-grid,
            .plc-grid,
            .sensors-container {
                grid-template-columns: 1fr;
            }
        }
        """

    def _create_header(self, data: Dict[str, Any]) -> str:
        """Crear header del reporte"""
        timestamp = data.get('timestamp', 'N/A')
        duration = data.get('duration_seconds', 0)

        return f"""
        <div class="header">
            <h1>🏭 SmartCompute Industrial</h1>
            <div class="subtitle">Reporte de Análisis de Sistemas Industriales</div>
            <div class="timestamp">
                📅 Generado: {timestamp} | ⏱️ Duración: {duration}s
            </div>
        </div>
        """

    def _create_overview_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de resumen general"""
        stats = data.get('statistics', {})
        protocols_count = len([p for p in data.get('protocols', {}).values() if p.get('detected', False)])

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">📊</span>
                Resumen General del Sistema
            </h2>
            <div class="overview-grid">
                <div class="metric-card">
                    <h3>{protocols_count}</h3>
                    <p>Protocolos Detectados</p>
                </div>
                <div class="metric-card">
                    <h3>{stats.get('plcs_discovered', 0)}</h3>
                    <p>PLCs Descubiertos</p>
                </div>
                <div class="metric-card">
                    <h3>{stats.get('sensors_active', 0)}</h3>
                    <p>Sensores Activos</p>
                </div>
                <div class="metric-card">
                    <h3>{stats.get('messages_processed', 0)}</h3>
                    <p>Mensajes SCADA</p>
                </div>
                <div class="metric-card">
                    <h3>{stats.get('errors_detected', 0)}</h3>
                    <p>Alertas Generadas</p>
                </div>
            </div>
        </div>
        """

    def _create_protocols_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de protocolos industriales"""
        protocols = data.get('protocols', {})

        protocol_cards = ""
        for proto_id, proto_data in protocols.items():
            detected = proto_data.get('detected', False)
            card_class = "detected" if detected else "not-detected"
            status_class = "status-online" if detected else "status-offline"
            status_text = "Detectado" if detected else "No detectado"
            traffic = proto_data.get('traffic_count', 0)
            last_seen = proto_data.get('last_seen', 'N/A')

            protocol_cards += f"""
            <div class="protocol-card {card_class}">
                <div class="protocol-status {status_class}"></div>
                <h4>{proto_data.get('name', 'Unknown')}</h4>
                <p><strong>Puerto:</strong> {proto_data.get('port', 'N/A')}</p>
                <p><strong>Descripción:</strong> {proto_data.get('description', 'N/A')}</p>
                <p><strong>Estado:</strong> {status_text}</p>
                {f'<p><strong>Tráfico:</strong> {traffic} conexiones</p>' if detected else ''}
                {f'<p><strong>Última detección:</strong> {last_seen}</p>' if detected and last_seen != 'N/A' else ''}
            </div>
            """

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">🔌</span>
                Protocolos Industriales
            </h2>
            <div class="protocols-grid">
                {protocol_cards}
            </div>
        </div>
        """

    def _create_plcs_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de PLCs"""
        plcs = data.get('plcs', [])

        plc_cards = ""
        for plc in plcs:
            status_class = "status-online" if plc.get('status') == 'Online' else "status-offline"

            plc_cards += f"""
            <div class="plc-card">
                <div class="plc-header">
                    <div class="plc-status {status_class}"></div>
                    <h4>{plc.get('manufacturer', 'Unknown')} {plc.get('model', 'Unknown')}</h4>
                </div>
                <div class="plc-info">
                    <div><strong>IP:</strong> {plc.get('ip_address', 'N/A')}</div>
                    <div><strong>MAC:</strong> {plc.get('mac_address', 'N/A')}</div>
                    <div><strong>Protocolo:</strong> {plc.get('protocol', 'N/A')}</div>
                    <div><strong>Firmware:</strong> {plc.get('firmware_version', 'N/A')}</div>
                    <div><strong>Estado:</strong> {plc.get('status', 'Unknown')}</div>
                    <div><strong>Rack/Slot:</strong> {plc.get('rack_slot', 'N/A')}</div>
                    <div><strong>Última comunicación:</strong> {plc.get('last_communication', 'N/A')}</div>
                    <div><strong>Errores:</strong> {plc.get('error_count', 0)}</div>
                </div>
            </div>
            """

        if not plc_cards:
            plc_cards = "<p>No se detectaron PLCs en la red.</p>"

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">🤖</span>
                Controladores PLC
            </h2>
            <div class="plc-grid">
                {plc_cards}
            </div>
        </div>
        """

    def _create_sensors_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de sensores"""
        sensors = data.get('sensors', [])

        sensor_cards = ""
        sensor_types = {}

        for sensor in sensors:
            status = sensor.get('status', 'unknown')
            value = sensor.get('value', 0)
            unit = sensor.get('unit', '')

            # Agrupar por tipo para gráficos
            sensor_type = sensor.get('type', 'unknown')
            if sensor_type not in sensor_types:
                sensor_types[sensor_type] = []
            sensor_types[sensor_type].append(sensor)

            sensor_cards += f"""
            <div class="sensor-card {status}">
                <h4>{sensor.get('name', 'Unknown Sensor')}</h4>
                <div class="sensor-value {status}">{value} {unit}</div>
                <p><strong>Tipo:</strong> {sensor_type.title()}</p>
                <p><strong>Ubicación:</strong> {sensor.get('location', 'N/A')}</p>
                <p><strong>Estado:</strong> {status.title()}</p>
                <p><strong>Umbrales:</strong> {sensor.get('min_threshold', 0)} - {sensor.get('max_threshold', 100)} {unit}</p>
                <p><strong>Actualizado:</strong> {sensor.get('timestamp', 'N/A')}</p>
            </div>
            """

        # Crear gráfico de sensores por tipo
        chart_data = self._generate_sensors_chart_data(sensor_types)

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">📡</span>
                Sensores en Tiempo Real
            </h2>
            <div class="chart-container">
                <canvas id="sensorsChart"></canvas>
            </div>
            <div class="sensors-container">
                {sensor_cards}
            </div>
        </div>

        <script>
            // Datos para gráfico de sensores
            const sensorsData = {chart_data};
            {self._get_sensors_chart_script()}
        </script>
        """

    def _create_switches_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de interruptores manuales"""
        switches = data.get('switches', [])

        switch_cards = ""
        for switch in switches:
            switch_type = switch.get('type', 'unknown')
            state = switch.get('state', 'unknown')

            # Definir clase CSS basada en el tipo
            card_class = "emergency" if switch_type == "emergency_stop" else ""

            # Definir icono basado en el tipo
            icons = {
                'emergency_stop': '🚨',
                'selector': '🔄',
                'pushbutton': '🔘',
                'main_switch': '⚡'
            }
            icon = icons.get(switch_type, '🔲')

            # Definir clase de estado
            state_class = ""
            if state in ['on', 'released', 'auto']:
                state_class = "state-on"
            elif state in ['off', 'manual']:
                state_class = "state-off"
            elif state == 'pressed':
                state_class = "state-pressed"

            maintenance_indicator = "⚠️ Mantenimiento requerido" if switch.get('maintenance_due', False) else ""

            switch_cards += f"""
            <div class="switch-card {card_class}">
                <div class="switch-icon">{icon}</div>
                <h4>{switch.get('name', 'Unknown Switch')}</h4>
                <div class="switch-state {state_class}">{state.title()}</div>
                <p><strong>Tipo:</strong> {switch_type.replace('_', ' ').title()}</p>
                <p><strong>Ubicación:</strong> {switch.get('location', 'N/A')}</p>
                <p><strong>Último cambio:</strong> {switch.get('last_changed', 'N/A')}</p>
                {f'<p style="color: #dc3545;"><strong>{maintenance_indicator}</strong></p>' if maintenance_indicator else ''}
            </div>
            """

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">🎛️</span>
                Interruptores Manuales
            </h2>
            <div class="switches-grid">
                {switch_cards}
            </div>
        </div>
        """

    def _create_scada_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de mensajes SCADA"""
        messages = data.get('scada_messages', [])

        message_items = ""
        for message in messages:
            priority = message.get('priority', 'low')
            acknowledged = message.get('acknowledged', False)
            ack_status = "✅" if acknowledged else "⏳"

            message_items += f"""
            <div class="message-item">
                <div class="message-priority priority-{priority}"></div>
                <div style="flex-grow: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <strong>{message.get('source', 'Unknown')} → {message.get('destination', 'Unknown')}</strong>
                        <span>{ack_status}</span>
                    </div>
                    <div><strong>Tipo:</strong> {message.get('message_type', 'Unknown').title()}</div>
                    <div><strong>Contenido:</strong> {message.get('content', 'N/A')}</div>
                    <div><strong>Prioridad:</strong> {priority.title()}</div>
                    <div style="color: #6c757d; font-size: 0.9em;">{message.get('timestamp', 'N/A')}</div>
                </div>
            </div>
            """

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">💬</span>
                Mensajes SCADA ({len(messages)})
            </h2>
            <div class="scada-messages">
                {message_items}
            </div>
        </div>
        """

    def _create_alerts_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de alertas"""
        alerts = data.get('alerts', [])

        alert_items = ""
        for alert in alerts:
            severity = alert.get('severity', 'low')

            alert_items += f"""
            <div class="alert-item {severity}">
                <div style="flex-grow: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <strong>{alert.get('type', 'Unknown').replace('_', ' ').title()}</strong>
                        <span class="priority-badge priority-{severity}">{severity.title()}</span>
                    </div>
                    <div style="margin-bottom: 10px;">{alert.get('message', 'N/A')}</div>
                    <div style="font-size: 0.9em; color: #6c757d;">
                        <strong>Fuente:</strong> {alert.get('source', 'N/A')} |
                        <strong>Timestamp:</strong> {alert.get('timestamp', 'N/A')}
                    </div>
                </div>
            </div>
            """

        if not alert_items:
            alert_items = "<p>No hay alertas activas en el sistema.</p>"

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">🚨</span>
                Alertas del Sistema ({len(alerts)})
            </h2>
            <div class="alerts-container">
                {alert_items}
            </div>
        </div>
        """

    def _create_recommendations_section(self, data: Dict[str, Any]) -> str:
        """Crear sección de recomendaciones ISA/IEC"""
        recommendations = data.get('recommendations', [])

        recommendation_cards = ""
        for i, rec in enumerate(recommendations):
            standard = rec.get('standard', 'Unknown')
            title = rec.get('title', 'Unknown')
            priority = rec.get('priority', 'medium')
            description = rec.get('description', 'N/A')
            technical_details = rec.get('technical_details', [])
            rec_list = rec.get('recommendations', [])
            applicable_to = rec.get('applicable_to', [])

            tech_details_html = ""
            if technical_details:
                tech_details_html = "<div class='technical-details'><h5>Detalles Técnicos:</h5><ul>"
                for detail in technical_details:
                    tech_details_html += f"<li>{detail}</li>"
                tech_details_html += "</ul></div>"

            rec_list_html = ""
            if rec_list:
                rec_list_html = "<h5>Recomendaciones:</h5><ul class='recommendation-list'>"
                for recommendation in rec_list:
                    rec_list_html += f"<li>{recommendation}</li>"
                rec_list_html += "</ul>"

            applicable_html = ""
            if applicable_to:
                applicable_html = f"<p><strong>Aplicable a:</strong> {', '.join(applicable_to)}</p>"

            recommendation_cards += f"""
            <div class="recommendation-card">
                <div class="recommendation-header" onclick="toggleRecommendation({i})">
                    <div>
                        <span class="standard-badge">{standard}</span>
                        <span class="priority-badge priority-{priority}">{priority.title()}</span>
                        <h4 style="margin: 10px 0 5px 0;">{title}</h4>
                        <p style="margin: 0; color: #6c757d;">{description}</p>
                    </div>
                    <span id="toggle-{i}">▼</span>
                </div>
                <div class="recommendation-content" id="content-{i}">
                    {tech_details_html}
                    {rec_list_html}
                    {applicable_html}
                </div>
            </div>
            """

        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">📋</span>
                Recomendaciones ISA/IEC ({len(recommendations)})
            </h2>
            <div class="recommendations-container">
                {recommendation_cards}
            </div>
        </div>
        """

    def _create_footer(self) -> str:
        """Crear footer del reporte"""
        return f"""
        <div class="section" style="text-align: center; background: rgba(255, 255, 255, 0.9);">
            <p style="color: #6c757d;">
                SmartCompute Industrial v1.0.0 |
                Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
                © 2025 SmartCompute Security Solutions
            </p>
        </div>
        """

    def _generate_sensors_chart_data(self, sensor_types: Dict[str, List]) -> str:
        """Generar datos para gráfico de sensores"""
        chart_data = {
            'labels': [],
            'datasets': [{
                'label': 'Valores de Sensores',
                'data': [],
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ]
            }]
        }

        for sensor_type, sensors in sensor_types.items():
            if sensors:
                avg_value = sum(s.get('value', 0) for s in sensors) / len(sensors)
                chart_data['labels'].append(sensor_type.title())
                chart_data['datasets'][0]['data'].append(round(avg_value, 2))

        return json.dumps(chart_data)

    def _get_sensors_chart_script(self) -> str:
        """Script JavaScript para gráfico de sensores"""
        return """
        const ctx = document.getElementById('sensorsChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: sensorsData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Valores Promedio por Tipo de Sensor'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        """

    def _get_javascript(self) -> str:
        """JavaScript para interactividad del reporte"""
        return """
        function toggleRecommendation(index) {
            const content = document.getElementById('content-' + index);
            const toggle = document.getElementById('toggle-' + index);

            if (content.classList.contains('active')) {
                content.classList.remove('active');
                toggle.textContent = '▼';
            } else {
                content.classList.add('active');
                toggle.textContent = '▲';
            }
        }

        // Auto-refresh para datos en tiempo real (opcional)
        function refreshData() {
            console.log('Refreshing data...');
            // Implementar lógica de actualización en tiempo real si es necesario
        }

        // Inicialización
        document.addEventListener('DOMContentLoaded', function() {
            console.log('SmartCompute Industrial Report loaded');

            // Agregar animaciones suaves
            const cards = document.querySelectorAll('.sensor-card, .plc-card, .protocol-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
        """

def main():
    """Función principal para generar reporte HTML industrial"""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python generate_industrial_html_reports.py <archivo_json>")
        return

    json_file = sys.argv[1]
    if not Path(json_file).exists():
        print(f"Error: El archivo {json_file} no existe")
        return

    generator = SmartComputeIndustrialHTMLGenerator()
    html_path = generator.generate_industrial_report(json_file)
    print(f"✅ Reporte HTML generado: {html_path}")

if __name__ == "__main__":
    main()