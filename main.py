#!/usr/bin/env python3
"""
SmartCompute - Main Entry Point
Performance-based anomaly detection system
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

from app.core.smart_compute import SmartComputeEngine
from app.core.portable_system import PortableSystemDetector
from app.services.monitoring import MonitoringService


def run_demo():
    """Run SmartCompute demonstration"""
    print("="*70)
    print("🧠 SMARTCOMPUTE - Performance-based Anomaly Detection")
    print("="*70)
    
    # Initialize system
    print("\n🔍 Detecting system capabilities...")
    detector = PortableSystemDetector()
    
    print("\n🚀 Initializing SmartCompute engine...")
    engine = SmartComputeEngine()
    
    # Demo menu
    print("\n" + "="*50)
    print("What would you like to do?")
    print("1. Quick Performance Optimization Demo")
    print("2. System Baseline and Anomaly Detection")
    print("3. Full System Report")
    print("4. Start Monitoring Service (Ctrl+C to stop)")
    print("5. API Server Mode")
    
    try:
        choice = input("\nSelect option (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return
    
    if choice == '1':
        run_optimization_demo(engine)
    elif choice == '2':
        run_anomaly_demo(detector)
    elif choice == '3':
        run_report_demo(detector)
    elif choice == '4':
        asyncio.run(run_monitoring_demo(detector))
    elif choice == '5':
        run_api_server()
    else:
        print("Invalid option. Please run again.")


def run_optimization_demo(engine: SmartComputeEngine):
    """Run optimization demonstration"""
    import numpy as np
    
    print("\n🔬 Performance Optimization Demo")
    print("-" * 40)
    
    # Test different scenarios
    test_cases = [
        {
            'name': 'High Precision Required',
            'size': (300, 300),
            'precision': 0.99,
            'speed': 0.2
        },
        {
            'name': 'Balanced Performance',
            'size': (500, 500),
            'precision': 0.95,
            'speed': 0.5
        },
        {
            'name': 'Speed Priority',
            'size': (400, 400),
            'precision': 0.90,
            'speed': 0.8
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🎯 Test {i}: {test['name']}")
        print(f"Matrix size: {test['size']}")
        
        # Generate test matrices
        np.random.seed(42 + i)
        a = np.random.rand(*test['size'])
        b = np.random.rand(*test['size'])
        
        # Run optimization
        result = engine.smart_multiply(
            a, b,
            precision_needed=test['precision'],
            speed_priority=test['speed']
        )
        
        print(f"✅ Result: {result['method']}")
        print(f"⚡ Speedup: {result['speedup']:.2f}x")
        print(f"📊 Accuracy: {result['accuracy']:.1%}")
    
    # Show summary
    print(f"\n📈 Performance Summary:")
    summary = engine.get_performance_summary()
    for key, value in summary.items():
        if key != 'operations':
            print(f"   {key}: {value}")


def run_anomaly_demo(detector: PortableSystemDetector):
    """Run anomaly detection demonstration"""
    import time
    
    print("\n🛡️ Anomaly Detection Demo")
    print("-" * 40)
    
    print("📊 Establishing performance baseline (30 seconds)...")
    baseline = detector.run_performance_baseline(30)
    
    print(f"\n✅ Baseline established:")
    for key, value in baseline.items():
        print(f"   {key}: {value:.2f}")
    
    print(f"\n⚠️ Monitoring for anomalies (press Ctrl+C to stop)...")
    try:
        while True:
            anomaly = detector.detect_anomalies()
            print(f"   Score: {anomaly['anomaly_score']:.1f} | "
                  f"Severity: {anomaly['severity']} | "
                  f"CPU: {anomaly['cpu_current']:.1f}% | "
                  f"Memory: {anomaly['memory_current']:.1f}%")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n🔚 Monitoring stopped.")


def run_report_demo(detector: PortableSystemDetector):
    """Run report generation demonstration"""
    import json
    import time
    
    print("\n📄 System Report Generation")
    print("-" * 40)
    
    print("🔍 Analyzing system performance...")
    detector.run_performance_baseline(20)
    
    print("📊 Generating comprehensive report...")
    report = detector.generate_report()
    
    # Save report
    filename = f"smartcompute_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
    filepath = Path(filename)
    
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved: {filepath.absolute()}")
    print(f"\n📋 System Summary:")
    print(f"   OS: {report['system_profile']['os']}")
    print(f"   Architecture: {report['system_profile']['architecture']}")
    print(f"   CPU: {report['system_profile']['cpu']}")
    print(f"   GPU: {report['system_profile']['gpu']}")
    print(f"   Optimizations: {len(report['optimization_applied']['optimizations_applied'])}")
    print(f"   Performance Gain: +{report['optimization_applied']['performance_gain']}%")
    
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"   • {rec}")


async def run_monitoring_demo(detector: PortableSystemDetector):
    """Run continuous monitoring demonstration"""
    print("\n⚡ Continuous Monitoring Service")
    print("-" * 40)
    
    # Establish baseline first
    print("📊 Establishing baseline...")
    detector.run_performance_baseline(20)
    
    # Initialize monitoring service
    monitoring = MonitoringService(detector, check_interval=3)
    
    # Start monitoring
    print("🚀 Starting monitoring service...")
    await monitoring.start_monitoring()
    
    try:
        # Show status updates
        while monitoring.is_monitoring:
            await asyncio.sleep(10)
            status = await monitoring.get_status()
            print(f"   Checks: {status['metrics_history_size']} | "
                  f"Alerts: {status['total_alerts']} | "
                  f"Recent alerts: {status['recent_alerts']}")
    
    except KeyboardInterrupt:
        print("\n🔚 Stopping monitoring service...")
        await monitoring.stop_monitoring()
        
        # Show final statistics
        stats = monitoring.get_statistics()
        if 'error' not in stats:
            print(f"\n📊 Final Statistics:")
            print(f"   Duration: {stats['monitoring_duration_hours']:.1f} hours")
            print(f"   Total checks: {stats['total_checks']}")
            print(f"   Alerts generated: {stats['anomaly_stats']['alerts_generated']}")
            print(f"   Max anomaly score: {stats['anomaly_stats']['max_score']:.1f}")


def run_api_server():
    """Run FastAPI server"""
    import uvicorn
    from app.api.main import app
    
    print("\n🌐 Starting SmartCompute API Server")
    print("-" * 40)
    print("🔗 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🔚 API server stopped.")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SmartCompute - Performance-based anomaly detection system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive demo mode
  python main.py --api              # Start API server
  python main.py --optimize         # Quick optimization demo
  python main.py --monitor          # Start monitoring service
  python main.py --report           # Generate system report
        """
    )
    
    parser.add_argument('--api', action='store_true', 
                       help='Start API server mode')
    parser.add_argument('--optimize', action='store_true',
                       help='Run optimization demonstration')
    parser.add_argument('--monitor', action='store_true',
                       help='Start monitoring service')
    parser.add_argument('--report', action='store_true',
                       help='Generate system report')
    parser.add_argument('--port', type=int, default=8000,
                       help='API server port (default: 8000)')
    
    args = parser.parse_args()
    
    if args.api:
        # Override port if specified
        if args.port != 8000:
            import uvicorn
            from app.api.main import app
            uvicorn.run(app, host="0.0.0.0", port=args.port)
        else:
            run_api_server()
    elif args.optimize:
        detector = PortableSystemDetector()
        engine = SmartComputeEngine()
        run_optimization_demo(engine)
    elif args.monitor:
        detector = PortableSystemDetector()
        asyncio.run(run_monitoring_demo(detector))
    elif args.report:
        detector = PortableSystemDetector()
        run_report_demo(detector)
    else:
        # Interactive demo mode
        run_demo()


if __name__ == "__main__":
    main()