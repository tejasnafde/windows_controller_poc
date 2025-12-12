#!/usr/bin/env python3
"""
Brain Example - High-level UI Automation

This demonstrates how the "brain" system sends high-level instructions
to the "hands" (Windows client) to perform UI automation tasks.

The brain doesn't need to know about coordinates - it just says
"click chart_e200" and the hands figure out where that is on the screen.
"""

import asyncio
import base64
from datetime import datetime
from action_executor import ActionExecutorContext
from instruction_schema import Action


# Configuration
SERVER_URL = 'ws://34.63.226.183:8765'  # Update with your server URL


async def save_screenshot(screenshot_b64: str, filename: str):
    """Save base64 screenshot to file."""
    if screenshot_b64:
        img_data = base64.b64decode(screenshot_b64)
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"   💾 Saved: {filename}")


async def main():
    """Main brain logic - click all Chart1 templates."""
    
    print("=" * 70)
    print("Brain Example: Click All Chart1 Templates")
    print("=" * 70)
    print(f"\nServer: {SERVER_URL}\n")
    
    # Define the sequence of actions using available templates
    # Each action specifies:
    # - element: template name (must match filename in templates/ folder)
    # - screenshot: when to capture screenshots
    # - delay: how long to wait after this action
    # - index: which match to click if template appears multiple times (0-based, optional)
    actions = [
        # Row 1 - Chart 1 templates
        Action("chart1_e200", screenshot=False, delay=1.0),
        Action("chart1_e400", screenshot=False, delay=1.0),
        Action("chart1_enh200", screenshot=False, delay=0.5),
        Action("chart1_eweme20", screenshot=False, delay=0.5),
        Action("chart1_hbv100", screenshot=False, delay=0.5),
        Action("chart1_m800", screenshot=False, delay=0.3),
        Action("chart1_mew100", screenshot=False, delay=0.3),
        Action("chart1_tzvec20", screenshot=False, delay=0.3),
        Action("chart1_vlnea70", screenshot=False, delay=0.3),
        Action("chart1_w150", screenshot=False, delay=0.3),
        Action("chart1_w400", screenshot=False, delay=0.3),
        Action("chart1_wemew40", screenshot=False, delay=0.3),
        Action("chart1_wemew70", screenshot=False, delay=1.0),
        
        # Navigation arrows - demonstrates using index for multiple matches
        # If navigate_chart_arrows has left/right arrows, use index to select which one
        # Action("navigate_chart_arrows", screenshot=False, delay=0.5, index=0),  # Click first (left) arrow
        # Action("navigate_chart_arrows", screenshot=False, delay=0.5, index=1),  # Click second (right) arrow
        
        # Chart selection - top 5 buttons (vertical layout)
        # Action("chart_top_5", screenshot=False, delay=0.5, index=0),  # Click topmost chart
        # Action("chart_top_5", screenshot=False, delay=0.5, index=2),  # Click middle chart
        # Action("chart_top_5", screenshot=False, delay=0.5, index=4),  # Click bottom chart
        
        # Chart selection - right 3 buttons (horizontal layout)
        # Action("chart_right_3", screenshot=False, delay=0.5, index=0),  # Click leftmost
        # Action("chart_right_3", screenshot=False, delay=0.5, index=1),  # Click middle
        # Action("chart_right_3", screenshot=False, delay=0.5, index=2),  # Click rightmost
        
        # Occlusion controls - left/right
        # Action("occlusion_l_r", screenshot=False, delay=0.5, index=0),  # Click left occlusion
        # Action("occlusion_l_r", screenshot=False, delay=0.5, index=1),  # Click right occlusion
        
        # PD value setter
        # Action("set_pd_value", screenshot=False, delay=0.5),
        
        # Tab navigation
        # Action("tab_chart2", screenshot=False, delay=0.5),
        
        # Right-click examples (useful for context menus)
        # Action("chart1_e200", screenshot=False, delay=0.5, button='right'),  # Right-click on chart
        
        # Middle-click examples (if needed)
        # Action("some_element", screenshot=False, delay=0.5, button='middle'),
    ]
    
    try:
        # Connect to server and execute actions
        async with ActionExecutorContext(SERVER_URL) as executor:
            print("✓ Connected to relay server\n")
            
            # Get connected clients
            clients = await executor.list_clients()
            
            if not clients:
                print("✗ No clients connected!")
                print("\nMake sure:")
                print("  1. Windows client is running")
                print("  2. Client is connected to the relay server")
                print("  3. Templates have been generated (run generate_templates.py)")
                return
            
            client_id = clients[0]
            print(f"Using client: {client_id}\n")
            
            # First, test basic mouse movement (no template matching)
            print("Testing basic mouse movement...")
            test_positions = [
                (500, 500),
                (800, 600),
                (600, 400),
                (700, 700),
            ]
            
            for i, (x, y) in enumerate(test_positions, 1):
                try:
                    response = await executor.controller.send_command(client_id, {
                        'action': 'move_cursor',
                        'x': x,
                        'y': y
                    })
                    if response.get('status') == 'success':
                        print(f"  ✓ Moved to ({x}, {y})")
                    else:
                        print(f"  ✗ Failed to move to ({x}, {y}): {response.get('message')}")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"  ✗ Error moving to ({x}, {y}): {e}")
            
            print("\n✓ Mouse movement test complete!\n")
            
            # Execute the sequence
            print(f"Executing {len(actions)} template-based actions...\n")
            results = await executor.execute_sequence(client_id, actions)
            
            # Process results
            print("\n" + "=" * 70)
            print("Results")
            print("=" * 70 + "\n")
            
            for i, result in enumerate(results, 1):
                status = "✓" if result.success else "✗"
                print(f"{status} Action {i}: {result.action.element}")
                
                if result.success:
                    print(f"   Clicked at: {result.clicked_at}")
                    print(f"   Execution time: {result.execution_time:.2f}s")
                    
                    # Save screenshots
                    if result.before_screenshot:
                        filename = f"screenshots/brain_{i}_before.png"
                        await save_screenshot(result.before_screenshot, filename)
                    
                    if result.after_screenshot:
                        filename = f"screenshots/brain_{i}_after.png"
                        await save_screenshot(result.after_screenshot, filename)
                else:
                    print(f"   Error: {result.error}")
                
                print()
            
            # Summary
            successful = sum(1 for r in results if r.success)
            total_time = sum(r.execution_time for r in results)
            
            print("=" * 70)
            print(f"Summary: {successful}/{len(results)} actions successful")
            print(f"Total execution time: {total_time:.2f}s")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Create screenshots directory
    import os
    os.makedirs('screenshots', exist_ok=True)
    
    # Run the brain
    asyncio.run(main())
