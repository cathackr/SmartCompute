#!/usr/bin/env python3
"""
SmartCompute Interactive Demo for Google Colab
Optimized for mobile and web browser viewing
"""

import time
import json
import random
from datetime import datetime
from IPython.display import display, HTML, clear_output
import matplotlib.pyplot as plt
import numpy as np

# Import our existing synthetic demo
from synthetic_demo import SyntheticTrafficGenerator, SyntheticThreatDetector

def display_header():
    """Display animated header for Colab"""
    header_html = """
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; color: white; text-align: center;
                margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
        <h1 style='margin: 0; font-size: 2.5em;'>🧠 SmartCompute Demo</h1>
        <p style='margin: 5px 0; font-size: 1.2em; opacity: 0.9;'>
            Análisis de Ciberseguridad en Tiempo Real
        </p>
        <div style='font-size: 0.9em; margin-top: 10px;'>
            📱 Optimizado para móviles | 🌐 Universal | ⚡ GPU Acelerado
        </div>
    </div>
    """
    display(HTML(header_html))

def create_live_chart(stats_history, threats_timeline):
    """Create real-time charts for the demo"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor('#f8f9fa')
    
    # Chart 1: Processing Speed
    times = [s['timestamp'] for s in stats_history]
    processing_times = [s['avg_processing_time'] for s in stats_history]
    
    ax1.plot(times, processing_times, 'b-', linewidth=2, marker='o')
    ax1.set_title('⚡ Velocidad de Procesamiento (ms)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Tiempo (ms)')
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor('#ffffff')
    
    # Chart 2: Threats Detection Rate
    detection_rates = [s['detection_rate'] for s in stats_history]
    ax2.plot(times, detection_rates, 'r-', linewidth=2, marker='s')
    ax2.set_title('🎯 Tasa de Detección (%)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Detección (%)')
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor('#ffffff')
    
    # Chart 3: Threat Types Distribution
    if threats_timeline:
        threat_types = {}
        for threat in threats_timeline[-20:]:  # Last 20 threats
            threat_type = threat.get('type', 'Unknown')
            threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
        
        if threat_types:
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7']
            wedges, texts, autotexts = ax3.pie(
                threat_types.values(), 
                labels=threat_types.keys(),
                autopct='%1.1f%%',
                colors=colors[:len(threat_types)],
                startangle=90
            )
            ax3.set_title('🚨 Tipos de Amenazas', fontsize=14, fontweight='bold')
    
    # Chart 4: Security Score Timeline
    security_scores = []
    for i, s in enumerate(stats_history):
        base_score = 85
        threat_penalty = s['detection_rate'] * 0.3
        speed_bonus = max(0, (50 - s['avg_processing_time']) * 0.5)
        score = max(0, min(100, base_score - threat_penalty + speed_bonus))
        security_scores.append(score)
    
    colors = ['#2ecc71' if s >= 80 else '#f39c12' if s >= 60 else '#e74c3c' for s in security_scores]
    ax4.bar(range(len(security_scores)), security_scores, color=colors, alpha=0.7)
    ax4.set_title('🛡️ Puntuación de Seguridad', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Puntuación (0-100)')
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3)
    ax4.set_facecolor('#ffffff')
    
    plt.tight_layout()
    plt.show()

def display_real_time_stats(stats, total_events, elapsed_time):
    """Display real-time statistics in a mobile-friendly format"""
    stats_html = f"""
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 15px; margin: 20px 0;'>
        <div style='background: linear-gradient(135deg, #3498db, #2980b9); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 1.1em;'>📊 Eventos Procesados</h3>
            <div style='font-size: 2.5em; font-weight: bold; margin: 10px 0;'>{total_events}</div>
            <div style='opacity: 0.8;'>En {elapsed_time:.1f} segundos</div>
        </div>
        
        <div style='background: linear-gradient(135deg, #e74c3c, #c0392b); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 1.1em;'>🚨 Amenazas Detectadas</h3>
            <div style='font-size: 2.5em; font-weight: bold; margin: 10px 0;'>{stats['threats_detected']}</div>
            <div style='opacity: 0.8;'>{stats['threat_detection_rate']:.1f}% del tráfico</div>
        </div>
        
        <div style='background: linear-gradient(135deg, #2ecc71, #27ae60); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 1.1em;'>⚡ Velocidad Promedio</h3>
            <div style='font-size: 2.5em; font-weight: bold; margin: 10px 0;'>{stats['avg_processing_time']:.1f}</div>
            <div style='opacity: 0.8;'>milisegundos por evento</div>
        </div>
        
        <div style='background: linear-gradient(135deg, #9b59b6, #8e44ad); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 1.1em;'>🎯 Rendimiento</h3>
            <div style='font-size: 2.5em; font-weight: bold; margin: 10px 0;'>
                {"✅ EXC" if stats['avg_processing_time'] < 10 else 
                 "✅ BUE" if stats['avg_processing_time'] < 25 else 
                 "⚠️ REG"}
            </div>
            <div style='opacity: 0.8;'>Clasificación de velocidad</div>
        </div>
    </div>
    """
    display(HTML(stats_html))

def display_threat_alert(threat_event, threat_result):
    """Display threat alert in mobile-friendly format"""
    threat_color = "#e74c3c" if threat_result.threat_score > 0.8 else \
                   "#f39c12" if threat_result.threat_score > 0.6 else "#3498db"
    
    threat_level = "🔴 CRÍTICA" if threat_result.threat_score > 0.8 else \
                   "🟡 ALTA" if threat_result.threat_score > 0.6 else \
                   "🟠 MEDIA"
    
    alert_html = f"""
    <div style='background: {threat_color}; color: white; padding: 15px; 
                margin: 10px 0; border-radius: 10px; border-left: 5px solid white;'>
        <div style='display: flex; justify-content: space-between; align-items: center; 
                    flex-wrap: wrap; gap: 10px;'>
            <div>
                <strong style='font-size: 1.1em;'>{threat_level}</strong>
                <div style='opacity: 0.9; margin-top: 5px;'>
                    {threat_event.src_ip}:{threat_event.src_port} → {threat_event.dst_ip}:{threat_event.dst_port}
                </div>
                <div style='opacity: 0.8; font-size: 0.9em; margin-top: 3px;'>
                    Tipo: {threat_result.threat_type or 'Desconocido'} | 
                    Confianza: {threat_result.confidence:.0%}
                </div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 1.5em; font-weight: bold;'>
                    {threat_result.threat_score:.2f}
                </div>
                <div style='opacity: 0.8; font-size: 0.8em;'>Score</div>
            </div>
        </div>
    </div>
    """
    display(HTML(alert_html))

def run_interactive_demo():
    """Run interactive demo optimized for Colab"""
    display_header()
    
    # Initialize components
    traffic_generator = SyntheticTrafficGenerator()
    threat_detector = SyntheticThreatDetector()
    
    # Demo configuration
    total_events = 150  # Reduced for mobile viewing
    batch_size = 10
    stats_history = []
    threats_timeline = []
    start_time = time.time()
    
    print("🚀 Iniciando análisis en tiempo real...")
    print("=" * 50)
    
    # Generate and analyze traffic in batches
    all_events = []
    normal_events = traffic_generator.generate_normal_traffic()
    threat_events = traffic_generator.generate_threat_traffic()
    all_events = (normal_events + threat_events)[:total_events]
    random.shuffle(all_events)
    
    processed = 0
    for i in range(0, len(all_events), batch_size):
        batch = all_events[i:i+batch_size]
        
        print(f"\n🔄 Procesando lote {(i//batch_size)+1}...")
        
        # Analyze batch
        for event in batch:
            result = threat_detector.analyze(event)
            processed += 1
            
            # Display threats in real-time
            if result.is_threat and len(threats_timeline) < 10:  # Limit display
                display_threat_alert(event, result)
                threats_timeline.append({
                    'timestamp': datetime.now(),
                    'type': result.threat_type,
                    'score': result.threat_score,
                    'source': event.src_ip,
                    'target': event.dst_ip
                })
        
        # Update stats
        current_stats = threat_detector.get_stats()
        current_stats['timestamp'] = i // batch_size
        stats_history.append(current_stats)
        
        # Display live stats
        elapsed = time.time() - start_time
        display_real_time_stats(current_stats, processed, elapsed)
        
        # Small delay for real-time effect
        time.sleep(0.5)
    
    # Final summary
    final_stats = threat_detector.get_stats()
    elapsed_total = time.time() - start_time
    
    print(f"\n🎉 ¡Demo Completado!")
    print("=" * 30)
    
    # Create final visualizations
    create_live_chart(stats_history, threats_timeline)
    
    # Performance summary
    summary_html = f"""
    <div style='background: linear-gradient(135deg, #2c3e50, #34495e); 
                color: white; padding: 30px; border-radius: 15px; margin: 20px 0;'>
        <h2 style='text-align: center; margin-bottom: 25px;'>📊 Resumen Final</h2>
        
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; margin: 20px 0;'>
            <div style='text-align: center;'>
                <div style='font-size: 3em; margin: 10px 0;'>⚡</div>
                <div style='font-size: 1.5em; font-weight: bold;'>{final_stats['avg_processing_time']:.2f}ms</div>
                <div style='opacity: 0.8;'>Velocidad Promedio</div>
            </div>
            
            <div style='text-align: center;'>
                <div style='font-size: 3em; margin: 10px 0;'>🎯</div>
                <div style='font-size: 1.5em; font-weight: bold;'>{final_stats['threat_detection_rate']:.1f}%</div>
                <div style='opacity: 0.8;'>Tasa de Detección</div>
            </div>
            
            <div style='text-align: center;'>
                <div style='font-size: 3em; margin: 10px 0;'>⏱️</div>
                <div style='font-size: 1.5em; font-weight: bold;'>{elapsed_total:.1f}s</div>
                <div style='opacity: 0.8;'>Tiempo Total</div>
            </div>
            
            <div style='text-align: center;'>
                <div style='font-size: 3em; margin: 10px 0;'>🛡️</div>
                <div style='font-size: 1.5em; font-weight: bold;'>{'✅ EXC' if final_stats['avg_processing_time'] < 10 else '✅ BUENO'}</div>
                <div style='opacity: 0.8;'>Rendimiento</div>
            </div>
        </div>
        
        <div style='text-align: center; margin-top: 25px; padding-top: 20px; 
                    border-top: 1px solid rgba(255,255,255,0.2);'>
            <p style='margin: 5px 0; opacity: 0.9;'>
                🧠 SmartCompute procesó <strong>{processed} eventos</strong> de red detectando 
                <strong>{final_stats['threats_detected']} amenazas</strong> con un rendimiento excelente.
            </p>
            <p style='margin: 15px 0; color: #3498db; font-weight: bold;'>
                ¡Listo para proteger tu red en producción! 🚀
            </p>
        </div>
    </div>
    """
    
    display(HTML(summary_html))
    
    return {
        'events_processed': processed,
        'threats_detected': final_stats['threats_detected'],
        'avg_processing_time': final_stats['avg_processing_time'],
        'total_time': elapsed_total,
        'demo_success': True
    }

# Instructions for Colab users
colab_instructions = """
🎮 INSTRUCCIONES PARA GOOGLE COLAB:

1. Ejecuta esta celda para ver el demo interactivo
2. Las amenazas aparecerán en tiempo real con alertas coloridas
3. Los gráficos se actualizarán automáticamente
4. Optimizado para móviles - funciona perfecto en iPhone/Android
5. ¡Comparte tu pantalla para impresionar colegas!

👆 Ejecuta la función run_interactive_demo() abajo
"""

if __name__ == "__main__":
    print(colab_instructions)
    print("\n" + "="*60)
    result = run_interactive_demo()
    print(f"\n✅ Demo ejecutado exitosamente: {result}")