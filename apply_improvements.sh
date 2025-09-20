#!/bin/bash
# SmartCompute - Auto-Apply System Improvements
# Aplica mejoras recomendadas de seguridad y performance

set -euo pipefail
IFS=$'\n\t'

# Función de logging seguro
log_action() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "/var/log/smartcompute/improvements.log"
}

# Verificar permisos antes de ejecutar
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        echo "❌ Error: No ejecutar como root directamente"
        echo "Use: ./apply_improvements.sh (el script pedirá sudo cuando sea necesario)"
        exit 1
    fi

    if ! sudo -n true 2>/dev/null; then
        echo "🔑 Este script requiere permisos sudo para algunas operaciones."
        echo "Se solicitará su password cuando sea necesario."
    fi
}

# Verificar integridad del sistema antes de cambios
verify_system_integrity() {
    log_action "Verificando integridad del sistema..."

    # Verificar espacio en disco
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        echo "⚠️  Advertencia: Espacio en disco bajo ($disk_usage%)"
        read -p "¿Continuar de todas formas? (y/N): " continue_anyway
        if [[ $continue_anyway != [yY] ]]; then
            exit 1
        fi
    fi

    # Verificar que no hay actualizaciones críticas pendientes
    if command -v apt &> /dev/null; then
        if sudo apt list --upgradable 2>/dev/null | grep -i security > /dev/null; then
            log_action "Se detectaron actualizaciones de seguridad pendientes"
        fi
    fi
}

echo "🚀 SmartCompute System Improvements"
echo "===================================="
echo "ADVERTENCIA: Este script realizará cambios en tu sistema."
echo "Recomendamos hacer un backup antes de continuar."
echo ""

# Verificaciones de seguridad
check_permissions
verify_system_integrity

read -p "¿Continuar con las mejoras? (y/N): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Operación cancelada."
    exit 0
fi

# Crear directorio de logs seguro
sudo mkdir -p /var/log/smartcompute
sudo chown root:root /var/log/smartcompute
sudo chmod 755 /var/log/smartcompute

echo ""
echo "🔄 Iniciando mejoras del sistema..."

# 1. Actualización del sistema
log_action "Actualizando sistema..."
echo "📦 Actualizando sistema..."
if sudo apt update && sudo apt upgrade -y; then
    log_action "Sistema actualizado exitosamente"
else
    log_action "ERROR: Fallo en actualización del sistema"
    exit 1
fi

# 2. Limpieza básica
echo "🧹 Limpiando sistema..."
sudo apt autoremove -y
sudo apt autoclean
sudo journalctl --vacuum-time=7d

# 3. Seguridad básica
echo "🔒 Configurando seguridad básica..."

# Instalar fail2ban
if ! command -v fail2ban-client &> /dev/null; then
    sudo apt install fail2ban -y
    sudo systemctl enable fail2ban
    sudo systemctl start fail2ban
    echo "✅ Fail2ban instalado y configurado"
fi

# Configurar firewall básico
if ! sudo ufw status | grep -q "Status: active"; then
    echo "🔥 Configurando firewall..."
    sudo ufw --force enable
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    echo "✅ Firewall configurado"
fi

# 4. Herramientas de monitoreo
echo "📊 Instalando herramientas de monitoreo..."
sudo apt install htop iotop nethogs logwatch -y

# 5. Optimizaciones de rendimiento
echo "⚡ Aplicando optimizaciones..."

# Optimizar swappiness
if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
fi

# Aplicar cambios sysctl
sudo sysctl -p

# 6. Configurar monitoreo automático
echo "🤖 Configurando monitoreo automático..."

# Crear directorio de logs si no existe
sudo mkdir -p /var/log/smartcompute

# Agregar cron job para health check
(crontab -l 2>/dev/null; echo "0 8 * * * /home/gatux/smartcompute/system_health_check.sh >> /var/log/smartcompute/health.log 2>&1") | crontab -

echo ""
echo "✅ MEJORAS APLICADAS EXITOSAMENTE"
echo "================================="
echo ""
echo "📋 Resumen de cambios:"
echo "  ✅ Sistema actualizado"
echo "  ✅ Limpieza realizada"
echo "  ✅ Fail2ban instalado"
echo "  ✅ Firewall configurado"
echo "  ✅ Herramientas de monitoreo instaladas"
echo "  ✅ Optimizaciones de rendimiento aplicadas"
echo "  ✅ Monitoreo automático configurado"
echo ""
echo "📄 Logs de monitoreo: /var/log/smartcompute/"
echo "🔄 Health check diario: 8:00 AM"
echo ""
echo "🎯 PRÓXIMOS PASOS RECOMENDADOS:"
echo "  1. Revisar configuración SSH en /etc/ssh/sshd_config"
echo "  2. Configurar backups automáticos"
echo "  3. Instalar ClamAV para detección de malware"
echo "  4. Considerar certificados SSL si tienes servicios web"
echo ""
echo "🚀 ¡Tu sistema ahora es más seguro y eficiente!"