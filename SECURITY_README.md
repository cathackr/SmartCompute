# 🔒 SmartCompute - Seguridad y Privacidad

## ⚠️ IMPORTANTE: Archivos Locales vs. GitHub

### 🏠 **Solo para Uso Local (NO subir a GitHub):**

Los siguientes archivos contienen **análisis reales** de tu sistema y **NO deben subirse** a repositorios públicos:

#### 🔍 **Scripts de Análisis Local:**
- `system_health_check.sh` - Datos reales del sistema
- `smartcompute_live_analysis.py` - Monitoreo en tiempo real
- `apply_improvements.sh` - Configuraciones específicas
- `comprehensive_integration_test.py` - Resultados de pruebas

#### 📊 **Reportes con Datos Reales:**
- `*_analysis_report.json` - Métricas del sistema
- `informe_evaluacion_completa.html` - Reporte visual completo
- `health_check*.log` - Logs de monitoreo
- `/tmp/smartcompute_*` - Archivos temporales

### ✅ **Seguro para GitHub (Código Genérico):**

Estos archivos contienen solo **código base** sin datos específicos:

- `smartcompute_core.py` - Motor principal
- `hrm_analysis_engine.py` - Algoritmos de análisis
- `threat_detection.py` - Lógica de detección
- `mcp_*.py` - Protocolo MCP implementación
- `README.md` - Documentación general

## 🛡️ **Medidas de Protección Implementadas:**

### 1. **GitIgnore Automático**
```bash
# Todos los archivos sensibles están en .gitignore
git status  # Verificar que no aparecen archivos sensibles
```

### 2. **Separación de Entornos**
```
smartcompute/
├── core/           # ✅ Código seguro para GitHub
├── enterprise/     # ❌ Análisis local (NO subir)
├── examples/       # ✅ Ejemplos sin datos reales
└── local_tests/    # ❌ Pruebas con datos reales
```

### 3. **Variables de Entorno**
```bash
# Usar variables para datos sensibles
export SMARTCOMPUTE_LOCAL_MODE=true
export SMARTCOMPUTE_SYSTEM_NAME="[REDACTED]"
```

## 🎯 **Comandos Seguros para Git:**

### **Antes de Commit - Verificación:**
```bash
# 1. Verificar archivos a subir
git status

# 2. Ver diferencias sin datos sensibles
git diff --name-only

# 3. Verificar .gitignore
cat .gitignore | grep -E "(health_check|analysis|local)"
```

### **Commit Seguro:**
```bash
# 1. Solo agregar archivos seguros
git add core/ examples/ README.md

# 2. NO usar 'git add .' (puede incluir archivos sensibles)
# ❌ git add .  # PELIGROSO

# 3. Commit con mensaje descriptivo
git commit -m "Update core SmartCompute algorithms (no local data)"
```

### **Push Seguro:**
```bash
# 1. Revisar commits antes de push
git log --oneline -5

# 2. Verificar ramas
git branch -a

# 3. Push seguro
git push origin main
```

## 🔧 **Script de Verificación de Seguridad:**

```bash
#!/bin/bash
# Verificar que no hay archivos sensibles en staging

echo "🔒 SmartCompute Security Check"
echo "=============================="

# Verificar archivos en staging
STAGED_FILES=$(git diff --cached --name-only)

# Lista de patrones sensibles
SENSITIVE_PATTERNS=(
    "health_check"
    "analysis_report"
    "system_info"
    "local_config"
    "real_data"
    "credentials"
    ".log"
)

FOUND_SENSITIVE=0

for file in $STAGED_FILES; do
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        if [[ $file == *"$pattern"* ]]; then
            echo "❌ ARCHIVO SENSIBLE DETECTADO: $file"
            FOUND_SENSITIVE=1
        fi
    done
done

if [ $FOUND_SENSITIVE -eq 0 ]; then
    echo "✅ No se encontraron archivos sensibles"
    echo "Seguro para commit"
else
    echo "⚠️  ABORTAR COMMIT - Archivos sensibles detectados"
    exit 1
fi
```

## 📋 **Checklist de Seguridad:**

### **Antes de cada Commit:**
- [ ] ✅ `git status` - solo archivos seguros
- [ ] ✅ No hay archivos `.log` o `*_report.*`
- [ ] ✅ No hay configuraciones locales
- [ ] ✅ No hay datos reales del sistema
- [ ] ✅ Mensaje de commit no menciona sistema específico

### **Mensajes de Commit Seguros:**
```bash
# ✅ BUENOS (genéricos)
git commit -m "Improve threat detection algorithms"
git commit -m "Add MCP protocol support"
git commit -m "Update documentation and examples"

# ❌ MALOS (específicos)
git commit -m "Fix bug in gatux server analysis"  # ❌
git commit -m "Add CPU metrics from production"    # ❌
git commit -m "Update config for our network"      # ❌
```

## 🚨 **Si Accidentalmente Subes Datos Sensibles:**

### **1. Remover del Historial:**
```bash
# Remover archivo específico
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch archivo_sensible.log' \
--prune-empty --tag-name-filter cat -- --all

# Forzar push
git push origin --force --all
```

### **2. Invalidar Datos Comprometidos:**
- Cambiar credenciales expuestas
- Rotar claves API
- Actualizar configuraciones

## 💡 **Mejores Prácticas:**

1. **🔄 Siempre usar .gitignore**
2. **📁 Separar código de datos**
3. **🔍 Revisar antes de commit**
4. **🤖 Automatizar verificaciones**
5. **📝 Documentar patrones sensibles**

---
**Recuerda: La seguridad es responsabilidad de todos. Mejor prevenir que lamentar.** 🛡️