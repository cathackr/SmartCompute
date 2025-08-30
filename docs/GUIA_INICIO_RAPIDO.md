# 🚀 SmartCompute Guía de Inicio Rápido

<div align="center">
  <img src="../assets/smartcompute_hmi_logo.png" alt="SmartCompute Logo" width="150">
  
  **Funcionando en 5 minutos** | [🇺🇸 English](QUICK_START_GUIDE.md)
</div>

---

## ⚡ Elige Tu Camino

<table>
<tr>
<td width="33%" align="center">

### 📱 **Móvil/Universal**
**Google Colab**

Perfecto para iPhone, Android, tablets

[👆 Empezar Aquí](#-móvil--universal-google-colab)

</td>
<td width="33%" align="center">

### 💻 **Escritorio/Servidor**
**Instalación Local**

Control total, características empresariales

[👆 Empezar Aquí](#-escritorio--servidor)

</td>
<td width="33%" align="center">

### 🏭 **Industrial**
**Monitoreo de Red**

Protección de infraestructura crítica

[👆 Empezar Aquí](#-industrial--monitoreo-de-red)

</td>
</tr>
</table>

---

## 📱 Móvil / Universal (Google Colab)

**✅ Funciona en: iPhone, Android, tablets, laptops, computadoras**  
**⏱️ Tiempo: 2-3 minutos**  
**💰 Costo: 100% Gratis (Google Colab)**

### Paso 1: Abrir Google Colab
👆 **Haz clic aquí:** [https://colab.research.google.com](https://colab.research.google.com)

### Paso 2: Crear Nuevo Notebook
- Hacer clic en **"+ Nuevo cuaderno"**
- Verás una celda de código vacía

### Paso 3: Copiar y Pegar Este Código

**Celda 1 - Descargar SmartCompute:**
```python
# Descargar y configurar SmartCompute
!git clone https://github.com/cathackr/SmartCompute.git
%cd SmartCompute
!pip install -r requirements-core.txt
```

**Celda 2 - Ejecutar Demo Interactivo:**
```python
# Ejecutar el demo interactivo de ciberseguridad
!python examples/colab_interactive_demo.py
```

### Paso 4: ¡Ver la Magia! ✨

Verás:
- 🚨 **Alertas de amenazas en tiempo real** con códigos de colores
- 📊 **Gráficos de rendimiento animados**
- 🎯 **Seguimiento de puntuación de seguridad**  
- 💻 **Interfaz optimizada para móviles**

### 🎮 Lo Que Estás Viendo

```
🔴 AMENAZA CRÍTICA (Puntuación: 0.87)
   192.168.1.45:2234 → 10.0.0.1:22
   Tipo: Fuerza Bruta SSH | Confianza: 94%

📊 Rendimiento: EXCELENTE (8.5ms promedio)
⚡ Eventos Procesados: 150/150
🛡️ Amenazas Detectadas: 23 (15.3%)
```

### 🔗 Opcional: Dashboard Web
```python
# OPCIONAL: Iniciar servidor web completo
!python main.py --starter &

# Acceder al dashboard (Colab mostrará la URL pública)
from IPython.display import IFrame
IFrame('http://localhost:8000', width=1000, height=600)
```

---

## 💻 Escritorio / Servidor

**✅ Funciona en: Windows, macOS, Linux**  
**⏱️ Tiempo: 3-5 minutos**  
**💰 Costo: Gratis (Starter) / Pago (Empresarial)**

### Verificar Prerequisitos

**Windows:**
```powershell
# Verificar versión de Python (necesario 3.8+)
python --version

# Si no está instalado:
winget install Python.Python.3.11
```

**macOS:**
```bash
# Verificar versión de Python
python3 --version

# Si no está instalado:
brew install python
```

**Linux:**
```bash
# Verificar versión de Python
python3 --version

# Si no está instalado (Ubuntu/Debian):
sudo apt update && sudo apt install python3 python3-pip git
```

### Paso 1: Descargar SmartCompute
```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
```

### Paso 2: Instalar Dependencias
```bash
# Para versión Starter (gratis)
pip install -r requirements-core.txt

# Para versión Empresarial (pago)
pip install -r requirements.txt
```

### Paso 3: Primera Ejecución
```bash
# Demo rápido
python examples/synthetic_demo.py

# Versión Starter completa
python main.py --starter

# Versión Empresarial (si tienes licencia)
python main.py --enterprise --api
```

### Paso 4: Acceder al Dashboard

Abrir el navegador e ir a:
- **Starter:** http://localhost:8000
- **Empresarial:** http://localhost:8000 (con características adicionales)

### 🎯 Lo Que Verás

**Dashboard Starter:**
- Métricas del sistema (CPU, Memoria, Red)
- Detección básica de amenazas
- Alertas simples

**Dashboard Empresarial:**
- Detección avanzada de amenazas con IA
- Reportes personalizados
- Acceso a APIs
- Soporte multi-usuario

---

## 🏭 Industrial / Monitoreo de Red

**✅ Funciona en: Redes industriales, PLCs, sistemas SCADA**  
**⏱️ Tiempo: 5-10 minutos**  
**💰 Costo: Licencia paga requerida**

### Prerequisitos

- **Acceso a red**: Requiere privilegios de monitoreo de red
- **Protocolos**: Modbus, Profinet, OPC UA, EtherNet/IP
- **Permisos**: acceso sudo/administrator

### Paso 1: Descargar Edición Industrial
```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute/smartcompute_industrial
```

### Paso 2: Instalar Dependencias Industriales
```bash
# Requiere privilegios elevados para acceso a red
sudo pip install -r requirements_industrial.txt
```

### Paso 3: Configurar Monitoreo de Red
```bash
# Editar configuración
nano industrial_config.yaml

# Configuración de ejemplo:
network_monitoring:
  target_networks:
    - "192.168.1.0/24"    # Tu red industrial
    - "10.0.0.0/16"       # Red extendida
  protocols:
    modbus: true
    profinet: true
    opc_ua: true
```

### Paso 4: Iniciar Monitoreo Industrial
```bash
# Iniciar con inteligencia de red
sudo ./start_network_intelligence.sh

# O inicio manual
sudo python network_api.py
```

### Paso 5: Acceder al Dashboard Industrial

Abrir: **http://127.0.0.1:8002**

### 🎯 Características Industriales

- **🏭 Análisis de Protocolos**: Monitoreo en tiempo real Modbus, Profinet
- **🗺️ Topología de Red**: Descubrimiento automático de dispositivos
- **⚠️ Detección de Conflictos**: Conflictos IP, alertas de alta latencia
- **📊 Métricas de Rendimiento**: KPIs industriales y SLAs
- **🛡️ Monitoreo de Seguridad**: Detección de amenazas específicas OT

---

## 🛠️ Solución de Problemas

### Problemas Comunes

**❌ "Comando no encontrado" / "python no reconocido"**
```bash
# Asegurar que Python esté instalado y en PATH
python --version  # o python3 --version

# Windows: Agregar Python a PATH en Variables de Entorno del Sistema
# macOS/Linux: Agregar a ~/.bashrc o ~/.zshrc
export PATH="/usr/local/bin/python3:$PATH"
```

**❌ "Permiso denegado" / "Acceso denegado"**
```bash
# Instalar como usuario (recomendado)
pip install --user -r requirements-core.txt

# O usar entorno virtual
python -m venv smartcompute_env
source smartcompute_env/bin/activate  # Windows: smartcompute_env\Scripts\activate
pip install -r requirements-core.txt
```

**❌ "Puerto 8000 ya en uso"**
```bash
# Verificar qué está usando el puerto
netstat -tulpn | grep 8000

# Matar el proceso o usar puerto diferente
python main.py --starter --port 8001
```

**❌ Google Colab "Runtime desconectado"**
- Esto es normal - Colab se desconecta después de inactividad
- Simplemente re-ejecutar las celdas para reiniciar
- Tu trabajo se guarda automáticamente en Google Drive

### Consejos de Rendimiento

**🚀 Acelerar instalación:**
```bash
# Usar índice de paquetes más rápido
pip install -r requirements-core.txt --index-url https://pypi.org/simple/

# Instalar en paralelo (Linux/macOS)
pip install -r requirements-core.txt --use-feature=fast-deps
```

**📊 Monitorear uso de recursos:**
```bash
# Verificar uso de CPU/memoria
htop  # Linux/macOS
taskmgr  # Windows

# Diagnósticos integrados de SmartCompute
python -m smartcompute.diagnostics
```

---

## 🎯 Próximos Pasos

### Después de la Configuración Básica

1. **📖 Leer la documentación**: [Documentación Técnica](DOCUMENTACION_TECNICA.md)
2. **🏢 Actualizar a Empresarial**: [Guía Empresarial](GUIA_EMPRESARIAL.md)
3. **🔗 Integrar con tus herramientas**: APIs, SIEM, plataformas en la nube
4. **📞 Obtener soporte**: Issues, soporte profesional, consultoría

### Configuración Avanzada

**Monitoreo Personalizado:**
```python
# Recolección de métricas personalizadas
from smartcompute import SmartComputeEngine

engine = SmartComputeEngine()
engine.add_metric('cpu_personalizado', source='tu_app')
engine.start_monitoring(interval=10)
```

**Integración API:**
```python
# Conectar a sistemas externos
import requests

# Enviar alertas a Slack
def enviar_alerta(alerta):
    requests.post('https://hooks.slack.com/tu-webhook', 
                  json={'text': f'🚨 Alerta SmartCompute: {alerta}'})

engine.on_alert(enviar_alerta)
```

### Despliegue en Producción

- **🐳 Docker**: `docker-compose up -d`
- **☁️ Nube**: AWS, Azure, Google Cloud
- **🎛️ Kubernetes**: Orquestación de nivel empresarial
- **🏢 On-premises**: Configuración de alta disponibilidad

---

## 💡 Consejos Rápidos

### Para Principiantes
- Empieza con Google Colab - es la forma más fácil
- Ejecuta primero el demo interactivo para ver qué puede hacer SmartCompute
- No te preocupes por la configuración - los valores por defecto funcionan genial

### Para Profesionales de TI  
- Usa la instalación de escritorio para producción
- Habilita el acceso API para integraciones
- Considera la edición Empresarial para entornos multi-usuario

### Para Ingenieros Industriales
- La edición industrial requiere privilegios de red
- Prueba primero en una red de desarrollo
- Configura cuidadosamente el monitoreo específico de protocolos

---

<div align="center">

### 🎉 ¡Felicitaciones!

**Ya tienes SmartCompute funcionando y protegiendo tu infraestructura.**

**¿Preguntas?** [📧 Contactar Soporte](mailto:ggwre04p0@mozmail.com) | [💬 Comunidad](https://github.com/cathackr/SmartCompute/discussions)

---

**⭐ ¿Te resultó útil?** [Danos una estrella en GitHub](https://github.com/cathackr/SmartCompute) 

</div>