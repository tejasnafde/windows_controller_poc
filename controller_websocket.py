#!/usr/bin/env python3
"""
Controller Service with WebSocket

Connects to relay server to send commands to Windows clients.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_SERVER_URL = 'ws://localhost:8765'
TIMEOUT = 10


class ControllerWebSocket:
    """Controller that connects to relay server to send commands."""
    
    def __init__(self, server_url: str = DEFAULT_SERVER_URL):
        self.server_url = server_url
        self.websocket = None
        self.connected_clients: List[str] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}
    
    async def connect(self):
        """Connect to relay server."""
        logger.info(f"Connecting to relay server at {self.server_url}")
        
        self.websocket = await websockets.connect(self.server_url)
        
        # Register as controller
        await self.websocket.send(json.dumps({
            'type': 'register_controller'
        }))
        
        # Wait for registration confirmation
        response = await self.websocket.recv()
        response_data = json.loads(response)
        
        if response_data.get('type') == 'registered':
            logger.info("Registered as controller")
            
            # Start listening for messages in background
            asyncio.create_task(self._listen_for_messages())
            
            return True
        else:
            logger.error(f"Registration failed: {response_data}")
            return False
    
    async def disconnect(self):
        """Disconnect from server."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from server")
    
    async def _listen_for_messages(self):
        """Listen for messages from server."""
        try:
            async for message_str in self.websocket:
                message = json.loads(message_str)
                await self._handle_server_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection to server closed")
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
    
    async def _handle_server_message(self, message: dict):
        """Handle message from server."""
        msg_type = message.get('type')
        
        if msg_type == 'client_list':
            self.connected_clients = message.get('clients', [])
            logger.info(f"Connected clients: {self.connected_clients}")
        
        elif msg_type == 'client_connected':
            client_id = message.get('client_id')
            if client_id not in self.connected_clients:
                self.connected_clients.append(client_id)
            logger.info(f"Client connected: {client_id}")
        
        elif msg_type == 'client_disconnected':
            client_id = message.get('client_id')
            if client_id in self.connected_clients:
                self.connected_clients.remove(client_id)
            logger.info(f"Client disconnected: {client_id}")
        
        elif msg_type == 'response':
            # Response from a client
            client_id = message.get('client_id')
            logger.info(f"Received response from {client_id}: {message.get('status')}")
            
            # If there's a pending future for this response, resolve it
            if client_id in self.pending_responses:
                future = self.pending_responses.pop(client_id)
                if not future.done():
                    future.set_result(message)
        
        elif msg_type == 'error':
            logger.error(f"Server error: {message.get('message')}")
    
    async def send_command(self, client_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to a specific client and wait for response.
        
        Args:
            client_id: Target client ID
            command: Command dictionary
            
        Returns:
            Response from client
        """
        if not self.websocket:
            raise ConnectionError("Not connected to server")
        
        # Add client_id to command
        command['client_id'] = client_id
        
        # Create future for response
        future = asyncio.Future()
        self.pending_responses[client_id] = future
        
        # Send command
        await self.websocket.send(json.dumps(command))
        logger.info(f"Sent command to {client_id}: {command.get('action')}")
        
        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=TIMEOUT)
            return response
        except asyncio.TimeoutError:
            self.pending_responses.pop(client_id, None)
            raise TimeoutError(f"Timeout waiting for response from {client_id}")
    
    async def list_clients(self) -> List[str]:
        """Get list of connected clients."""
        return self.connected_clients.copy()
    
    async def move_cursor(self, client_id: str, x: int, y: int) -> Dict[str, Any]:
        """Move cursor on target client."""
        command = {
            'action': 'move_cursor',
            'x': x,
            'y': y
        }
        return await self.send_command(client_id, command)
    
    async def click(self, client_id: str, x: int = None, y: int = None, 
                   button: str = 'left') -> Dict[str, Any]:
        """Click on target client."""
        command = {
            'action': 'click',
            'button': button
        }
        if x is not None:
            command['x'] = x
        if y is not None:
            command['y'] = y
        return await self.send_command(client_id, command)
    
    async def move_relative(self, client_id: str, x: int, y: int) -> Dict[str, Any]:
        """Move cursor relatively on target client."""
        command = {
            'action': 'move_relative',
            'x': x,
            'y': y
        }
        return await self.send_command(client_id, command)
    
    async def get_cursor_position(self, client_id: str) -> Dict[str, Any]:
        """Get cursor position from target client."""
        command = {
            'action': 'get_position'
        }
        return await self.send_command(client_id, command)


async def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WebSocket Controller')
    parser.add_argument('--server', default=DEFAULT_SERVER_URL, help='Relay server URL')
    parser.add_argument('--client-id', help='Target client ID')
    parser.add_argument('--action', choices=['list', 'move', 'click', 'get_pos'], 
                       default='list', help='Action to perform')
    parser.add_argument('--x', type=int, help='X coordinate')
    parser.add_argument('--y', type=int, help='Y coordinate')
    
    args = parser.parse_args()
    
    controller = ControllerWebSocket(server_url=args.server)
    
    try:
        # Connect to server
        await controller.connect()
        
        # Wait a moment for client list
        await asyncio.sleep(0.5)
        
        if args.action == 'list':
            clients = await controller.list_clients()
            print(f"\nConnected clients: {len(clients)}")
            for client in clients:
                print(f"  - {client}")
        
        elif args.client_id:
            if args.action == 'move':
                if args.x is None or args.y is None:
                    print("Error: --x and --y required for move action")
                else:
                    response = await controller.move_cursor(args.client_id, args.x, args.y)
                    print(f"\nResponse: {json.dumps(response, indent=2)}")
            
            elif args.action == 'click':
                response = await controller.click(args.client_id, args.x, args.y)
                print(f"\nResponse: {json.dumps(response, indent=2)}")
            
            elif args.action == 'get_pos':
                response = await controller.get_cursor_position(args.client_id)
                print(f"\nResponse: {json.dumps(response, indent=2)}")
        else:
            print("Error: --client-id required for this action")
        
        await controller.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
