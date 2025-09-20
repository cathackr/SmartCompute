#!/bin/bash
# SmartCompute Industrial - Script de Instalación
# Desarrollado por: ggwre04p0@mozmail.com

echo "🏭 ======== SMARTCOMPUTE INDUSTRIAL - INSTALACIÓN ========"
echo "📧 Desarrollado por: ggwre04p0@mozmail.com"
echo "🔗 LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/"
echo

# Verificar permisos de administrador
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script debe ejecutarse como administrador (sudo)"
   exit 1
fi

echo "🔧 Instalando dependencias del sistema..."

# Actualizar repositorios
apt-get update

# Instalar Python y dependencias
apt-get install -y python3 python3-pip python3-venv nodejs npm

# Instalar dependencias Python específicas
apt-get install -y python3-pil python3-opencv

echo "📦 Creando entorno virtual Python..."
python3 -m venv /opt/smartcompute/venv
source /opt/smartcompute/venv/bin/activate

echo "📦 Instalando paquetes Python..."
pip install pillow opencv-python qrcode pyotp pyjwt cryptography

echo "📦 Instalando paquetes Node.js..."
npm install

echo "📁 Configurando directorios..."
mkdir -p /opt/smartcompute/{data,logs,config,reports}
mkdir -p /var/log/smartcompute
mkdir -p /etc/smartcompute

# Copiar archivos de configuración
cp config/* /etc/smartcompute/

# Configurar permisos
chown -R smartcompute:smartcompute /opt/smartcompute
chmod +x *.py
chmod +x *.js

echo "🔐 Configurando servicio systemd..."
cat > /etc/systemd/system/smartcompute.service << EOF
[Unit]
Description=SmartCompute Industrial Service
After=network.target

[Service]
Type=simple
User=smartcompute
WorkingDirectory=/opt/smartcompute
ExecStart=/opt/smartcompute/venv/bin/python smartcompute_integrated_workflow.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable smartcompute

echo "✅ ======== INSTALACIÓN COMPLETADA ========"
echo "🚀 Para iniciar el servicio:"
echo "   systemctl start smartcompute"
echo
echo "📊 Para ver el estado:"
echo "   systemctl status smartcompute"
echo
echo "📋 Para ver logs:"
echo "   journalctl -u smartcompute -f"
echo
echo "🌐 Dashboard disponible en: http://localhost:3000"
echo
echo "📞 Soporte técnico:"
echo "📧 Email: ggwre04p0@mozmail.com"
echo "🔗 LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/"
