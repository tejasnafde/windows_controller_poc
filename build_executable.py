#!/usr/bin/env python3
"""
Build Executable - Package Windows client as standalone .exe

This script uses PyInstaller to create a Windows executable from windows_client.py
"""

import os
import sys
import subprocess
import shutil


def build_executable():
    """Build the Windows executable using PyInstaller."""
    
    print("=" * 60)
    print("Building Windows Client Executable")
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
    if not os.path.exists('windows_client.py'):
        print("\n✗ Error: windows_client.py not found!")
        print("Make sure you're running this script from the project directory.")
        return False
    
    print("\n✓ Source file found: windows_client.py")
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    for directory in ['build', 'dist', '__pycache__']:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"  Removed {directory}/")
    
    # Remove old spec file
    if os.path.exists('windows_client.spec'):
        os.remove('windows_client.spec')
        print("  Removed windows_client.spec")
    
    # PyInstaller command
    print("\nBuilding executable with PyInstaller...")
    print("This may take a few minutes...\n")
    
    cmd = [
        'pyinstaller',
        '--onefile',           # Single executable file
        '--noconsole',         # No console window (comment out for debugging)
        '--name', 'windows_client',
        'windows_client.py'
    ]
    
    # Note: For debugging, you might want to use --console instead of --noconsole
    # This will show the console window with logs
    
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        print("\n" + "=" * 60)
        print("Build Successful!")
        print("=" * 60)
        
        # Check if executable was created
        exe_path = os.path.join('dist', 'windows_client.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✓ Executable created: {exe_path}")
            print(f"✓ File size: {size_mb:.2f} MB")
            
            print("\nNext steps:")
            print("  1. Copy dist/windows_client.exe to your Windows PC")
            print("  2. Run the executable on Windows")
            print("  3. Use controller_service.py to send commands")
            print("\nNote: Windows Defender might flag the executable.")
            print("      This is normal for PyInstaller executables.")
            print("      Add an exception if needed.")
            
            return True
        else:
            print("\n✗ Error: Executable not found in dist/")
            return False
            
    except subprocess.CalledProcessError as e:
        print("\n✗ Build failed!")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def build_with_console():
    """Build executable with console window for debugging."""
    print("\nBuilding with console window for debugging...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--console',  # Show console window
        '--name', 'windows_client_debug',
        'windows_client.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Debug executable created: dist/windows_client_debug.exe")
        return True
    except subprocess.CalledProcessError:
        print("\n✗ Debug build failed!")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Build Windows client executable')
    parser.add_argument('--debug', action='store_true', 
                       help='Build with console window for debugging')
    
    args = parser.parse_args()
    
    if args.debug:
        success = build_with_console()
    else:
        success = build_executable()
    
    sys.exit(0 if success else 1)
