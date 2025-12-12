#!/usr/bin/env python3
"""
Crop templates to only show static labels (ADD, S, C, A)
This removes the dynamic number portion.
"""

from PIL import Image
import os

# Template files to process
templates_to_crop = {
    # Right eye templates - crop left side (keep right portion with label)
    'right_add.png': {'side': 'right', 'keep_percent': 0.5},  # Keep right 50%
    'right_axial.png': {'side': 'right', 'keep_percent': 0.5},
    'right_spherical.png': {'side': 'right', 'keep_percent': 0.5},
    'right_cylindrical.png': {'side': 'right', 'keep_percent': 0.5},
    
    # Left eye templates - crop right side (keep left portion with label)  
    'left_add.png': {'side': 'left', 'keep_percent': 0.5},  # Keep left 50%
    'left_axial.png': {'side': 'left', 'keep_percent': 0.5},
    'left_spherical.png': {'side': 'left', 'keep_percent': 0.5},
    'left_cylindrical.png': {'side': 'left', 'keep_percent': 0.5},
}

templates_dir = 'templates'

def crop_template(filename, config):
    """Crop template to remove dynamic content."""
    filepath = os.path.join(templates_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"⚠️  Template not found: {filename}")
        return
    
    # Open image
    img = Image.open(filepath)
    width, height = img.size
    
    # Calculate crop box
    if config['side'] == 'right':
        # Keep right portion (label), remove left portion (number)
        crop_x = int(width * (1 - config['keep_percent']))
        crop_box = (crop_x, 0, width, height)
    else:  # left
        # Keep left portion (label), remove right portion (number)
        crop_x = int(width * config['keep_percent'])
        crop_box = (0, 0, crop_x, height)
    
    # Crop and save
    cropped = img.crop(crop_box)
    
    # Save backup
    backup_path = filepath.replace('.png', '_original.png')
    if not os.path.exists(backup_path):
        img.save(backup_path)
        print(f"📦 Backed up: {filename} → {os.path.basename(backup_path)}")
    
    # Save cropped version
    cropped.save(filepath)
    print(f"✂️  Cropped: {filename} ({width}x{height} → {cropped.size[0]}x{cropped.size[1]})")

def main():
    print("=" * 70)
    print("Cropping Templates to Remove Dynamic Content")
    print("=" * 70)
    print()
    
    for filename, config in templates_to_crop.items():
        crop_template(filename, config)
    
    print()
    print("=" * 70)
    print("✓ Template cropping complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. The templates now only contain static labels")
    print("  2. Use offset parameter in Action to click the number field")
    print("  3. Example: Action('right_add', offset=(-100, 0))  # Click 100px left of label")

if __name__ == '__main__':
    main()
