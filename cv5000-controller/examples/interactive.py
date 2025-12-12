"""Interactive CLI for CV-5000"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.device import CV5000Device

def print_menu():
    print("\n" + "=" * 50)
    print("CV-5000 Interactive Controller")
    print("=" * 50)
    print("1. Set Right Sphere")
    print("2. Set Left Sphere")
    print("3. Set Right Cylinder")
    print("4. Set Right Axis")
    print("5. Set Both Sphere")
    print("6. Set PD")
    print("7. Reset to Zero")
    print("8. Show E-Chart")
    print("9. Show Current State")
    print("0. Exit")
    print("=" * 50)

def main():
    device = CV5000Device(port="COM7", debug=False)
    
    try:
        device.connect()
        print("✅ Connected to CV-5000")
        
        while True:
            print_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            
            elif choice == "1":
                value = float(input("Enter R_SPH value: "))
                device.set_prescription(r_sph=value)
                print(f"✓ Set R_SPH to {value:+.2f}")
            
            elif choice == "2":
                value = float(input("Enter L_SPH value: "))
                device.set_prescription(l_sph=value)
                print(f"✓ Set L_SPH to {value:+.2f}")
            
            elif choice == "3":
                value = float(input("Enter R_CYL value: "))
                device.set_prescription(r_cyl=value)
                print(f"✓ Set R_CYL to {value:+.2f}")
            
            elif choice == "4":
                value = int(input("Enter R_AXIS value: "))
                device.set_prescription(r_axis=value)
                print(f"✓ Set R_AXIS to {value}°")
            
            elif choice == "5":
                value = float(input("Enter sphere value (both eyes): "))
                device.set_sphere_both(value)
                print(f"✓ Set both eyes to {value:+.2f}")
            
            elif choice == "6":
                value = float(input("Enter PD value: "))
                device.set_pd(value)
                print(f"✓ Set PD to {value:.1f}mm")
            
            elif choice == "7":
                device.reset_to_zero()
                print("✓ Reset to zero")
            
            elif choice == "8":
                device.show_echart()
                print("✓ E-chart displayed")
            
            elif choice == "9":
                state = device.get_state()
                print("\n📊 Current State:")
                print(f"  R_SPH: {state['r_sph']:+.2f}")
                print(f"  R_CYL: {state['r_cyl']:+.2f}")
                print(f"  R_AXIS: {state['r_axis']}°")
                print(f"  L_SPH: {state['l_sph']:+.2f}")
                print(f"  L_CYL: {state['l_cyl']:+.2f}")
                print(f"  L_AXIS: {state['l_axis']}°")
                print(f"  PD: {state['pd']:.1f}mm")
            
            else:
                print("❌ Invalid option")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        device.disconnect()
        print("\n👋 Disconnected")

if __name__ == "__main__":
    main()

