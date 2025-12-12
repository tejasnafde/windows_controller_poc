#!/usr/bin/env python3
"""
Screenshot Capture Tool for YOLO Training

Run this on the Windows machine with CV5000 UI visible.
It will capture screenshots at regular intervals.
"""

import pyautogui
import time
import os
from datetime import datetime

# Configuration
OUTPUT_DIR = "training_data/images"
NUM_SCREENSHOTS = 30  # Start small for proof of concept
INTERVAL_SECONDS = 3  # Time between screenshots

def main():
    """Capture screenshots for YOLO training."""
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("YOLO Training Data Capture")
    print("=" * 60)
    print(f"\nWill capture {NUM_SCREENSHOTS} screenshots")
    print(f"Interval: {INTERVAL_SECONDS} seconds")
    print(f"Output: {OUTPUT_DIR}/")
    
    print("\n⚠️  IMPORTANT:")
    print("  1. Make sure CV5000 UI is visible and in focus")
    print("  2. Vary the UI between captures:")
    print("     - Change charts")
    print("     - Change power values")
    print("     - Show different screens")
    print("\nStarting in 5 seconds...")
    
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("\n🎬 Starting capture!\n")
    
    for i in range(NUM_SCREENSHOTS):
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/cv5000_{i:04d}_{timestamp}.png"
        screenshot.save(filename)
        
        print(f"✓ Captured {i+1}/{NUM_SCREENSHOTS}: {os.path.basename(filename)}")
        
        # Remind user to vary UI
        if (i + 1) % 10 == 0 and i < NUM_SCREENSHOTS - 1:
            print(f"\n  💡 TIP: Change the UI for variety (next {10} screenshots)\n")
            time.sleep(3)  # Extra time to make changes
        
        # Wait before next capture
        if i < NUM_SCREENSHOTS - 1:
            time.sleep(INTERVAL_SECONDS)
    
    print("\n" + "=" * 60)
    print("✅ Capture Complete!")
    print("=" * 60)
    print(f"\nCaptured {NUM_SCREENSHOTS} screenshots to: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("  1. Review screenshots - delete any bad ones")
    print("  2. Run labelImg to label UI elements:")
    print(f"     labelImg {OUTPUT_DIR}")
    print("  3. Label these elements:")
    print("     - sphere_plus_re")
    print("     - sphere_minus_re") 
    print("     - chart_6_12 (or any chart button)")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Capture interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
