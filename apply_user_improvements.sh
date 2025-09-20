#!/bin/bash
# SmartCompute - User-Level System Improvements
# Aplica mejoras que no requieren permisos administrativos

echo "🚀 SmartCompute User-Level Improvements"
echo "======================================="
echo "Aplicando mejoras de usuario (sin sudo requerido)"
echo ""

# 1. Verificar estado actual del sistema
echo "📊 ESTADO ACTUAL DEL SISTEMA:"
echo "CPU Load: $(cat /proc/loadavg | awk '{print $1}')"
echo "Memoria: $(free | grep Mem | awk '{printf("%.1f%% usada\n", $3/$2 * 100.0)}')"
echo "Disco: $(df -h / | awk 'NR==2 {print $5 " usado"}')"
echo "Procesos: $(ps aux | wc -l)"
echo "Conexiones: $(netstat -tuln 2>/dev/null | grep LISTEN | wc -l)"
echo ""

# 2. Limpiar archivos temporales de usuario
echo "🧹 Limpiando archivos temporales de usuario..."
rm -rf ~/.cache/thumbnails/*
rm -rf ~/.local/share/Trash/files/*
find ~/.cache -type f -atime +7 -delete 2>/dev/null || true
echo "✅ Limpieza de usuario completada"

# 3. Configurar aliases útiles
echo "⚙️ Configurando aliases útiles..."
if ! grep -q "# SmartCompute aliases" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# SmartCompute aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias sysinfo='echo "=== SYSTEM INFO ==="; echo "CPU: $(cat /proc/loadavg | awk "{print \$1}")"; echo "MEM: $(free | grep Mem | awk "{printf(\"%.1f%%\n\", \$3/\$2 * 100.0)}")"; echo "DISK: $(df -h / | awk "NR==2 {print \$5}")"; echo "PROCS: $(ps aux | wc -l)"; echo "CONNS: $(netstat -tuln 2>/dev/null | grep LISTEN | wc -l)"'
alias netcheck='netstat -tuln | grep LISTEN'
alias proccheck='ps aux --sort=-%cpu | head -10'
alias memcheck='ps aux --sort=-%mem | head -10'
alias diskcheck='df -h'
EOF
    echo "✅ Aliases configurados en ~/.bashrc"
fi

# 4. Configurar cron job para health check (sin sudo)
echo "🤖 Configurando monitoreo automático de usuario..."
(crontab -l 2>/dev/null | grep -v "system_health_check.sh"; echo "0 8 * * * /home/gatux/smartcompute/system_health_check.sh >> /tmp/health_check_user.log 2>&1") | crontab -
echo "✅ Health check diario configurado (8:00 AM)"

# 5. Optimizar configuración de usuario
echo "⚡ Aplicando optimizaciones de usuario..."

# Aumentar límite de archivos abiertos para el usuario
if ! grep -q "ulimit -n" ~/.bashrc; then
    echo "ulimit -n 4096" >> ~/.bashrc
    echo "✅ Límite de archivos abiertos aumentado"
fi

# Configurar historial bash más útil
if ! grep -q "HISTSIZE=10000" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# SmartCompute bash history optimization
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups
EOF
    echo "✅ Historial bash optimizado"
fi

# 6. Crear script de monitoreo personal
echo "📊 Creando script de monitoreo personal..."
cat > ~/smartcompute_monitor.sh << 'EOF'
#!/bin/bash
# SmartCompute Personal Monitor

clear
echo "🖥️  SmartCompute Personal System Monitor"
echo "======================================="
echo "Fecha: $(date)"
echo ""

echo "📊 RECURSOS:"
echo "CPU Load: $(cat /proc/loadavg | awk '{print $1, $2, $3}')"
echo "Memoria: $(free -h | grep '^Mem:' | awk '{print $3 "/" $2 " (" int($3/$2 * 100) "%)"}')"
echo "Disco /: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
echo ""

echo "🔥 TOP 5 PROCESOS CPU:"
ps aux --sort=-%cpu --no-headers | head -5 | awk '{printf("%-20s %5s%% %s\n", $11, $3, $1)}'
echo ""

echo "🧠 TOP 5 PROCESOS MEMORIA:"
ps aux --sort=-%mem --no-headers | head -5 | awk '{printf("%-20s %5s%% %s\n", $11, $4, $1)}'
echo ""

echo "🌐 CONEXIONES DE RED:"
netstat -tuln 2>/dev/null | grep LISTEN | wc -l | xargs echo "Puertos escuchando:"
netstat -tun 2>/dev/null | grep ESTABLISHED | wc -l | xargs echo "Conexiones establecidas:"
echo ""

echo "💾 ESPACIO EN DISCO:"
df -h | awk 'NR>1 && $5+0 > 80 {print "⚠️  " $6 ": " $5 " usado"}'
df -h | awk 'NR>1 && $5+0 <= 80 {print "✅ " $6 ": " $5 " usado"}' | head -3
echo ""

echo "📈 UPTIME:"
uptime
echo ""
echo "Presiona Enter para continuar..."
read
EOF

chmod +x ~/smartcompute_monitor.sh
echo "✅ Monitor personal creado: ~/smartcompute_monitor.sh"

# 7. Crear script de limpieza rápida
echo "🧹 Creando script de limpieza rápida..."
cat > ~/smartcompute_cleanup.sh << 'EOF'
#!/bin/bash
# SmartCompute Quick Cleanup

echo "🧹 SmartCompute Quick Cleanup"
echo "============================="

echo "Limpiando cache de usuario..."
rm -rf ~/.cache/thumbnails/* 2>/dev/null
find ~/.cache -name "*.log" -delete 2>/dev/null
find ~/.cache -type f -atime +3 -delete 2>/dev/null

echo "Limpiando archivos temporales..."
find /tmp -user $(whoami) -type f -atime +1 -delete 2>/dev/null || true

echo "Limpiando historial de comandos duplicados..."
history -w
awk '!seen[$0]++' ~/.bash_history > /tmp/bash_history_clean
mv /tmp/bash_history_clean ~/.bash_history

echo "✅ Limpieza completada!"
EOF

chmod +x ~/smartcompute_cleanup.sh
echo "✅ Script de limpieza creado: ~/smartcompute_cleanup.sh"

# 8. Verificar mejoras aplicadas
echo ""
echo "🔍 VERIFICANDO MEJORAS APLICADAS:"

# Verificar cron job
if crontab -l 2>/dev/null | grep -q "system_health_check.sh"; then
    echo "✅ Monitoreo automático: CONFIGURADO"
else
    echo "⚠️ Monitoreo automático: NO CONFIGURADO"
fi

# Verificar aliases
if grep -q "SmartCompute aliases" ~/.bashrc; then
    echo "✅ Aliases útiles: CONFIGURADOS"
else
    echo "⚠️ Aliases útiles: NO CONFIGURADOS"
fi

# Verificar scripts
if [ -x ~/smartcompute_monitor.sh ]; then
    echo "✅ Monitor personal: CREADO"
else
    echo "⚠️ Monitor personal: NO CREADO"
fi

if [ -x ~/smartcompute_cleanup.sh ]; then
    echo "✅ Script limpieza: CREADO"
else
    echo "⚠️ Script limpieza: NO CREADO"
fi

echo ""
echo "✅ MEJORAS DE USUARIO COMPLETADAS"
echo "================================="
echo ""
echo "📋 RESUMEN DE MEJORAS APLICADAS:"
echo "  ✅ Limpieza de archivos temporales"
echo "  ✅ Aliases útiles configurados"
echo "  ✅ Monitoreo automático diario (8:00 AM)"
echo "  ✅ Optimizaciones de bash y límites"
echo "  ✅ Monitor personal: ~/smartcompute_monitor.sh"
echo "  ✅ Limpieza rápida: ~/smartcompute_cleanup.sh"
echo ""
echo "🚀 COMANDOS ÚTILES AGREGADOS:"
echo "  sysinfo     - Ver información del sistema"
echo "  netcheck    - Ver puertos abiertos"
echo "  proccheck   - Ver procesos que más CPU usan"
echo "  memcheck    - Ver procesos que más memoria usan"
echo ""
echo "📄 LOGS DE MONITOREO:"
echo "  Health check: /tmp/health_check_user.log"
echo ""
echo "🔄 PARA ACTIVAR LOS ALIAS AHORA:"
echo "  source ~/.bashrc"
echo ""
echo "🎯 PRÓXIMOS PASOS OPCIONALES (requieren sudo):"
echo "  1. Instalar fail2ban para seguridad"
echo "  2. Configurar firewall básico"
echo "  3. Instalar herramientas de monitoreo avanzado"
echo ""
echo "🎉 ¡Tu entorno de usuario está optimizado!"
EOF