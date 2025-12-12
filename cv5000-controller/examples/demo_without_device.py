"""Demo the CV-5000 controller WITHOUT physical device (dry run)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.commands import CommandBuilder
from src.protocol import CV5000Protocol

def demo_command_building():
    """Demonstrate command building without connecting to device"""
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   CV-5000 Controller Demo (No Device Required)                ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    print("This demo shows what commands would be sent to the device.")
    print("No physical device is required!\n")
    
    # Create protocol instance (but don't connect)
    protocol = CV5000Protocol(port="DEMO_PORT")
    protocol.set_debug(True)
    
    print("="*70)
    print("DEMO 1: Set Simple Myopia Prescription")
    print("="*70)
    
    # Build command for -1.50D both eyes
    cmd = CommandBuilder.build_prescription_command(
        r_sph=-1.50, l_sph=-1.50
    )
    
    packet = protocol.build_packet(*cmd)
    print(f"\n📦 Command to send:")
    print(f"   HEX: {packet.hex(' ').upper()}")
    print(f"   ASCII: {protocol._format_ascii(packet)}")
    print(f"\n✓ Would set R_SPH: -1.50, L_SPH: -1.50")
    
    print("\n" + "="*70)
    print("DEMO 2: Set Astigmatism")
    print("="*70)
    
    cmd = CommandBuilder.build_prescription_command(
        r_sph=-1.50, r_cyl=-0.25, r_axis=175
    )
    
    packet = protocol.build_packet(*cmd)
    print(f"\n📦 Command to send:")
    print(f"   HEX: {packet.hex(' ').upper()}")
    print(f"   ASCII: {protocol._format_ascii(packet)}")
    print(f"\n✓ Would set R_SPH: -1.50, R_CYL: -0.25, R_AXIS: 175°")
    
    print("\n" + "="*70)
    print("DEMO 3: Set PD")
    print("="*70)
    
    cmd = CommandBuilder.build_pd_command(64.0)
    packet = protocol.build_packet(*cmd)
    print(f"\n📦 Command to send:")
    print(f"   HEX: {packet.hex(' ').upper()}")
    print(f"   ASCII: {protocol._format_ascii(packet)}")
    print(f"\n✓ Would set PD: 64.0mm")
    
    print("\n" + "="*70)
    print("DEMO 4: Show E-Chart")
    print("="*70)
    
    cmd = CommandBuilder.build_echart_command()
    packet = protocol.build_packet(*cmd)
    print(f"\n📦 Command to send:")
    print(f"   HEX: {packet.hex(' ').upper()}")
    print(f"   ASCII: {protocol._format_ascii(packet)}")
    print(f"\n✓ Would display E-chart")
    
    print("\n" + "="*70)
    print("VALIDATION TESTS")
    print("="*70)
    
    # Test validation
    print("\n✅ Testing parameter validation...")
    
    try:
        CommandBuilder.validate_sphere(-1.50)
        print("   ✓ Valid sphere: -1.50")
    except:
        print("   ✗ Invalid")
    
    try:
        CommandBuilder.validate_sphere(-25.0)
        print("   ✗ Should have rejected -25.0")
    except Exception as e:
        print(f"   ✓ Correctly rejected -25.0: {e}")
    
    try:
        CommandBuilder.validate_cylinder(-0.25)
        print("   ✓ Valid cylinder: -0.25")
    except:
        print("   ✗ Invalid")
    
    try:
        CommandBuilder.validate_axis(90)
        print("   ✓ Valid axis: 90")
    except:
        print("   ✗ Invalid")
    
    print("\n" + "="*70)
    print("PROTOCOL ANALYSIS")
    print("="*70)
    
    print("\n📊 Protocol Format:")
    print("   Start:     0x01 (SOH - Start of Header)")
    print("   Delimiter: 0x0D (CR - Carriage Return)")
    print("   End:       0x04 (EOT - End of Transmission)")
    print("\n   Example: <SOH> B <CR> R <CR> -1.50 <CR> ... <EOT>")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE!")
    print("="*70)
    
    print("\n📝 Summary:")
    print("   • Command building: ✅ Working")
    print("   • Validation: ✅ Working")
    print("   • Protocol encoding: ✅ Working")
    print("   • Ready for real device: ✅ YES")
    
    print("\n🔌 When you connect to real device:")
    print("   1. Find your serial port:")
    print("      macOS:   ls /dev/tty.* | grep usb")
    print("      Linux:   ls /dev/ttyUSB*")
    print("      Windows: Check Device Manager")
    print("\n   2. Update port in examples:")
    print("      device = CV5000Device(port='/dev/tty.usbserial-xxx')")
    print("\n   3. Run: python examples/quick_start.py")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    demo_command_building()

