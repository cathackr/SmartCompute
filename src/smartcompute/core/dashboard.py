#!/usr/bin/env python3
"""
SmartCompute Dashboard Template - Standard Format
Plantilla estandarizada para todos los dashboards SmartCompute

Este template mantiene el formato visual consistente pero permite
cambiar completamente los datos y gráficos según el análisis requerido.

Ejemplos de uso:
- Análisis OSI completo (7 capas)
- Análisis específico L3-L4 (Red + Transporte)
- Análisis L7 (APIs, puertos, lenguajes)
- Monitoreo IoT (sensores, temperatura, humedad)
- Análisis de seguridad (amenazas, vulnerabilidades)
- Performance de aplicaciones
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

# Configuración estándar SmartCompute
plt.style.use('dark_background')
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 15,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 11
})

class SmartComputeDashboard:
    """Template base para dashboards SmartCompute estandarizados"""

    def __init__(self, title="SMARTCOMPUTE SYSTEM MONITOR", status="ONLINE"):
        self.title = title
        self.status = status
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Colores estándar SmartCompute
        self.colors = {
            'background': '#0c1420',
            'panel_bg': '#1a2332',
            'primary': '#00ff88',
            'secondary': '#ffd700',
            'danger': '#ff6b6b',
            'warning': '#ffa502',
            'info': '#48dbfb',
            'grid': '#444444',
            'text': 'white'
        }

    def create_base_layout(self):
        """Crear layout base estandarizado"""

        # Figura con tamaño estándar
        self.fig = plt.figure(figsize=(24, 18))
        self.fig.patch.set_facecolor(self.colors['background'])

        # Header estándar - System Status
        self.fig.text(0.02, 0.97, f'SYSTEM STATUS: {self.status}',
                     fontsize=14, color=self.colors['primary'], fontweight='bold')
        self.fig.text(0.02, 0.94, f'TIMESTAMP: {self.timestamp}',
                     fontsize=12, color=self.colors['secondary'], fontweight='bold')
        self.fig.text(0.02, 0.91, 'ANALYSIS DURATION: 30s',
                     fontsize=12, color=self.colors['secondary'], fontweight='bold')

        # Título principal estándar
        self.fig.suptitle(self.title, fontsize=32, fontweight='bold',
                         color=self.colors['text'], y=0.96)

        # Layout estándar: 4 filas, proporciones fijas
        self.gs = self.fig.add_gridspec(4, 4,
                                       height_ratios=[2, 1.5, 1.5, 0.9],
                                       width_ratios=[1.5, 1, 1, 1],
                                       hspace=0.9, wspace=0.4,
                                       top=0.88, bottom=0.12,
                                       left=0.05, right=0.95)
        return self.gs

    def create_main_analysis_panel(self, gs, data, title, xlabel):
        """Panel principal de análisis (fila superior izquierda)"""
        ax = self.fig.add_subplot(gs[0, :3])

        # Configuración estándar del panel principal
        bars = ax.barh(data['labels'], data['values'],
                      color=data['colors'], height=0.7,
                      edgecolor='white', linewidth=2)

        # Posicionamiento inteligente de valores
        for i, (bar, value) in enumerate(zip(bars, data['values'])):
            if value > 80:  # Valor alto - dentro
                ax.text(value - 5, i, f'{value}%', va='center', ha='right',
                       color='white', fontweight='bold', fontsize=16)
            else:  # Valor bajo - fuera
                ax.text(value + 2, i, f'{value}%', va='center', ha='left',
                       color='white', fontweight='bold', fontsize=16)

        ax.set_title(title, fontsize=20, fontweight='bold',
                    color=self.colors['primary'], pad=40)
        ax.set_xlabel(xlabel, fontweight='bold', color='white', fontsize=14)
        ax.set_xlim(0, 105)
        ax.grid(axis='x', alpha=0.3, color=self.colors['grid'])
        ax.tick_params(colors='white', labelsize=11)
        ax.set_facecolor(self.colors['panel_bg'])

        return ax

    def create_metrics_panel(self, gs, data, title):
        """Panel de métricas del sistema (fila superior derecha)"""
        ax = self.fig.add_subplot(gs[0, 3])

        bars = ax.bar(range(len(data['labels'])), data['values'],
                     color=data['colors'], edgecolor='white',
                     linewidth=2, width=0.6)

        ax.set_xticks(range(len(data['labels'])))
        ax.set_xticklabels([label.split('\n')[0] for label in data['labels']])

        # Valores encima
        for i, (bar, value, label) in enumerate(zip(bars, data['values'], data['labels'])):
            height = bar.get_height()
            percentage = label.split('\n')[1] if '\n' in label else f'{value}%'
            ax.text(i, height + 2, percentage, ha='center', va='bottom',
                   color='white', fontweight='bold', fontsize=12)

        ax.set_title(title, fontsize=16, fontweight='bold',
                    color=self.colors['primary'], pad=30)
        ax.set_ylabel('USAGE (%)', fontweight='bold', color='white')
        ax.set_ylim(0, 100)
        ax.tick_params(colors='white')
        ax.grid(axis='y', alpha=0.3, color=self.colors['grid'])
        ax.set_facecolor(self.colors['panel_bg'])

        return ax

    def create_bar_panel(self, gs, position, data, title, ylabel, intelligent_labels=True):
        """Panel de barras genérico"""
        ax = self.fig.add_subplot(gs[position[0], position[1]])

        bars = ax.bar(data['labels'], data['values'], color=data['colors'],
                     edgecolor='white', linewidth=2, width=0.6)

        # Posicionamiento inteligente opcional
        if intelligent_labels:
            max_val = max(data['values']) if data['values'] else 1
            for bar, value in zip(bars, data['values']):
                height = bar.get_height()
                if height > max_val * 0.8:  # Alto - dentro
                    ax.text(bar.get_x() + bar.get_width()/2., height - max_val*0.05,
                           f'{value}', ha='center', va='top',
                           color='white', fontweight='bold', fontsize=11)
                else:  # Bajo - fuera
                    ax.text(bar.get_x() + bar.get_width()/2., height + max_val*0.02,
                           f'{value}', ha='center', va='bottom',
                           color='white', fontweight='bold', fontsize=11)

        ax.set_title(title, fontsize=14, fontweight='bold',
                    color=self.colors['primary'], pad=25)
        ax.set_ylabel(ylabel, fontweight='bold', color='white')
        ax.tick_params(colors='white', labelsize=10)
        ax.grid(axis='y', alpha=0.3, color=self.colors['grid'])
        ax.set_facecolor(self.colors['panel_bg'])

        return ax

    def create_horizontal_bar_panel(self, gs, position, data, title, xlabel, intelligent_labels=True):
        """Panel de barras horizontales genérico"""
        ax = self.fig.add_subplot(gs[position[0], position[1]])

        bars = ax.barh(data['labels'], data['values'], color=data['colors'],
                      edgecolor='white', linewidth=2, height=0.6)

        # Posicionamiento inteligente opcional
        if intelligent_labels:
            max_val = max(data['values']) if data['values'] else 1
            for i, (bar, value) in enumerate(zip(bars, data['values'])):
                if value > max_val * 0.7:  # Alto - dentro
                    ax.text(value - max_val*0.05, i, f'{value}', va='center', ha='right',
                           color='white', fontweight='bold', fontsize=11)
                else:  # Bajo - fuera
                    ax.text(value + max_val*0.02, i, f'{value}', va='center', ha='left',
                           color='white', fontweight='bold', fontsize=11)

        ax.set_title(title, fontsize=14, fontweight='bold',
                    color=self.colors['primary'], pad=25)
        ax.set_xlabel(xlabel, fontweight='bold', color='white')
        ax.tick_params(colors='white', labelsize=10)
        ax.grid(axis='x', alpha=0.3, color=self.colors['grid'])
        ax.set_facecolor(self.colors['panel_bg'])

        return ax

    def create_realtime_panel(self, gs, data, title):
        """Panel de gráfico en tiempo real (fila completa)"""
        ax = self.fig.add_subplot(gs[2, :])

        # Gráfico de líneas múltiples
        for line_data in data['lines']:
            ax.plot(line_data['x'], line_data['y'],
                   color=line_data['color'], linewidth=3,
                   label=line_data['label'], alpha=0.9,
                   marker=line_data.get('marker', 'o'), markersize=3)

            # Fill area opcional
            if line_data.get('fill', False):
                ax.fill_between(line_data['x'], line_data['y'],
                               alpha=0.2, color=line_data['color'])

        ax.set_title(title, fontsize=18, fontweight='bold',
                    color=self.colors['primary'], pad=30)
        ax.set_xlabel(data['xlabel'], color='white', fontweight='bold', fontsize=12)
        ax.set_ylabel(data['ylabel'], color='white', fontweight='bold', fontsize=12)
        ax.legend(loc='upper right', framealpha=0.9, fontsize=12)
        ax.grid(alpha=0.3, color=self.colors['grid'])
        ax.tick_params(colors='white')
        ax.set_facecolor(self.colors['panel_bg'])

        if 'ylim' in data:
            ax.set_ylim(data['ylim'])

        return ax

    def create_info_panel(self, gs, left_data, right_data):
        """Panel de información estilo CLI (fila inferior)"""
        ax = self.fig.add_subplot(gs[3, :])
        ax.axis('off')

        # Columna izquierda
        ax.text(0.02, 0.5, left_data, transform=ax.transAxes, fontsize=11,
               ha='left', va='center', color=self.colors['primary'],
               fontweight='bold', fontfamily='monospace', linespacing=1.4)

        # Columna derecha
        ax.text(0.52, 0.5, right_data, transform=ax.transAxes, fontsize=11,
               ha='left', va='center', color=self.colors['primary'],
               fontweight='bold', fontfamily='monospace', linespacing=1.4)

        return ax

    def add_footer(self, text):
        """Agregar footer estándar"""
        self.fig.text(0.5, 0.02, text, ha='center', va='bottom',
                     fontsize=10, color='#666666', style='italic')

    def finalize(self, filename):
        """Finalizar y guardar dashboard"""
        plt.subplots_adjust(top=0.88, bottom=0.12, left=0.05, right=0.95,
                           hspace=0.9, wspace=0.4)

        plt.savefig(filename, dpi=300, bbox_inches='tight',
                   facecolor=self.colors['background'], edgecolor='none', pad_inches=0.5)

        print(f"✅ Dashboard SmartCompute creado: {filename}")
        return filename

def create_osi_example():
    """Ejemplo: Dashboard OSI completo usando el template"""

    dashboard = SmartComputeDashboard("SMARTCOMPUTE SYSTEM MONITOR - OSI LAYER ANALYSIS")
    gs = dashboard.create_base_layout()

    # Panel principal - OSI Analysis
    osi_data = {
        'labels': ['LAYER 7 - APPLICATION', 'LAYER 6 - PRESENTATION', 'LAYER 5 - SESSION',
                   'LAYER 4 - TRANSPORT', 'LAYER 3 - NETWORK', 'LAYER 2 - DATA LINK', 'LAYER 1 - PHYSICAL'],
        'values': [89, 75, 68, 92, 85, 94, 97],
        'colors': ['#ff6b6b', '#ffa502', '#3742fa', '#2f3542', '#1dd1a1', '#5352ed', '#70a1ff']
    }
    dashboard.create_main_analysis_panel(gs, osi_data,
                                        'OSI MODEL - 7 LAYER ACTIVITY ANALYSIS',
                                        'ACTIVITY LEVEL (%)')

    # Panel de métricas del sistema
    system_data = {
        'labels': ['CPU\n13.2%', 'RAM\n46.6%', 'DISK\n32.4%', 'NET\n85%'],
        'values': [13.2, 46.6, 32.4, 85],
        'colors': ['#00ff88', '#ffd700', '#ff6b6b', '#48dbfb']
    }
    dashboard.create_metrics_panel(gs, system_data, 'SYSTEM RESOURCES')

    # Paneles de segunda fila
    protocols_data = {
        'labels': ['HTTPS', 'HTTP', 'SSH', 'DNS', 'OTHER'],
        'values': [45, 12, 8, 15, 20],
        'colors': ['#1dd1a1', '#feca57', '#ff6b6b', '#48dbfb', '#ff9ff3']
    }
    dashboard.create_bar_panel(gs, (1, 0), protocols_data, 'NETWORK PROTOCOLS', 'CONNECTIONS')

    # Panel tiempo real
    realtime_data = {
        'lines': [
            {
                'x': np.linspace(0, 30, 31),
                'y': 13 + 5 * np.sin(np.linspace(0, 30, 31)/5) + np.random.normal(0, 1, 31),
                'color': '#00ff88',
                'label': 'CPU USAGE (%)',
                'marker': 'o',
                'fill': True
            },
            {
                'x': np.linspace(0, 30, 31),
                'y': 46 + 3 * np.cos(np.linspace(0, 30, 31)/7) + np.random.normal(0, 0.8, 31),
                'color': '#ffd700',
                'label': 'MEMORY USAGE (%)',
                'marker': 's',
                'fill': True
            }
        ],
        'xlabel': 'TIME (SECONDS)',
        'ylabel': 'USAGE (%)',
        'ylim': (0, 100)
    }
    dashboard.create_realtime_panel(gs, realtime_data, 'REAL-TIME SYSTEM PERFORMANCE MONITORING')

    # Panel de información
    left_info = """NETWORK ANALYSIS:
