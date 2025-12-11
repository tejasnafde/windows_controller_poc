"""
WebSocket Relay Server

Central server that relays commands between controllers and Windows clients.
Clients and controllers connect to this server via WebSocket.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
import websockets
from websockets.server import WebSocketServerProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8123

# Connected clients and controllers
clients: Dict[str, WebSocketServerProtocol] = {}  # client_id -> websocket
controllers: Set[WebSocketServerProtocol] = set()


class RelayServer:
    """WebSocket relay server for remote control."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
    
    async def register_client(self, websocket: WebSocketServerProtocol, client_id: str):
        """Register a Windows client."""
        clients[client_id] = websocket
        logger.info(f"Client registered: {client_id} from {websocket.remote_address}")
        
        # Notify all controllers about new client
        await self.broadcast_to_controllers({
            'type': 'client_connected',
            'client_id': client_id,
            'timestamp': datetime.now().isoformat()
        })
    
    async def unregister_client(self, client_id: str):
        """Unregister a Windows client."""
        if client_id in clients:
            del clients[client_id]
            logger.info(f"Client unregistered: {client_id}")
            
            # Notify controllers
            await self.broadcast_to_controllers({
                'type': 'client_disconnected',
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            })
    
    async def register_controller(self, websocket: WebSocketServerProtocol):
        """Register a controller."""
        controllers.add(websocket)
        logger.info(f"Controller registered from {websocket.remote_address}")
        
        # Send list of connected clients
        await websocket.send(json.dumps({
            'type': 'client_list',
            'clients': list(clients.keys()),
            'timestamp': datetime.now().isoformat()
        }))
    
    async def unregister_controller(self, websocket: WebSocketServerProtocol):
        """Unregister a controller."""
        controllers.discard(websocket)
        logger.info(f"Controller unregistered from {websocket.remote_address}")
    
    async def broadcast_to_controllers(self, message: dict):
        """Send message to all connected controllers."""
        if controllers:
            message_str = json.dumps(message)
            await asyncio.gather(
                *[controller.send(message_str) for controller in controllers],
                return_exceptions=True
            )
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, message: dict, client_id: str):
        """Handle message from a Windows client (usually responses)."""
        # Client is sending a response to a command
        # Forward it to all controllers
        message['client_id'] = client_id
        message['timestamp'] = datetime.now().isoformat()
        await self.broadcast_to_controllers(message)
        logger.info(f"Forwarded response from client {client_id}: {message.get('type', 'unknown')}")
    
    async def handle_controller_message(self, websocket: WebSocketServerProtocol, message: dict):
        """Handle message from a controller (usually commands)."""
        target_client_id = message.get('client_id')
        
        if not target_client_id:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'No client_id specified',
                'timestamp': datetime.now().isoformat()
            }))
            return
        
        if target_client_id not in clients:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Client {target_client_id} not connected',
                'timestamp': datetime.now().isoformat()
            }))
            return
        
        # Forward command to target client
        target_websocket = clients[target_client_id]
        try:
            await target_websocket.send(json.dumps(message))
            logger.info(f"Forwarded command to client {target_client_id}: {message.get('action', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to send to client {target_client_id}: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Failed to send to client: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handler(self, websocket: WebSocketServerProtocol, path: str):
        """Main WebSocket connection handler."""
        connection_type = None
        client_id = None
        
        try:
            # First message should identify the connection type
            async for message_str in websocket:
                message = json.loads(message_str)
                
                # Handle registration
                if connection_type is None:
                    if message.get('type') == 'register_client':
                        connection_type = 'client'
                        client_id = message.get('client_id')
                        if not client_id:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': 'client_id required'
                            }))
                            break
                        await self.register_client(websocket, client_id)
                        await websocket.send(json.dumps({
                            'type': 'registered',
                            'client_id': client_id
                        }))
                    
                    elif message.get('type') == 'register_controller':
                        connection_type = 'controller'
                        await self.register_controller(websocket)
                        await websocket.send(json.dumps({
                            'type': 'registered',
                            'role': 'controller'
                        }))
                    
                    else:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'First message must be registration'
                        }))
                        break
                
                # Handle subsequent messages
                else:
                    if connection_type == 'client':
                        await self.handle_client_message(websocket, message, client_id)
                    elif connection_type == 'controller':
                        await self.handle_controller_message(websocket, message)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"Error handling connection: {e}")
        finally:
            # Cleanup
            if connection_type == 'client' and client_id:
                await self.unregister_client(client_id)
            elif connection_type == 'controller':
                await self.unregister_controller(websocket)
    
    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket relay server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handler, self.host, self.port):
            logger.info(f"Server running on ws://{self.host}:{self.port}")
            logger.info("Waiting for clients and controllers to connect...")
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WebSocket Relay Server')
    parser.add_argument('--host', default=DEFAULT_HOST, help='Host to bind to')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port to listen on')
    
    args = parser.parse_args()
    
    server = RelayServer(host=args.host, port=args.port)
    await server.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
