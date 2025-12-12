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


async def verify_click_result(result, template_name: str) -> dict:
    """Verify if a click action was successful and return detailed info.
    
    Args:
        result: ActionResult object from the click action
        template_name: Name of the template that was clicked
    
    Returns:
        dict with verification details including success status, coordinates, etc.
    """
    verification = {
        'template': template_name,
        'success': result.success,
        'clicked_at': result.clicked_at,
        'execution_time': result.execution_time,
        'error': result.error,
        'has_before_screenshot': result.before_screenshot is not None,
        'has_after_screenshot': result.after_screenshot is not None
    }
    
    if result.success:
        if result.clicked_at:
            x, y = result.clicked_at
            verification['message'] = f"✓ Successfully clicked {template_name} at ({x}, {y})"
        else:
            verification['message'] = f"✓ Clicked {template_name} but coordinates not available"
    else:
        verification['message'] = f"✗ Failed to click {template_name}: {result.error}"
    
    return verification


async def test_left_right_templates(executor, client_id: str):
    """Test clicking on left and right eye templates (add, axial, spherical, cylindrical).
    
    Args:
        executor: ActionExecutor instance
        client_id: Target client ID
    
    Returns:
        List of verification results for each template
    """
    print("=" * 70)
    print("Testing Left/Right Eye Templates")
    print("=" * 70 + "\n")
    
    # Define all left/right templates to test
    templates_to_test = [
        "right_add",
        "right_axial",
        "right_spherical",
        "right_cylindrical",
        "left_add",
        "left_axial",
        "left_spherical",
        "left_cylindrical",
    ]
    
    # Create actions with screenshots enabled for verification
    actions = [
        Action(template, screenshot=True, delay=1.0)
        for template in templates_to_test
    ]
    
    print(f"Testing {len(templates_to_test)} templates...\n")
    
    # Execute actions and collect results
    results = await executor.execute_sequence(client_id, actions)
    
    # Verify each result
    verifications = []
    for i, (result, template_name) in enumerate(zip(results, templates_to_test), 1):
        verification = await verify_click_result(result, template_name)
        verifications.append(verification)
        
        # Print verification status
        status = "✓" if verification['success'] else "✗"
        print(f"{status} Test {i}/{len(templates_to_test)}: {template_name}")
        print(f"   {verification['message']}")
        
        if verification['success']:
            print(f"   Execution time: {verification['execution_time']:.2f}s")
            
            # Save screenshots for verification
            if result.before_screenshot:
                filename = f"screenshots/test_{template_name}_before.png"
                await save_screenshot(result.before_screenshot, filename)
            
            if result.after_screenshot:
                filename = f"screenshots/test_{template_name}_after.png"
                await save_screenshot(result.after_screenshot, filename)
        else:
            print(f"   Error: {verification['error']}")
        
        print()
    
    # Summary
    successful = sum(1 for v in verifications if v['success'])
    print("=" * 70)
    print(f"Left/Right Templates Test Summary: {successful}/{len(verifications)} successful")
    print("=" * 70 + "\n")
    
    return verifications


