#!/usr/bin/env python3
"""
Build MyOptum Installer - Package Windows client as standalone .exe

This script uses PyInstaller to create the MyOptum Activity Monitor executable.
"""

import os
import sys
import subprocess
import shutil

# Version - increment with each commit
VERSION = "0.0.4"


def build_myoptum_installer():
    """Build the MyOptum Installer executable using PyInstaller."""
    
    print("=" * 60)
    print(f"Building MyOptum Installer v{VERSION}")
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
    if not os.path.exists('windows_client_websocket.py'):
        print("\n✗ Error: windows_client_websocket.py not found!")
        print("Make sure you're running this script from the project directory.")
        return False
    
    print("\n✓ Source file found: windows_client_websocket.py")
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    for directory in ['build', 'dist', '__pycache__']:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"  Removed {directory}/")
    
    # Remove old spec files
    for spec_file in ['MyOptum_Installer.spec', 'windows_client_websocket.spec']:
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"  Removed {spec_file}")
    
    # PyInstaller command for MyOptum Installer
    print("\nBuilding MyOptum Installer with PyInstaller...")
    print("This may take a few minutes...\n")
    
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable file
        '--windowed',                   # GUI mode (no console window)
        '--name', 'MyOptum_Installer',  # Executable name
        '--icon', 'NONE',              # You can add an icon file here
        '--hidden-import', 'cv2',       # Include OpenCV
        '--hidden-import', 'numpy',     # Include NumPy
        '--collect-all', 'cv2',         # Include all OpenCV files
        'windows_client_websocket.py'
    ]
    
    # Add templates directory if it exists
    if os.path.exists('templates'):
        cmd.insert(-1, '--add-data')
        if sys.platform == 'win32':
            cmd.insert(-1, 'templates;templates')  # Windows format
        else:
            cmd.insert(-1, 'templates:templates')  # Unix format
        print("✓ Templates directory will be bundled\n")
    else:
        print("⚠️  Warning: templates/ directory not found")
        print("   Run generate_templates.py to create templates\n")

    
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
            exe_path = os.path.join('dist', 'MyOptum_Installer.exe')
        else:
            # On macOS/Linux
            exe_path = os.path.join('dist', 'MyOptum_Installer')
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✓ MyOptum Installer v{VERSION} created: {exe_path}")
            print(f"✓ File size: {size_mb:.2f} MB")
            
            if system == 'Windows':
                print("\nNext steps:")
                print("  1. Run dist/MyOptum_Installer.exe")
                print("  2. Enter your relay server URL")
                print("  3. Click 'Connect to Server'")
                print("  4. The Activity Monitor will show all remote commands")
            else:
                print(f"\n⚠️  Note: You built on {system}, not Windows!")
                print("   This executable will only work on macOS/Linux.")
                print("\nTo create a Windows .exe:")
                print("  1. Run this build script on a Windows machine")
                print("  2. Or use a Windows VM")
                print("\nFor testing on this Mac:")
                print(f"  1. Run: {exe_path}")
                print("  2. Enter server URL and click 'Connect to Server'")
            
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
    success = build_myoptum_installer()
    sys.exit(0 if success else 1)
