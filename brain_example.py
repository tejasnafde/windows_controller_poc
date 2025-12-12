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
SERVER_URL = 'wss://29cb14c9edd5.ngrok-free.app'  # Update with your server URL


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
    actions = [
        # Row 1 - Chart 1 templates (with full screenshots for first few)
        Action("chart1_e200", screenshot=True, delay=1.0),
        Action("chart1_e400", screenshot=True, delay=1.0),
        Action("chart1_enh200", screenshot={"before": True, "after": False}, delay=0.5),
        Action("chart1_eweme20", screenshot={"before": True, "after": False}, delay=0.5),
        Action("chart1_hbv100", screenshot={"before": False, "after": True}, delay=0.5),
        Action("chart1_m800", screenshot=False, delay=0.3),
        Action("chart1_mew100", screenshot=False, delay=0.3),
        Action("chart1_tzvec20", screenshot=False, delay=0.3),
        Action("chart1_vlnea70", screenshot=False, delay=0.3),
        Action("chart1_w150", screenshot=False, delay=0.3),
        Action("chart1_w400", screenshot=False, delay=0.3),
        Action("chart1_wemew40", screenshot=False, delay=0.3),
        Action("chart1_wemew70", screenshot=True, delay=1.0),  # Last one with screenshot
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
            
            # Execute the sequence
            print(f"Executing {len(actions)} actions...\n")
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
