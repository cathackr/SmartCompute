#!/usr/bin/env python3
"""
SmartCompute Cat Logo Creator
Generate cat-themed logo with screen design using blue, red, green, and black
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path


def create_cat_screen_logo(size=512):
    """Create SmartCompute cat on screen logo"""
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Color scheme: Blue, Red, Green, Black
    screen_black = (25, 25, 25)      # Dark screen frame
    screen_blue = (0, 120, 255)      # Blue screen glow
    cat_red = (220, 50, 47)          # Red cat body
    cat_green = (46, 160, 67)        # Green cat accents
    highlight_white = (255, 255, 255) # White highlights
    
    # Calculate proportions
    center = size // 2
    screen_width = int(size * 0.85)
    screen_height = int(size * 0.75)
    
    # Draw computer screen/monitor frame
    screen_frame = [
        center - screen_width//2,
        center - screen_height//2,
        center + screen_width//2,
        center + screen_height//2
    ]
    
    # Screen outer frame (black)
    frame_thickness = int(size * 0.04)
    outer_frame = [
        screen_frame[0] - frame_thickness,
        screen_frame[1] - frame_thickness,
        screen_frame[2] + frame_thickness,
        screen_frame[3] + frame_thickness
    ]
    draw.rounded_rectangle(outer_frame, radius=int(size*0.03), fill=screen_black)
    
    # Screen inner display (blue background)
    draw.rounded_rectangle(screen_frame, radius=int(size*0.02), fill=screen_blue)
    
    # Screen scanlines effect
    for y in range(screen_frame[1], screen_frame[3], 4):
        draw.line([screen_frame[0], y, screen_frame[2], y], 
                 fill=(0, 100, 200, 100), width=1)
    
    # Cat design on screen
    cat_center_x = center
    cat_center_y = center - int(size * 0.05)
    
    # Cat body (red)
    body_width = int(size * 0.25)
    body_height = int(size * 0.35)
    cat_body = [
        cat_center_x - body_width//2,
        cat_center_y - body_height//4,
        cat_center_x + body_width//2,
        cat_center_y + body_height//2
    ]
    draw.ellipse(cat_body, fill=cat_red)
    
    # Cat head (red)
    head_size = int(size * 0.22)
    cat_head = [
        cat_center_x - head_size//2,
        cat_center_y - body_height//2,
        cat_center_x + head_size//2,
        cat_center_y - body_height//4 + int(size * 0.03)
    ]
    draw.ellipse(cat_head, fill=cat_red)
    
    # Cat ears (black)
    ear_size = int(size * 0.06)
    # Left ear
    left_ear = [
        cat_center_x - int(size * 0.08),
        cat_center_y - body_height//2 - int(size * 0.02),
        cat_center_x - int(size * 0.08) + ear_size,
        cat_center_y - body_height//2 + ear_size//2
    ]
    draw.ellipse(left_ear, fill=screen_black)
    
    # Right ear
    right_ear = [
        cat_center_x + int(size * 0.08) - ear_size,
        cat_center_y - body_height//2 - int(size * 0.02),
        cat_center_x + int(size * 0.08),
        cat_center_y - body_height//2 + ear_size//2
    ]
    draw.ellipse(right_ear, fill=screen_black)
    
    # Cat eyes (green)
    eye_size = int(size * 0.035)
    # Left eye
    left_eye = [
        cat_center_x - int(size * 0.05),
        cat_center_y - body_height//2 + int(size * 0.06),
        cat_center_x - int(size * 0.05) + eye_size,
        cat_center_y - body_height//2 + int(size * 0.06) + eye_size
    ]
    draw.ellipse(left_eye, fill=cat_green)
    
    # Right eye
    right_eye = [
        cat_center_x + int(size * 0.05) - eye_size,
        cat_center_y - body_height//2 + int(size * 0.06),
        cat_center_x + int(size * 0.05),
        cat_center_y - body_height//2 + int(size * 0.06) + eye_size
    ]
    draw.ellipse(right_eye, fill=cat_green)
    
    # Cat eye pupils (black)
    pupil_size = int(size * 0.015)
    # Left pupil
    draw.ellipse([
        left_eye[0] + (eye_size - pupil_size)//2,
        left_eye[1] + (eye_size - pupil_size)//2,
        left_eye[0] + (eye_size + pupil_size)//2,
        left_eye[1] + (eye_size + pupil_size)//2
    ], fill=screen_black)
    
    # Right pupil
    draw.ellipse([
        right_eye[0] + (eye_size - pupil_size)//2,
        right_eye[1] + (eye_size - pupil_size)//2,
        right_eye[0] + (eye_size + pupil_size)//2,
        right_eye[1] + (eye_size + pupil_size)//2
    ], fill=screen_black)
    
    # Cat nose (black triangle)
    nose_y = cat_center_y - body_height//2 + int(size * 0.11)
    nose_size = int(size * 0.02)
    nose_points = [
        (cat_center_x, nose_y - nose_size//2),
        (cat_center_x - nose_size//2, nose_y + nose_size//2),
        (cat_center_x + nose_size//2, nose_y + nose_size//2)
    ]
    draw.polygon(nose_points, fill=screen_black)
    
    # Cat mouth (black curves)
    mouth_y = nose_y + int(size * 0.02)
    # Left mouth curve
    draw.arc([
        cat_center_x - int(size * 0.04),
        mouth_y,
        cat_center_x - int(size * 0.01),
        mouth_y + int(size * 0.03)
    ], start=0, end=180, fill=screen_black, width=2)
    
    # Right mouth curve
    draw.arc([
        cat_center_x + int(size * 0.01),
        mouth_y,
        cat_center_x + int(size * 0.04),
        mouth_y + int(size * 0.03)
    ], start=0, end=180, fill=screen_black, width=2)
    
    # Cat whiskers (white)
    whisker_length = int(size * 0.08)
    whisker_y = nose_y
    
    # Left whiskers
    draw.line([cat_center_x - int(size * 0.12), whisker_y - int(size * 0.01),
              cat_center_x - int(size * 0.12) - whisker_length, whisker_y - int(size * 0.01)], 
              fill=highlight_white, width=2)
    draw.line([cat_center_x - int(size * 0.12), whisker_y + int(size * 0.01),
              cat_center_x - int(size * 0.12) - whisker_length, whisker_y + int(size * 0.01)], 
              fill=highlight_white, width=2)
    
    # Right whiskers
    draw.line([cat_center_x + int(size * 0.12), whisker_y - int(size * 0.01),
              cat_center_x + int(size * 0.12) + whisker_length, whisker_y - int(size * 0.01)], 
              fill=highlight_white, width=2)
    draw.line([cat_center_x + int(size * 0.12), whisker_y + int(size * 0.01),
              cat_center_x + int(size * 0.12) + whisker_length, whisker_y + int(size * 0.01)], 
              fill=highlight_white, width=2)
    
    # Cat paws (green accents)
    paw_size = int(size * 0.04)
    # Left paw
    left_paw = [
        cat_center_x - int(size * 0.08),
        cat_center_y + body_height//3,
        cat_center_x - int(size * 0.08) + paw_size,
        cat_center_y + body_height//3 + paw_size
    ]
    draw.ellipse(left_paw, fill=cat_green)
    
    # Right paw
    right_paw = [
        cat_center_x + int(size * 0.08) - paw_size,
        cat_center_y + body_height//3,
        cat_center_x + int(size * 0.08),
        cat_center_y + body_height//3 + paw_size
    ]
    draw.ellipse(right_paw, fill=cat_green)
    
    # Cat tail (curved red line)
    tail_points = []
    import math
    for i in range(20):
        angle = (i / 19) * math.pi * 1.5  # 1.5 * pi for nice curve
        tail_x = cat_center_x + body_width//2 + int(math.cos(angle) * size * 0.15)
        tail_y = cat_center_y + int(math.sin(angle) * size * 0.12)
        tail_points.append((tail_x, tail_y))
    
    # Draw tail as thick line
    for i in range(len(tail_points)-1):
        draw.line([tail_points[i], tail_points[i+1]], fill=cat_red, width=int(size*0.02))
    
    # Screen reflection/highlight
    reflect_size = int(size * 0.15)
    draw.ellipse([
        screen_frame[0] + int(size * 0.05),
        screen_frame[1] + int(size * 0.05),
        screen_frame[0] + int(size * 0.05) + reflect_size,
        screen_frame[1] + int(size * 0.05) + reflect_size
    ], fill=(255, 255, 255, 60))
    
    # Monitor stand/base (black)
    stand_width = int(size * 0.15)
    stand_height = int(size * 0.08)
    stand_base = [
        center - stand_width//2,
        screen_frame[3] + frame_thickness,
        center + stand_width//2,
        screen_frame[3] + frame_thickness + stand_height
    ]
    draw.rounded_rectangle(stand_base, radius=int(size*0.01), fill=screen_black)
    
    # Add "SC" text if large enough
    if size >= 256:
        try:
            # Try to load a font, fallback to default
            try:
                font_size = max(12, size // 30)
                font = ImageFont.load_default()
            except:
                font = None
            
            # Draw "SC" in corner of screen
            text = "SC"
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                draw.text((
                    screen_frame[2] - text_width - int(size * 0.02),
                    screen_frame[1] + int(size * 0.02)
                ), text, fill=highlight_white, font=font)
            
        except Exception:
            pass
    
    return img


def create_all_cat_icons():
    """Create all required cat icon sizes"""
    print("🐱 Creating SmartCompute Cat Logo...")
    
    # Ensure assets directory exists
    Path("assets").mkdir(exist_ok=True)
    
    # Icon sizes needed
    sizes = [16, 32, 48, 64, 96, 128, 192, 256, 512, 1024]
    
    for size in sizes:
        logo = create_cat_screen_logo(size)
        logo.save(f'assets/cat_icon_{size}.png')
        print(f"   ✓ Created: assets/cat_icon_{size}.png")
    
    # Create main icons
    create_cat_screen_logo(512).save('assets/cat_icon.png')
    create_cat_screen_logo(256).save('assets/cat_icon_large.png')
    create_cat_screen_logo(64).save('assets/cat_icon_small.png')
    
    print("   ✓ Created main cat icon files")
    
    # Create Android specific icons
    android_sizes = {
        'ldpi': 36, 'mdpi': 48, 'hdpi': 72,
        'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192
    }
    
    for density, size in android_sizes.items():
        logo = create_cat_screen_logo(size)
        logo.save(f'assets/cat_icon_android_{density}.png')
        print(f"   ✓ Created: assets/cat_icon_android_{density}.png")
    
    # Create iOS specific icons
    ios_sizes = {
        20: 'settings_1x', 29: 'settings_2x', 40: 'spotlight_2x',
        58: 'settings_2x', 60: 'app_2x', 80: 'spotlight_3x',
        87: 'settings_3x', 120: 'app_2x', 180: 'app_3x', 1024: 'store'
    }
    
    for size, desc in ios_sizes.items():
        logo = create_cat_screen_logo(size)
        logo.save(f'assets/cat_icon_ios_{size}.png')
        print(f"   ✓ Created: assets/cat_icon_ios_{size}.png ({desc})")
    
    # Create favicons
    for size in [16, 32, 96, 192]:
        logo = create_cat_screen_logo(size)
        logo.save(f'assets/cat_favicon_{size}x{size}.png')
        print(f"   ✓ Created: assets/cat_favicon_{size}x{size}.png")
    
    # Replace old icons with cat icons
    create_cat_screen_logo(512).save('assets/cat_icon.png')
    create_cat_screen_logo(256).save('assets/icon_large.png')
    create_cat_screen_logo(64).save('assets/icon_small.png')
    
    print("   ✓ Replaced main application icons with cat theme")
    
    return True


def main():
    """Main function"""
    print("🐱 SmartCompute Cat Logo Creator")
    print("=" * 40)
    
    create_all_cat_icons()
    
    print("\n✅ Cat logo creation completed successfully!")
    print("\n📁 Created cat-themed assets:")
    print("   • Cat on screen design with blue, red, green, black colors")
    print("   • Platform-specific cat icons in multiple sizes")
    print("   • Android density-specific cat icons")
    print("   • iOS app cat icons for all sizes")
    print("   • Cat favicons for web")
    print("\n🎨 Design features:")
    print("   • Computer screen/monitor frame (black)")
    print("   • Blue screen background with scanlines")
    print("   • Red cat body and head")
    print("   • Green cat eyes and paws")
    print("   • Black accents (ears, nose, pupils)")
    print("   • White whiskers and highlights")
    print("   • Curved tail and monitor stand")
    print("\n💡 Next steps:")
    print("   1. Review the new cat logo design")
    print("   2. Update applications to use new cat icons")
    print("   3. Test on different platforms and sizes")


if __name__ == "__main__":
    main()