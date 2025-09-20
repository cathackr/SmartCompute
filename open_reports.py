#!/usr/bin/env python3
"""
SmartCompute - Abridor de Reportes
==================================

Script para abrir los últimos reportes HTML generados en el navegador.
"""

import sys
from pathlib import Path

# Agregar el directorio actual al path para importar el generador
sys.path.append(str(Path(__file__).parent))

from generate_html_reports import SmartComputeHTMLReportGenerator


def main():
    """Abre los últimos reportes HTML generados"""

    print("🌐 Abriendo Reportes SmartCompute Enterprise")
    print("=" * 50)

    generator = SmartComputeHTMLReportGenerator()

    # Verificar si existen reportes
    reports_dir = generator.output_dir
    if not reports_dir.exists():
        print("❌ No se encontró el directorio de reportes")
        return

    analysis_reports = list(reports_dir.glob("smartcompute_enterprise_analysis_*.html"))
    security_reports = list(reports_dir.glob("smartcompute_security_report_*.html"))

    if not analysis_reports and not security_reports:
        print("❌ No se encontraron reportes HTML")
        print("💡 Ejecuta primero: python3 run_enterprise_analysis.py")
        return

    print(f"📊 Reportes de análisis encontrados: {len(analysis_reports)}")
    print(f"🔒 Reportes de seguridad encontrados: {len(security_reports)}")
    print()

    # Abrir últimos reportes
    generator.open_latest_reports()

    print()
    print("✅ Reportes abiertos en el navegador")

    # Mostrar ubicación de archivos
    if analysis_reports:
        latest_analysis = max(analysis_reports, key=lambda p: p.stat().st_mtime)
        print(f"📁 Último análisis: {latest_analysis}")

    if security_reports:
        latest_security = max(security_reports, key=lambda p: p.stat().st_mtime)
        print(f"📁 Último seguridad: {latest_security}")


if __name__ == "__main__":
    main()