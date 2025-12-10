#!/usr/bin/env python3
"""
Unit Tests for Controller Service

Tests the controller service command building and error handling.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from controller_service import ControllerService


class TestControllerService:
    """Test suite for ControllerService class."""
    
    def test_initialization(self):
        """Test controller service initialization."""
        controller = ControllerService('192.168.1.100', 5555, timeout=10)
        assert controller.host == '192.168.1.100'
        assert controller.port == 5555
        assert controller.timeout == 10
    
    def test_move_cursor_command(self):
        """Test move cursor command building."""
        controller = ControllerService('localhost', 5555)
        
        with patch.object(controller, '_send_command') as mock_send:
            mock_send.return_value = {'status': 'success'}
            
            result = controller.move_cursor(100, 200)
            
            mock_send.assert_called_once_with({
                'action': 'move_cursor',
                'x': 100,
                'y': 200
            })
            assert result['status'] == 'success'
    
    def test_click_command_with_position(self):
        """Test click command with position."""
        controller = ControllerService('localhost', 5555)
        
        with patch.object(controller, '_send_command') as mock_send:
            mock_send.return_value = {'status': 'success'}
            
            result = controller.click(300, 400, button='right')
            
            expected_command = {
                'action': 'click',
                'x': 300,
                'y': 400,
                'button': 'right'
            }
            mock_send.assert_called_once_with(expected_command)
    
    def test_click_command_without_position(self):
        """Test click command at current position."""
        controller = ControllerService('localhost', 5555)
        
        with patch.object(controller, '_send_command') as mock_send:
            mock_send.return_value = {'status': 'success'}
            
            result = controller.click(button='left')
            
            expected_command = {
                'action': 'click',
                'button': 'left'
            }
            mock_send.assert_called_once_with(expected_command)
    
    def test_move_relative_command(self):
        """Test relative move command."""
        controller = ControllerService('localhost', 5555)
        
        with patch.object(controller, '_send_command') as mock_send:
            mock_send.return_value = {'status': 'success'}
            
            result = controller.move_relative(50, -30)
            
            mock_send.assert_called_once_with({
                'action': 'move_relative',
                'x': 50,
                'y': -30
            })
    
    def test_get_position_command(self):
        """Test get position command."""
        controller = ControllerService('localhost', 5555)
        
        with patch.object(controller, '_send_command') as mock_send:
            mock_send.return_value = {
                'status': 'success',
                'data': {'x': 500, 'y': 600}
            }
            
            result = controller.get_cursor_position()
            
            mock_send.assert_called_once_with({
                'action': 'get_position'
            })
            assert result['data']['x'] == 500
            assert result['data']['y'] == 600
    
    @patch('socket.socket')
    def test_send_command_success(self, mock_socket_class):
        """Test successful command sending."""
        # Setup mock socket
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        
        # Mock response
        response_data = json.dumps({'status': 'success', 'message': 'OK'})
        mock_socket.recv.return_value = response_data.encode('utf-8')
        
        controller = ControllerService('localhost', 5555)
        command = {'action': 'move_cursor', 'x': 100, 'y': 200}
        
        result = controller._send_command(command)
        
        assert result['status'] == 'success'
        mock_socket.connect.assert_called_once_with(('localhost', 5555))
        mock_socket.send.assert_called_once()
    
    @patch('socket.socket')
    def test_connection_refused(self, mock_socket_class):
        """Test connection refused error handling."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.connect.side_effect = ConnectionRefusedError()
        
        controller = ControllerService('localhost', 5555)
        command = {'action': 'get_position'}
        
        with pytest.raises(ConnectionError) as exc_info:
            controller._send_command(command)
        
        assert 'Connection refused' in str(exc_info.value)
    
    @patch('socket.socket')
    def test_timeout_error(self, mock_socket_class):
        """Test timeout error handling."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.connect.side_effect = TimeoutError()
        
        controller = ControllerService('localhost', 5555, timeout=1)
        command = {'action': 'get_position'}
        
        with pytest.raises((TimeoutError, ConnectionError)):
            controller._send_command(command)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
