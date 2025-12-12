"""
Action Executor - High-level interface for executing UI actions

This module provides a high-level interface for the "brain" to send
instructions to the "hands" (Windows client) via the relay server.
"""

import asyncio
from typing import List
from datetime import datetime
from controller_websocket import ControllerWebSocket
from instruction_schema import Action, ActionResult


class ActionExecutor:
    """Execute high-level UI actions on remote client."""
    
    def __init__(self, server_url: str):
        """Initialize action executor.
        
        Args:
            server_url: WebSocket relay server URL
        """
        self.server_url = server_url
        self.controller = ControllerWebSocket(server_url=server_url)
        self.connected = False
    
    async def connect(self):
        """Connect to relay server."""
        await self.controller.connect()
        self.connected = True
    
    async def disconnect(self):
        """Disconnect from relay server."""
        await self.controller.disconnect()
        self.connected = False
    
    async def list_clients(self) -> List[str]:
        """Get list of connected clients."""
        return await self.controller.list_clients()
    
    async def click_element(self, client_id: str, element: str, 
                           screenshot: dict = None) -> ActionResult:
        """Click a UI element by template name.
        
        Args:
            client_id: Target client ID
            element: Template name (e.g., "chart_e200")
            screenshot: Screenshot config, e.g.:
                        {"before": True, "after": True}
                        {"before": True, "after": False}
                        True (shorthand for both)
                        False (shorthand for neither)
        
        Returns:
            ActionResult with success status, coordinates, and screenshots
        """
        if screenshot is None:
            screenshot = {"before": True, "after": True}
        
        action = Action(element, screenshot=screenshot)
        command = action.to_command()
        
        start_time = datetime.now()
        response = await self.controller.send_command(client_id, command)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = ActionResult.from_response(response, action)
        result.execution_time = execution_time
        
        return result
    
    async def execute_sequence(self, client_id: str, 
                              actions: List[Action]) -> List[ActionResult]:
        """Execute a sequence of actions.
        
        Args:
            client_id: Target client ID
            actions: List of Action objects
        
        Returns:
            List of ActionResult objects
        """
        results = []
        
        for action in actions:
            try:
                result = await self.click_element(
                    client_id, 
                    action.element, 
                    action.screenshot.to_dict()
                )
                results.append(result)
            except (TimeoutError, Exception) as e:
                # Create a failed ActionResult for this action
                error_result = ActionResult(
                    success=False,
                    action=action,  # Pass the Action object, not just element string
                    clicked_at=None,
                    before_screenshot=None,
                    after_screenshot=None,
                    error=str(e),
                    execution_time=0.0
                )
                results.append(error_result)
                print(f"⚠️  Action failed for {action.element}: {e}")
                print(f"   Continuing with next action...")
            
            # Wait before next action
            if action.delay > 0:
                await asyncio.sleep(action.delay)
        
        return results


# Context manager support
class ActionExecutorContext:
    """Context manager for ActionExecutor."""
    
    def __init__(self, server_url: str):
        self.executor = ActionExecutor(server_url)
    
    async def __aenter__(self):
        await self.executor.connect()
        return self.executor
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.executor.disconnect()


# Example usage
if __name__ == '__main__':
    async def main():
        server_url = 'wss://example.lhr.life'
        
        async with ActionExecutorContext(server_url) as executor:
            # Get clients
            clients = await executor.list_clients()
            print(f"Connected clients: {clients}")
            
            if clients:
                client_id = clients[0]
                
                # Click single element
                result = await executor.click_element(
                    client_id,
                    "chart_e200",
                    screenshot={"before": True, "after": True}
                )
                
                print(result)
    
    asyncio.run(main())
