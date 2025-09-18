#!/usr/bin/env python3
"""
SmartCompute Unified - Versión Integrada
========================================

Script unificado que permite ejecutar análisis tanto para:
- SmartCompute Enterprise (sistemas tradicionales)
- SmartCompute Industrial (sistemas SCADA/PLC)

Uso:
    python3 smartcompute_unified.py [enterprise|industrial|both]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

def print_banner():
    """Mostrar banner principal"""
    print("🚀 SmartCompute Unified - Plataforma de Análisis de Seguridad")
    print("=" * 60)
    print("   Enterprise: Sistemas tradicionales de TI")
    print("   Industrial: Sistemas SCADA, PLC y protocolos industriales")
    print("=" * 60)
    print()

def run_enterprise_analysis():
    """Ejecutar análisis enterprise"""
    print("🏢 Iniciando análisis SmartCompute Enterprise...")
    print("-" * 50)

    try:
        # Importar y ejecutar análisis enterprise
        from run_enterprise_analysis import main as enterprise_main
        return enterprise_main()

    except ImportError as e:
        print(f"❌ Error: No se pudo importar módulo enterprise: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error durante análisis enterprise: {e}")
        return 1

def run_industrial_analysis():
    """Ejecutar análisis industrial"""
    print("🏭 Iniciando análisis SmartCompute Industrial...")
    print("-" * 50)

    try:
        # Importar y ejecutar análisis industrial
        from run_industrial_analysis import main as industrial_main
        return industrial_main()

    except ImportError as e:
        print(f"❌ Error: No se pudo importar módulo industrial: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error durante análisis industrial: {e}")
        return 1

def run_both_analyses():
    """Ejecutar ambos análisis"""
    print("🔄 Ejecutando análisis completo (Enterprise + Industrial)...")
    print("=" * 60)

    results = {}

    # Ejecutar análisis enterprise
    print("\n📍 FASE 1: Análisis Enterprise")
    enterprise_result = run_enterprise_analysis()
    results['enterprise'] = enterprise_result

    print("\n" + "="*60)

    # Ejecutar análisis industrial
    print("\n📍 FASE 2: Análisis Industrial")
    industrial_result = run_industrial_analysis()
    results['industrial'] = industrial_result

    # Mostrar resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("-" * 30)
    print(f"• Análisis Enterprise: {'✅ Completado' if enterprise_result == 0 else '❌ Falló'}")
    print(f"• Análisis Industrial: {'✅ Completado' if industrial_result == 0 else '❌ Falló'}")

    if enterprise_result == 0 and industrial_result == 0:
        print("\n🎉 Todos los análisis completados exitosamente!")
        return 0
    else:
        print(f"\n⚠️  Algunos análisis fallaron (Enterprise: {enterprise_result}, Industrial: {industrial_result})")
        return 1

def create_combined_report():
    """Crear reporte combinado si existen ambos tipos de análisis"""
    print("\n📋 Verificando reportes para crear resumen combinado...")

    # Buscar archivos de análisis recientes
    enterprise_files = list(Path('.').glob('enterprise_analysis_*.json'))
    industrial_files = list(Path('.').glob('smartcompute_industrial_analysis_*.json'))

    if enterprise_files and industrial_files:
        # Tomar los más recientes
        latest_enterprise = max(enterprise_files, key=os.path.getctime)
        latest_industrial = max(industrial_files, key=os.path.getctime)

        print(f"✅ Encontrados reportes para combinar:")
        print(f"   - Enterprise: {latest_enterprise}")
        print(f"   - Industrial: {latest_industrial}")

        # Crear resumen combinado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_summary = f"smartcompute_combined_summary_{timestamp}.md"

        with open(combined_summary, 'w', encoding='utf-8') as f:
            f.write("# SmartCompute Unified - Resumen Combinado\n\n")
            f.write(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 🏢 Análisis Enterprise\n\n")
            f.write(f"- Archivo JSON: `{latest_enterprise}`\n")
            f.write("- Reporte HTML: Ver archivos `*enterprise_analysis*.html`\n\n")
            f.write("## 🏭 Análisis Industrial\n\n")
            f.write(f"- Archivo JSON: `{latest_industrial}`\n")
            f.write("- Reporte HTML: Ver archivos `*industrial_report*.html`\n\n")
            f.write("## 📊 Archivos de Reporte\n\n")
            f.write("### Enterprise\n")
            f.write("- Análisis completo de seguridad OWASP/NIST/ISO 27001\n")
            f.write("- Monitoreo de procesos y conexiones de red\n")
            f.write("- Detección de vulnerabilidades tradicionales\n\n")
            f.write("### Industrial\n")
            f.write("- Protocolos industriales (Modbus, EtherNet/IP, PROFINET)\n")
            f.write("- Monitoreo de PLCs y dispositivos industriales\n")
            f.write("- Sensores en tiempo real y estados de interruptores\n")
            f.write("- Mensajes SCADA y recomendaciones ISA/IEC\n\n")
            f.write("## 🔗 Integración\n\n")
            f.write("Ambos análisis pueden ejecutarse independientemente o en conjunto\n")
            f.write("para proporcionar una visión completa de la infraestructura.\n")

        print(f"📄 Resumen combinado creado: {combined_summary}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='SmartCompute Unified - Análisis de seguridad empresarial e industrial',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 smartcompute_unified.py enterprise    # Solo análisis enterprise
  python3 smartcompute_unified.py industrial    # Solo análisis industrial
  python3 smartcompute_unified.py both          # Ambos análisis
  python3 smartcompute_unified.py               # Menú interactivo
        """
    )

    parser.add_argument(
        'mode',
        nargs='?',
        choices=['enterprise', 'industrial', 'both'],
        help='Modo de análisis a ejecutar'
    )

    args = parser.parse_args()

    print_banner()

    # Si no se especifica modo, mostrar menú interactivo
    if not args.mode:
        print("Seleccione el tipo de análisis:")
        print("1. Enterprise (sistemas tradicionales)")
        print("2. Industrial (SCADA/PLC)")
        print("3. Ambos")
        print("4. Salir")

        try:
            choice = input("\nIngrese su opción (1-4): ").strip()
            if choice == '1':
                args.mode = 'enterprise'
            elif choice == '2':
                args.mode = 'industrial'
            elif choice == '3':
                args.mode = 'both'
            elif choice == '4':
                print("👋 Saliendo...")
                return 0
            else:
                print("❌ Opción inválida")
                return 1
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            return 0

    # Ejecutar análisis según el modo seleccionado
    try:
        if args.mode == 'enterprise':
            result = run_enterprise_analysis()
        elif args.mode == 'industrial':
            result = run_industrial_analysis()
        elif args.mode == 'both':
            result = run_both_analyses()
            # Crear reporte combinado si ambos tuvieron éxito
            if result == 0:
                create_combined_report()

        return result

    except KeyboardInterrupt:
        print("\n\n⚠️ Análisis interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())