"""Complete eye examination workflow"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.device import CV5000Device
import time

def simulate_examination():
    """Simulate a complete eye examination"""
    
    print("🏥 Complete Eye Examination Workflow")
    print("=" * 60)
    
    with CV5000Device(port="COM4", debug=False) as device:
        
        # Step 1: Initialize
        print("\n[Step 1] Initializing device...")
        device.reset_to_zero()
        time.sleep(0.5)
        
        # Step 2: Set PD
        print("\n[Step 2] Measuring pupillary distance...")
        device.set_pd(64.0)
        print("  ✓ PD set to 64.0mm")
        time.sleep(0.5)
        
        # Step 3: Initial refraction (right eye)
        print("\n[Step 3] Testing right eye sphere...")
        for sph in [-0.25, -0.50, -1.00, -1.50]:
            print(f"  Testing R_SPH: {sph:+.2f}")
            device.set_prescription(r_sph=sph)
            time.sleep(0.3)
        print("  ✓ Best R_SPH: -1.50")
        
        # Step 4: Right eye cylinder
        print("\n[Step 4] Testing right eye cylinder...")
        device.set_prescription(r_cyl=-0.25, r_axis=175)
        print("  ✓ R_CYL: -0.25 @ 175°")
        time.sleep(0.5)
        
        # Step 5: Left eye
        print("\n[Step 5] Testing left eye...")
        device.set_prescription(l_sph=-1.75, l_cyl=-0.50, l_axis=5)
        print("  ✓ L_SPH: -1.75, L_CYL: -0.50 @ 5°")
        time.sleep(0.5)
        
        # Step 6: Binocular balance
        print("\n[Step 6] Binocular balance test...")
        device.show_echart()
        time.sleep(0.5)
        
        # Step 7: Final prescription
        print("\n[Step 7] Final prescription set:")
        final_rx = {
            'r_sph': -1.50,
            'r_cyl': -0.25,
            'r_axis': 175,
            'l_sph': -1.75,
            'l_cyl': -0.50,
            'l_axis': 5
        }
        device.set_prescription(**final_rx)
        
        print("\n📋 Final Prescription:")
        print(f"  OD: {final_rx['r_sph']:+.2f} {final_rx['r_cyl']:+.2f} × {final_rx['r_axis']}°")
        print(f"  OS: {final_rx['l_sph']:+.2f} {final_rx['l_cyl']:+.2f} × {final_rx['l_axis']}°")
        print(f"  PD: 64.0mm")
        
        print("\n✅ Examination complete!")

if __name__ == "__main__":
    try:
        simulate_examination()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

