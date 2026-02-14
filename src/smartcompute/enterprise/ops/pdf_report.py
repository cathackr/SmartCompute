#!/usr/bin/env python3
"""
Generador de PDF para el informe de evaluación SmartCompute Enterprise
"""

import os
import subprocess
from pathlib import Path


def generate_pdf_report():
    """Generar PDF desde HTML usando herramientas disponibles"""

    html_file = Path("/home/gatux/smartcompute/enterprise/informe_evaluacion_completa.html")
    pdf_file = Path("/home/gatux/smartcompute/enterprise/SmartCompute_Enterprise_Evaluacion_Completa.pdf")

    if not html_file.exists():
        print("❌ Archivo HTML no encontrado")
        return False

    print("🔍 Buscando herramientas para generación de PDF...")

    # Intentar con diferentes herramientas
    pdf_tools = [
        # wkhtmltopdf (más común)
        {
            'cmd': 'wkhtmltopdf',
            'args': [
                '--page-size', 'A4',
                '--orientation', 'Portrait',
                '--margin-top', '0.75in',
                '--margin-right', '0.75in',
                '--margin-bottom', '0.75in',
                '--margin-left', '0.75in',
                '--encoding', 'UTF-8',
                '--print-media-type',
                '--enable-local-file-access',
                str(html_file),
                str(pdf_file)
            ]
        },
        # weasyprint
        {
            'cmd': 'weasyprint',
            'args': [str(html_file), str(pdf_file)]
        },
        # chromium/chrome headless
        {
            'cmd': 'google-chrome',
            'args': [
                '--headless',
                '--disable-gpu',
                '--print-to-pdf=' + str(pdf_file),
                '--print-to-pdf-no-header',
                str(html_file)
            ]
        },
        {
            'cmd': 'chromium-browser',
            'args': [
                '--headless',
                '--disable-gpu',
                '--print-to-pdf=' + str(pdf_file),
                '--print-to-pdf-no-header',
                str(html_file)
            ]
        }
    ]

    for tool in pdf_tools:
        try:
            # Check if tool is available
            result = subprocess.run(['which', tool['cmd']],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Encontrado: {tool['cmd']}")
                print(f"📄 Generando PDF con {tool['cmd']}...")

                # Generate PDF
                result = subprocess.run([tool['cmd']] + tool['args'],
                                      capture_output=True, text=True)

                if result.returncode == 0 and pdf_file.exists():
                    print(f"✅ PDF generado exitosamente: {pdf_file}")
                    print(f"📊 Tamaño: {pdf_file.stat().st_size / 1024:.1f} KB")
                    return True
                else:
                    print(f"❌ Error generando PDF: {result.stderr}")

        except Exception as e:
            print(f"❌ Error con {tool['cmd']}: {e}")
            continue

    # Fallback: crear instrucciones para generar PDF manualmente
    print("\n⚠️  No se encontraron herramientas de PDF instaladas")
    create_manual_instructions(html_file)
    return False


def create_manual_instructions(html_file):
    """Crear instrucciones para generar PDF manualmente"""

    instructions_file = Path("/home/gatux/smartcompute/enterprise/INSTRUCCIONES_PDF.txt")

    instructions = f"""
INSTRUCCIONES PARA GENERAR PDF DEL INFORME SMARTCOMPUTE ENTERPRISE
================================================================

El informe HTML ha sido generado en:
{html_file}

Para convertirlo a PDF, puede usar una de estas opciones:

OPCIÓN 1: Navegador Web (Más Fácil)
-----------------------------------
1. Abra el archivo HTML en cualquier navegador web:
   - Firefox: firefox "{html_file}"
   - Chrome: google-chrome "{html_file}"
   - Edge: microsoft-edge "{html_file}"

2. Presione Ctrl+P (Cmd+P en Mac) para imprimir

3. Seleccione "Guardar como PDF" como destino

4. Configure:
   - Tamaño: A4
   - Márgenes: Normales
   - Escala: 100%
   - Incluir gráficos de fondo: SÍ

5. Guarde como: SmartCompute_Enterprise_Evaluacion_Completa.pdf

OPCIÓN 2: Instalar herramientas de línea de comandos
---------------------------------------------------
# Ubuntu/Debian:
sudo apt-get install wkhtmltopdf

# CentOS/RHEL/Fedora:
sudo yum install wkhtmltopdf
# o
sudo dnf install wkhtmltopdf

# macOS:
brew install wkhtmltopdf

Luego ejecute:
wkhtmltopdf --page-size A4 --margin-top 0.75in --margin-right 0.75in \\
  --margin-bottom 0.75in --margin-left 0.75in --encoding UTF-8 \\
  --print-media-type --enable-local-file-access \\
  "{html_file}" "SmartCompute_Enterprise_Evaluacion_Completa.pdf"

OPCIÓN 3: Herramientas online
-----------------------------
1. Suba el archivo HTML a un convertidor online como:
   - https://www.ilovepdf.com/html-to-pdf
   - https://smallpdf.com/html-to-pdf
   - https://www.pdf24.org/html-to-pdf.html

2. Descargue el PDF generado

NOTA: El informe está completamente autocontenido en el HTML,
      con todos los estilos CSS embebidos.
"""

    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)

    print(f"📄 Instrucciones creadas en: {instructions_file}")


def create_viewing_script():
    """Crear script para abrir el informe HTML"""

    script_file = Path("/home/gatux/smartcompute/enterprise/ver_informe.sh")
    html_file = Path("/home/gatux/smartcompute/enterprise/informe_evaluacion_completa.html")

    script_content = f"""#!/bin/bash
# Script para abrir el informe SmartCompute Enterprise

echo "🚀 Abriendo informe SmartCompute Enterprise..."

# Buscar navegadores disponibles
if command -v google-chrome &> /dev/null; then
    google-chrome "{html_file}"
elif command -v firefox &> /dev/null; then
    firefox "{html_file}"
elif command -v chromium-browser &> /dev/null; then
    chromium-browser "{html_file}"
elif command -v microsoft-edge &> /dev/null; then
    microsoft-edge "{html_file}"
else
    echo "❌ No se encontró navegador web instalado"
    echo "📄 Abra manualmente: {html_file}"
fi
"""

    with open(script_file, 'w') as f:
        f.write(script_content)

    # Make executable
    script_file.chmod(0o755)

    print(f"📜 Script de visualización creado: {script_file}")
    print(f"    Ejecute: bash {script_file}")


if __name__ == "__main__":
    print("📄 SmartCompute Enterprise - Generador de PDF")
    print("=" * 50)

    success = generate_pdf_report()
    create_viewing_script()

    if success:
        print("\n🎉 ¡Informe PDF generado exitosamente!")
    else:
        print("\n📋 Informe HTML disponible - consulte instrucciones para PDF")

    print("\n📁 Archivos generados:")
    files = [
        "informe_evaluacion_completa.html",
        "SmartCompute_Enterprise_Evaluacion_Completa.pdf",
        "INSTRUCCIONES_PDF.txt",
        "ver_informe.sh"
    ]

    base_path = Path("/home/gatux/smartcompute/enterprise/")
    for file in files:
        file_path = base_path / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {file} ({size:,} bytes)")
        else:
            print(f"  ⚠️  {file} (no generado)")