"""Basic connectivity and command tests for CV-5000"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.device import CV5000Device
from src.exceptions import ValidationError
import time

def test_connection():
    """Test basic connection to device"""
    print("\n" + "=" * 60)
    print("TEST: Basic Connection")
    print("=" * 60)
    
    try:
        device = CV5000Device(port="COM4", debug=False)
        device.connect()
        print("✅ Connection successful")
        
        assert device.is_connected(), "Device should be connected"
        print("✅ Connection status check passed")
        
        device.disconnect()
        print("✅ Disconnection successful")
        
        assert not device.is_connected(), "Device should be disconnected"
        print("✅ Disconnection status check passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_version_query():
    """Test version query command"""
    print("\n" + "=" * 60)
    print("TEST: Version Query")
    print("=" * 60)
    
    try:
        with CV5000Device(port="COM4", debug=True) as device:
            versions = device.get_version()
            print(f"\n📟 Device Versions:")
            print(f"  Software: {versions.get('software', 'N/A')}")
            print(f"  Controller: {versions.get('controller', 'N/A')}")
            
            assert 'software' in versions or 'controller' in versions, "Should get at least one version"
            print("\n✅ Version query test passed")
            
        return True
        
    except Exception as e:
        print(f"❌ Version query test failed: {e}")
        return False

def test_reset():
    """Test reset command"""
    print("\n" + "=" * 60)
    print("TEST: Reset Command")
    print("=" * 60)
    
    try:
        with CV5000Device(port="COM4", debug=False) as device:
            device.reset_to_zero()
            print("✅ Reset command sent")
            
            state = device.get_state()
            assert state['r_sph'] == 0.0, "R_SPH should be 0.0"
            assert state['l_sph'] == 0.0, "L_SPH should be 0.0"
            print("✅ State reset confirmed")
            
        return True
        
    except Exception as e:
        print(f"❌ Reset test failed: {e}")
        return False

def test_validation():
    """Test parameter validation"""
    print("\n" + "=" * 60)
    print("TEST: Parameter Validation")
    print("=" * 60)
    
    try:
        from src.commands import CommandBuilder
        
        # Test valid values
        CommandBuilder.validate_sphere(-1.50)
        CommandBuilder.validate_cylinder(-0.25)
        CommandBuilder.validate_axis(90)
        CommandBuilder.validate_pd(64.0)
        print("✅ Valid values accepted")
        
        # Test invalid sphere
        try:
            CommandBuilder.validate_sphere(-25.0)
            print("❌ Should reject sphere out of range")
            return False
        except ValidationError:
            print("✅ Rejected invalid sphere")
        
        # Test invalid cylinder
        try:
            CommandBuilder.validate_cylinder(5.0)
            print("❌ Should reject cylinder out of range")
            return False
        except ValidationError:
            print("✅ Rejected invalid cylinder")
        
        # Test invalid axis
        try:
            CommandBuilder.validate_axis(200)
            print("❌ Should reject axis out of range")
            return False
        except ValidationError:
            print("✅ Rejected invalid axis")
        
        # Test invalid step
        try:
            CommandBuilder.validate_sphere(-1.33)
            print("❌ Should reject invalid step")
            return False
        except ValidationError:
            print("✅ Rejected invalid step size")
        
        print("\n✅ All validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def run_all_tests():
    """Run all basic tests"""
    print("\n" + "=" * 60)
    print("CV-5000 BASIC TESTS")
    print("=" * 60)
    
    results = {
        "Connection": test_connection(),
        "Version Query": test_version_query(),
        "Reset": test_reset(),
        "Validation": test_validation()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

