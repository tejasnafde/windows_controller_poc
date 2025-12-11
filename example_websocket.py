#!/usr/bin/env python3
"""
Simple Screenshot Test - Take screenshot, right-click, take another screenshot

This demonstrates:
1. Taking a screenshot of the Windows PC
2. Sending it to the controller
3. Right-clicking
4. Taking another screenshot
"""

import asyncio
import base64
from datetime import datetime
from controller_websocket import ControllerWebSocket


async def main():
    """Simple screenshot and click test."""
    
    SERVER_URL = 'wss://d315fa0e928740.lhr.life'
    
    print("=" * 60)
    print("Screenshot & Click Test")
    print("=" * 60)
    print(f"\nConnecting to relay server at {SERVER_URL}\n")
    
    controller = ControllerWebSocket(server_url=SERVER_URL)
    
    try:
        # Connect
        await controller.connect()
        print("✓ Connected to relay server\n")
        await asyncio.sleep(1)
        
        # Get connected clients
        clients = await controller.list_clients()
        if not clients:
            print("✗ No clients connected!")
            return
        
        client_id = clients[0]
        print(f"Using client: {client_id}\n")
        
        # Step 1: Take first screenshot
        print("1. Taking screenshot...")
        response = await controller.take_screenshot(client_id)
        
        if response['status'] == 'success':
            screenshot_data = response['data']['screenshot']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_before_{timestamp}.png"
            
            # Decode and save
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(screenshot_data))
            
            print(f"   ✓ Screenshot saved: {filename}")
        else:
            print(f"   ✗ Error: {response['message']}")
            return
        
        await asyncio.sleep(1)
        
        # Step 2: Right-click at center
        print("\n2. Right-clicking at center of screen...")
        response = await controller.get_cursor_position(client_id)
        data = response['data']
        center_x = data['screen_width'] // 2
        center_y = data['screen_height'] // 2
        
        response = await controller.click(client_id, center_x, center_y, button='right')
        if response['status'] == 'success':
            print(f"   ✓ Right-clicked at ({center_x}, {center_y})")
        else:
            print(f"   ✗ Error: {response['message']}")
            return
        
        await asyncio.sleep(1)
        
        # Step 3: Take second screenshot
        print("\n3. Taking screenshot after right-click...")
        response = await controller.take_screenshot(client_id)
        
        if response['status'] == 'success':
            screenshot_data = response['data']['screenshot']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_after_{timestamp}.png"
            
            # Decode and save
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(screenshot_data))
            
            print(f"   ✓ Screenshot saved: {filename}")
        else:
            print(f"   ✗ Error: {response['message']}")
            return
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("Check the current directory for screenshot files.")
        print("=" * 60)
        
        await controller.disconnect()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
