#!/usr/bin/env python3
"""
Example Usage - WebSocket Architecture

Demonstrates how to use the WebSocket-based remote control system.
"""

import asyncio
import time
from controller_websocket import ControllerWebSocket


async def main():
    """Demonstrate WebSocket controller usage."""
    
    # Update this to your relay server URL
    # For local testing: ws://localhost:8765
    # For deployed server: ws://your-server.com:8765
    SERVER_URL = 'ws://localhost:8765'
    
    print("=" * 60)
    print("Remote Windows Control - WebSocket Example")
    print("=" * 60)
    print(f"\nConnecting to relay server at {SERVER_URL}")
    print("Make sure the relay server is running!\n")
    
    controller = ControllerWebSocket(server_url=SERVER_URL)
    
    try:
        # Connect to relay server
        await controller.connect()
        print("✓ Connected to relay server\n")
        
        # Wait a moment for client list to populate
        await asyncio.sleep(1)
        
        # List connected clients
        print("1. Listing connected clients...")
        clients = await controller.list_clients()
        
        if not clients:
            print("   ✗ No clients connected!")
            print("\n   Make sure Windows client is running and connected to the server.")
            print("   On Windows: python windows_client_websocket.py")
            return
        
        print(f"   ✓ Found {len(clients)} client(s):")
        for client in clients:
            print(f"     - {client}")
        
        # Use the first client
        client_id = clients[0]
        print(f"\n   Using client: {client_id}\n")
        
        await asyncio.sleep(1)
        
        # Get current cursor position
        print("2. Getting current cursor position...")
        response = await controller.get_cursor_position(client_id)
        if response['status'] == 'success':
            data = response['data']
            print(f"   ✓ Current position: ({data['x']}, {data['y']})")
            print(f"   ✓ Screen size: {data['screen_width']}x{data['screen_height']}")
        else:
            print(f"   ✗ Error: {response['message']}")
            return
        
        await asyncio.sleep(1)
        
        # Move cursor to center of screen
        print("\n3. Moving cursor to center of screen...")
        center_x = data['screen_width'] // 2
        center_y = data['screen_height'] // 2
        response = await controller.move_cursor(client_id, center_x, center_y)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        await asyncio.sleep(1)
        
        # Move cursor to specific position
        print("\n4. Moving cursor to (500, 500)...")
        response = await controller.move_cursor(client_id, 500, 500)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        await asyncio.sleep(1)
        
        # Click at current position
        print("\n5. Clicking at current position...")
        response = await controller.click(client_id)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        await asyncio.sleep(1)
        
        # Move cursor relatively
        print("\n6. Moving cursor right by 100 pixels...")
        response = await controller.move_relative(client_id, 100, 0)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
            print(f"   ✓ New position: ({response['data']['x']}, {response['data']['y']})")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        await asyncio.sleep(1)
        
        # Move down relatively
        print("\n7. Moving cursor down by 50 pixels...")
        response = await controller.move_relative(client_id, 0, 50)
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
            print(f"   ✓ New position: ({response['data']['x']}, {response['data']['y']})")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        await asyncio.sleep(1)
        
        # Right click at specific position
        print("\n8. Right-clicking at (300, 300)...")
        response = await controller.click(client_id, 300, 300, button='right')
        if response['status'] == 'success':
            print(f"   ✓ {response['message']}")
        else:
            print(f"   ✗ Error: {response['message']}")
        
        await asyncio.sleep(1)
        
        # Draw a square pattern
        print("\n9. Drawing a square pattern with cursor...")
        start_x, start_y = 400, 400
        size = 200
        
        # Top edge
        await controller.move_cursor(client_id, start_x, start_y)
        await asyncio.sleep(0.3)
        await controller.move_cursor(client_id, start_x + size, start_y)
        await asyncio.sleep(0.3)
        # Right edge
        await controller.move_cursor(client_id, start_x + size, start_y + size)
        await asyncio.sleep(0.3)
        # Bottom edge
        await controller.move_cursor(client_id, start_x, start_y + size)
        await asyncio.sleep(0.3)
        # Left edge (back to start)
        await controller.move_cursor(client_id, start_x, start_y)
        print("   ✓ Square pattern completed!")
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
        # Disconnect
        await controller.disconnect()
        
    except ConnectionError as e:
        print(f"\n✗ Connection Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure the relay server is running:")
        print("     python relay_server.py")
        print("  2. Make sure the Windows client is connected:")
        print("     python windows_client_websocket.py")
        print("  3. Check the server URL is correct")
    except TimeoutError as e:
        print(f"\n✗ Timeout Error: {e}")
        print("\nThe client may be unresponsive")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
