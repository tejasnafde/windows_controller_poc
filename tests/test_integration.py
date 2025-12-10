#!/usr/bin/env python3
"""
Integration Tests

Tests the full client-server communication flow.
"""

import pytest
import json
import socket
import threading
import time
from unittest.mock import patch, MagicMock
from controller_service import ControllerService


class MockWindowsClient:
    """Mock Windows client for testing."""
    
    def __init__(self, port=5556):
        self.port = port
        self.socket = None
        self.running = False
        self.thread = None
    
    def start(self):
        """Start mock server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', self.port))
        self.socket.listen(1)
        self.running = True
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        time.sleep(0.1)  # Give server time to start
    
    def _run(self):
        """Run server loop."""
        while self.running:
            try:
                self.socket.settimeout(1.0)
                client_socket, _ = self.socket.accept()
                self._handle_client(client_socket)
            except socket.timeout:
                continue
            except Exception:
                break
    
    def _handle_client(self, client_socket):
        """Handle client connection."""
        try:
            data = client_socket.recv(1024)
            command = json.loads(data.decode('utf-8'))
            
            # Mock responses based on action
            if command['action'] == 'move_cursor':
                response = {
                    'status': 'success',
                    'message': f"Moved to ({command['x']}, {command['y']})",
                    'data': {'x': command['x'], 'y': command['y']}
                }
            elif command['action'] == 'click':
                response = {
                    'status': 'success',
                    'message': 'Clicked'
                }
            elif command['action'] == 'get_position':
                response = {
                    'status': 'success',
                    'message': 'Position retrieved',
                    'data': {'x': 100, 'y': 200, 'screen_width': 1920, 'screen_height': 1080}
                }
            elif command['action'] == 'move_relative':
                response = {
                    'status': 'success',
                    'message': f"Moved by ({command['x']}, {command['y']})",
                    'data': {'x': 150, 'y': 250}
                }
            else:
                response = {
                    'status': 'error',
                    'message': f"Unknown action: {command['action']}"
                }
            
            client_socket.send(json.dumps(response).encode('utf-8'))
        finally:
            client_socket.close()
    
    def stop(self):
        """Stop mock server."""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=2)


class TestIntegration:
    """Integration tests for client-server communication."""
    
    @pytest.fixture
    def mock_server(self):
        """Fixture to start and stop mock server."""
        server = MockWindowsClient(port=5556)
        server.start()
        yield server
        server.stop()
    
    def test_move_cursor_integration(self, mock_server):
        """Test move cursor command end-to-end."""
        controller = ControllerService('localhost', 5556)
        
        response = controller.move_cursor(500, 600)
        
        assert response['status'] == 'success'
        assert response['data']['x'] == 500
        assert response['data']['y'] == 600
    
    def test_click_integration(self, mock_server):
        """Test click command end-to-end."""
        controller = ControllerService('localhost', 5556)
        
        response = controller.click(300, 400, button='left')
        
        assert response['status'] == 'success'
        assert 'Clicked' in response['message']
    
    def test_get_position_integration(self, mock_server):
        """Test get position command end-to-end."""
        controller = ControllerService('localhost', 5556)
        
        response = controller.get_cursor_position()
        
        assert response['status'] == 'success'
        assert 'x' in response['data']
        assert 'y' in response['data']
        assert 'screen_width' in response['data']
        assert 'screen_height' in response['data']
    
    def test_move_relative_integration(self, mock_server):
        """Test relative move command end-to-end."""
        controller = ControllerService('localhost', 5556)
        
        response = controller.move_relative(50, -30)
        
        assert response['status'] == 'success'
        assert 'data' in response
    
    def test_connection_error_no_server(self):
        """Test connection error when server is not running."""
        controller = ControllerService('localhost', 9999, timeout=1)
        
        with pytest.raises(ConnectionError):
            controller.move_cursor(100, 200)
    
    def test_multiple_commands(self, mock_server):
        """Test sending multiple commands in sequence."""
        controller = ControllerService('localhost', 5556)
        
        # Send multiple commands
        r1 = controller.get_cursor_position()
        r2 = controller.move_cursor(100, 100)
        r3 = controller.click()
        r4 = controller.move_relative(50, 50)
        
        assert r1['status'] == 'success'
        assert r2['status'] == 'success'
        assert r3['status'] == 'success'
        assert r4['status'] == 'success'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
