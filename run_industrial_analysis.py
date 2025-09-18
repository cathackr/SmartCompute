#!/usr/bin/env python3
"""
SmartCompute Industrial - Ejecutor Principal
===========================================

Script principal que ejecuta análisis completo de sistemas industriales
y genera reportes HTML detallados.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Agregar directorio actual al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importar módulos locales
from smartcompute_industrial_monitor import SmartComputeIndustrialMonitor
from generate_industrial_html_reports import SmartComputeIndustrialHTMLGenerator

def main():
    """Función principal del análisis industrial"""
    print("🏭 SmartCompute Industrial - Análisis Completo de Sistemas Industriales")
    print("=" * 70)
    print()

    try:
        # Inicializar monitor industrial
        monitor = SmartComputeIndustrialMonitor()

        # Ejecutar análisis completo
        print("🔍 Iniciando análisis del sistema industrial...")
        analysis_data = monitor.analyze_industrial_system()

        # Guardar análisis en JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"smartcompute_industrial_analysis_{timestamp}.json"

        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Análisis JSON guardado: {json_filename}")

        # Generar reporte HTML
        print("🎨 Generando reporte HTML...")
        html_generator = SmartComputeIndustrialHTMLGenerator()
        html_path = html_generator.generate_industrial_report(json_filename)

        # Mostrar resumen
        print()
        print("📊 RESUMEN DEL ANÁLISIS")
        print("-" * 30)

        stats = analysis_data.get('statistics', {})
        protocols_detected = len([p for p in analysis_data.get('protocols', {}).values() if p.get('detected', False)])

        print(f"• Protocolos industriales detectados: {protocols_detected}")
        print(f"• PLCs descubiertos: {stats.get('plcs_discovered', 0)}")
        print(f"• Sensores monitoreados: {stats.get('sensors_active', 0)}")
        print(f"• Mensajes SCADA procesados: {stats.get('messages_processed', 0)}")
        print(f"• Alertas generadas: {stats.get('errors_detected', 0)}")
        print(f"• Duración del análisis: {analysis_data.get('duration_seconds', 0)} segundos")

        # Mostrar alertas críticas
        alerts = analysis_data.get('alerts', [])
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        if critical_alerts:
            print(f"⚠️  ALERTAS CRÍTICAS: {len(critical_alerts)}")
            for alert in critical_alerts[:3]:  # Mostrar solo las primeras 3
                print(f"   - {alert.get('message', 'N/A')}")

        # Mostrar recomendaciones principales
        recommendations = analysis_data.get('recommendations', [])
        critical_recs = [r for r in recommendations if r.get('priority') == 'critical']
        if critical_recs:
            print(f"📋 RECOMENDACIONES CRÍTICAS: {len(critical_recs)}")
            for rec in critical_recs[:2]:  # Mostrar solo las primeras 2
                print(f"   - {rec.get('standard')}: {rec.get('title')}")

        print()
        print("🌐 ARCHIVOS GENERADOS:")
        print(f"• Análisis JSON: {json_filename}")
        print(f"• Reporte HTML: {html_path}")
        print()
        print("✅ Análisis industrial completado exitosamente!")

        # Abrir reporte HTML automáticamente
        try:
            import webbrowser
            webbrowser.open(f'file://{Path(html_path).absolute()}')
            print("🌐 Reporte HTML abierto en navegador")
        except:
            print("ℹ️  Abra manualmente el reporte HTML para visualizar los resultados")

    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())