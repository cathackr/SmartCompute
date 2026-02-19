# 🚀 SmartCompute - Guía de Inicio Rápido

## ⚡ Instalación Express (30 segundos)

### Windows - Un Click
1. **Descargar:** [SmartCompute_Express_Windows.bat](../download/SmartCompute_Express_Windows.bat)
2. **Ejecutar:** Doble click en el archivo
3. **¡Listo!** Se abre automáticamente en tu navegador

### Linux/macOS - Terminal
```bash
# Descargar
curl -O https://github.com/cathackr/SmartCompute/raw/main/download/SmartCompute_Express_Linux.sh

# Ejecutar
chmod +x SmartCompute_Express_Linux.sh
./SmartCompute_Express_Linux.sh

# Dashboard disponible en: http://localhost:8002
```

## 🎯 Primer Análisis

Una vez instalado, ejecuta tu primer análisis:

### CLI Simple
```bash
# Análisis completo de infraestructura
smartcompute scan infrastructure

# Análisis de red OSI completo
smartcompute scan network --osi-all

# Solo capas específicas
smartcompute scan network --layers 3,4

# APIs y aplicaciones
smartcompute scan apis

# Sensores IoT
smartcompute scan iot --sensors all
```

### Opciones de Salida
```bash
# Solo terminal
smartcompute scan infrastructure --output cli

# Solo dashboard HTML
smartcompute scan infrastructure --output html

# Ambos (predeterminado)
smartcompute scan infrastructure --output both
```

## 📊 Interpretando Resultados

### Dashboard Principal
El dashboard muestra 4 secciones clave:

1. **System Status:** Estado general del sistema
2. **OSI Analysis:** Actividad por capa de red
3. **Resource Usage:** CPU, RAM, Disco, Red
4. **Real-time Monitoring:** Gráficos en tiempo real

### Códigos de Color
- 🟢 **Verde:** Normal (0-60%)
- 🟡 **Amarillo:** Advertencia (60-80%)
- 🔴 **Rojo:** Crítico (80-100%)

### Métricas Clave
```
CPU Usage: 13.2%     ← Uso de procesador
RAM Usage: 46.6%     ← Memoria utilizada
Disk Usage: 32.4%    ← Espacio en disco
Network: 85%         ← Utilización de red
```

## 🔍 Análisis OSI Detallado

### ¿Qué es el Modelo OSI?
El modelo OSI divide la comunicación de red en 7 capas:

| Capa | Nombre | Función | SmartCompute Analiza |
|------|--------|---------|---------------------|
| **7** | Application | HTTP, HTTPS, SSH, DNS | Protocolos y aplicaciones |
| **6** | Presentation | Cifrado, compresión | Formatos de datos |
| **5** | Session | Sesiones activas | Persistencia conexiones |
| **4** | Transport | TCP, UDP | Puertos y servicios |
| **3** | Network | IP, ICMP | Enrutamiento y IPs |
| **2** | Data Link | Ethernet, ARP | MACs y switches |
| **1** | Physical | Cables, interfaces | Hardware de red |

### Interpretación de Resultados
```
LAYER 7 - APPLICATION: 89%    ← Alto tráfico web/email
LAYER 4 - TRANSPORT:   92%    ← Muchas conexiones TCP
LAYER 1 - PHYSICAL:    97%    ← Red física funcionando bien
```

## 🏢 Upgrading a Enterprise

### ¿Cuándo necesitas Enterprise?
- Más de 3 análisis por día
- Integración con SIEM corporativo
- Exportación a CrowdStrike/Sentinel
- Recomendaciones AI
- Soporte empresarial

### Proceso de Compra
1. **Escanear QR** del README
2. **Completar formulario** con datos de GitHub
3. **Pago seguro** vía MercadoPago/Bitso
4. **Acceso automático** al repo privado
5. **Instalación Enterprise** en minutos

## 🏭 Upgrading a Industrial

### ¿Cuándo necesitas Industrial?
- Entornos industriales críticos
- Protocolos Modbus/Profinet/OPC UA
- Cumplimiento ISA/IEC 62443
- Monitoreo SCADA/PLC
- Agentes ilimitados

### Funciones Industriales
```bash
# Escaneo de protocolos industriales
smartcompute scan industrial --protocols modbus,profinet

# Monitoreo de PLCs
smartcompute monitor plc --ip-range 192.168.1.0/24

# Análisis de seguridad industrial
smartcompute scan security --industrial
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Duración predeterminada
export SMARTCOMPUTE_DURATION=60

# Nivel de logging
export SMARTCOMPUTE_LOG_LEVEL=INFO

# Puerto del dashboard
export SMARTCOMPUTE_PORT=8002

# Licencia (Enterprise/Industrial)
export SMARTCOMPUTE_LICENSE_KEY="your-key"
```

