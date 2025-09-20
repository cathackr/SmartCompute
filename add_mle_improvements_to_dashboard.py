#!/usr/bin/env python3
"""
SmartCompute Industrial - Agregar Mejoras MLE Star al Dashboard Existente
Desarrollado por: ggwre04p0@mozmail.com
LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/

Agregar análisis MLE Star como sección adicional al dashboard existente
SIN modificar el diagrama de flujo ni las funcionalidades existentes.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from mle_star_analysis_engine import MLEStarAnalysisEngine
from generate_interactive_industrial_dashboard import generate_comprehensive_industrial_data

def add_mle_section_to_existing_dashboard():
    """Agregar sección MLE Star al dashboard existente sin modificar nada más"""

    # Leer el dashboard existente
    existing_dashboard_file = "reports/smartcompute_interactive_industrial_20250919_170101.html"

    try:
        with open(existing_dashboard_file, 'r', encoding='utf-8') as f:
            existing_html = f.read()
    except FileNotFoundError:
        print("❌ No se encontró el dashboard existente. Generando uno nuevo...")
        # Si no existe, generar uno nuevo
        from generate_interactive_industrial_dashboard import main as generate_dashboard
        generate_dashboard()
        existing_dashboard_file = "reports/smartcompute_interactive_industrial_20250919_170101.html"
        with open(existing_dashboard_file, 'r', encoding='utf-8') as f:
            existing_html = f.read()

    # Generar análisis MLE Star
    system_data = generate_comprehensive_industrial_data()
    mle_engine = MLEStarAnalysisEngine()
    report, recommendations = mle_engine.generate_comprehensive_analysis(system_data)

    # Crear la sección MLE Star a insertar
    mle_section = f"""
        <!-- MLE Star Analysis Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-card p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-robot me-2"></i>
                        Análisis MLE Star - Mejoras Identificadas
                        <button class="btn btn-sm btn-outline-light ms-2" onclick="toggleMLESection()">
                            <i class="fas fa-eye" id="mleToggleIcon"></i> <span id="mleToggleText">Mostrar</span>
                        </button>
                        <button class="btn btn-sm btn-outline-info ms-2" onclick="refreshMLEAnalysis()">
                            <i class="fas fa-sync-alt"></i> Actualizar Análisis
                        </button>
                    </h5>

                    <div id="mleAnalysisSection" style="display: none;">
                        <!-- Summary Stats -->
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="p-3 bg-dark rounded text-center">
                                    <h6 class="text-info">Total Mejoras</h6>
                                    <h4 class="text-white">{len(recommendations)}</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-3 bg-dark rounded text-center">
                                    <h6 class="text-danger">Alta Prioridad</h6>
                                    <h4 class="text-white">{len([r for r in recommendations if r["priority"] == "HIGH"])}</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-3 bg-dark rounded text-center">
                                    <h6 class="text-warning">Media Prioridad</h6>
                                    <h4 class="text-white">{len([r for r in recommendations if r["priority"] == "MEDIUM"])}</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-3 bg-dark rounded text-center">
                                    <h6 class="text-success">Baja Prioridad</h6>
                                    <h4 class="text-white">{len([r for r in recommendations if r["priority"] == "LOW"])}</h4>
                                </div>
                            </div>
                        </div>

                        <!-- Improvements List -->
                        <div class="row">
                            <div class="col-12">
                                <h6 class="text-warning mb-3">Mejoras Prioritarias Identificadas:</h6>
                                <div class="row">"""

    # Agregar las mejoras como tarjetas
    for i, rec in enumerate(recommendations[:6], 1):  # Solo top 6 para no sobrecargar
        priority_class = 'danger' if rec['priority'] == 'HIGH' else 'warning' if rec['priority'] == 'MEDIUM' else 'success'

        mle_section += f"""
                                    <div class="col-md-6 mb-3">
                                        <div class="p-3 border border-{priority_class} rounded bg-dark">
                                            <div class="d-flex justify-content-between align-items-start mb-2">
                                                <span class="badge bg-{priority_class}">#{i}</span>
                                                <span class="badge bg-secondary">{rec['category'].replace('_', ' ')}</span>
                                            </div>
                                            <h6 class="text-white mb-2">{rec['title']}</h6>
                                            <p class="text-light small mb-2">{rec['description']}</p>
                                            <div class="mb-2">
                                                <small class="text-info">
                                                    <i class="fas fa-cogs me-1"></i>
                                                    {rec['process_name']}
                                                </small>
                                            </div>
                                            <div class="mb-2">
                                                <small class="text-warning">
                                                    <i class="fas fa-lightbulb me-1"></i>
                                                    Causa: {rec['root_cause']}
                                                </small>
                                            </div>
                                            <button class="btn btn-sm btn-outline-info" onclick="showMLEDetails('{rec['process_id']}', {i-1})">
                                                <i class="fas fa-info-circle me-1"></i>Ver Detalles
                                            </button>
                                        </div>
                                    </div>"""

    mle_section += f"""
                                </div>

                                <!-- Action Buttons -->
                                <div class="text-center mt-3">
                                    <button class="btn btn-outline-primary me-2" onclick="viewAllMLERecommendations()">
                                        <i class="fas fa-list me-2"></i>Ver Todas las Recomendaciones
                                    </button>
                                    <button class="btn btn-outline-success me-2" onclick="generateActionPlan()">
                                        <i class="fas fa-project-diagram me-2"></i>Generar Plan de Acción
                                    </button>
                                    <button class="btn btn-outline-warning" onclick="exportMLEAnalysis()">
                                        <i class="fas fa-download me-2"></i>Exportar Análisis
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""

    # JavaScript adicional para MLE
    mle_javascript = f"""
        // Datos MLE Star
        const mleRecommendations = {json.dumps(recommendations, indent=4, default=str)};
        let mleVisible = false;

        // Toggle MLE section
        function toggleMLESection() {{
            const section = document.getElementById('mleAnalysisSection');
            const icon = document.getElementById('mleToggleIcon');
            const text = document.getElementById('mleToggleText');

            if (mleVisible) {{
                section.style.display = 'none';
                icon.className = 'fas fa-eye';
                text.textContent = 'Mostrar';
                mleVisible = false;
            }} else {{
                section.style.display = 'block';
                icon.className = 'fas fa-eye-slash';
                text.textContent = 'Ocultar';
                mleVisible = true;
            }}
        }}

        // Mostrar detalles de mejora MLE
        function showMLEDetails(processId, index) {{
            const rec = mleRecommendations[index];

            // Reutilizar el modal existente del sector
            document.getElementById('sectorTitle').textContent = 'MLE Star: ' + rec.title;

            let actionsHtml = '<h6 class="text-warning mb-2">Acciones Recomendadas:</h6><ol class="text-light">';
            rec.recommended_actions.forEach(action => {{
                actionsHtml += `<li class="mb-1">${{action}}</li>`;
            }});
            actionsHtml += '</ol>';

            document.getElementById('sectorBody').innerHTML = `
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Proceso:</strong> ${{rec.process_name}}<br>
                        <strong>Categoría:</strong> ${{rec.category.replace('_', ' ')}}<br>
                        <strong>Prioridad:</strong> <span class="badge bg-${{rec.priority.toLowerCase()}}">${{rec.priority}}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>Implementación:</strong> ${{rec.implementation_time}}<br>
                        <strong>Confianza:</strong> ${{(rec.confidence * 100).toFixed(0)}}%
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="text-info mb-2">Descripción:</h6>
                    <p class="text-light">${{rec.description}}</p>
                </div>
                <div class="mb-3">
                    <h6 class="text-warning mb-2">Causa Raíz Identificada:</h6>
                    <p class="text-warning">${{rec.root_cause}}</p>
                </div>
                <div class="mb-3">
                    ${{actionsHtml}}
                </div>
                <div class="text-center mt-4">
                    <button class="btn btn-success me-2" onclick="implementMLE('${{rec.process_id}}')">
                        <i class="fas fa-play me-1"></i>Implementar Ahora
                    </button>
                    <button class="btn btn-info me-2" onclick="scheduleMLE('${{rec.process_id}}')">
                        <i class="fas fa-calendar me-1"></i>Programar
                    </button>
                    <button class="btn btn-warning" onclick="consultMLE('${{rec.process_id}}')">
                        <i class="fas fa-users me-1"></i>Consultar Equipo
                    </button>
                </div>
            `;

            new bootstrap.Modal(document.getElementById('sectorModal')).show();
        }}

        // Funciones MLE adicionales
        function refreshMLEAnalysis() {{
            alert('🔄 Actualizando análisis MLE Star...\\n\\nRe-analizando datos de sensores y procesos en tiempo real.');
        }}

        function viewAllMLERecommendations() {{
            alert(`📋 Mostrando todas las recomendaciones MLE Star\\n\\nTotal: ${{mleRecommendations.length}} mejoras identificadas\\n\\nSe abrirá vista detallada.`);
        }}

        function generateActionPlan() {{
            alert('📋 Generando plan de acción...\\n\\nCreando cronograma de implementación basado en prioridades y dependencias.');
        }}

        function exportMLEAnalysis() {{
            const dataStr = JSON.stringify(mleRecommendations, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'mle_star_recommendations_' + new Date().toISOString().slice(0, 10) + '.json';
            link.click();
        }}

        function implementMLE(processId) {{
            alert(`✅ Iniciando implementación de mejora\\n\\nProceso: ${{processId}}\\n\\nSe creará ticket de trabajo y se asignarán recursos.`);
        }}

        function scheduleMLE(processId) {{
            const date = prompt('Ingrese fecha para implementación (YYYY-MM-DD):');
            if (date) {{
                alert(`📅 Mejora programada para ${{date}}\\n\\nSe agregará al cronograma de mantenimiento.`);
            }}
        }}

        function consultMLE(processId) {{
            alert(`👥 Consultando con equipo técnico...\\n\\nSe enviará solicitud de revisión a ingeniería y mantenimiento.`);
        }}"""

    # Insertar la sección MLE antes del área de exportación de reportes
    insertion_point = existing_html.find('<!-- Report Export with User Selection -->')
    if insertion_point == -1:
        # Si no encuentra ese comentario, insertar antes del footer
        insertion_point = existing_html.find('<!-- Footer -->')

    if insertion_point != -1:
        # Insertar la sección MLE
        modified_html = existing_html[:insertion_point] + mle_section + existing_html[insertion_point:]

        # Insertar el JavaScript antes del cierre del script existente
        script_insertion = modified_html.rfind('console.log(\'✅ SmartCompute Industrial Dashboard iniciado\');')
        if script_insertion != -1:
            modified_html = (modified_html[:script_insertion] +
                           mle_javascript + '\n\n        ' +
                           modified_html[script_insertion:])

        return modified_html
    else:
        print("❌ No se pudo encontrar punto de inserción en el HTML")
        return existing_html

