#!/bin/bash
# SmartCompute - System Health Check Script
# Ejecutar diariamente para monitoreo proactivo

echo "🏥 SmartCompute System Health Check - $(date)"
echo "=" * 50

# CPU y Memoria
echo "📊 RECURSOS DEL SISTEMA"
echo "CPU: $(cat /proc/loadavg | awk '{print $1}')"
echo "Memoria: $(free | grep Mem | awk '{printf("%.1f%% usada\n", $3/$2 * 100.0)}')"
echo "Disco: $(df -h / | awk 'NR==2 {print $5 " usado"}')"

# Procesos con mayor consumo
echo -e "\n🔥 TOP 5 PROCESOS CPU:"
ps aux --sort=-%cpu | head -6

echo -e "\n🧠 TOP 5 PROCESOS MEMORIA:"
ps aux --sort=-%mem | head -6

# Conexiones de red
echo -e "\n🌐 CONEXIONES DE RED:"
netstat -tuln | grep LISTEN | wc -l | xargs echo "Puertos escuchando:"

# Usuarios conectados
echo -e "\n👥 USUARIOS ACTIVOS:"
who

# Servicios críticos
echo -e "\n⚙️ SERVICIOS CRÍTICOS:"
for service in ssh cron systemd-resolved; do
    if systemctl is-active --quiet $service; then
        echo "✅ $service: ACTIVO"
    else
        echo "❌ $service: INACTIVO"
    fi
done

# Actualizaciones pendientes
echo -e "\n📦 ACTUALIZACIONES:"
apt list --upgradable 2>/dev/null | wc -l | xargs echo "Paquetes para actualizar:"

# Espacio en disco crítico
echo -e "\n💾 ESPACIO EN DISCO:"
df -h | awk '$5 > 80 {print "⚠️ " $6 ": " $5 " usado"}'

echo -e "\n✅ Health check completado - $(date)"