#!/usr/bin/env python3
"""
Click All Row 1 Charts with Screenshots

This script clicks all 6 chart items in the first row of Chart1 section
using relative positioning from a base coordinate.

For each chart:
1. Takes a screenshot before clicking
2. Clicks the chart
3. Takes a screenshot after clicking
"""

import asyncio
import base64
from datetime import datetime
from controller_websocket import ControllerWebSocket


# Configuration
SERVER_URL = 'wss://d315fa0e928740.lhr.life'

# Base position for first chart in row 1
# Adjust these based on where Chart1 grid starts on your screen
BASE_X = 150  # X coordinate of first chart
BASE_Y = 450  # Y coordinate of first chart

# Chart grid layout
CHART_WIDTH = 100  # Approximate width of each chart item
CHART_GAP = 8      # Gap between charts
CHARTS_IN_ROW = 6  # Number of charts in row 1


async def take_and_save_screenshot(controller, client_id, label):
    """Take a screenshot and save it with a label."""
    print(f"  📸 Taking screenshot: {label}...")
    response = await controller.take_screenshot(client_id)
    
    if response['status'] == 'success':
        screenshot_data = response['data']['screenshot']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        filename = f"screenshot_{label}_{timestamp}.png"
        
        # Decode and save
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(screenshot_data))
        
        print(f"     ✓ Saved: {filename}")
        return filename
    else:
        print(f"     ✗ Error: {response['message']}")
        return None


async def click_at_position(controller, client_id, x, y, button='left'):
    """Click at specified coordinates."""
    response = await controller.click(client_id, x, y, button=button)
    
    if response['status'] == 'success':
        return True
    else:
        print(f"     ✗ Click failed: {response['message']}")
        return False


def calculate_chart_position(chart_index):
    """
    Calculate the click position for a chart in row 1.
    
    Args:
        chart_index: 0-5 for the 6 charts in row 1
    
    Returns:
        (x, y) tuple for the center of the chart
    """
    # Calculate X position: base + (chart_width + gap) * index + half_width
    x = BASE_X + (CHART_WIDTH + CHART_GAP) * chart_index + (CHART_WIDTH // 2)
    y = BASE_Y  # Same Y for all charts in row 1
    
    return (x, y)


async def main():
    """Main test flow - click all charts in row 1."""
    
    print("=" * 70)
    print("Click All Row 1 Charts Test")
    print("=" * 70)
    print(f"\nServer: {SERVER_URL}")
    print(f"Base Position: ({BASE_X}, {BASE_Y})")
    print(f"Charts to click: {CHARTS_IN_ROW} (Row 1 of Chart1 section)\n")
    
    controller = ControllerWebSocket(server_url=SERVER_URL)
    
    try:
        # Connect to relay server
        await controller.connect()
        print("✓ Connected to relay server\n")
        await asyncio.sleep(1)
        
        # Get connected clients
        clients = await controller.list_clients()
        if not clients:
            print("✗ No clients connected!")
            print("\nMake sure:")
            print("  1. Windows client is running")
            print("  2. Client is connected to the relay server")
            return
        
        client_id = clients[0]
        print(f"Using client: {client_id}\n")
        
        # Get screen info
        response = await controller.get_cursor_position(client_id)
        if response['status'] == 'success':
            data = response['data']
            print(f"Screen size: {data['screen_width']}x{data['screen_height']}\n")
        
        await asyncio.sleep(1)
        
        # Chart names for row 1
        chart_names = [
            "E 200",
            "E 100", 
            "E 70",
            "E 50",
            "E N 100 / D L C 50",
            "H B V 30 / P H T 40"
        ]
        
        results = []
        
        # Click each chart in row 1
        for i in range(CHARTS_IN_ROW):
            chart_name = chart_names[i]
            x, y = calculate_chart_position(i)
            
            print("=" * 70)
            print(f"Chart {i+1}/{CHARTS_IN_ROW}: {chart_name}")
            print(f"Position: ({x}, {y})")
            print("=" * 70)
            
            # Screenshot before
            before_file = await take_and_save_screenshot(
                controller, client_id, f"chart{i+1}_before"
            )
            
            await asyncio.sleep(0.5)
            
            # Click the chart
            print(f"  🖱️  Clicking chart at ({x}, {y})...")
            success = await click_at_position(controller, client_id, x, y, 'left')
            
            if success:
                print(f"     ✓ Clicked successfully")
            
            await asyncio.sleep(0.5)
            
            # Screenshot after
            after_file = await take_and_save_screenshot(
                controller, client_id, f"chart{i+1}_after"
            )
            
            results.append({
                'chart': chart_name,
                'position': (x, y),
                'before': before_file,
                'after': after_file,
                'success': success
            })
            
            await asyncio.sleep(1)
            print()
        
        # Summary
        print("=" * 70)
        print("Test Completed!")
        print("=" * 70)
        print(f"\nClicked {CHARTS_IN_ROW} charts in Row 1:\n")
        
        for i, result in enumerate(results, 1):
            status = "✓" if result['success'] else "✗"
            print(f"{status} Chart {i}: {result['chart']}")
            print(f"   Position: {result['position']}")
            print(f"   Before:   {result['before']}")
            print(f"   After:    {result['after']}")
            print()
        
        print("=" * 70)
        print("Check the 'LAST CLICKED' box in screenshots to verify each click!")
        print("=" * 70)
        
        await controller.disconnect()
        
    except ConnectionError as e:
        print(f"\n✗ Connection Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure relay server is running")
        print("  2. Make sure Windows client is connected")
        print("  3. Check server URL is correct")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