async def test_single_template(executor, client_id: str, template_name: str, 
                               screenshot: bool = True, delay: float = 1.0) -> dict:
    """Test clicking on a single template with detailed verification.
    
    Args:
        executor: ActionExecutor instance
        client_id: Target client ID
        template_name: Name of template to test
        screenshot: Whether to capture screenshots
        delay: Delay after action
    
    Returns:
        Verification dict with detailed results
    """
    print(f"Testing single template: {template_name}")
    
    action = Action(template_name, screenshot=screenshot, delay=delay)
    result = await executor.click_element(
        client_id, 
        template_name,
        action.screenshot.to_dict()
    )
    
    verification = await verify_click_result(result, template_name)
    
    # Print results
    status = "✓" if verification['success'] else "✗"
    print(f"{status} {verification['message']}")
    
    if verification['success']:
        print(f"   Clicked at: {verification['clicked_at']}")
        print(f"   Execution time: {verification['execution_time']:.2f}s")
        
        # Save screenshots
        if result.before_screenshot:
            filename = f"screenshots/single_{template_name}_before.png"
            await save_screenshot(result.before_screenshot, filename)
        
        if result.after_screenshot:
            filename = f"screenshots/single_{template_name}_after.png"
            await save_screenshot(result.after_screenshot, filename)
    else:
        print(f"   Error: {verification['error']}")
    
    print()
    return verification


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
        # Action("chart1_e200", screenshot=False, delay=1.0),
        # Action("chart1_e400", screenshot=False, delay=1.0),
        # Action("chart1_enh200", screenshot=False, delay=0.5),
        # Action("chart1_eweme20", screenshot=False, delay=0.5),
        # Action("chart1_hbv100", screenshot=False, delay=0.5),
        # Action("chart1_m800", screenshot=False, delay=0.3),
        # Action("chart1_mew100", screenshot=False, delay=0.3),
        # Action("chart1_tzvec20", screenshot=False, delay=0.3),
        # Action("chart1_vlnea70", screenshot=False, delay=0.3),
        # Action("chart1_w150", screenshot=False, delay=0.3),
        # Action("chart1_w400", screenshot=False, delay=0.3),
        # Action("chart1_wemew40", screenshot=False, delay=0.3),
        # Action("chart1_wemew70", screenshot=False, delay=1.0),
        
        # Left/Right eye templates with offset to click number fields
        # Match the static label (e.g., "ADD") and click the number field to the left/right
        # Negative X offset = click to the left, Positive X offset = click to the right
        Action("right_add", screenshot=False, delay=1.0, offset=(-100, 0)),  # Click 100px left of "ADD" label
        Action("right_axial", screenshot=False, delay=1.0, offset=(-100, 0)),
        Action("right_spherical", screenshot=False, delay=1.0, offset=(-100, 0)),
        Action("right_cylindrical", screenshot=False, delay=1.0, offset=(-100, 0)),
        Action("left_add", screenshot=False, delay=1.0, offset=(100, 0)),  # Click 100px right of "ADD" label
        Action("left_axial", screenshot=False, delay=1.0, offset=(100, 0)),
        Action("left_spherical", screenshot=False, delay=1.0, offset=(100, 0)),
        Action("left_cylindrical", screenshot=False, delay=1.0, offset=(100, 0)),
        
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
            print("FINAL SUMMARY")
            print("=" * 70)
            print(f"Total actions: {successful}/{len(results)} successful")
            print(f"Total execution time: {total_time:.2f}s")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_only_left_right_templates():
    """Standalone function to test only left/right eye templates."""
    print("=" * 70)
    print("Left/Right Eye Templates Test Only")
    print("=" * 70)
    print(f"\nServer: {SERVER_URL}\n")
    
    try:
        async with ActionExecutorContext(SERVER_URL) as executor:
            print("✓ Connected to relay server\n")
            
            clients = await executor.list_clients()
            
            if not clients:
                print("✗ No clients connected!")
                return
            
            client_id = clients[0]
            print(f"Using client: {client_id}\n")
            
            # Run the left/right templates test
            results = await test_left_right_templates(executor, client_id)
            
            # Print detailed summary
            print("\n" + "=" * 70)
            print("Detailed Results")
            print("=" * 70 + "\n")
            
            for verification in results:
                status = "✓" if verification['success'] else "✗"
                print(f"{status} {verification['template']}")
                if verification['success']:
                    print(f"   Clicked at: {verification['clicked_at']}")
                    print(f"   Time: {verification['execution_time']:.2f}s")
                else:
                    print(f"   Error: {verification['error']}")
                print()
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Create screenshots directory
    import os
    import sys
    os.makedirs('screenshots', exist_ok=True)
    
    # Check if user wants to test only left/right templates
    if len(sys.argv) > 1 and sys.argv[1] == '--test-left-right':
        # Run only left/right templates test
        asyncio.run(test_only_left_right_templates())
    else:
        # Run the full brain example
        asyncio.run(main())