├─ INTERFACES:      3 ACTIVE (WLAN0, ETH0, LOOPBACK)
├─ CONNECTIONS:     45 TCP, 8 UDP ACTIVE
├─ PROTOCOLS:       HTTPS(443), HTTP(80), SSH(22), DNS(53)
├─ SECURITY:        95% SECURE, 2% SUSPICIOUS, 3% BLOCKED
└─ BANDWIDTH:       85% UTILIZATION

SYSTEM RESOURCES:
├─ CPU USAGE:       13.2% (4 CORES @ 3.22GHZ)
├─ MEMORY USAGE:    46.6% (3.5GB / 7.51GB)
├─ DISK USAGE:      32.4% (84GB / 260GB)
└─ SYSTEM UPTIME:   1.73 HOURS"""

    right_info = """PROCESS MONITORING:
├─ TOTAL PROCESSES:     223
├─ ACTIVE PROCESSES:    32
├─ HIGH MEMORY APPS:    FIREFOX(604MB), CHROME(594MB)
├─ SYSTEM PROCESSES:    PYTHON(273MB), SYSTEM(256MB)
└─ PERFORMANCE SCORE:   100/100

DATA COLLECTION:
├─ OSI LAYERS:          7 ANALYZED
├─ DATA POINTS:         1,500+ COLLECTED
├─ SCAN DURATION:       30 SECONDS
├─ THREAT DETECTIONS:   2 SUSPICIOUS FLAGGED
└─ ANALYSIS STATUS:     COMPLETED SUCCESSFULLY"""

    dashboard.create_info_panel(gs, left_info, right_info)
    dashboard.add_footer("SmartCompute Express | github.com/cathackr/SmartCompute | Contact: ggwre04p0@mozmail.com")

    return dashboard.finalize('smartcompute_osi_template_example.png')

if __name__ == "__main__":
    # Crear ejemplo OSI usando el template
    create_osi_example()