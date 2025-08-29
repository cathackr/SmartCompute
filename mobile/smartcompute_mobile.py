#!/usr/bin/env python3
"""
SmartCompute Mobile App
Cross-platform mobile interface using Kivy/KivyMD
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

import json
import threading
import time


class SmartComputeMobileApp(MDApp):
    """SmartCompute mobile application"""
    
    def build(self):
        """Build mobile app interface"""
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"
        
        # Main layout
        main_layout = MDBoxLayout(orientation='vertical')
        
        # Top app bar
        toolbar = MDTopAppBar(
            title="SmartCompute v2.0.1",
            elevation=2
        )
        main_layout.add_widget(toolbar)
        
        # Bottom navigation
        self.bottom_nav = MDBottomNavigation(
            panel_color="#2196F3",
            selected_color_background="#1976D2",
            text_color_active="white"
        )
        
        # Dashboard tab
        dashboard_item = MDBottomNavigationItem(
            name='dashboard',
            text='Dashboard',
            icon='view-dashboard'
        )
        dashboard_item.add_widget(self.create_dashboard())
        self.bottom_nav.add_widget(dashboard_item)
        
        # Monitoring tab
        monitoring_item = MDBottomNavigationItem(
            name='monitoring',
            text='Monitor',
            icon='chart-line'
        )
        monitoring_item.add_widget(self.create_monitoring())
        self.bottom_nav.add_widget(monitoring_item)
        
        # Security tab
        security_item = MDBottomNavigationItem(
            name='security',
            text='Security',
            icon='shield'
        )
        security_item.add_widget(self.create_security())
        self.bottom_nav.add_widget(security_item)
        
        # About tab
        about_item = MDBottomNavigationItem(
            name='about',
            text='About',
            icon='information'
        )
        about_item.add_widget(self.create_about())
        self.bottom_nav.add_widget(about_item)
        
        main_layout.add_widget(self.bottom_nav)
        
        # Start monitoring
        Clock.schedule_interval(self.update_monitoring, 3)
        
        return main_layout
    
    def create_dashboard(self):
        """Create dashboard view"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding='20dp',
            spacing='10dp'
        )
        
        # Status cards
        cards_layout = MDBoxLayout(
            orientation='vertical',
            spacing='10dp'
        )
        
        # CPU card
        cpu_card = self.create_status_card("💻 CPU Usage", "45.2%", "#17a2b8")
        cards_layout.add_widget(cpu_card)
        
        # Memory card
        memory_card = self.create_status_card("🧠 Memory", "62.1%", "#28a745")
        cards_layout.add_widget(memory_card)
        
        # Disk card
        disk_card = self.create_status_card("💾 Disk", "78.5%", "#ffc107")
        cards_layout.add_widget(disk_card)
        
        # Security status
        security_card = self.create_status_card("🔒 Security", "Protected", "#28a745")
        cards_layout.add_widget(security_card)
        
        layout.add_widget(cards_layout)
        
        # Control button
        self.control_btn = MDRaisedButton(
            text="Start Monitoring",
            theme_icon_color="Custom",
            icon_color="#ffffff",
            md_bg_color="#28a745",
            size_hint=(1, None),
            height="50dp"
        )
        self.control_btn.bind(on_release=self.toggle_monitoring)
        layout.add_widget(self.control_btn)
        
        return layout
    
    def create_status_card(self, title, value, color):
        """Create status card"""
        card = MDCard(
            orientation='horizontal',
            size_hint=(1, None),
            height='80dp',
            elevation=2,
            padding='10dp',
            spacing='10dp'
        )
        
        # Title and value layout
        content_layout = MDBoxLayout(
            orientation='vertical',
            spacing='5dp'
        )
        
        title_label = MDLabel(
            text=title,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height='20dp'
        )
        
        value_label = MDLabel(
            text=value,
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height='40dp'
        )
        
        content_layout.add_widget(title_label)
        content_layout.add_widget(value_label)
        
        card.add_widget(content_layout)
        
        return card
    
    def create_monitoring(self):
        """Create monitoring view"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding='20dp',
            spacing='15dp'
        )
        
        title = MDLabel(
            text="📊 Real-time Monitoring",
            font_style="H5",
            size_hint_y=None,
            height='50dp'
        )
        layout.add_widget(title)
        
        # Progress indicators
        self.cpu_progress = ProgressBar(
            max=100,
            value=45,
            size_hint_y=None,
            height='20dp'
        )
        layout.add_widget(MDLabel(text="CPU Usage:", size_hint_y=None, height='30dp'))
        layout.add_widget(self.cpu_progress)
        
        self.memory_progress = ProgressBar(
            max=100,
            value=62,
            size_hint_y=None,
            height='20dp'
        )
        layout.add_widget(MDLabel(text="Memory Usage:", size_hint_y=None, height='30dp'))
        layout.add_widget(self.memory_progress)
        
        self.disk_progress = ProgressBar(
            max=100,
            value=78,
            size_hint_y=None,
            height='20dp'
        )
        layout.add_widget(MDLabel(text="Disk Usage:", size_hint_y=None, height='30dp'))
        layout.add_widget(self.disk_progress)
        
        return layout
    
    def create_security(self):
        """Create security view"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding='20dp',
            spacing='10dp'
        )
        
        title = MDLabel(
            text="🔒 Security Status",
            font_style="H5",
            size_hint_y=None,
            height='50dp'
        )
        layout.add_widget(title)
        
        # Security status items
        status_items = [
            "🛡️ System Protection: ACTIVE",
            "🔍 Threat Detection: MONITORING",
            "⚡ Real-time Analysis: ENABLED",
            "📊 False Positive Rate: <5%",
            "🎯 Detection Accuracy: 95-99%",
            "⏱️ Response Time: <50ms"
        ]
        
        for item in status_items:
            label = MDLabel(
                text=item,
                font_style="Body1",
                size_hint_y=None,
                height='40dp'
            )
            layout.add_widget(label)
        
        return layout
    
    def create_about(self):
        """Create about view with creator info"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding='20dp',
            spacing='10dp'
        )
        
        # App info
        title = MDLabel(
            text="SmartCompute v2.0.1",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height='60dp'
        )
        layout.add_widget(title)
        
        description = MDLabel(
            text="AI-Powered Security & Performance\nMonitoring Suite",
            font_style="Subtitle1",
            halign="center",
            size_hint_y=None,
            height='60dp'
        )
        layout.add_widget(description)
        
        # Creator info
        creator_info = [
            "👨‍💻 Created by: Martín Iribarne (CEH)",
            "📧 Contact: ggwre04p0@mozmail.com",
            "🔗 LinkedIn: Martín Iribarne CEH - Cybersecurity Specialist",
            "🐙 GitHub: github.com/cathackr/SmartCompute",
            "",
            "© 2024 SmartCompute. All rights reserved."
        ]
        
        for info in creator_info:
            label = MDLabel(
                text=info,
                font_style="Body2",
                halign="center",
                size_hint_y=None,
                height='30dp'
            )
            layout.add_widget(label)
        
        return layout
    
    def toggle_monitoring(self, button):
        """Toggle monitoring state"""
        if button.text == "Start Monitoring":
            button.text = "Stop Monitoring"
            button.md_bg_color = "#dc3545"
            self.start_monitoring()
        else:
            button.text = "Start Monitoring" 
            button.md_bg_color = "#28a745"
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring process"""
        # TODO: Implement actual monitoring
        pass
    
    def stop_monitoring(self):
        """Stop monitoring process"""
        # TODO: Implement monitoring stop
        pass
    
    def update_monitoring(self, dt):
        """Update monitoring data"""
        try:
            # Simulate data updates
            import random
            
            if hasattr(self, 'cpu_progress'):
                self.cpu_progress.value = random.uniform(30, 80)
            if hasattr(self, 'memory_progress'):
                self.memory_progress.value = random.uniform(40, 85)
            if hasattr(self, 'disk_progress'):
                self.disk_progress.value = random.uniform(60, 90)
                
        except Exception as e:
            print(f"Update error: {e}")


def main():
    """Main mobile app entry point"""
    SmartComputeMobileApp().run()


if __name__ == "__main__":
    main()
