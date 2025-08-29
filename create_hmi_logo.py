#!/usr/bin/env python3
"""
Create HMI-style logo for SmartCompute
Industrial HMI screen with green lightning bolt
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_hmi_logo():
    # HMI screen dimensions
    width, height = 512, 384
    
    # Create image with dark background (typical HMI color)
    img = Image.new('RGB', (width, height), '#1a1a2e')  # Dark blue-gray
    draw = ImageDraw.Draw(img)
    
    # Draw HMI screen border (beveled effect)
    border_color = '#16213e'
    for i in range(8):
        draw.rectangle([i, i, width-1-i, height-1-i], outline=border_color, width=1)
        border_color = '#' + format(min(255, int(border_color[1:], 16) + 0x030303), '06x')
    
    # Inner screen area
    inner_margin = 20
    inner_rect = [inner_margin, inner_margin, width-inner_margin, height-inner_margin-60]
    draw.rectangle(inner_rect, fill='#0f3460', outline='#4a90e2', width=2)
    
    # Lightning bolt coordinates (centered)
    center_x, center_y = width // 2, (height - 60) // 2
    lightning_color = '#00ff41'  # Bright green
    
    # Main lightning bolt path
    bolt_points = [
        (center_x - 30, center_y - 60),  # Top
        (center_x - 10, center_y - 20),  # Upper middle left
        (center_x + 15, center_y - 20),  # Upper middle right
        (center_x - 5, center_y + 20),   # Lower middle left
        (center_x + 30, center_y + 60),  # Bottom right
        (center_x + 10, center_y + 20),  # Lower middle right
        (center_x - 15, center_y + 20),  # Lower middle left back
        (center_x + 5, center_y - 20),   # Upper middle left back
    ]
    
    # Draw lightning bolt with glow effect
    for glow in range(5, 0, -1):
        glow_color = f'#{int(0x00 + glow*10):02x}{int(0xff - glow*20):02x}{int(0x41 + glow*5):02x}'
        draw.polygon(bolt_points, fill=glow_color, outline=glow_color, width=glow)
    
    # Main bolt
    draw.polygon(bolt_points, fill=lightning_color, outline='#ffffff', width=1)
    
    # Add some HMI-style indicators (small LEDs)
    led_positions = [(40, 40), (width-40, 40), (40, height-100), (width-40, height-100)]
    for i, (x, y) in enumerate(led_positions):
        color = '#00ff41' if i % 2 == 0 else '#ff6b35'
        draw.ellipse([x-6, y-6, x+6, y+6], fill=color, outline='#ffffff', width=1)
    
    # Bottom section for text
    text_area = [0, height-60, width, height]
    draw.rectangle(text_area, fill='#16213e', outline='#4a90e2', width=1)
    
    # Try to use a system font, fallback to default
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 24)
        small_font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 16)
    except:
        try:
            font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 24)
            small_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 16)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Text
    text = "SMARTCOMPUTE"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    text_y = height - 45
    
    # Draw text with glow
    for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
        draw.text((text_x + offset[0], text_y + offset[1]), text, fill='#4a90e2', font=font)
    draw.text((text_x, text_y), text, fill='#ffffff', font=font)
    
    # Industrial subtitle
    subtitle = "INDUSTRIAL NETWORK INTELLIGENCE"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=small_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0] 
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = height - 20
    draw.text((subtitle_x, subtitle_y), subtitle, fill='#00ff41', font=small_font)
    
    return img

def create_sizes():
    """Create different sizes of the logo"""
    base_logo = create_hmi_logo()
    
    sizes = [
        (512, 384, 'cat_icon_large.png'),
        (256, 192, 'cat_icon.png'), 
        (128, 96, 'cat_icon_128.png'),
        (64, 48, 'cat_icon_64.png'),
        (32, 24, 'cat_icon_32.png'),
        (16, 12, 'cat_icon_16.png')
    ]
    
    assets_dir = '/home/gatux/smartcompute/assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    for width, height, filename in sizes:
        resized = base_logo.resize((width, height), Image.Resampling.LANCZOS)
        filepath = os.path.join(assets_dir, filename)
        resized.save(filepath, 'PNG')
        print(f"Created: {filepath}")
    
    # Also create square versions for social media
    square_logo = base_logo.resize((512, 512), Image.Resampling.LANCZOS)
    square_logo.save(os.path.join(assets_dir, 'smartcompute_square.png'))
    print("Created: smartcompute_square.png")

if __name__ == "__main__":
    create_sizes()
    print("🚀 HMI-style logo created successfully!")