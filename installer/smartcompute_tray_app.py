#!/usr/bin/env python3
"""
SmartCompute Enterprise - System Tray Application
================================================

Aplicación de bandeja del sistema para SmartCompute Enterprise con capacidades
de escaneo continuo, gestión de múltiples objetivos y exportación cifrada.
"""

import sys
import os
import json
import asyncio
import threading
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import webbrowser

# Detectar sistema operativo para imports específicos
if platform.system() == "Windows":
    try:
        import pystray
        from pystray import MenuItem as item
        from PIL import Image, ImageDraw
        import win32api
        import win32con
        import win32service
        import win32serviceutil
    except ImportError:
        print("Windows dependencies not installed. Install: pip install pystray pillow pywin32")
        sys.exit(1)
else:
    try:
        import pystray
        from pystray import MenuItem as item
        from PIL import Image, ImageDraw
    except ImportError:
        print("Linux dependencies not installed. Install: pip install pystray pillow")
        sys.exit(1)


class SmartComputeConfig:
    """Configuración de SmartCompute Enterprise"""

    def __init__(self):
        self.config_dir = Path.home() / ".smartcompute"
        self.config_file = self.config_dir / "config.json"
        self.credentials_file = self.config_dir / "credentials.enc"
        self.config_dir.mkdir(exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Carga configuración desde archivo"""
        default_config = {
            "continuous_scan": False,
            "scan_interval": 300,  # 5 minutos
            "targets": {
                "local": True,
                "network_ranges": [],
                "domains": [],
                "vlans": [],
                "cloud_providers": []
            },
            "credentials": {
                "admin_username": "",
                "active_directory": {
                    "domain": "",
                    "username": "",
                    "enabled": False
                },
                "cloud": {
                    "aws": {"access_key": "", "secret_key": "", "region": "us-east-1"},
                    "azure": {"client_id": "", "client_secret": "", "tenant_id": ""},
                    "gcp": {"project_id": "", "credentials_file": ""}
                }
            },
            "export": {
                "encryption_enabled": True,
                "auto_export": False,
                "export_path": str(Path.home() / "Documents" / "SmartCompute"),
                "retention_days": 30
            },
            "ui": {
                "minimize_to_tray": True,
                "start_with_windows": True,
                "show_notifications": True
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._deep_update(default_config, loaded_config)
                    return default_config
            except Exception as e:
                print(f"Error loading config: {e}")

        return default_config

    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Actualización profunda de diccionario"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def save_config(self):
        """Guarda configuración a archivo"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False


class SmartComputeTrayApp:
    """Aplicación principal de bandeja del sistema"""

    def __init__(self):
        self.config = SmartComputeConfig()
        self.scanning = False
        self.scan_thread = None
        self.icon = None
        self.last_scan_time = None
        self.scan_results = {}

        # Detectar rutas del sistema
        self.is_windows = platform.system() == "Windows"
        self.smartcompute_path = self._find_smartcompute_path()

    def _find_smartcompute_path(self) -> Path:
        """Encuentra la ruta de instalación de SmartCompute"""
        # Buscar en rutas comunes
        possible_paths = [
            Path.cwd(),
            Path.home() / "smartcompute",
            Path("/opt/smartcompute") if not self.is_windows else Path("C:/Program Files/SmartCompute"),
            Path("/usr/local/bin/smartcompute") if not self.is_windows else Path("C:/Program Files (x86)/SmartCompute")
        ]

        for path in possible_paths:
            if (path / "run_enterprise_analysis.py").exists():
                return path

        return Path.cwd()

    def create_image(self, width: int, height: int, color1: str, color2: str) -> Image.Image:
        """Crea icono para la bandeja del sistema"""
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)

        # Dibujar icono de escudo de seguridad
        dc.rectangle([4, 4, width-4, height-4], fill=color2)
        dc.ellipse([8, 8, width-8, height-8], fill=color1)
        dc.text((width//4, height//3), "SC", fill=color2)

        return image

    def get_menu(self):
        """Crea menú contextual de la bandeja"""
        scan_text = "🛑 Detener Escaneo" if self.scanning else "🔍 Iniciar Escaneo"

        return pystray.Menu(
            item("SmartCompute Enterprise", self.show_main_window),
            pystray.Menu.SEPARATOR,
            item("📊 Análisis Local", self.run_local_analysis),
            item("🌐 Análisis de Red", self.show_network_menu),
            item("☁️ Análisis en Nube", self.show_cloud_menu),
            pystray.Menu.SEPARATOR,
            item(scan_text, self.toggle_continuous_scan),
            item("📈 Ver Últimos Resultados", self.show_last_results),
            item("📤 Exportar Informes", self.export_reports),
            pystray.Menu.SEPARATOR,
            item("⚙️ Configuración", self.show_config),
            item("💻 Abrir Terminal", self.open_terminal),
            item("🔐 Gestionar Credenciales", self.manage_credentials),
            pystray.Menu.SEPARATOR,
            item("❓ Ayuda", self.show_help),
            item("🚪 Salir", self.quit_application)
        )

    def show_main_window(self, icon=None, item=None):
        """Muestra ventana principal"""
        root = tk.Tk()
        root.title("SmartCompute Enterprise")
        root.geometry("800x600")

        # Crear interfaz principal
        notebook = ttk.Notebook(root)

        # Pestaña de Estado
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="Estado")

        status_text = tk.Text(status_frame, wrap=tk.WORD)
        status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        status_info = f"""SmartCompute Enterprise - Estado del Sistema

🕐 Última ejecución: {self.last_scan_time or 'Nunca'}
🔄 Escaneo continuo: {'Activo' if self.scanning else 'Inactivo'}
📍 Ruta de instalación: {self.smartcompute_path}
💻 Sistema operativo: {platform.system()} {platform.release()}

📊 Configuración actual:
- Intervalo de escaneo: {self.config.config['scan_interval']} segundos
- Objetivos configurados: {len(self.config.config['targets']['network_ranges']) + len(self.config.config['targets']['domains'])}
- Exportación cifrada: {'Habilitada' if self.config.config['export']['encryption_enabled'] else 'Deshabilitada'}
- Notificaciones: {'Habilitadas' if self.config.config['ui']['show_notifications'] else 'Deshabilitadas'}
"""

        status_text.insert(tk.END, status_info)
        status_text.config(state=tk.DISABLED)

        # Pestaña de Objetivos
        targets_frame = ttk.Frame(notebook)
        notebook.add(targets_frame, text="Objetivos de Escaneo")

        self._create_targets_tab(targets_frame)

        # Pestaña de Configuración
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuración")

        self._create_config_tab(config_frame)

        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Botones de acción
        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Ejecutar Análisis Local",
                  command=self.run_local_analysis).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Exportar Informes",
                  command=self.export_reports).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Abrir Terminal",
                  command=self.open_terminal).pack(side=tk.LEFT, padx=5)

        root.mainloop()

    def _create_targets_tab(self, parent):
        """Crea pestaña de configuración de objetivos"""
        # Frame para rangos de red
        net_frame = ttk.LabelFrame(parent, text="Rangos de Red")
        net_frame.pack(fill=tk.X, padx=10, pady=5)

        self.net_listbox = tk.Listbox(net_frame, height=4)
        self.net_listbox.pack(fill=tk.X, padx=5, pady=5)

        net_button_frame = ttk.Frame(net_frame)
        net_button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(net_button_frame, text="Agregar IP/Rango",
                  command=self.add_network_range).pack(side=tk.LEFT, padx=2)
        ttk.Button(net_button_frame, text="Eliminar",
                  command=self.remove_network_range).pack(side=tk.LEFT, padx=2)

        # Frame para dominios
        domain_frame = ttk.LabelFrame(parent, text="Dominios")
        domain_frame.pack(fill=tk.X, padx=10, pady=5)

        self.domain_listbox = tk.Listbox(domain_frame, height=4)
        self.domain_listbox.pack(fill=tk.X, padx=5, pady=5)

        domain_button_frame = ttk.Frame(domain_frame)
        domain_button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(domain_button_frame, text="Agregar Dominio",
                  command=self.add_domain).pack(side=tk.LEFT, padx=2)
        ttk.Button(domain_button_frame, text="Eliminar",
                  command=self.remove_domain).pack(side=tk.LEFT, padx=2)

        # Cargar datos existentes
        self._load_targets_data()

    def _create_config_tab(self, parent):
        """Crea pestaña de configuración general"""
        # Configuración de escaneo
        scan_frame = ttk.LabelFrame(parent, text="Configuración de Escaneo")
        scan_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(scan_frame, text="Intervalo (segundos):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.interval_var = tk.StringVar(value=str(self.config.config['scan_interval']))
        ttk.Entry(scan_frame, textvariable=self.interval_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        self.continuous_var = tk.BooleanVar(value=self.config.config['continuous_scan'])
        ttk.Checkbutton(scan_frame, text="Escaneo continuo",
                       variable=self.continuous_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        # Configuración de exportación
        export_frame = ttk.LabelFrame(parent, text="Configuración de Exportación")
        export_frame.pack(fill=tk.X, padx=10, pady=5)

        self.encryption_var = tk.BooleanVar(value=self.config.config['export']['encryption_enabled'])
        ttk.Checkbutton(export_frame, text="Cifrado habilitado",
                       variable=self.encryption_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        ttk.Label(export_frame, text="Ruta de exportación:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.export_path_var = tk.StringVar(value=self.config.config['export']['export_path'])
        ttk.Entry(export_frame, textvariable=self.export_path_var, width=40).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(export_frame, text="Examinar",
                  command=self.browse_export_path).grid(row=1, column=2, padx=5, pady=2)

        # Botón para guardar configuración
        ttk.Button(parent, text="Guardar Configuración",
                  command=self.save_configuration).pack(pady=10)

    def _load_targets_data(self):
        """Carga datos de objetivos en las listas"""
        # Cargar rangos de red
        self.net_listbox.delete(0, tk.END)
        for net_range in self.config.config['targets']['network_ranges']:
            self.net_listbox.insert(tk.END, net_range)

        # Cargar dominios
        self.domain_listbox.delete(0, tk.END)
        for domain in self.config.config['targets']['domains']:
            self.domain_listbox.insert(tk.END, domain)

    def add_network_range(self):
        """Agrega rango de red"""
        range_input = simpledialog.askstring("Agregar Rango",
                                            "Ingrese IP o rango (ej: 192.168.1.0/24, 10.0.0.1-10.0.0.100):")
        if range_input:
            self.config.config['targets']['network_ranges'].append(range_input)
            self.net_listbox.insert(tk.END, range_input)

    def remove_network_range(self):
        """Elimina rango de red seleccionado"""
        selection = self.net_listbox.curselection()
        if selection:
            index = selection[0]
            self.config.config['targets']['network_ranges'].pop(index)
            self.net_listbox.delete(index)

    def add_domain(self):
        """Agrega dominio"""
        domain_input = simpledialog.askstring("Agregar Dominio",
                                             "Ingrese dominio (ej: example.com):")
        if domain_input:
            self.config.config['targets']['domains'].append(domain_input)
            self.domain_listbox.insert(tk.END, domain_input)

    def remove_domain(self):
        """Elimina dominio seleccionado"""
        selection = self.domain_listbox.curselection()
        if selection:
            index = selection[0]
            self.config.config['targets']['domains'].pop(index)
            self.domain_listbox.delete(index)

    def browse_export_path(self):
        """Examina directorio de exportación"""
        directory = filedialog.askdirectory(initialdir=self.export_path_var.get())
        if directory:
            self.export_path_var.set(directory)

    def save_configuration(self):
        """Guarda configuración"""
        try:
            self.config.config['scan_interval'] = int(self.interval_var.get())
            self.config.config['continuous_scan'] = self.continuous_var.get()
            self.config.config['export']['encryption_enabled'] = self.encryption_var.get()
            self.config.config['export']['export_path'] = self.export_path_var.get()

            if self.config.save_config():
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración")
        except ValueError:
            messagebox.showerror("Error", "Intervalo debe ser un número válido")

    def show_network_menu(self, icon=None, item=None):
        """Muestra submenú de análisis de red"""
        # Implementar submenú dinámico
        pass

    def show_cloud_menu(self, icon=None, item=None):
        """Muestra submenú de análisis en nube"""
        # Implementar submenú de proveedores cloud
        pass

    def run_local_analysis(self, icon=None, item=None):
        """Ejecuta análisis local"""
        def run_analysis():
            try:
                script_path = self.smartcompute_path / "run_enterprise_analysis.py"
                if script_path.exists():
                    if self.is_windows:
                        subprocess.Popen([sys.executable, str(script_path)],
                                       creationflags=subprocess.CREATE_NEW_CONSOLE)
                    else:
                        subprocess.Popen([sys.executable, str(script_path)])

                    self.last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.show_notification("SmartCompute", "Análisis local iniciado")
                else:
                    self.show_notification("Error", "No se encontró el script de análisis")
            except Exception as e:
                self.show_notification("Error", f"Error ejecutando análisis: {e}")

        threading.Thread(target=run_analysis, daemon=True).start()

    def toggle_continuous_scan(self, icon=None, item=None):
        """Alterna escaneo continuo"""
        if self.scanning:
            self.stop_continuous_scan()
        else:
            self.start_continuous_scan()

    def start_continuous_scan(self):
        """Inicia escaneo continuo"""
        if not self.scanning:
            self.scanning = True
            self.config.config['continuous_scan'] = True
            self.config.save_config()

            def continuous_scan_worker():
                while self.scanning:
                    try:
                        self.run_local_analysis()
                        # Esperar intervalo configurado
                        for _ in range(self.config.config['scan_interval']):
                            if not self.scanning:
                                break
                            threading.Event().wait(1)
                    except Exception as e:
                        print(f"Error in continuous scan: {e}")
                        break

            self.scan_thread = threading.Thread(target=continuous_scan_worker, daemon=True)
            self.scan_thread.start()

            self.show_notification("SmartCompute", "Escaneo continuo iniciado")
            if self.icon:
                self.icon.menu = self.get_menu()

    def stop_continuous_scan(self):
        """Detiene escaneo continuo"""
        if self.scanning:
            self.scanning = False
            self.config.config['continuous_scan'] = False
            self.config.save_config()

            self.show_notification("SmartCompute", "Escaneo continuo detenido")
            if self.icon:
                self.icon.menu = self.get_menu()

    def show_last_results(self, icon=None, item=None):
        """Muestra últimos resultados"""
        try:
            reports_dir = Path.home() / "smartcompute" / "reports"
            if reports_dir.exists():
                html_files = list(reports_dir.glob("*.html"))
                if html_files:
                    latest_report = max(html_files, key=lambda p: p.stat().st_mtime)
                    webbrowser.open(f"file://{latest_report.absolute()}")
                else:
                    self.show_notification("Info", "No se encontraron reportes")
            else:
                self.show_notification("Info", "Directorio de reportes no encontrado")
        except Exception as e:
            self.show_notification("Error", f"Error abriendo reportes: {e}")

    def export_reports(self, icon=None, item=None):
        """Exporta informes con cifrado opcional"""
        def export_worker():
            try:
                export_path = Path(self.config.config['export']['export_path'])
                export_path.mkdir(parents=True, exist_ok=True)

                # Buscar reportes recientes
                reports_dir = Path.home() / "smartcompute"
                report_files = []

                # Buscar archivos JSON y HTML
                for pattern in ["enterprise_analysis_*.json", "*.html"]:
                    report_files.extend(list(reports_dir.glob(pattern)))

                if not report_files:
                    self.show_notification("Info", "No se encontraron reportes para exportar")
                    return

                # Copiar archivos
                import shutil
                exported_count = 0

                for report_file in report_files:
                    dest_file = export_path / report_file.name
                    shutil.copy2(report_file, dest_file)

                    # Cifrar si está habilitado
                    if self.config.config['export']['encryption_enabled']:
                        self._encrypt_file(dest_file)

                    exported_count += 1

                self.show_notification("Éxito", f"{exported_count} reportes exportados a {export_path}")

            except Exception as e:
                self.show_notification("Error", f"Error exportando: {e}")

        threading.Thread(target=export_worker, daemon=True).start()

    def _encrypt_file(self, file_path: Path):
        """Cifra archivo usando AES"""
        try:
            from cryptography.fernet import Fernet
            import base64

            # Generar clave simple (en producción usar gestión segura de claves)
            key = Fernet.generate_key()
            fernet = Fernet(key)

            # Leer, cifrar y guardar
            with open(file_path, 'rb') as f:
                data = f.read()

            encrypted_data = fernet.encrypt(data)

            # Guardar archivo cifrado
            encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)

            # Guardar clave en archivo separado
            key_path = file_path.with_suffix(file_path.suffix + '.key')
            with open(key_path, 'wb') as f:
                f.write(key)

            # Eliminar archivo original
            file_path.unlink()

        except ImportError:
            print("Cryptography library not installed. Install: pip install cryptography")
        except Exception as e:
            print(f"Error encrypting file: {e}")

    def show_config(self, icon=None, item=None):
        """Muestra configuración"""
        self.show_main_window()

    def open_terminal(self, icon=None, item=None):
        """Abre terminal del sistema"""
        try:
            if self.is_windows:
                # Abrir PowerShell
                subprocess.Popen(["powershell.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Detectar terminal disponible en Linux
                terminals = ["gnome-terminal", "konsole", "xterm", "terminal"]
                for terminal in terminals:
                    try:
                        subprocess.Popen([terminal])
                        break
                    except FileNotFoundError:
                        continue
                else:
                    # Fallback a xterm
                    subprocess.Popen(["xterm"])
        except Exception as e:
            self.show_notification("Error", f"No se pudo abrir terminal: {e}")

    def manage_credentials(self, icon=None, item=None):
        """Gestiona credenciales"""
        # Implementar ventana de gestión de credenciales
        self.show_notification("Info", "Gestión de credenciales - En desarrollo")

    def show_help(self, icon=None, item=None):
        """Muestra ayuda"""
        help_text = """SmartCompute Enterprise - Ayuda

Funciones principales:
- Análisis Local: Escanea el sistema local
- Análisis de Red: Escanea rangos IP y dominios
- Análisis en Nube: Conecta con AWS, Azure, GCP
- Escaneo Continuo: Monitoreo automático
- Exportación Cifrada: Informes seguros

Comandos rápidos:
- Click derecho en icono: Menú completo
- Doble click: Ventana principal
- Ctrl+Shift+S: Iniciar/detener escaneo

Para más información: https://smartcompute.enterprise
"""
        messagebox.showinfo("Ayuda - SmartCompute Enterprise", help_text)

    def show_notification(self, title: str, message: str):
        """Muestra notificación del sistema"""
        if self.config.config['ui']['show_notifications']:
            if self.icon:
                self.icon.notify(message, title)
            else:
                print(f"{title}: {message}")

    def quit_application(self, icon=None, item=None):
        """Cierra aplicación"""
        self.stop_continuous_scan()
        if self.icon:
            self.icon.stop()

    def run(self):
        """Ejecuta aplicación de bandeja"""
        # Crear icono
        image = self.create_image(64, 64, 'white', 'blue')

        self.icon = pystray.Icon(
            "SmartCompute Enterprise",
            image,
            "SmartCompute Enterprise - Análisis de Seguridad",
            self.get_menu()
        )

        # Configurar doble click
        self.icon.run_detached()

        # Iniciar escaneo continuo si está configurado
        if self.config.config['continuous_scan']:
            self.start_continuous_scan()

        self.icon.run()


def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--install-service":
        # Instalar como servicio del sistema
        install_system_service()
    else:
        # Ejecutar aplicación de bandeja
        app = SmartComputeTrayApp()
        app.run()


def install_system_service():
    """Instala SmartCompute como servicio del sistema"""
    if platform.system() == "Windows":
        install_windows_service()
    else:
        install_linux_service()


def install_windows_service():
    """Instala servicio de Windows"""
    print("Instalando servicio de Windows...")
    # Implementar instalación de servicio Windows
    pass


def install_linux_service():
    """Instala servicio systemd de Linux"""
    print("Instalando servicio systemd...")

    service_content = f"""[Unit]
Description=SmartCompute Enterprise Security Analysis
After=network.target

[Service]
Type=simple
User=smartcompute
ExecStart={sys.executable} {__file__}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_path = Path("/etc/systemd/system/smartcompute.service")
    try:
        with open(service_path, 'w') as f:
            f.write(service_content)

        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable smartcompute")
        print("Servicio instalado correctamente")
    except Exception as e:
        print(f"Error instalando servicio: {e}")


if __name__ == "__main__":
    main()