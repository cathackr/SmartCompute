#!/usr/bin/env python3
"""
Generador de códigos QR para repositorios SmartCompute
Crea QR codes para acceso rápido a repositorios privados
"""

import requests
import os
from pathlib import Path

def generate_qr_code(url, filename, size="200x200"):
    """
    Genera un código QR usando API pública de qr-server.com
    """
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/"
    params = {
        'size': size,
        'data': url,
        'format': 'png',
        'ecc': 'M',  # Error correction level
        'margin': 10
    }
    
    try:
        response = requests.get(qr_api_url, params=params)
        response.raise_for_status()
        
        # Asegurar que existe el directorio
        os.makedirs('assets/qr_codes', exist_ok=True)
        
        # Guardar el QR
        qr_path = f"assets/qr_codes/{filename}"
        with open(qr_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ QR generado: {qr_path}")
        return qr_path
        
    except Exception as e:
        print(f"❌ Error generando QR para {url}: {e}")
        return None

def main():
    """Generar códigos QR para todos los repositorios SmartCompute"""
    
    print("🔄 Generando códigos QR para repositorios SmartCompute...")
    
    repositories = [
        {
            'name': 'SmartCompute Principal',
            'url': 'https://github.com/cathackr/SmartCompute',
            'filename': 'smartcompute_main_qr.png'
        },
        {
            'name': 'SmartCompute Enterprise',
            'url': 'https://github.com/cathackr/SmartCompute-Enterprise',
            'filename': 'smartcompute_enterprise_qr.png'
        },
        {
            'name': 'SmartCompute Industrial',
            'url': 'https://github.com/cathackr/SmartCompute-Industrial',
            'filename': 'smartcompute_industrial_qr.png'
        }
    ]
    
    generated_qrs = []
    
    for repo in repositories:
        print(f"\n📱 Generando QR para: {repo['name']}")
        qr_path = generate_qr_code(repo['url'], repo['filename'])
        
        if qr_path:
            generated_qrs.append({
                'name': repo['name'],
                'url': repo['url'],
                'qr_path': qr_path
            })
    
    # Generar también QRs con información adicional
    print(f"\n📱 Generando QR con información de acceso...")
    
    # QR con instrucciones de acceso
    access_info = """SmartCompute Repositories:
    
🏠 Main: github.com/cathackr/SmartCompute
🏢 Enterprise: github.com/cathackr/SmartCompute-Enterprise (Private)
🏭 Industrial: github.com/cathackr/SmartCompute-Industrial (Private)

Authentication required for private repos."""
    
    generate_qr_code(access_info, 'smartcompute_access_info_qr.png', '300x300')
    
    print("\n" + "="*60)
    print("✅ CÓDIGOS QR GENERADOS EXITOSAMENTE")
    print("="*60)
    
    for qr in generated_qrs:
        print(f"📱 {qr['name']}")
        print(f"   URL: {qr['url']}")
        print(f"   QR:  {qr['qr_path']}")
        print()
    
    print("📁 Ubicación: assets/qr_codes/")
    print("💡 Uso: Incluir en README.md y documentación")
    
    return generated_qrs

if __name__ == "__main__":
    main()