#!/usr/bin/env python3
"""
Complete CV-5000 Workflow Example
Demonstrates all commands including new discoveries from events_config.csv
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.device import CV5000Device
import time


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  CV-5000 Complete Workflow - All Commands Demo            ║")
    print("║  Including NEW commands from events_config.csv             ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Configuration
    PORT = "COM4"  # Change to your port
    
    try:
        # Create device
        device = CV5000Device(port=PORT, debug=True)
        
        print(f"Connecting to CV-5000 on {PORT}...")
        device.connect()
        print("✅ Connected!\n")
        
        # ============================================================
        # STEP 1: INITIALIZATION (NEW!)
        # ============================================================
        print_section("1. Initialize Device (NEW Command)")
        print("Sending initialization command ('r')...")
        init_result = device.initialize()
        print(f"Initialization result: {init_result}")
        time.sleep(1)
        
        # ============================================================
        # STEP 2: QUERY DEVICE INFORMATION (NEW!)
        # ============================================================
        print_section("2. Query Device Information")
        
        print("Getting device version...")
        versions = device.get_version()
        print(f"Software version: {versions.get('software', 'Unknown')}")
        print(f"Controller version: {versions.get('controller', 'Unknown')}")
        time.sleep(0.5)
        
        print("\nGetting current values (NEW!)...")
        current_vals = device.get_current_values()
        print(f"Current values: {current_vals}")
        time.sleep(1)
        
        # ============================================================
        # STEP 3: CHART SWITCHING (NEW!)
        # ============================================================
        print_section("3. Chart Switching (NEW Commands)")
        
        print("Switching to Chart 1 (simple command)...")
        device.switch_chart(1)
        time.sleep(1)
        
        print("Switching to Chart 2...")
        device.switch_chart(2)
        time.sleep(1)
        
        print("Back to Chart 1...")
        device.switch_chart(1)
        time.sleep(1)
        
        # ============================================================
        # STEP 4: CHART PATTERNS (NEW!)
        # ============================================================
        print_section("4. Chart Patterns (NEW Commands)")
        
        print("Setting chart pattern 12 (Chart 1, Mode 2)...")
        device.set_chart_pattern(12)
        time.sleep(1)
        
        print("Setting chart pattern 21 (Chart 2, Mode 1)...")
        device.set_chart_pattern(21)
        time.sleep(1)
        
        print("Setting chart pattern 47...")
        device.set_chart_pattern(47)
        time.sleep(1)
        
        # ============================================================
        # STEP 5: BASIC PRESCRIPTION
        # ============================================================
        print_section("5. Set Basic Prescription")
        
        print("Resetting to zero...")
        device.reset_to_zero()
        time.sleep(1)
        
        print("Setting prescription: R: -1.50/-0.50x90, L: -2.00/-0.75x180")
        device.set_prescription(
            r_sph=-1.50, r_cyl=-0.50, r_axis=90,
            l_sph=-2.00, l_cyl=-0.75, l_axis=180
        )
        time.sleep(1)
        
        # ============================================================
        # STEP 6: PRESCRIPTION WITH CHART/MODE (NEW!)
        # ============================================================
        print_section("6. Prescription with Chart/Mode Parameters (NEW!)")
        
        print("Setting prescription with chart=1, mode=1, display=0...")
        device.set_prescription(
            r_sph=-1.75, r_cyl=-0.50, r_axis=90,
            l_sph=-2.25, l_cyl=-0.75, l_axis=180,
            chart=1, mode=1, display=0
        )
        time.sleep(1)
        
        print("Changing to chart=2, display=2...")
        device.set_prescription(
            chart=2, display=2  # Keep same prescription, change chart/display
        )
        time.sleep(1)
        
        # ============================================================
        # STEP 7: AXIS MODE COMMANDS (NEW!)
        # ============================================================
        print_section("7. Axis Mode Commands (NEW!)")
        
        print("Setting right eye axis mode (25°, mode 2)...")
        device.set_axis_mode('R', 25, 2)
        time.sleep(1)
        
        print("Setting left eye axis mode (25°, mode 1)...")
        device.set_axis_mode('L', 25, 1)
        time.sleep(1)
        
        # ============================================================
        # STEP 8: PD SETTING
        # ============================================================
        print_section("8. Set Pupillary Distance")
        
        print("Setting PD to 64.0mm...")
        device.set_pd(64.0)
        time.sleep(1)
        
        # ============================================================
        # STEP 9: COMPLETE EXAM WORKFLOW
        # ============================================================
        print_section("9. Complete Exam Workflow")
        
        print("Starting complete exam simulation...")
        
        # Chart 1 examination
        print("\n  📊 Chart 1 - Distance Vision")
        device.set_chart_pattern(1)
        device.set_prescription(
            r_sph=-1.00, r_cyl=-0.50, r_axis=90,
            l_sph=-1.25, l_cyl=-0.50, l_axis=85,
            chart=1, mode=1, display=2
        )
        time.sleep(1.5)
        
        # Chart 2 examination
        print("  📊 Chart 2 - Near Vision")
        device.switch_chart(2)
        device.set_prescription(
            r_sph=-0.75, r_cyl=-0.50, r_axis=90,
            l_sph=-1.00, l_cyl=-0.50, l_axis=85,
            chart=2, mode=1, display=2
        )
        time.sleep(1.5)
        
        # Chart 7 - Different test
        print("  📊 Chart 7")
        device.set_chart_pattern(7)
        device.set_prescription(
            chart=7, mode=1, display=2
        )
        time.sleep(1.5)
        
        # ============================================================
        # STEP 10: FINAL STATE
        # ============================================================
        print_section("10. Final Device State")
        
        state = device.get_state()
        print("Current device state:")
        print(f"  Right Eye: SPH={state['r_sph']:+.2f} CYL={state['r_cyl']:+.2f} AXIS={state['r_axis']}")
        print(f"  Left Eye:  SPH={state['l_sph']:+.2f} CYL={state['l_cyl']:+.2f} AXIS={state['l_axis']}")
        print(f"  PD: {state['pd']:.1f}mm")
        print(f"  Chart: {state['chart_num']}, Mode: {state['chart_mode']}, Display: {state['display_mode']}")
        print(f"  Initialized: {state['initialized']}")
        
        # Disconnect
        print("\nDisconnecting...")
        device.disconnect()
        print("✅ Complete!\n")
        
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ✅ ALL COMMANDS EXECUTED SUCCESSFULLY!                    ║")
        print("║                                                            ║")
        print("║  Commands demonstrated:                                    ║")
        print("║  ✅ Initialization ('r')                                   ║")
        print("║  ✅ Version query ('v PS', 'v CV')                         ║")
        print("║  ✅ Chart switching ('c 1', 'c 2')                         ║")
        print("║  ✅ Chart patterns ('CE 12', 'CE 47', etc.)                ║")
        print("║  ✅ Axis modes ('c R A 25 2')                              ║")
        print("║  ✅ Prescription with chart/mode/display                   ║")
        print("║  ✅ Basic prescription ('B')                               ║")
        print("║  ✅ PD setting ('D')                                       ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        if device.is_connected():
            device.disconnect()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if device.is_connected():
            device.disconnect()


if __name__ == "__main__":
    main()

