"""Quick start example for CV-5000"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.device import CV5000Device
import time

def main():
    print("CV-5000 Quick Start Demo")
    print("=" * 50)
    
    # Connect to device
    device = CV5000Device(port="COM7", debug=True)
    
    try:
        device.connect()
        print("\n✅ Connected!")
        
        # Get version
        print("\n📟 Getting device version...")
        versions = device.get_version()
        print(f"  Software: {versions.get('software', 'Unknown')}")
        print(f"  Controller: {versions.get('controller', 'Unknown')}")
        
        # Reset to zero
        print("\n🔄 Resetting to zero...")
        device.reset_to_zero()
        time.sleep(1)
        
        # Set simple myopia
        print("\n👓 Setting prescription: -1.50 both eyes")
        device.set_sphere_both(-1.50)
        time.sleep(1)
        
        # Set PD
        print("\n📏 Setting PD to 63.5mm")
        device.set_pd(63.5)
        time.sleep(1)
        
        # Show E-chart
        print("\n📊 Displaying E-chart")
        device.show_echart()
        time.sleep(1)
        
        print("\n✅ Demo complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        device.disconnect()
        print("\n👋 Disconnected")

if __name__ == "__main__":
    main()

