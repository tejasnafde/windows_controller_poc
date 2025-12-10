#!/usr/bin/env python3
"""
Controller Service - Remote Windows Control

This service sends commands to the Windows client to control cursor and clicks.
"""

import socket
import json
import logging
from typing import Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_PORT = 5555
BUFFER_SIZE = 1024
TIMEOUT = 5


class ControllerService:
    """Service to send commands to Windows client."""
    
    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: int = TIMEOUT):
        """
        Initialize controller service.
        
        Args:
            host: IP address or hostname of Windows client
            port: Port number to connect to
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
    
    def _send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to the Windows client and get response.
        
        Args:
            command: Command dictionary to send
            
        Returns:
            Response dictionary from the client
            
        Raises:
            ConnectionError: If connection fails
            TimeoutError: If request times out
        """
        try:
            # Create socket and connect
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                
                logger.info(f"Connecting to {self.host}:{self.port}")
                sock.connect((self.host, self.port))
                
                # Send command
                command_json = json.dumps(command)
                sock.send(command_json.encode('utf-8'))
                logger.info(f"Sent command: {command}")
                
                # Receive response
                data = sock.recv(BUFFER_SIZE)
                response = json.loads(data.decode('utf-8'))
                logger.info(f"Received response: {response}")
                
                return response
                
        except socket.timeout:
            raise TimeoutError(f"Connection to {self.host}:{self.port} timed out")
        except ConnectionRefusedError:
            raise ConnectionError(f"Connection refused by {self.host}:{self.port}. Is the client running?")
        except Exception as e:
            raise ConnectionError(f"Failed to send command: {str(e)}")
    
    def move_cursor(self, x: int, y: int) -> Dict[str, Any]:
        """
        Move cursor to absolute position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Response from client
        """
        command = {
            'action': 'move_cursor',
            'x': x,
            'y': y
        }
        return self._send_command(command)
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left') -> Dict[str, Any]:
        """
        Click at specified position or current position.
        
        Args:
            x: X coordinate (optional, clicks at current position if not provided)
            y: Y coordinate (optional)
            button: Mouse button ('left', 'right', or 'middle')
            
        Returns:
            Response from client
        """
        command = {
            'action': 'click',
            'button': button
        }
        if x is not None:
            command['x'] = x
        if y is not None:
            command['y'] = y
            
        return self._send_command(command)
    
    def move_relative(self, x: int, y: int) -> Dict[str, Any]:
        """
        Move cursor relative to current position.
        
        Args:
            x: X offset
            y: Y offset
            
        Returns:
            Response from client
        """
        command = {
            'action': 'move_relative',
            'x': x,
            'y': y
        }
        return self._send_command(command)
    
    def get_cursor_position(self) -> Dict[str, Any]:
        """
        Get current cursor position and screen information.
        
        Returns:
            Response from client with position data
        """
        command = {
            'action': 'get_position'
        }
        return self._send_command(command)


# Convenience functions for quick usage
def send_move_cursor(host: str, port: int, x: int, y: int) -> Dict[str, Any]:
    """Send move cursor command."""
    controller = ControllerService(host, port)
    return controller.move_cursor(x, y)


def send_click(host: str, port: int, x: Optional[int] = None, 
               y: Optional[int] = None, button: str = 'left') -> Dict[str, Any]:
    """Send click command."""
    controller = ControllerService(host, port)
    return controller.click(x, y, button)


def send_move_relative(host: str, port: int, x: int, y: int) -> Dict[str, Any]:
    """Send relative move command."""
    controller = ControllerService(host, port)
    return controller.move_relative(x, y)


def get_cursor_position(host: str, port: int) -> Dict[str, Any]:
    """Get cursor position."""
    controller = ControllerService(host, port)
    return controller.get_cursor_position()


if __name__ == '__main__':
    # Simple CLI interface
    import argparse
    
    parser = argparse.ArgumentParser(description='Send commands to Windows client')
    parser.add_argument('host', help='Windows client IP address')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port number')
    parser.add_argument('--action', required=True, 
                       choices=['move', 'click', 'move_rel', 'get_pos'],
                       help='Action to perform')
    parser.add_argument('--x', type=int, help='X coordinate')
    parser.add_argument('--y', type=int, help='Y coordinate')
    parser.add_argument('--button', default='left', 
                       choices=['left', 'right', 'middle'],
                       help='Mouse button for click action')
    
    args = parser.parse_args()
    
    controller = ControllerService(args.host, args.port)
    
    try:
        if args.action == 'move':
            if args.x is None or args.y is None:
                parser.error("--x and --y required for move action")
            response = controller.move_cursor(args.x, args.y)
            
        elif args.action == 'click':
            response = controller.click(args.x, args.y, args.button)
            
        elif args.action == 'move_rel':
            if args.x is None or args.y is None:
                parser.error("--x and --y required for move_rel action")
            response = controller.move_relative(args.x, args.y)
            
        elif args.action == 'get_pos':
            response = controller.get_cursor_position()
        
        print(f"\nResponse: {json.dumps(response, indent=2)}")
        
        if response.get('status') == 'success':
            print("✓ Command executed successfully")
        else:
            print("✗ Command failed")
            
    except (ConnectionError, TimeoutError) as e:
        print(f"Error: {e}")
        exit(1)
