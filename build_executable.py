#!/usr/bin/env python3
"""
Build GUI Executable - Package Windows client GUI as standalone .exe

This script uses PyInstaller to create a Windows executable from windows_client_gui.py
"""

import os
import sys
import subprocess
import shutil


def build_gui_executable():
    """Build the Windows GUI executable using PyInstaller."""
    
    print("=" * 60)
    print("Building Windows Client GUI Executable")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"\n✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("\n✗ PyInstaller not found!")
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    # Check if source file exists
    if not os.path.exists('windows_client_gui.py'):
        print("\n✗ Error: windows_client_gui.py not found!")
        print("Make sure you're running this script from the project directory.")
        return False
    
    print("\n✓ Source file found: windows_client_gui.py")
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    for directory in ['build', 'dist', '__pycache__']:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"  Removed {directory}/")
    
    # Remove old spec files
    for spec_file in ['windows_client_gui.spec', 'windows_client.spec']:
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"  Removed {spec_file}")
    
    # PyInstaller command for GUI version
    print("\nBuilding GUI executable with PyInstaller...")
    print("This may take a few minutes...\n")
    
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable file
        '--windowed',                   # GUI mode (no console window)
        '--name', 'windows_client_gui',
        '--icon', 'NONE',              # You can add an icon file here
        'windows_client_gui.py'
    ]
    
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        print("\n" + "=" * 60)
        print("Build Successful!")
        print("=" * 60)
        
        # Check if executable was created (platform-specific naming)
        import platform
        system = platform.system()
        
        if system == 'Windows':
            exe_path = os.path.join('dist', 'windows_client_gui.exe')
        else:
            # On macOS/Linux
            exe_path = os.path.join('dist', 'windows_client_gui')
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✓ GUI Executable created: {exe_path}")
            print(f"✓ File size: {size_mb:.2f} MB")
            
            if system == 'Windows':
                print("\nNext steps:")
                print("  1. Run dist/windows_client_gui.exe")
                print("  2. Click 'Start Server' button")
                print("  3. Use controller_service.py from another machine")
            else:
                print(f"\n⚠️  Note: You built on {system}, not Windows!")
                print("   This executable will only work on macOS/Linux.")
                print("\nTo create a Windows .exe:")
                print("  1. Run this build script on a Windows machine")
                print("\nFor testing on this Mac:")
                print(f"  1. Run: {exe_path}")
                print("  2. Click 'Start Server'")
                print("  3. Use controller_service.py to send commands to localhost")
            
            return True
        else:
            print("\n✗ Error: Executable not found in dist/")
            print(f"   Expected: {exe_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print("\n✗ Build failed!")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    success = build_gui_executable()
    sys.exit(0 if success else 1)
