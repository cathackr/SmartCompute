#!/usr/bin/env python3
"""
SmartCompute Simple Logo Creator
Generate basic logos for all platforms
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path


def create_simple_logo(size=512):
    """Create simple SmartCompute logo"""
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    primary_color = (46, 134, 171)      # #2E86AB
    secondary_color = (162, 59, 114)    # #A23B72
    accent_color = (241, 143, 1)        # #F18F01
    
    # Calculate proportions
    center = size // 2
    circle_radius = int(size * 0.4)
    
    # Draw main circle
    draw.ellipse([
        center - circle_radius,
        center - circle_radius,
        center + circle_radius,
        center + circle_radius
    ], fill=primary_color)
    
    # Draw inner circle
    inner_radius = int(size * 0.3)
    draw.ellipse([
        center - inner_radius,
        center - inner_radius,
        center + inner_radius,
        center + inner_radius
    ], fill=(255, 255, 255))
    
    # Draw brain pattern (simplified)
    brain_radius = int(size * 0.25)
    
    # Central nodes
    node_radius = int(size * 0.02)
    nodes = [
        (center, center - brain_radius//2),
        (center - brain_radius//2, center),
        (center + brain_radius//2, center),
        (center, center + brain_radius//2),
        (center - brain_radius//3, center - brain_radius//3),
        (center + brain_radius//3, center - brain_radius//3),
        (center - brain_radius//3, center + brain_radius//3),
        (center + brain_radius//3, center + brain_radius//3),
    ]
    
    # Draw connections
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes[i+1:], i+1):
            if abs(node1[0] - node2[0]) + abs(node1[1] - node2[1]) < brain_radius//1.5:
                draw.line([node1, node2], fill=secondary_color, width=2)
    
    # Draw nodes
    for i, (x, y) in enumerate(nodes):
        color = accent_color if i % 2 == 0 else secondary_color
        draw.ellipse([
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius
        ], fill=color)
    
    # Draw central CPU
    cpu_size = int(size * 0.06)
    draw.rectangle([
        center - cpu_size//2,
        center - cpu_size//2,
        center + cpu_size//2,
        center + cpu_size//2
    ], fill=(45, 55, 72), outline=primary_color, width=2)
    
    # Add text if size is large enough
    if size >= 256:
        try:
            font_size = max(12, size // 25)
            font = ImageFont.load_default()
            
            # Draw "SC" in center
            text = "SC"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            draw.text((
                center - text_width//2,
                center - text_height//2
            ), text, fill=(255, 255, 255), font=font)
            
        except Exception:
            pass
    
    return img


def create_all_icons():
    """Create all required icon sizes"""
    print("🎨 Creating SmartCompute icons...")
    
    # Ensure assets directory exists
    Path("assets").mkdir(exist_ok=True)
    
    # Icon sizes needed
    sizes = [16, 32, 48, 64, 96, 128, 192, 256, 512, 1024]
    
    for size in sizes:
        logo = create_simple_logo(size)
        logo.save(f'assets/icon_{size}.png')
        print(f"   ✓ Created: assets/icon_{size}.png")
    
    # Create main icons
    create_simple_logo(512).save('assets/cat_icon.png')
    create_simple_logo(256).save('assets/icon_large.png')
    create_simple_logo(64).save('assets/icon_small.png')
    
    print("   ✓ Created main icon files")
    
    # Create Android specific icons
    android_sizes = {
        'ldpi': 36, 'mdpi': 48, 'hdpi': 72,
        'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192
    }
    
    for density, size in android_sizes.items():
        logo = create_simple_logo(size)
        logo.save(f'assets/icon_android_{density}.png')
        print(f"   ✓ Created: assets/icon_android_{density}.png")
    
    # Create iOS specific icons
    ios_sizes = {
        20: 'settings_1x', 29: 'settings_2x', 40: 'spotlight_2x',
        58: 'settings_2x', 60: 'app_2x', 80: 'spotlight_3x',
        87: 'settings_3x', 120: 'app_2x', 180: 'app_3x', 1024: 'store'
    }
    
    for size, desc in ios_sizes.items():
        logo = create_simple_logo(size)
        logo.save(f'assets/icon_ios_{size}.png')
        print(f"   ✓ Created: assets/icon_ios_{size}.png ({desc})")
    
    # Create favicons
    for size in [16, 32, 96, 192]:
        logo = create_simple_logo(size)
        logo.save(f'assets/favicon_{size}x{size}.png')
        print(f"   ✓ Created: assets/favicon_{size}x{size}.png")
    
    return True


def create_branded_readme():
    """Create README with logo"""
    print("📖 Creating branded README...")
    
    readme_content = '''
<div align="center">
  <img src="assets/icon_large.png" alt="SmartCompute Logo" width="128" height="128">
  
  # 🧠 SmartCompute v2.0.1
  
  ### AI-Powered Security & Performance Monitoring Suite
  
  [![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-blue.svg)](https://github.com/cathackr/SmartCompute)
  [![Multi Platform](https://img.shields.io/badge/Platform-Multi--Platform-green.svg)](https://github.com/cathackr/SmartCompute)
  [![License](https://img.shields.io/badge/License-Commercial-red.svg)](https://github.com/cathackr/SmartCompute)
  
</div>

---

## 🎯 Overview

SmartCompute is an **enterprise-grade** AI-powered security and performance monitoring suite that provides:

- ⚡ **Real-time Threat Detection** with <50ms response time
- 🧠 **AI-Powered Analytics** with 95-99% accuracy
- 🔒 **Enterprise Security** with self-protection mechanisms  
- 📊 **Performance Monitoring** with minimal system impact
- 🛡️ **False Positive Reduction** by 85% using machine learning
- 🌍 **Multi-Platform Support** for Windows, macOS, Linux, Android, iOS

## 🚀 Quick Start

### Desktop Installation

```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
pip install -r requirements.txt
python main.py
```

### Mobile Installation

- **Android**: [Download APK](https://github.com/cathackr/SmartCompute/releases)
- **iOS**: Coming soon to App Store

## 📊 Enterprise Results

| Industry | ROI | Deployment Time | Satisfaction |
|----------|-----|----------------|--------------|
| Banking & Finance | 420% | 6 hours | 9.2/10 |
| Healthcare | 285% | 4 hours | 8.9/10 |
| Manufacturing | 515% | 8 hours | 9.4/10 |
| SaaS Technology | 225% | 3 hours | 8.7/10 |

## 💰 Pricing

- **🔍 STARTER**: $199 setup + $89/month
- **🏢 BUSINESS**: $499 setup + $199/month  
- **🏭 ENTERPRISE**: $999 setup + $399/month

**Special Discounts (Non-cumulative):**
- 🇦🇷 Argentine Companies: 25% OFF
- 🪙 Crypto Payment: 15% OFF
- 💸 Annual Payment: 30% OFF
- 🎓 Startups/NGOs: 40% OFF

*Note: Discounts are exclusive - only the highest applicable discount applies.*

## 📱 Downloads

### Desktop
- **Windows**: [SmartCompute-Setup-2.0.1.exe](https://github.com/cathackr/SmartCompute/releases)
- **macOS**: [SmartCompute-2.0.1.dmg](https://github.com/cathackr/SmartCompute/releases)
- **Linux**: [smartcompute_2.0.1_amd64.deb](https://github.com/cathackr/SmartCompute/releases)

### Mobile
- **Android**: [Google Play Store](https://play.google.com/store)
- **iOS**: [App Store](https://apps.apple.com) (coming soon)

## 📚 Documentation

- 📖 [Technical Documentation](TECHNICAL_ENTERPRISE_DOCUMENTATION.md)
- 🚀 [Quick Start Guide](https://smartcompute.ar/quickstart)
- 💼 [Enterprise Guide](https://smartcompute.ar/enterprise)

## 👨‍💻 Creator

**SmartCompute** is created by **Martín Iribarne** - **CEH (Certified Ethical Hacker)**

🛡️ **Senior Cybersecurity & Networks Specialist** with 10+ years of experience in:
- 🔐 **Industrial Network Security** (ISA/IEC 62443 certified)
- 🎯 **Penetration Testing & Vulnerability Assessment**
- 📊 **SIEM Implementation & Security Monitoring**
- ☁️ **Cloud Security** (Azure AZ-900, AWS Cloud Practitioner)
- 🌐 **Network Infrastructure** (CCNA certified)

- 🔗 **LinkedIn**: [Martín Iribarne CEH](https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/)
- 📧 **Contact**: ggwre04p0@mozmail.com | ggwre04p0@mozmail.com
- 📍 **Location**: Mar del Plata, Argentina
- 🐙 **GitHub**: [cathackr](https://github.com/cathackr)

---

## 📞 Support

- **📧 Email**: ggwre04p0@mozmail.com
- **🐙 Issues**: [GitHub Issues](https://github.com/cathackr/SmartCompute/issues)
- **💼 Enterprise**: 24/7 support available

---

© 2024 SmartCompute. All rights reserved.

<div align="center">
  
### 🚀 **Ready to revolutionize your security monitoring?**

[**Download SmartCompute**](https://github.com/cathackr/SmartCompute/releases) • [**Get Enterprise Quote**](mailto:ggwre04p0@mozmail.com)

</div>
'''
    
    with open('README.md', 'w') as f:
        f.write(readme_content.strip())
    
    print("   ✓ Created branded README.md")


def main():
    """Main function"""
    print("🎨 SmartCompute Simple Logo Creator")
    print("=" * 40)
    
    create_all_icons()
    create_branded_readme()
    
    print("\n✅ Logo creation completed successfully!")
    print("\n📁 Created assets:")
    print("   • Platform-specific icons in multiple sizes")
    print("   • Android density-specific icons")
    print("   • iOS app icons for all sizes")
    print("   • Favicons for web")
    print("   • Branded README.md")
    print("\n💡 Next steps:")
    print("   1. Add your personal info to README.md")
    print("   2. Build applications using created assets")
    print("   3. Submit to app stores")


if __name__ == "__main__":
    main()