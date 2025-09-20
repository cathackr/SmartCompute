#!/usr/bin/env python3
"""
SmartCompute Industrial - Herramienta de Descifrado de Reportes
Autor: SmartCompute Industrial Team
Fecha: 2024-09-19

Herramienta para descifrar reportes exportados con el sistema de exportación industrial.
Permite recuperar el contenido original usando la clave proporcionada por el operador.
"""

import json
import hashlib
import sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def decrypt_report(encrypted_file_path: str, operator_key: str, output_path: str = None) -> bool:
    """
    Descifra un reporte industrial cifrado

    Args:
        encrypted_file_path: Ruta al archivo cifrado
        operator_key: Clave proporcionada por el operador
        output_path: Ruta de salida (opcional)

    Returns:
        bool: True si el descifrado fue exitoso
    """
    try:
        # Leer archivo cifrado
        with open(encrypted_file_path, 'rb') as f:
            # Leer tamaño de metadata (primeros 4 bytes)
            metadata_size = int.from_bytes(f.read(4), byteorder='big')

            # Leer metadata JSON
            metadata_json = f.read(metadata_size)
            encryption_info = json.loads(metadata_json.decode('utf-8'))

            # Leer contenido cifrado
            encrypted_content = f.read()

        print(f"Información de cifrado:")
        print(f"  Algoritmo: {encryption_info['algorithm']}")
        print(f"  Derivación: {encryption_info['key_derivation']}")
        print(f"  Iteraciones: {encryption_info['iterations']}")
        print(f"  Cifrado por: {encryption_info['encrypted_by']}")
        print(f"  Fecha: {encryption_info['encrypted_at']}")

        # Extraer salt del contenido cifrado
        salt = bytes.fromhex(encryption_info['salt'])

        # Derivar clave de descifrado
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=encryption_info['iterations']
        )
        decryption_key = kdf.derive(operator_key.encode('utf-8'))

        # El archivo tiene estructura: [4 bytes size][metadata JSON][salt(16) + nonce(12) + encrypted_data]
        # Separar el salt del contenido cifrado
        salt_from_content = encrypted_content[:16]     # Salt (16 bytes)
        nonce = encrypted_content[16:28]              # Nonce (12 bytes)
        actual_encrypted_data = encrypted_content[28:] # Datos cifrados

        # Verificar que el salt coincida
        expected_salt = bytes.fromhex(encryption_info['salt'])
        if salt_from_content != expected_salt:
            print(f"Advertencia: Salt no coincide")
            print(f"  Esperado: {expected_salt.hex()}")
            print(f"  Encontrado: {salt_from_content.hex()}")

        # Usar el salt del metadata para consistencia
        salt = expected_salt

        # Descifrar
        aesgcm = AESGCM(decryption_key)
        decrypted_content = aesgcm.decrypt(nonce, actual_encrypted_data, None)

        # Determinar archivo de salida
        if not output_path:
            # Remover .encrypted de la extensión
            original_path = Path(encrypted_file_path)
            if original_path.name.endswith('.encrypted'):
                output_path = str(original_path.with_name(original_path.name[:-10]))  # Remove .encrypted
            else:
                output_path = str(original_path.with_suffix('.decrypted' + original_path.suffix))

        # Escribir contenido descifrado
        with open(output_path, 'wb') as f:
            f.write(decrypted_content)

        # Verificar integridad si hay checksum original
        calculated_checksum = hashlib.sha256(decrypted_content).hexdigest()
        print(f"\nArchivo descifrado exitosamente: {output_path}")
        print(f"Checksum calculado: {calculated_checksum}")

        return True

    except Exception as e:
        print(f"Error durante el descifrado: {str(e)}")
        print("Verifique que la clave de descifrado sea correcta")
        return False

def main():
    """Función principal para descifrado interactivo"""
    print("=== SmartCompute Industrial - Descifrador de Reportes ===\n")

    if len(sys.argv) < 2:
        print("Uso: python3 decrypt_report.py <archivo_cifrado> [archivo_salida]")
        print("\nEjemplo:")
        print("  python3 decrypt_report.py report_vulnerability_assessment_REQ123.pdf.encrypted")
        print("  python3 decrypt_report.py report_scada_logs_REQ456.xlsx.encrypted mi_reporte.xlsx")
        return

    encrypted_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(encrypted_file).exists():
        print(f"Error: Archivo no encontrado: {encrypted_file}")
        return

    # Solicitar clave de descifrado
    operator_key = input("Ingrese la clave de descifrado: ")

    if not operator_key:
        print("Error: Debe proporcionar una clave de descifrado")
        return

    print(f"\nDescrifrando archivo: {encrypted_file}")
    success = decrypt_report(encrypted_file, operator_key, output_file)

    if success:
        print("\n✓ Descifrado completado exitosamente")

        # Mostrar instrucciones si existe archivo de instrucciones
        instructions_file = encrypted_file + ".instructions.txt"
        if Path(instructions_file).exists():
            print(f"\nConsulte las instrucciones completas en: {instructions_file}")
    else:
        print("\n✗ Error en el descifrado")

if __name__ == "__main__":
    main()