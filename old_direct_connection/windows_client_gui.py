#!/usr/bin/env python3
"""
Windows Client with GUI - Remote Control Agent

This script runs on a Windows PC with a simple GUI showing logs and status.
"""

import socket
import json
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import pyautogui
from typing import Dict, Any

# Configuration
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5555
BUFFER_SIZE = 1024

# PyAutoGUI safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class WindowsClientGUI:
    """Windows automation client with GUI for logs."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.server_thread = None
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Windows Remote Control Client")
        self.root.geometry("700x500")
        self.root.configure(bg='#2b2b2b')
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2b2b2b')
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="● Stopped",
            font=('Consolas', 12, 'bold'),
            fg='#ff4444',
            bg='#2b2b2b'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Info label
        screen_size = pyautogui.size()
        info_text = f"Screen: {screen_size.width}x{screen_size.height} | Port: {port}"
        self.info_label = tk.Label(
            status_frame,
            text=info_text,
            font=('Consolas', 10),
            fg='#888888',
            bg='#2b2b2b'
        )
        self.info_label.pack(side=tk.RIGHT)
        
        # Log area
        log_frame = tk.Frame(self.root, bg='#2b2b2b')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        tk.Label(
            log_frame,
            text="Activity Log:",
            font=('Consolas', 10, 'bold'),
            fg='#ffffff',
            bg='#2b2b2b',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#00ff00',
            insertbackground='#00ff00',
            state='disabled',
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ Start Server",
            command=self.start_server,
            font=('Consolas', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="■ Stop Server",
            command=self.stop_server,
            font=('Consolas', 10, 'bold'),
            bg='#f44336',
            fg='white',
            activebackground='#da190b',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state='disabled'
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="Clear Logs",
            command=self.clear_logs,
            font=('Consolas', 10),
            bg='#555555',
            fg='white',
            activebackground='#666666',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial log
        self.log("Windows Remote Control Client initialized", "INFO")
        self.log(f"Ready to listen on {host}:{port}", "INFO")
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log message to the GUI."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "INFO": "#00ff00",
            "SUCCESS": "#00ffff",
            "WARNING": "#ffaa00",
            "ERROR": "#ff4444",
            "COMMAND": "#ff00ff"
        }
        color = colors.get(level, "#00ff00")
        
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"[{level}] ", level)
        self.log_text.insert(tk.END, f"{message}\n")
        
        # Apply colors
        self.log_text.tag_config("timestamp", foreground="#888888")
        self.log_text.tag_config(level, foreground=color)
        
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)
    
    def clear_logs(self):
        """Clear the log area."""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        self.log("Logs cleared", "INFO")
    
    def start_server(self):
        """Start the server in a background thread."""
        if self.running:
            return
        
        self.running = True
        self.start_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        self.status_label.configure(text="● Running", fg='#44ff44')
        
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        self.log(f"Server started on {self.host}:{self.port}", "SUCCESS")
    
    def stop_server(self):
        """Stop the server."""
        if not self.running:
            return
        
        self.running = False
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        self.status_label.configure(text="● Stopped", fg='#ff4444')
        
        if self.socket:
            self.socket.close()
        
        self.log("Server stopped", "WARNING")
    
    def _run_server(self):
        """Run the server loop."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            
            self.log("Waiting for connections...", "INFO")
            
            while self.running:
                try:
                    self.socket.settimeout(1.0)
                    client_socket, address = self.socket.accept()
                    self.log(f"Connection from {address[0]}:{address[1]}", "SUCCESS")
                    self._handle_client(client_socket, address)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"Error accepting connection: {e}", "ERROR")
                    break
                    
        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            self.root.after(0, self.stop_server)
    
    def _handle_client(self, client_socket: socket.socket, address):
        """Handle commands from a connected client."""
        try:
            while self.running:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                    
                try:
                    command = json.loads(data.decode('utf-8'))
                    action = command.get('action', 'unknown')
                    self.log(f"Command from {address[0]}: {action}", "COMMAND")
                    
                    response = self._execute_command(command)
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                    if response['status'] == 'success':
                        self.log(f"✓ {response['message']}", "SUCCESS")
                    else:
                        self.log(f"✗ {response['message']}", "ERROR")
                    
                except json.JSONDecodeError as e:
                    error_response = {
                        'status': 'error',
                        'message': f'Invalid JSON: {str(e)}'
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                    self.log(f"JSON decode error: {e}", "ERROR")
                    
        except Exception as e:
            self.log(f"Error handling client: {e}", "ERROR")
        finally:
            client_socket.close()
            self.log(f"Client {address[0]} disconnected", "INFO")
    
    def _execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command and return the result."""
        action = command.get('action')
        
        try:
            if action == 'move_cursor':
                return self._move_cursor(command)
            elif action == 'click':
                return self._click(command)
            elif action == 'move_relative':
                return self._move_relative(command)
            elif action == 'get_position':
                return self._get_position()
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown action: {action}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _move_cursor(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Move cursor to absolute position."""
        x = command.get('x')
        y = command.get('y')
        
        if x is None or y is None:
            return {'status': 'error', 'message': 'Missing x or y coordinates'}
        
        pyautogui.moveTo(x, y)
        current_pos = pyautogui.position()
        return {
            'status': 'success',
            'message': f'Moved cursor to ({x}, {y})',
            'data': {'x': current_pos.x, 'y': current_pos.y}
        }
    
    def _click(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Click at specified position."""
        x = command.get('x')
        y = command.get('y')
        button = command.get('button', 'left')
        
        if button not in ['left', 'right', 'middle']:
            return {'status': 'error', 'message': f'Invalid button: {button}'}
        
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
            message = f'Clicked {button} button at ({x}, {y})'
        else:
            pyautogui.click(button=button)
            pos = pyautogui.position()
            message = f'Clicked {button} button at current position ({pos.x}, {pos.y})'
        
        return {'status': 'success', 'message': message}
    
    def _move_relative(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Move cursor relative to current position."""
        x = command.get('x', 0)
        y = command.get('y', 0)
        
        pyautogui.moveRel(x, y)
        current_pos = pyautogui.position()
        return {
            'status': 'success',
            'message': f'Moved cursor by ({x}, {y})',
            'data': {'x': current_pos.x, 'y': current_pos.y}
        }
    
    def _get_position(self) -> Dict[str, Any]:
        """Get current cursor position."""
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
    
    def on_closing(self):
        """Handle window close event."""
        if self.running:
            self.stop_server()
        self.root.destroy()
    
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows Remote Control Client (GUI)')
    parser.add_argument('--host', default=DEFAULT_HOST, help='Host to bind to')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port to listen on')
    parser.add_argument('--autostart', action='store_true', help='Start server automatically')
    
    args = parser.parse_args()
    
    client = WindowsClientGUI(host=args.host, port=args.port)
    
    if args.autostart:
        client.start_server()
    
    client.run()


if __name__ == '__main__':
    main()
