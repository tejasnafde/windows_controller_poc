#!/usr/bin/env python3
"""
Windows Client - Remote Control Agent

This script runs on a Windows PC and listens for remote commands to control
the cursor and perform click actions.
"""

import socket
import json
import logging
import sys
import pyautogui
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('windows_client.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5555
BUFFER_SIZE = 1024

# PyAutoGUI safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions


class WindowsClient:
    """Windows automation client that executes remote commands."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def start(self):
        """Start the client server and listen for connections."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logger.info(f"Windows Client listening on {self.host}:{self.port}")
            logger.info(f"Screen size: {pyautogui.size()}")
            logger.info("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    logger.info(f"Connection from {address}")
                    self.handle_client(client_socket)
                except KeyboardInterrupt:
                    logger.info("Shutting down...")
                    self.running = False
                except Exception as e:
                    logger.error(f"Error accepting connection: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
        finally:
            self.stop()
    
    def handle_client(self, client_socket: socket.socket):
        """Handle commands from a connected client."""
        try:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                    
                try:
                    command = json.loads(data.decode('utf-8'))
                    logger.info(f"Received command: {command}")
                    
                    response = self.execute_command(command)
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    logger.info(f"Sent response: {response}")
                    
                except json.JSONDecodeError as e:
                    error_response = {
                        'status': 'error',
                        'message': f'Invalid JSON: {str(e)}'
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                    logger.error(f"JSON decode error: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()
            logger.info("Client disconnected")
    
    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command and return the result.
        
        Args:
            command: Dictionary containing action and parameters
            
        Returns:
            Dictionary with status and result data
        """
        action = command.get('action')
        
        try:
            if action == 'move_cursor':
                return self.move_cursor(command)
            elif action == 'click':
                return self.click(command)
            elif action == 'move_relative':
                return self.move_relative(command)
            elif action == 'get_position':
                return self.get_position()
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown action: {action}'
                }
        except Exception as e:
            logger.error(f"Error executing command {action}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def move_cursor(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Move cursor to absolute position."""
        x = command.get('x')
        y = command.get('y')
        
        if x is None or y is None:
            return {
                'status': 'error',
                'message': 'Missing x or y coordinates'
            }
        
        try:
            pyautogui.moveTo(x, y)
            current_pos = pyautogui.position()
            return {
                'status': 'success',
                'message': f'Moved cursor to ({x}, {y})',
                'data': {
                    'x': current_pos.x,
                    'y': current_pos.y
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to move cursor: {str(e)}'
            }
    
    def click(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Click at specified position."""
        x = command.get('x')
        y = command.get('y')
        button = command.get('button', 'left')
        
        if button not in ['left', 'right', 'middle']:
            return {
                'status': 'error',
                'message': f'Invalid button: {button}'
            }
        
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
                message = f'Clicked {button} button at ({x}, {y})'
            else:
                pyautogui.click(button=button)
                pos = pyautogui.position()
                message = f'Clicked {button} button at current position ({pos.x}, {pos.y})'
            
            return {
                'status': 'success',
                'message': message
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to click: {str(e)}'
            }
    
    def move_relative(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Move cursor relative to current position."""
        x = command.get('x', 0)
        y = command.get('y', 0)
        
        try:
            pyautogui.moveRel(x, y)
            current_pos = pyautogui.position()
            return {
                'status': 'success',
                'message': f'Moved cursor by ({x}, {y})',
                'data': {
                    'x': current_pos.x,
                    'y': current_pos.y
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to move cursor: {str(e)}'
            }
    
    def get_position(self) -> Dict[str, Any]:
        """Get current cursor position."""
        try:
            pos = pyautogui.position()
            screen_size = pyautogui.size()
            return {
                'status': 'success',
                'message': 'Retrieved cursor position',
                'data': {
                    'x': pos.x,
                    'y': pos.y,
                    'screen_width': screen_size.width,
                    'screen_height': screen_size.height
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to get position: {str(e)}'
            }
    
    def stop(self):
        """Stop the server and cleanup."""
        self.running = False
        if self.socket:
            self.socket.close()
        logger.info("Server stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows Remote Control Client')
    parser.add_argument('--host', default=DEFAULT_HOST, help='Host to bind to')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port to listen on')
    
    args = parser.parse_args()
    
    client = WindowsClient(host=args.host, port=args.port)
    
    try:
        client.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