### Configuración Manual
```bash
# Editar configuración
nano ~/.smartcompute/config.json

{
  "analysis": {
    "default_duration": 30,
    "auto_open_browser": true,
    "save_results": true
  },
  "dashboard": {
    "port": 8002,
    "theme": "hmi",
    "update_interval": 5
  },
  "security": {
    "enable_encryption": true,
    "log_sensitive_data": false
  }
}
```

## 📋 Solución de Problemas

### Windows - Errores Comunes

**"Python no encontrado"**
```cmd
# El installer debería instalar Python automáticamente
# Si falla, descarga desde: https://python.org
# O ejecuta: SmartCompute_Express_PS.bat (PowerShell)
```

**"No se puede ejecutar scripts"**
```powershell
# Abrir PowerShell como Administrador
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# Luego ejecutar el .bat
```

### Linux/macOS - Errores Comunes

**"Permission denied"**
```bash
# Asegurar permisos de ejecución
chmod +x SmartCompute_Express_Linux.sh
sudo ./SmartCompute_Express_Linux.sh
```

**"Command not found: smartcompute"**
```bash
# Verificar instalación
which smartcompute

# Si no existe, reinstalar
./SmartCompute_Express_Linux.sh
source ~/.bashrc
```

### Problemas de Red

**"No se detectan interfaces"**
```bash
# Ejecutar con privilegios admin
sudo smartcompute scan network

# Verificar interfaces manualmente
ip addr show  # Linux
ifconfig      # macOS
ipconfig /all # Windows
```

**"Dashboard no se abre"**
```bash
# Verificar puerto
netstat -tulpn | grep :8002

# Cambiar puerto si está ocupado
smartcompute scan infrastructure --port 8003

# Abrir manualmente
firefox http://localhost:8002
```

## 🎯 Casos de Uso Comunes

### 1. Monitoreo de Home Office
```bash
# Análisis básico cada mañana
smartcompute scan network --duration 30

# Verificar aplicaciones que consumen ancho de banda
smartcompute scan apis --layer 7
```

### 2. Auditoría de Red Corporativa
```bash
# Análisis completo de infraestructura
smartcompute scan infrastructure --output html

# Exportar resultados para compliance
smartcompute export --format pdf --output security_audit.pdf
```

### 3. Troubleshooting de Conectividad
```bash
# Enfoque en capas L3-L4 (red y transporte)
smartcompute scan network --layers 3,4 --duration 60

# Análisis específico de puertos
smartcompute scan network --port 443 --protocols https
```

### 4. Monitoreo IoT
```bash
# Escaneo de dispositivos IoT
smartcompute scan iot --sensors all

# Análisis de protocolos específicos
smartcompute scan iot --protocols mqtt,coap
```

## 📚 Próximos Pasos

### Aprende Más
1. **[Documentación Técnica](TECHNICAL_DOCUMENTATION.md)** - Detalles avanzados
2. **[LinkedIn](https://www.linkedin.com/in/martín-iribarne-swtf)** - Conecta con el desarrollador
3. **[GitHub Issues](https://github.com/cathackr/SmartCompute/issues)** - Reporta bugs

### Únete a la Comunidad
- ⭐ **Star** el repositorio en GitHub
- 🐛 **Reporta bugs** via Issues
- 💡 **Sugiere features** via Discussions
- 📧 **Contacto directo:** ggwre04p0@mozmail.com

### Contribuye
```bash
# Fork del repositorio
git clone https://github.com/tu-usuario/SmartCompute.git

# Crear branch para feature
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commit
git commit -m "feat: nueva funcionalidad"

# Push y crear Pull Request
git push origin feature/nueva-funcionalidad
```

---

## 🆘 Soporte

### Express (Gratuito)
- 📚 **Documentación:** Esta guía + README
- 🐛 **Issues:** GitHub Issues únicamente
- ⏱️ **Respuesta:** Best effort (community)

### Enterprise ($200-750/año)
- 📧 **Email:** Soporte business hours
- 🎯 **SLA:** 99.5% uptime garantizado
- ⏱️ **Respuesta:** 4h crítico, 24h normal

### Industrial ($5,000/3 años)
- 📞 **24/7:** Soporte prioritario
- 🎯 **SLA:** 99.9% uptime garantizado
- ⏱️ **Respuesta:** 1h crítico, 4h normal
- 👨‍💼 **TAM:** Technical Account Manager dedicado

---

*¡Bienvenido a SmartCompute! 🚀*

*© 2024 SmartCompute by Martín Iribarne - Technology Architect*