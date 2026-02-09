#!/usr/bin/env python3
"""
Screenshot Capture Tool for SmartCompute
Automatically captures screenshots of generated dashboards for marketing
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def capture_express_dashboard():
    """Capture screenshot of Express dashboard"""
    print("📸 Capturing Express Dashboard screenshot...")

    # Run Express to generate dashboard
    print("   ⚙️  Generating Express dashboard...")
    result = subprocess.run(
        ['python3', 'smartcompute_express.py'],
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check if dashboard was created
    dashboard_path = '/home/gatux/smartcompute/smartcompute_express_dashboard.html'
    if not os.path.exists(dashboard_path):
        print(f"   ❌ Dashboard not found at {dashboard_path}")
        return False

    print(f"   ✅ Dashboard generated: {dashboard_path}")

    # Instructions for manual screenshot
    print("\n   📋 MANUAL SCREENSHOT INSTRUCTIONS:")
    print(f"   1. Open: file://{dashboard_path}")
    print("   2. Wait for charts to load (3 seconds)")
    print("   3. Take screenshot (Print Screen or Cmd+Shift+4)")
    print("   4. Save as: assets/screenshots/express_dashboard.png")
    print("   5. Crop to remove browser chrome")

    # Auto-open browser
    try:
        subprocess.run(['xdg-open', dashboard_path], timeout=5)
        print("   🌐 Browser opened automatically")
    except:
        pass

    return True

def capture_grafana_dashboard():
    """Instructions for capturing Grafana screenshots"""
    print("\n📸 Capturing Grafana Dashboard screenshot...")
    print("   📋 MANUAL INSTRUCTIONS:")
    print("   1. Start Docker stack: docker-compose -f docker-compose.quickstart.yml up -d")
    print("   2. Wait 60 seconds for services to start")
    print("   3. Open: http://localhost:3000")
    print("   4. Login: admin / smartcompute123")
    print("   5. Navigate to Dashboards → SmartCompute Overview")
    print("   6. Wait for metrics to load (10 seconds)")
    print("   7. Take screenshot")
    print("   8. Save as: assets/screenshots/grafana_dashboard.png")

def capture_docker_ps():
    """Capture docker ps output"""
    print("\n📸 Capturing Docker Stack screenshot...")
    print("   📋 MANUAL INSTRUCTIONS:")
    print("   1. Run: docker-compose -f docker-compose.quickstart.yml up -d")
    print("   2. Run: docker-compose ps")
    print("   3. Take screenshot of terminal showing all services")
    print("   4. Save as: assets/screenshots/docker_stack.png")

def create_demo_gif_instructions():
    """Instructions for creating demo GIF"""
    print("\n🎬 Creating Demo GIF...")
    print("   📋 INSTRUCTIONS:")
    print("   1. Install Gifski or LICEcap (for screen recording)")
    print("   2. Start recording")
    print("   3. Open terminal")
    print("   4. Type: cd SmartCompute")
    print("   5. Type: python3 smartcompute_express.py --auto-open")
    print("   6. Wait for dashboard to open and load")
    print("   7. Pan around dashboard showing metrics")
    print("   8. Stop recording after 10-15 seconds")
    print("   9. Export as: assets/demo.gif")
    print("   10. Optimize with: gifsicle -O3 demo.gif -o demo_optimized.gif")
    print("\n   Alternative: Use https://gifcap.dev (browser-based)")

def main():
    print("=" * 60)
    print("📸 SmartCompute Screenshot Capture Tool")
    print("=" * 60)
    print()

    # Create screenshots directory
    screenshots_dir = Path('assets/screenshots')
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Screenshots directory: {screenshots_dir}")
    print()

    # Capture screenshots
    print("Starting screenshot capture process...")
    print()

    # 1. Express Dashboard
    capture_express_dashboard()

    # 2. Grafana
    time.sleep(2)
    capture_grafana_dashboard()

    # 3. Docker Stack
    time.sleep(2)
    capture_docker_ps()

    # 4. Demo GIF
    time.sleep(2)
    create_demo_gif_instructions()

    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print("\nScreenshots needed:")
    print("   [ ] assets/screenshots/express_dashboard.png")
    print("   [ ] assets/screenshots/grafana_dashboard.png")
    print("   [ ] assets/screenshots/docker_stack.png")
    print("   [ ] assets/demo.gif")
    print("\nOnce captured, update README.md with:")
    print("   ![Express](./assets/screenshots/express_dashboard.png)")
    print("   ![Grafana](./assets/screenshots/grafana_dashboard.png)")
    print("   ![Demo](./assets/demo.gif)")
    print("\n✅ Done! Follow instructions above to capture screenshots manually.")
    print("=" * 60)

if __name__ == "__main__":
    main()
