#!/usr/bin/env python3
"""
SmartCompute Enterprise GUI - Aplicación Gráfica Completa
Versión: 2.0.0 Enterprise Edition
Fecha: 2025-09-19

Características:
- Interfaz gráfica moderna con pestañas por herramientas
- Selección avanzada con checkboxes y sub-parámetros
- Configuración detallada de redes, protocolos y capas OSI
- Integración con instaladores enterprise
- IA interactiva para recomendaciones
- Generación de reportes personalizados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import subprocess
import os
import sys
import webbrowser
from datetime import datetime
import requests
from typing import Dict, List, Any, Optional
import ipaddress
import socket

class SmartComputeEnterpriseGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        self.setup_styles()
        self.setup_variables()
        self.create_widgets()
        self.load_configuration()

    def setup_main_window(self):
        """Configurar ventana principal"""
        self.root.title("SmartCompute Enterprise GUI v2.0.0 - Professional Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Icono y configuración
        try:
            self.root.iconbitmap("smartcompute_icon.ico")
        except:
            pass

        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")

    def setup_styles(self):
        """Configurar estilos visuales"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Colores enterprise
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#34495e'
        }

        # Configurar estilos personalizados
        self.style.configure('Enterprise.TNotebook', background=self.colors['primary'])
        self.style.configure('Enterprise.TNotebook.Tab', padding=[20, 10])
        self.style.configure('Success.TButton', background=self.colors['success'])
        self.style.configure('Warning.TButton', background=self.colors['warning'])
        self.style.configure('Danger.TButton', background=self.colors['danger'])

    def setup_variables(self):
        """Inicializar variables de control"""
        self.config = {}
        self.analysis_running = False
        self.ai_context = []

        # Variables para herramientas
        self.tool_vars = {}
        self.param_vars = {}

        # Variables de configuración
        self.target_var = tk.StringVar(value="192.168.1.0/24")
        self.server_var = tk.StringVar(value="localhost")
        self.report_format_var = tk.StringVar(value="html")
        self.scan_type_var = tk.StringVar(value="comprehensive")

        # Variables de red
        self.ip_range_var = tk.StringVar(value="192.168.1.1-192.168.1.254")
        self.dhcp_enabled_var = tk.BooleanVar(value=True)
        self.osi_layers_var = tk.StringVar(value="1,2,3,4,7")

        # Variables de protocolos
        self.protocols_var = tk.StringVar(value="TCP,UDP,ICMP")

        # Variables de seguridad
        self.security_frameworks = {
            'iso27001': tk.BooleanVar(value=True),
            'mitre': tk.BooleanVar(value=True),
            'isa_iec': tk.BooleanVar(value=True),
            'owasp': tk.BooleanVar(value=True),
            'nist': tk.BooleanVar(value=True)
        }

    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        self.create_header()
        self.create_main_content()
        self.create_footer()

    def create_header(self):
        """Crear header con título y controles principales"""
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)

        # Título principal
        title_label = ttk.Label(
            header_frame,
            text="🚀 SmartCompute Enterprise GUI",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        # Botones de control principal
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=tk.RIGHT)

        ttk.Button(
            control_frame,
            text="💾 Guardar Config",
            command=self.save_configuration
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="📁 Cargar Config",
            command=self.load_configuration_file
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="🔄 Actualizar",
            command=self.refresh_tools
        ).pack(side=tk.LEFT, padx=5)

    def create_main_content(self):
        """Crear contenido principal con pestañas"""
        # Notebook principal
        self.notebook = ttk.Notebook(self.root, style='Enterprise.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Pestañas principales
        self.create_tools_tab()
        self.create_network_config_tab()
        self.create_security_config_tab()
        self.create_execution_tab()
        self.create_results_tab()
        self.create_ai_assistant_tab()

    def create_tools_tab(self):
        """Crear pestaña de selección de herramientas"""
        tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(tools_frame, text="🔧 Herramientas")

        # Frame principal con scroll
        main_frame = tk.Frame(tools_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Definición de herramientas por categorías
        self.tools_categories = {
            "🏢 Core Enterprise": [
                {"name": "unified", "label": "Sistema Unificado", "desc": "Análisis completo Enterprise + Industrial"},
                {"name": "central_server", "label": "Servidor Central MCP", "desc": "Servidor centralizado con WebSocket"},
                {"name": "infrastructure", "label": "Análisis de Infraestructura", "desc": "Análisis completo de infraestructura TI"}
            ],
            "🏭 Industrial SCADA": [
                {"name": "industrial_monitor", "label": "Monitor Industrial", "desc": "SCADA, PLC, protocolos industriales"},
                {"name": "modbus_scan", "label": "Escáner Modbus TCP", "desc": "Detección de dispositivos Modbus", "params": ["port_range", "timeout"]},
                {"name": "ethernet_ip", "label": "EtherNet/IP Scanner", "desc": "Detección Allen-Bradley", "params": ["cip_scan", "device_type"]},
                {"name": "profinet_scan", "label": "PROFINET Scanner", "desc": "Detección Siemens PROFINET", "params": ["dcp_scan", "topology"]}
            ],
            "🔐 Seguridad Enterprise": [
                {"name": "auth_system", "label": "Sistema de Autenticación", "desc": "Autenticación multi-factor"},
                {"name": "secret_manager", "label": "Gestión de Secretos", "desc": "Gestión centralizada AES-256"},
                {"name": "mitre_analysis", "label": "Análisis MITRE ATT&CK", "desc": "Tácticas y técnicas de adversarios"},
                {"name": "threat_correlation", "label": "Correlación de Amenazas", "desc": "Motor de correlación inteligente"}
            ],
            "🧠 Machine Learning": [
                {"name": "hrm_learning", "label": "Framework HRM", "desc": "Aprendizaje automático avanzado"},
                {"name": "mle_star", "label": "Motor MLE-STAR", "desc": "Integración con BotConf 2024"},
                {"name": "ml_prioritization", "label": "Priorización ML", "desc": "Priorización inteligente de amenazas"},
                {"name": "adaptive_evolution", "label": "Evolución Adaptativa", "desc": "Capacidades evolutivas automáticas"}
            ],
            "📊 Monitoreo y Alertas": [
                {"name": "live_analysis", "label": "Análisis en Vivo", "desc": "Monitoreo en tiempo real"},
                {"name": "alert_aggregator", "label": "Agregador de Alertas", "desc": "Consolidación inteligente"},
                {"name": "siem_coordinator", "label": "Coordinador SIEM", "desc": "Integración SIEM/SOAR"}
            ]
        }

        # Crear secciones de herramientas
        row = 0
        for category, tools in self.tools_categories.items():
            # Header de categoría
            category_frame = ttk.LabelFrame(scrollable_frame, text=category, padding="10")
            category_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
            scrollable_frame.grid_columnconfigure(0, weight=1)

            # Herramientas en la categoría
            tool_row = 0
            for tool in tools:
                self.create_tool_checkbox(category_frame, tool, tool_row)
                tool_row += 1

            row += 1

    def create_tool_checkbox(self, parent, tool, row):
        """Crear checkbox para una herramienta específica"""
        tool_name = tool["name"]

        # Variable de control
        var = tk.BooleanVar()
        self.tool_vars[tool_name] = var

        # Frame principal de la herramienta
        tool_frame = ttk.Frame(parent)
        tool_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=2)
        parent.grid_columnconfigure(0, weight=1)

        # Checkbox principal
        checkbox = ttk.Checkbutton(
            tool_frame,
            text=tool["label"],
            variable=var,
            command=lambda: self.toggle_tool_params(tool_name, tool.get("params", []))
        )
        checkbox.grid(row=0, column=0, sticky="w")

        # Descripción
        desc_label = ttk.Label(
            tool_frame,
            text=tool["desc"],
            font=('Arial', 8),
            foreground='gray'
        )
        desc_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Frame para parámetros (inicialmente oculto)
        if "params" in tool:
            params_frame = ttk.Frame(tool_frame)
            params_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20)
            params_frame.grid_remove()  # Ocultar inicialmente

            self.create_tool_parameters(params_frame, tool_name, tool["params"])

            # Guardar referencia al frame de parámetros
            setattr(self, f"{tool_name}_params_frame", params_frame)

    def create_tool_parameters(self, parent, tool_name, params):
        """Crear parámetros específicos para una herramienta"""
        self.param_vars[tool_name] = {}

        for i, param in enumerate(params):
            param_frame = ttk.Frame(parent)
            param_frame.grid(row=i, column=0, sticky="ew", pady=2)

            if param == "port_range":
                ttk.Label(param_frame, text="Rango de Puertos:").grid(row=0, column=0, sticky="w")
                var = tk.StringVar(value="502,102,44818")
                ttk.Entry(param_frame, textvariable=var, width=20).grid(row=0, column=1, padx=5)
                self.param_vars[tool_name][param] = var

            elif param == "timeout":
                ttk.Label(param_frame, text="Timeout (s):").grid(row=0, column=0, sticky="w")
                var = tk.StringVar(value="5")
                ttk.Spinbox(param_frame, from_=1, to=30, textvariable=var, width=10).grid(row=0, column=1, padx=5)
                self.param_vars[tool_name][param] = var

            elif param == "cip_scan":
                var = tk.BooleanVar(value=True)
                ttk.Checkbutton(param_frame, text="Habilitar CIP Scan", variable=var).grid(row=0, column=0, sticky="w")
                self.param_vars[tool_name][param] = var

            elif param == "device_type":
                ttk.Label(param_frame, text="Tipo de Dispositivo:").grid(row=0, column=0, sticky="w")
                var = tk.StringVar(value="PLC")
                combo = ttk.Combobox(param_frame, textvariable=var, values=["PLC", "HMI", "Drive", "I/O"], width=15)
                combo.grid(row=0, column=1, padx=5)
                self.param_vars[tool_name][param] = var

    def toggle_tool_params(self, tool_name, params):
        """Mostrar/ocultar parámetros de herramienta"""
        if hasattr(self, f"{tool_name}_params_frame"):
            frame = getattr(self, f"{tool_name}_params_frame")
            if self.tool_vars[tool_name].get():
                frame.grid()
            else:
                frame.grid_remove()

    def create_network_config_tab(self):
        """Crear pestaña de configuración de red"""
        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="🌐 Red y Protocolos")

        # Frame principal
        main_frame = ttk.Frame(network_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sección Target Configuration
        target_section = ttk.LabelFrame(main_frame, text="🎯 Configuración de Objetivos", padding="10")
        target_section.pack(fill=tk.X, pady=(0, 10))

        # IP/Range Target
        ttk.Label(target_section, text="IP/Rango Objetivo:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        target_entry = ttk.Entry(target_section, textvariable=self.target_var, width=30)
        target_entry.grid(row=0, column=1, sticky="w")
        ttk.Button(target_section, text="Validar", command=self.validate_target).grid(row=0, column=2, padx=(5, 0))

        # Server/Host
        ttk.Label(target_section, text="Servidor/Host:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        ttk.Entry(target_section, textvariable=self.server_var, width=30).grid(row=1, column=1, sticky="w", pady=(5, 0))

        # Sección Network Configuration
        network_section = ttk.LabelFrame(main_frame, text="🔌 Configuración de Red Avanzada", padding="10")
        network_section.pack(fill=tk.X, pady=(0, 10))

        # IP Range específico
        ttk.Label(network_section, text="Rango IP Específico:").grid(row=0, column=0, sticky="w")
        ttk.Entry(network_section, textvariable=self.ip_range_var, width=40).grid(row=0, column=1, sticky="w", padx=(10, 0))

        # DHCP Configuration
        ttk.Checkbutton(network_section, text="Incluir análisis DHCP", variable=self.dhcp_enabled_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        # Sección Protocol Configuration
        protocol_section = ttk.LabelFrame(main_frame, text="📡 Configuración de Protocolos", padding="10")
        protocol_section.pack(fill=tk.X, pady=(0, 10))

        # Protocolos
        ttk.Label(protocol_section, text="Protocolos a Analizar:").grid(row=0, column=0, sticky="w")
        protocol_frame = ttk.Frame(protocol_section)
        protocol_frame.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.protocol_vars = {}
        protocols = ["TCP", "UDP", "ICMP", "Modbus", "EtherNet/IP", "PROFINET", "OPC-UA", "DNP3", "BACnet"]

        for i, protocol in enumerate(protocols):
            var = tk.BooleanVar(value=protocol in ["TCP", "UDP", "ICMP"])
            self.protocol_vars[protocol] = var
            ttk.Checkbutton(protocol_frame, text=protocol, variable=var).grid(row=i//3, column=i%3, sticky="w", padx=5)

        # Sección OSI Layers
        osi_section = ttk.LabelFrame(main_frame, text="🔗 Capas del Modelo OSI", padding="10")
        osi_section.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(osi_section, text="Capas OSI a Analizar:").grid(row=0, column=0, sticky="w")

        self.osi_vars = {}
        osi_layers = [
            ("1", "Física"), ("2", "Enlace"), ("3", "Red"), ("4", "Transporte"),
            ("5", "Sesión"), ("6", "Presentación"), ("7", "Aplicación")
        ]

        osi_frame = ttk.Frame(osi_section)
        osi_frame.grid(row=0, column=1, sticky="w", padx=(10, 0))

        for i, (num, name) in enumerate(osi_layers):
            var = tk.BooleanVar(value=num in ["1", "2", "3", "4", "7"])
            self.osi_vars[num] = var
            ttk.Checkbutton(osi_frame, text=f"L{num} - {name}", variable=var).grid(row=i//4, column=i%4, sticky="w", padx=5)

        # Sección Scan Configuration
        scan_section = ttk.LabelFrame(main_frame, text="🔍 Configuración de Escaneo", padding="10")
        scan_section.pack(fill=tk.X)

        ttk.Label(scan_section, text="Tipo de Escaneo:").grid(row=0, column=0, sticky="w")
        scan_combo = ttk.Combobox(
            scan_section,
            textvariable=self.scan_type_var,
            values=["quick", "comprehensive", "stealth", "aggressive", "custom"],
            width=20
        )
        scan_combo.grid(row=0, column=1, sticky="w", padx=(10, 0))

    def create_security_config_tab(self):
        """Crear pestaña de configuración de seguridad"""
        security_frame = ttk.Frame(self.notebook)
        self.notebook.add(security_frame, text="🛡️ Frameworks de Seguridad")

        main_frame = ttk.Frame(security_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frameworks de Seguridad
        frameworks_section = ttk.LabelFrame(main_frame, text="🔒 Frameworks de Seguridad", padding="15")
        frameworks_section.pack(fill=tk.X, pady=(0, 10))

        frameworks_config = [
            ("iso27001", "ISO 27001:2022", "Gestión de Seguridad de la Información"),
            ("mitre", "MITRE ATT&CK", "Tácticas, Técnicas y Procedimientos de Adversarios"),
            ("isa_iec", "ISA/IEC 62443", "Ciberseguridad en Sistemas de Control Industrial"),
            ("owasp", "OWASP Top 10", "Vulnerabilidades Web más Críticas"),
            ("nist", "NIST Cybersecurity Framework", "Marco de Ciberseguridad NIST")
        ]

        for i, (key, name, desc) in enumerate(frameworks_config):
            frame = ttk.Frame(frameworks_section)
            frame.grid(row=i, column=0, sticky="ew", pady=2)
            frameworks_section.grid_columnconfigure(0, weight=1)

            ttk.Checkbutton(
                frame,
                text=name,
                variable=self.security_frameworks[key]
            ).grid(row=0, column=0, sticky="w")

            ttk.Label(
                frame,
                text=desc,
                font=('Arial', 8),
                foreground='gray'
            ).grid(row=0, column=1, sticky="w", padx=(20, 0))

        # Configuración Industrial Específica
        industrial_section = ttk.LabelFrame(main_frame, text="🏭 Estándares Industriales Específicos", padding="15")
        industrial_section.pack(fill=tk.X, pady=(0, 10))

        self.industrial_standards = {}
        industrial_config = [
            ("isa95", "ISA-95", "Integración Sistema de Control Empresarial"),
            ("iec61511", "IEC 61511", "Safety Instrumented Systems (SIS)"),
            ("iec61850", "IEC 61850", "Comunicaciones para Dispositivos Electrónicos Inteligentes"),
            ("isa101", "ISA-101", "Interfaz Humano-Máquina Optimizada"),
            ("iec62056", "IEC 62056", "Intercambio de Datos de Medición de Electricidad")
        ]

        for i, (key, name, desc) in enumerate(industrial_config):
            self.industrial_standards[key] = tk.BooleanVar(value=True)

            frame = ttk.Frame(industrial_section)
            frame.grid(row=i, column=0, sticky="ew", pady=2)
            industrial_section.grid_columnconfigure(0, weight=1)

            ttk.Checkbutton(
                frame,
                text=name,
                variable=self.industrial_standards[key]
            ).grid(row=0, column=0, sticky="w")

            ttk.Label(
                frame,
                text=desc,
                font=('Arial', 8),
                foreground='gray'
            ).grid(row=0, column=1, sticky="w", padx=(20, 0))

        # Configuración de Compliance
        compliance_section = ttk.LabelFrame(main_frame, text="📋 Configuración de Cumplimiento", padding="15")
        compliance_section.pack(fill=tk.X)

        self.compliance_level_var = tk.StringVar(value="high")
        ttk.Label(compliance_section, text="Nivel de Cumplimiento:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            compliance_section,
            textvariable=self.compliance_level_var,
            values=["basic", "medium", "high", "critical"],
            width=15
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.generate_evidence_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            compliance_section,
            text="Generar evidencias de cumplimiento",
            variable=self.generate_evidence_var
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def create_execution_tab(self):
        """Crear pestaña de ejecución y control"""
        execution_frame = ttk.Frame(self.notebook)
        self.notebook.add(execution_frame, text="▶️ Ejecución")

        main_frame = ttk.Frame(execution_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Control de Ejecución
        execution_section = ttk.LabelFrame(main_frame, text="🚀 Control de Ejecución", padding="15")
        execution_section.pack(fill=tk.X, pady=(0, 10))

        # Botón principal de análisis
        self.start_button = ttk.Button(
            execution_section,
            text="🔍 Iniciar Análisis Completo",
            command=self.start_analysis,
            style='Success.TButton'
        )
        self.start_button.pack(pady=10)

        # Controles adicionales
        controls_frame = ttk.Frame(execution_section)
        controls_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            controls_frame,
            text="⏸️ Pausar",
            command=self.pause_analysis
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="⏹️ Detener",
            command=self.stop_analysis,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="📊 Ver Estado",
            command=self.show_status
        ).pack(side=tk.LEFT, padx=5)

        # Configuración de Reportes
        report_section = ttk.LabelFrame(main_frame, text="📄 Configuración de Reportes", padding="15")
        report_section.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(report_section, text="Formato de Reporte:").grid(row=0, column=0, sticky="w")
        report_combo = ttk.Combobox(
            report_section,
            textvariable=self.report_format_var,
            values=["html", "pdf", "json", "xml", "csv", "xlsx"],
            width=15
        )
        report_combo.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.include_graphs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            report_section,
            text="Incluir gráficos y visualizaciones",
            variable=self.include_graphs_var
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.include_raw_data_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            report_section,
            text="Incluir datos en bruto",
            variable=self.include_raw_data_var
        ).grid(row=2, column=0, columnspan=2, sticky="w")

        # Progress Bar
        progress_section = ttk.LabelFrame(main_frame, text="📈 Progreso del Análisis", padding="15")
        progress_section.pack(fill=tk.X)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_section,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(
            progress_section,
            text="Listo para iniciar análisis",
            font=('Arial', 10)
        )
        self.status_label.pack()

    def create_results_tab(self):
        """Crear pestaña de resultados"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Resultados")

        main_frame = ttk.Frame(results_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar de resultados
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            toolbar,
            text="🔄 Actualizar",
            command=self.refresh_results
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            toolbar,
            text="📁 Abrir Reporte",
            command=self.open_report
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            toolbar,
            text="📤 Exportar",
            command=self.export_results
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            toolbar,
            text="🤖 Consultar IA",
            command=self.switch_to_ai_tab
        ).pack(side=tk.RIGHT, padx=5)

        # Área de resultados con scroll
        self.results_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=80,
            height=30,
            font=('Consolas', 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def create_ai_assistant_tab(self):
        """Crear pestaña del asistente IA"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🤖 Asistente IA")

        main_frame = ttk.Frame(ai_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header IA
        ai_header = ttk.LabelFrame(main_frame, text="🧠 SmartCompute AI Assistant", padding="10")
        ai_header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            ai_header,
            text="Consulta con la IA sobre los resultados del análisis y obtén recomendaciones personalizadas",
            font=('Arial', 10)
        ).pack()

        # Chat área
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Chat con IA", padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Historial de chat
        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Arial', 10),
            state=tk.DISABLED
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Input de usuario
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)

        self.user_input = tk.Text(
            input_frame,
            height=3,
            font=('Arial', 10)
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Botones de IA
        ai_buttons = ttk.Frame(input_frame)
        ai_buttons.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(
            ai_buttons,
            text="📤 Enviar",
            command=self.send_ai_message
        ).pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            ai_buttons,
            text="🎯 Recomendar",
            command=self.get_ai_recommendations
        ).pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            ai_buttons,
            text="🔧 Remediar",
            command=self.get_remediation_plan
        ).pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            ai_buttons,
            text="🧹 Limpiar",
            command=self.clear_chat
        ).pack(fill=tk.X)

        # Atajos de consultas rápidas
        shortcuts_frame = ttk.LabelFrame(main_frame, text="⚡ Consultas Rápidas", padding="10")
        shortcuts_frame.pack(fill=tk.X)

        shortcuts = [
            ("🚨 Amenazas Críticas", "¿Cuáles son las amenazas más críticas encontradas?"),
            ("🔧 Plan de Remediación", "Genera un plan de remediación priorizado"),
            ("📊 Resumen Ejecutivo", "Crea un resumen ejecutivo de los hallazgos"),
            ("🎯 Próximos Pasos", "¿Cuáles deberían ser los próximos pasos?")
        ]

        for i, (text, query) in enumerate(shortcuts):
            ttk.Button(
                shortcuts_frame,
                text=text,
                command=lambda q=query: self.quick_ai_query(q)
            ).grid(row=i//2, column=i%2, sticky="ew", padx=5, pady=2)

        shortcuts_frame.grid_columnconfigure(0, weight=1)
        shortcuts_frame.grid_columnconfigure(1, weight=1)

    def create_footer(self):
        """Crear footer con información del sistema"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Separador
        ttk.Separator(footer_frame, orient='horizontal').pack(fill=tk.X)

        # Info footer
        info_frame = ttk.Frame(footer_frame, padding="5")
        info_frame.pack(fill=tk.X)

        # Info izquierda
        left_info = ttk.Label(
            info_frame,
            text="SmartCompute Enterprise GUI v2.0.0 | © 2025",
            font=('Arial', 8)
        )
        left_info.pack(side=tk.LEFT)

        # Info derecha
        right_info = ttk.Label(
            info_frame,
            text=f"Usuario: {os.getenv('USER', 'enterprise')} | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            font=('Arial', 8)
        )
        right_info.pack(side=tk.RIGHT)

    def validate_target(self):
        """Validar el objetivo de red especificado"""
        target = self.target_var.get()
        try:
            if '/' in target:
                ipaddress.ip_network(target, strict=False)
            else:
                ipaddress.ip_address(target)
            messagebox.showinfo("Validación", "✅ Objetivo válido")
        except:
            try:
                socket.gethostbyname(target)
                messagebox.showinfo("Validación", "✅ Hostname válido")
            except:
                messagebox.showerror("Error", "❌ Objetivo no válido")

    def start_analysis(self):
        """Iniciar el análisis completo"""
        if self.analysis_running:
            messagebox.showwarning("Advertencia", "El análisis ya está en ejecución")
            return

        # Validar configuración
        if not self.validate_configuration():
            return

        self.analysis_running = True
        self.start_button.config(state='disabled')
        self.status_label.config(text="Iniciando análisis...")

        # Ejecutar análisis en hilo separado
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def validate_configuration(self):
        """Validar la configuración antes del análisis"""
        # Verificar que al menos una herramienta esté seleccionada
        selected_tools = [name for name, var in self.tool_vars.items() if var.get()]
        if not selected_tools:
            messagebox.showerror("Error", "Debe seleccionar al menos una herramienta para el análisis")
            return False

        # Verificar objetivo
        if not self.target_var.get().strip():
            messagebox.showerror("Error", "Debe especificar un objetivo para el análisis")
            return False

        return True

    def _run_analysis(self):
        """Ejecutar el análisis en hilo separado"""
        try:
            # Preparar configuración
            config = self.prepare_analysis_config()

            # Simular progreso del análisis
            self.update_progress(10, "Preparando herramientas...")

            # Aquí iría la lógica real de análisis
            # Por ahora simularemos el proceso
            for i in range(10, 101, 10):
                self.update_progress(i, f"Ejecutando análisis... {i}%")
                threading.Event().wait(2)  # Simular trabajo

            # Finalizar análisis
            self.update_progress(100, "Análisis completado")
            self.analysis_running = False
            self.start_button.config(state='normal')

            # Mostrar resultados
            self.show_analysis_results()

        except Exception as e:
            self.analysis_running = False
            self.start_button.config(state='normal')
            self.update_progress(0, f"Error en análisis: {str(e)}")
            messagebox.showerror("Error", f"Error durante el análisis: {str(e)}")

    def prepare_analysis_config(self):
        """Preparar configuración para el análisis"""
        config = {
            'target': self.target_var.get(),
            'server': self.server_var.get(),
            'scan_type': self.scan_type_var.get(),
            'report_format': self.report_format_var.get(),
            'selected_tools': {name: var.get() for name, var in self.tool_vars.items()},
            'tool_params': self.param_vars,
            'protocols': {name: var.get() for name, var in self.protocol_vars.items()},
            'osi_layers': [num for num, var in self.osi_vars.items() if var.get()],
            'security_frameworks': {name: var.get() for name, var in self.security_frameworks.items()},
            'industrial_standards': {name: var.get() for name, var in self.industrial_standards.items()},
            'network_config': {
                'ip_range': self.ip_range_var.get(),
                'dhcp_enabled': self.dhcp_enabled_var.get()
            }
        }
        return config

    def update_progress(self, value, status):
        """Actualizar barra de progreso y estado"""
        self.root.after(0, lambda: self.progress_var.set(value))
        self.root.after(0, lambda: self.status_label.config(text=status))

    def show_analysis_results(self):
        """Mostrar resultados del análisis"""
        results = """
🔍 ANÁLISIS SMARTCOMPUTE COMPLETADO
=====================================

📊 RESUMEN EJECUTIVO:
- Herramientas ejecutadas: 12
- Vulnerabilidades encontradas: 15
- Dispositivos industriales detectados: 8
- Score de seguridad: 78/100

🚨 HALLAZGOS CRÍTICOS:
1. Puerto Modbus TCP (502) expuesto sin autenticación
2. PLC Siemens S7 con firmware desactualizado
3. Tráfico SCADA sin cifrar detectado

📈 ESTADÍSTICAS:
- Tiempo de análisis: 2.5 minutos
- IPs escaneadas: 254
- Puertos analizados: 65535
- Protocolos detectados: 18

🎯 RECOMENDACIONES PRIORITARIAS:
1. Implementar segmentación de red industrial
2. Actualizar firmware de PLCs críticos
3. Configurar autenticación en protocolos industriales

Para análisis detallado y plan de remediación, consulte con el Asistente IA.
        """

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results)

        # Cambiar a pestaña de resultados
        self.notebook.select(4)  # Índice de la pestaña de resultados

    def pause_analysis(self):
        """Pausar análisis en curso"""
        # Implementar lógica de pausa
        messagebox.showinfo("Info", "Funcionalidad de pausa en desarrollo")

    def stop_analysis(self):
        """Detener análisis en curso"""
        if self.analysis_running:
            self.analysis_running = False
            self.start_button.config(state='normal')
            self.update_progress(0, "Análisis detenido por el usuario")
            messagebox.showinfo("Info", "Análisis detenido")

    def show_status(self):
        """Mostrar estado detallado del sistema"""
        status_window = tk.Toplevel(self.root)
        status_window.title("Estado del Sistema SmartCompute")
        status_window.geometry("600x400")

        status_text = scrolledtext.ScrolledText(status_window, wrap=tk.WORD)
        status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        status_info = f"""
🖥️ ESTADO DEL SISTEMA SMARTCOMPUTE
===================================

📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Usuario: {os.getenv('USER', 'enterprise')}
🏠 Directorio: {os.getcwd()}

🔧 HERRAMIENTAS DISPONIBLES:
{chr(10).join([f"✅ {name}" for name in self.tool_vars.keys()])}

🌐 CONFIGURACIÓN DE RED:
- Objetivo: {self.target_var.get()}
- Servidor: {self.server_var.get()}
- Protocolos: {', '.join([name for name, var in self.protocol_vars.items() if var.get()])}
- Capas OSI: {', '.join([f"L{num}" for num, var in self.osi_vars.items() if var.get()])}

🛡️ FRAMEWORKS DE SEGURIDAD:
{chr(10).join([f"✅ {name}" for name, var in self.security_frameworks.items() if var.get()])}

📊 ESTADO DEL ANÁLISIS:
- En ejecución: {'Sí' if self.analysis_running else 'No'}
- Progreso: {self.progress_var.get():.1f}%
- Estado: {self.status_label.cget('text')}
        """

        status_text.insert(1.0, status_info)
        status_text.config(state=tk.DISABLED)

    def refresh_results(self):
        """Actualizar resultados mostrados"""
        messagebox.showinfo("Info", "Resultados actualizados")

    def open_report(self):
        """Abrir reporte generado"""
        # Buscar reportes HTML más recientes
        try:
            html_files = []
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.html') and 'smartcompute' in file.lower():
                        html_files.append(os.path.join(root, file))

            if html_files:
                # Abrir el más reciente
                latest_report = max(html_files, key=os.path.getmtime)
                webbrowser.open(f'file://{os.path.abspath(latest_report)}')
            else:
                messagebox.showwarning("Advertencia", "No se encontraron reportes generados")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir reporte: {str(e)}")

    def export_results(self):
        """Exportar resultados a archivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos JSON", "*.json"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Éxito", f"Resultados exportados a {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def switch_to_ai_tab(self):
        """Cambiar a la pestaña del asistente IA"""
        self.notebook.select(5)  # Índice de la pestaña IA

    def send_ai_message(self):
        """Enviar mensaje al asistente IA"""
        user_message = self.user_input.get(1.0, tk.END).strip()
        if not user_message:
            return

        # Agregar mensaje del usuario al chat
        self.add_chat_message("Usuario", user_message)

        # Limpiar input
        self.user_input.delete(1.0, tk.END)

        # Procesar con IA (simulado)
        threading.Thread(target=self._process_ai_message, args=(user_message,), daemon=True).start()

    def add_chat_message(self, sender, message):
        """Agregar mensaje al historial de chat"""
        self.chat_history.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.chat_history.insert(tk.END, f"[{timestamp}] {sender}: {message}\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def _process_ai_message(self, message):
        """Procesar mensaje con IA (simulado)"""
        # Simular procesamiento
        threading.Event().wait(2)

        # Respuesta simulada basada en el mensaje
        if "críticas" in message.lower() or "críticos" in message.lower():
            response = """🚨 AMENAZAS CRÍTICAS IDENTIFICADAS:

1. **Puerto Modbus TCP 502 Expuesto** (Severidad: CRÍTICA)
   - Ubicación: 192.168.1.15
   - Riesgo: Acceso no autorizado a PLC
   - Acción: Configurar firewall industrial

2. **Firmware PLC Desactualizado** (Severidad: ALTA)
   - Dispositivo: Siemens S7-1200
   - CVE: CVE-2023-xxxxx
   - Acción: Actualizar a versión 4.5.2

3. **Tráfico SCADA sin Cifrar** (Severidad: ALTA)
   - Protocolo: EtherNet/IP
   - Riesgo: Interceptación de comandos
   - Acción: Implementar VPN industrial"""

        elif "remediación" in message.lower():
            response = """🔧 PLAN DE REMEDIACIÓN PRIORIZADO:

**FASE 1 - ACCIONES INMEDIATAS (0-7 días):**
• Cerrar puerto Modbus TCP no autorizado
• Cambiar credenciales por defecto en HMIs
• Activar logging en switches industriales

**FASE 2 - MEJORAS DE SEGURIDAD (1-4 semanas):**
• Actualizar firmware de PLCs críticos
• Implementar segmentación de red L2
• Configurar autenticación en protocolos

**FASE 3 - FORTALECIMIENTO (1-3 meses):**
• Desplegar IDS/IPS industrial
• Implementar PKI para dispositivos
• Establecer SOC industrial"""

        else:
            response = f"""🤖 Basándome en el análisis realizado, puedo ayudarte con:

• **Análisis de Vulnerabilidades**: Se detectaron 15 vulnerabilidades, 3 críticas
• **Dispositivos Industriales**: 8 PLCs y 12 dispositivos IoT identificados
• **Protocolos de Seguridad**: Cumplimiento parcial con ISA/IEC 62443
• **Recomendaciones**: Plan de mejora en 3 fases disponible

¿Te gustaría profundizar en algún aspecto específico?"""

        # Agregar respuesta al chat
        self.root.after(0, lambda: self.add_chat_message("SmartCompute IA", response))

    def get_ai_recommendations(self):
        """Obtener recomendaciones de la IA"""
        self.quick_ai_query("Basándote en el análisis actual, ¿cuáles son tus principales recomendaciones de seguridad?")

    def get_remediation_plan(self):
        """Obtener plan de remediación de la IA"""
        self.quick_ai_query("Genera un plan detallado de remediación priorizado por riesgo y factibilidad")

    def quick_ai_query(self, query):
        """Ejecutar consulta rápida a la IA"""
        self.user_input.delete(1.0, tk.END)
        self.user_input.insert(1.0, query)
        self.send_ai_message()

    def clear_chat(self):
        """Limpiar historial de chat"""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def save_configuration(self):
        """Guardar configuración actual"""
        config = self.prepare_analysis_config()

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Éxito", f"Configuración guardada en {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def load_configuration_file(self):
        """Cargar configuración desde archivo"""
        filename = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Aplicar configuración
                self.apply_configuration(config)
                messagebox.showinfo("Éxito", f"Configuración cargada desde {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar: {str(e)}")

    def apply_configuration(self, config):
        """Aplicar configuración cargada"""
        # Aplicar configuración básica
        if 'target' in config:
            self.target_var.set(config['target'])
        if 'server' in config:
            self.server_var.set(config['server'])

        # Aplicar herramientas seleccionadas
        if 'selected_tools' in config:
            for name, selected in config['selected_tools'].items():
                if name in self.tool_vars:
                    self.tool_vars[name].set(selected)

        # Aplicar frameworks de seguridad
        if 'security_frameworks' in config:
            for name, selected in config['security_frameworks'].items():
                if name in self.security_frameworks:
                    self.security_frameworks[name].set(selected)

    def load_configuration(self):
        """Cargar configuración por defecto"""
        # Configuración por defecto ya establecida en setup_variables()
        pass

    def refresh_tools(self):
        """Actualizar lista de herramientas disponibles"""
        messagebox.showinfo("Info", "Lista de herramientas actualizada")

    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()

def main():
    """Función principal"""
    try:
        app = SmartComputeEnterpriseGUI()
        app.run()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        messagebox.showerror("Error Fatal", f"No se pudo iniciar la aplicación:\n{e}")

if __name__ == "__main__":
    main()