def main():
    """Función principal"""
    try:
        print("=== SmartCompute Industrial - Agregar Análisis MLE Star ===")
        print("Desarrollado por: ggwre04p0@mozmail.com")
        print("LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/")
        print()

        # Crear directorio de reportes si no existe
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Modificar dashboard existente
        modified_html = add_mle_section_to_existing_dashboard()

        # Guardar el dashboard modificado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/smartcompute_with_mle_improvements_{timestamp}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(modified_html)

        print(f"✅ Dashboard con análisis MLE Star generado exitosamente:")
        print(f"📄 Archivo: {Path.cwd()}/{filename}")
        print(f"🌐 Para visualizar: file://{Path.cwd()}/{filename}")
        print()
        print("🎯 Funcionalidades agregadas:")
        print("  ✅ Sección MLE Star manteniendo diagrama de flujo original")
        print("  ✅ Mejoras identificadas como información adicional")
        print("  ✅ Botón mostrar/ocultar para no interferir con funcionalidad existente")
        print("  ✅ Detalles técnicos de cada mejora (SIN costos/ROI)")
        print("  ✅ Acciones de implementación, programación y consulta")
        print("  ✅ Exportación de análisis completo")
        print()
        print("📋 El diagrama de flujo y todas las funcionalidades existentes se mantienen intactas.")

    except Exception as e:
        print(f"❌ Error agregando análisis MLE Star: {e}")
        return False

    return True

if __name__ == "__main__":
    main()