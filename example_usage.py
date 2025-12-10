#!/usr/bin/env python3
"""
Example Usage - Demonstrates how to use the controller service

This script shows various ways to control the remote Windows client.
"""

import time
from controller_service import ControllerService

# Configuration - Update this with your Windows PC's IP address
WINDOWS_CLIENT_HOST = '10.211.21.126'  # Change to Windows PC IP for remote control
WINDOWS_CLIENT_PORT = 5555


def main():
    """Demonstrate various control commands."""
    
    print("=" * 60)
    print("Remote Windows Control - Example Usage")
    print("=" * 60)
    print(f"\nConnecting to Windows client at {WINDOWS_CLIENT_HOST}:{WINDOWS_CLIENT_PORT}")
    print("Make sure the Windows client is running!\n")
    
    # Create controller instance
    controller = ControllerService(WINDOWS_CLIENT_HOST, WINDOWS_CLIENT_PORT)
    
    try:
        # 1. Get current cursor position
        print("\n1. Getting current cursor position...")
        response = controller.get_cursor_position()
        if response['status'] == 'success':
            data = response['data']
            print(f"   ✓ Current position: ({data['x']}, {data['y']})")
            print(f"   ✓ Screen size: {data['screen_width']}x{data['screen_height']}")
        else:
            print(f"   ✗ Error: {response['message']}")
            return
        
        time.sleep(1)
        
        # 2. Move cursor to center of screen
        print("\n2. Moving cursor to center of screen...")
        center_x = data['screen_width'] // 2
        center_y = data['screen_height'] // 2
        response = controller.move_cursor(center_x, center_y)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        time.sleep(1)
        
        # 3. Move cursor to specific position
        print("\n3. Moving cursor to (500, 500)...")
        response = controller.move_cursor(500, 500)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        time.sleep(1)
        
        # 4. Click at current position
        print("\n4. Clicking at current position...")
        response = controller.click()
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        time.sleep(1)
        
        # 5. Move cursor relatively
        print("\n5. Moving cursor right by 100 pixels...")
        response = controller.move_relative(100, 0)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
            print(f"   ✓ New position: ({response['data']['x']}, {response['data']['y']})")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        time.sleep(1)
        
        # 6. Move down relatively
        print("\n6. Moving cursor down by 50 pixels...")
        response = controller.move_relative(0, 50)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
            print(f"   ✓ New position: ({response['data']['x']}, {response['data']['y']})")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        time.sleep(1)
        
        # 7. Right click at specific position
        print("\n7. Right-clicking at (300, 300)...")
        response = controller.click(300, 300, button='right')
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        time.sleep(1)
        
        # 8. Draw a square pattern
        print("\n8. Drawing a square pattern with cursor...")
        start_x, start_y = 400, 400
        size = 200
        
        # Top edge
        controller.move_cursor(start_x, start_y)
        time.sleep(0.3)
        controller.move_cursor(start_x + size, start_y)
        time.sleep(0.3)
        # Right edge
        controller.move_cursor(start_x + size, start_y + size)
        time.sleep(0.3)
        # Bottom edge
        controller.move_cursor(start_x, start_y + size)
        time.sleep(0.3)
        # Left edge (back to start)
        controller.move_cursor(start_x, start_y)
        print("   ✓ Square pattern completed!")
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except ConnectionError as e:
        print(f"\n✗ Connection Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure the Windows client is running")
        print("  2. Check the IP address and port are correct")
        print("  3. Verify firewall settings allow the connection")
    except TimeoutError as e:
        print(f"\n✗ Timeout Error: {e}")
        print("\nThe client may be unresponsive or network is slow")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")


if __name__ == '__main__':
    main()
