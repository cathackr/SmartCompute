#!/usr/bin/env python3
"""
SmartCompute Industrial - Dashboard de Análisis MLE Star
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Dashboard interactivo para visualizar análisis y recomendaciones de MLE Star
"""

import json
from datetime import datetime
from pathlib import Path
from mle_star_analysis_engine import MLEStarAnalysisEngine
from generate_interactive_industrial_dashboard import generate_comprehensive_industrial_data

def generate_mle_dashboard():
    """Generar dashboard interactivo de análisis MLE Star"""

    # Ejecutar análisis MLE Star
    system_data = generate_comprehensive_industrial_data()
    mle_engine = MLEStarAnalysisEngine()
    report, recommendations = mle_engine.generate_comprehensive_analysis(system_data)

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartCompute Industrial - Análisis MLE Star</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #ffffff;
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
        .recommendation-card {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .recommendation-card:hover {{
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-3px);
        }}
        .priority-high {{
            border-left: 5px solid #dc3545;
        }}
        .priority-medium {{
            border-left: 5px solid #ffc107;
        }}
        .priority-low {{
            border-left: 5px solid #28a745;
        }}
        .mle-header {{
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .savings-highlight {{
            background: linear-gradient(45deg, #28a745, #20c997);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
            font-size: 1.8rem;
        }}
        .action-btn {{
            background: linear-gradient(45deg, #007bff, #6610f2);
            border: none;
            border-radius: 25px;
            color: white;
            padding: 10px 20px;
            margin: 5px;
            transition: all 0.3s ease;
        }}
        .action-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            color: white;
        }}
        .confidence-bar {{
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .confidence-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.5s ease;
        }}
        .category-badge {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 0.8rem;
            margin-right: 8px;
        }}
        .roi-indicator {{
            background: rgba(40, 167, 69, 0.2);
            border: 1px solid #28a745;
            border-radius: 10px;
            padding: 8px 12px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4 text-center">
                    <h1 class="mle-header display-4 mb-3">
                        <i class="fas fa-robot me-3"></i>
                        MLE Star - Análisis de Mejoras
                    </h1>
                    <h2 class="text-white mb-3">
                        Machine Learning Engine para Optimización Industrial
                    </h2>
                    <div class="row text-white">
                        <div class="col-md-3">
                            <i class="fas fa-clock me-2"></i>
                            <strong>Análisis:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-lightbulb me-2"></i>
                            <strong>Recomendaciones:</strong> {report['total_recommendations']}
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-dollar-sign me-2"></i>
                            <strong>Ahorros:</strong> ${report['total_estimated_savings']:,.0f}
                        </div>
                        <div class="col-md-3">
                            <i class="fas fa-chart-line me-2"></i>
                            <strong>ROI Promedio:</strong> {report['average_roi_months']:.1f} meses
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- KPIs del Análisis -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-exclamation-triangle text-danger"></i>
                    </div>
                    <h5 class="text-white">Alta Prioridad</h5>
                    <h3 class="text-danger">{report['high_priority']}</h3>
                    <small class="text-light">Recomendaciones críticas</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-clock text-warning"></i>
                    </div>
                    <h5 class="text-white">Media Prioridad</h5>
                    <h3 class="text-warning">{report['medium_priority']}</h3>
                    <small class="text-light">Mejoras importantes</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-info-circle text-success"></i>
                    </div>
                    <h5 class="text-white">Baja Prioridad</h5>
                    <h3 class="text-success">{report['low_priority']}</h3>
                    <small class="text-light">Optimizaciones menores</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="glass-card p-4 text-center metric-card">
                    <div class="display-4 mb-2">
                        <i class="fas fa-money-bill-wave text-success"></i>
                    </div>
                    <h5 class="text-white">Ahorro Anual</h5>
                    <h3 class="savings-highlight">${report['total_estimated_savings']:,.0f}</h3>
                    <small class="text-light">Proyección estimada</small>
                </div>
            </div>
        </div>

        <!-- Gráficos de Análisis -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-chart-pie me-2"></i>
                        Distribución por Categorías
                    </h5>
                    <div class="chart-container">
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-chart-bar me-2"></i>
                        ROI vs Ahorros (Top 10)
                    </h5>
                    <div class="chart-container">
                        <canvas id="roiChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recomendaciones Detalladas -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-4">
                        <i class="fas fa-list-ol me-2"></i>
                        Recomendaciones Prioritarias de MLE Star
                        <button class="btn btn-sm btn-outline-light ms-2" onclick="filterRecommendations('ALL')">
                            <i class="fas fa-filter"></i> Mostrar Todas
                        </button>
                        <button class="btn btn-sm btn-outline-danger ms-1" onclick="filterRecommendations('HIGH')">
                            Alta
                        </button>
                        <button class="btn btn-sm btn-outline-warning ms-1" onclick="filterRecommendations('MEDIUM')">
                            Media
                        </button>
                        <button class="btn btn-sm btn-outline-success ms-1" onclick="filterRecommendations('LOW')">
                            Baja
                        </button>
                    </h5>

                    <div id="recommendationsContainer">"""

    # Generar tarjetas de recomendaciones
    for i, rec in enumerate(recommendations, 1):
        priority_class = f"priority-{rec['priority'].lower()}"
        confidence_percent = rec.get('confidence', 0.5) * 100

        html_content += f"""
                        <div class="recommendation-card {priority_class}" data-priority="{rec['priority']}" onclick="showRecommendationDetail('{rec['process_id']}', {i-1})">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="d-flex align-items-center mb-2">
                                        <span class="badge bg-{rec['priority'].lower()} me-2">#{i}</span>
                                        <span class="category-badge">{rec['category'].replace('_', ' ')}</span>
                                        <span class="badge bg-info">{rec['priority']}</span>
                                    </div>
                                    <h6 class="text-white mb-2">{rec['title']}</h6>
                                    <p class="text-light small mb-2">{rec['description']}</p>
                                    <div class="row">
                                        <div class="col-sm-6">
                                            <small class="text-info">
                                                <i class="fas fa-cogs me-1"></i>
                                                Proceso: {rec['process_name']}
                                            </small>
                                        </div>
                                        <div class="col-sm-6">
                                            <small class="text-warning">
                                                <i class="fas fa-clock me-1"></i>
                                                Implementación: {rec['implementation_time']}
                                            </small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <h6 class="text-success mb-1">{rec['estimated_savings']}</h6>
                                        <div class="roi-indicator">
                                            <small class="text-white">ROI: {rec.get('roi_months', 'N/A')} meses</small>
                                        </div>
                                        <small class="text-light mt-1 d-block">Confianza: {confidence_percent:.0f}%</small>
                                        <div class="confidence-bar">
                                            <div class="confidence-fill" style="width: {confidence_percent}%"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>"""

    html_content += f"""
                    </div>
                </div>
            </div>
        </div>

        <!-- Resumen Ejecutivo -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h6 class="text-white mb-3">
                        <i class="fas fa-key me-2"></i>
                        Hallazgos Clave
                    </h6>
                    <ul class="text-light">"""

    for finding in report['executive_summary']['key_findings']:
        html_content += f"<li>{finding}</li>"

    html_content += f"""
                    </ul>
                </div>
            </div>
            <div class="col-md-6">
                <div class="glass-card p-4">
                    <h6 class="text-white mb-3">
                        <i class="fas fa-bolt me-2"></i>
                        Acciones Inmediatas
                    </h6>"""

    if report['executive_summary']['immediate_actions']:
        html_content += "<ul class='text-light'>"
        for action in report['executive_summary']['immediate_actions']:
            html_content += f"<li class='text-danger'><strong>{action}</strong></li>"
        html_content += "</ul>"
    else:
        html_content += "<p class='text-light'>No hay acciones inmediatas requeridas.</p>"

    html_content += f"""
                </div>
            </div>
        </div>

        <!-- Controles de Implementación -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4 text-center">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-play-circle me-2"></i>
                        Centro de Implementación MLE Star
                    </h5>
                    <button class="action-btn" onclick="generateImplementationPlan()">
                        <i class="fas fa-project-diagram me-2"></i>Generar Plan de Implementación
                    </button>
                    <button class="action-btn" onclick="exportAnalysis()">
                        <i class="fas fa-download me-2"></i>Exportar Análisis Completo
                    </button>
                    <button class="action-btn" onclick="scheduleReview()">
                        <i class="fas fa-calendar-alt me-2"></i>Programar Revisión
                    </button>
                    <button class="action-btn" onclick="notifyStakeholders()">
                        <i class="fas fa-bell me-2"></i>Notificar Stakeholders
                    </button>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="row">
            <div class="col-12">
                <div class="glass-card p-3 text-center">
                    <small class="text-white">
                        <i class="fas fa-robot me-1"></i>
                        Análisis generado por MLE Star Engine |
                        <a href="mailto:ggwre04p0@mozmail.com" class="text-info">ggwre04p0@mozmail.com</a> |
                        <a href="https://www.linkedin.com/in/martín-iribarne-swtf/" class="text-info" target="_blank">LinkedIn</a>
                    </small>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Detalle de Recomendación -->
    <div class="modal fade" id="recommendationModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content bg-dark text-white">
                <div class="modal-header">
                    <h5 class="modal-title" id="recommendationTitle">Detalles de Recomendación MLE Star</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="recommendationBody">
                    <!-- Content will be populated by JavaScript -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-success" onclick="approveRecommendation()">
                        <i class="fas fa-check me-1"></i>Aprobar Implementación
                    </button>
                    <button type="button" class="btn btn-warning" onclick="scheduleRecommendation()">
                        <i class="fas fa-calendar me-1"></i>Programar para Después
                    </button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Datos del análisis
        const analysisData = {json.dumps(recommendations, indent=4, default=str)};
        const reportData = {json.dumps(report, indent=4, default=str)};

        // Configuración global de gráficos
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.color = '#ffffff';

        // Gráfico de categorías
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        const categoryData = Object.keys(reportData.categories);
        const categoryCounts = Object.values(reportData.categories).map(arr => arr.length);

        const categoryChart = new Chart(categoryCtx, {{
            type: 'doughnut',
            data: {{
                labels: categoryData.map(cat => cat.replace('_', ' ')),
                datasets: [{{
                    data: categoryCounts,
                    backgroundColor: [
                        '#FF6B6B',
                        '#4ECDC4',
                        '#45B7D1',
                        '#96CEB4',
                        '#FECA57',
                        '#FF9FF3',
                        '#54A0FF'
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
                            color: '#ffffff',
                            padding: 15
                        }}
                    }}
                }}
            }}
        }});

        // Gráfico ROI vs Ahorros
        const roiCtx = document.getElementById('roiChart').getContext('2d');
        const top10 = analysisData.slice(0, 10);

        const roiChart = new Chart(roiCtx, {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Recomendaciones',
                    data: top10.map(rec => ({{
                        x: rec.roi_months || 12,
                        y: parseFloat(rec.estimated_savings.replace(/[^\\d.-]/g, '')) || 0
                    }})),
                    backgroundColor: '#4ECDC4',
                    borderColor: '#45B7D1',
                    borderWidth: 2,
                    pointRadius: 8,
                    pointHoverRadius: 10
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
                        title: {{
                            display: true,
                            text: 'ROI (meses)',
                            color: '#ffffff'
                        }},
                        ticks: {{
                            color: '#ffffff'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Ahorros Estimados ($)',
                            color: '#ffffff'
                        }},
                        ticks: {{
                            color: '#ffffff',
                            callback: function(value) {{
                                return '$' + value.toLocaleString();
                            }}
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }}
                }}
            }}
        }});

        // Funciones de interacción
        function filterRecommendations(priority) {{
            const cards = document.querySelectorAll('.recommendation-card');
            cards.forEach(card => {{
                if (priority === 'ALL' || card.dataset.priority === priority) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function showRecommendationDetail(processId, index) {{
            const rec = analysisData[index];
            document.getElementById('recommendationTitle').textContent = rec.title;

            let actionsHtml = '<ol>';
            rec.recommended_actions.forEach(action => {{
                actionsHtml += `<li class="mb-2">${{action}}</li>`;
            }});
            actionsHtml += '</ol>';

            document.getElementById('recommendationBody').innerHTML = `
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Proceso:</strong> ${{rec.process_name}}<br>
                        <strong>Categoría:</strong> ${{rec.category.replace('_', ' ')}}<br>
                        <strong>Prioridad:</strong> <span class="badge bg-${{rec.priority.toLowerCase()}}">${{rec.priority}}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>Ahorro Estimado:</strong> ${{rec.estimated_savings}}<br>
                        <strong>ROI:</strong> ${{rec.roi_months || 'N/A'}} meses<br>
                        <strong>Confianza:</strong> ${{(rec.confidence * 100).toFixed(0)}}%
                    </div>
                </div>
                <div class="mb-3">
                    <strong>Descripción:</strong><br>
                    <p class="text-light">${{rec.description}}</p>
                </div>
                <div class="mb-3">
                    <strong>Causa Raíz:</strong><br>
                    <p class="text-warning">${{rec.root_cause}}</p>
                </div>
                <div class="mb-3">
                    <strong>Acciones Recomendadas:</strong>
                    ${{actionsHtml}}
                </div>
                <div class="mb-3">
                    <strong>Tiempo de Implementación:</strong> ${{rec.implementation_time}}
                </div>
            `;

            new bootstrap.Modal(document.getElementById('recommendationModal')).show();
        }}

        function generateImplementationPlan() {{
            alert('🚀 Generando plan de implementación detallado...\\n\\nSe creará un cronograma con dependencias, recursos y milestones.');
        }}

        function exportAnalysis() {{
            const dataStr = JSON.stringify({{
                report: reportData,
                recommendations: analysisData
            }}, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'mle_star_analysis_' + new Date().toISOString().slice(0, 10) + '.json';
            link.click();
        }}

        function scheduleReview() {{
            alert('📅 Programando revisión de progreso...\\n\\nSe enviará recordatorio en 30 días para evaluar implementación.');
        }}

        function notifyStakeholders() {{
            alert('📧 Enviando notificaciones a stakeholders...\\n\\nGerencia, Ingeniería y Mantenimiento serán notificados.');
        }}

        function approveRecommendation() {{
            alert('✅ Recomendación aprobada para implementación\\n\\nSe creará ticket en sistema de gestión de proyectos.');
        }}

        function scheduleRecommendation() {{
            const date = prompt('Ingrese fecha para programar implementación (YYYY-MM-DD):');
            if (date) {{
                alert(`📅 Recomendación programada para ${{date}}`);
            }}
        }}

        console.log('🤖 MLE Star Dashboard iniciado');
        console.log('📊 Total recomendaciones:', analysisData.length);
        console.log('💰 Ahorros totales:', reportData.total_estimated_savings);
    </script>
</body>
</html>"""

    return html_content

def main():
    """Función principal"""
    try:
        print("=== SmartCompute Industrial - Dashboard MLE Star ===")
        print("Desarrollado por: ggwre04p0@mozmail.com")
        print("LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
        print()

        # Crear directorio de reportes si no existe
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Generar dashboard
        html_content = generate_mle_dashboard()

        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/mle_star_dashboard_{timestamp}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Dashboard MLE Star generado exitosamente:")
        print(f"📄 Archivo: {Path.cwd()}/{filename}")
        print(f"🌐 Para visualizar: file://{Path.cwd()}/{filename}")
        print()
        print("🎯 Características del Dashboard MLE Star:")
        print("  ✅ Análisis predictivo con Machine Learning")
        print("  ✅ Recomendaciones priorizadas por ROI y impacto")
        print("  ✅ Visualizaciones interactivas de mejoras")
        print("  ✅ Detalles técnicos por recomendación")
        print("  ✅ Centro de implementación integrado")
        print("  ✅ Filtrado por prioridad de recomendaciones")
        print("  ✅ Exportación de análisis completo")
        print()

    except Exception as e:
        print(f"❌ Error generando dashboard MLE Star: {e}")
        return False

    return True

if __name__ == "__main__":
    main()