# 🔒 CONFIGURACIÓN SEGURA - SMARTCOMPUTE INDUSTRIAL

## ⚠️ ADVERTENCIAS CRÍTICAS DE SEGURIDAD

### 🚨 ANTES DE LA PRIMERA EJECUCIÓN:

1. **CAMBIAR TODAS LAS CLAVES DE EJEMPLO**
   ```bash
   # Generar clave JWT segura
   openssl rand -hex 32

   # Generar clave de encriptación AES-256
   openssl rand -hex 32

   # Generar secreto TOTP único por operador
   python3 -c "import pyotp; print(pyotp.random_base32())"
   ```

2. **CONFIGURAR UBICACIONES GPS REALES**
   - Usar coordenadas exactas de tu planta
   - Ajustar radio de seguridad apropiado
   - Verificar precisión GPS en el sitio

3. **CONFIGURAR OPERADORES REALES**
   - Crear cuentas individuales por técnico
   - Asignar niveles apropiados
   - Configurar 2FA único por persona

### 🛡️ PRÁCTICAS OBLIGATORIAS:

- ✅ Usar HTTPS en producción
- ✅ Configurar firewall restrictivo
- ✅ Habilitar logs de auditoría
- ✅ Backup automático de configuración
- ✅ Monitoreo de accesos

### ❌ NUNCA HACER:

- ❌ Usar configuración de ejemplo en producción
- ❌ Compartir secretos TOTP entre operadores
- ❌ Deshabilitar verificación GPS
- ❌ Ejecutar con permisos de root
- ❌ Conectar directamente a internet

## 📋 CHECKLIST DE SEGURIDAD:

- [ ] Claves únicas generadas
- [ ] GPS configurado y verificado
- [ ] Operadores con 2FA habilitado
- [ ] Firewall configurado
- [ ] SSL/TLS habilitado
- [ ] Logs de auditoría activos
- [ ] Backup automático configurado
- [ ] Personal entrenado en procedimientos

**📞 Soporte de seguridad:** ggwre04p0@mozmail.com
