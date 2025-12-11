#!/usr/bin/env python3
"""
Windows Client with WebSocket - Remote Control Agent

This client connects TO a relay server instead of listening for connections.
Works across any network, even behind NAT/firewall.
"""

import asyncio
import json
import sys
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import pyautogui
from typing import Dict, Any
import websockets
import socket

# Configuration
DEFAULT_SERVER_URL = 'ws://localhost:8765'
DEFAULT_CLIENT_ID = socket.gethostname()  # Use computer name as default ID

# PyAutoGUI safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class WindowsClientWebSocket:
    """Windows automation client that connects to relay server."""
    
    def __init__(self, server_url: str = DEFAULT_SERVER_URL, client_id: str = None):
        self.server_url = server_url
        self.client_id = client_id or DEFAULT_CLIENT_ID
        self.websocket = None
        self.running = False
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title(f"MyOptum Activity Monitor - {self.client_id}")
        self.root.geometry("700x550")
        self.root.configure(bg='#2b2b2b')
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2b2b2b')
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="● Disconnected",
            font=('Consolas', 12, 'bold'),
            fg='#ff4444',
            bg='#2b2b2b'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Info label
        screen_size = pyautogui.size()
        info_text = f"ID: {self.client_id} | Screen: {screen_size.width}x{screen_size.height}"
        self.info_label = tk.Label(
            status_frame,
            text=info_text,
            font=('Consolas', 10),
            fg='#888888',
            bg='#2b2b2b'
        )
        self.info_label.pack(side=tk.RIGHT)
        
        # Server URL frame
        url_frame = tk.Frame(self.root, bg='#2b2b2b')
        url_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            url_frame,
            text="Server URL:",
            font=('Consolas', 10),
            fg='#ffffff',
            bg='#2b2b2b'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.url_entry = tk.Entry(
            url_frame,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#00ff00',
            insertbackground='#00ff00'
        )
        self.url_entry.insert(0, server_url)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
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
        
        self.connect_button = tk.Button(
            button_frame,
            text="▶ Connect to Server",
            command=self.start_connection,
            font=('Consolas', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_button = tk.Button(
            button_frame,
            text="■ Disconnect",
            command=self.stop_connection,
            font=('Consolas', 10, 'bold'),
            bg='#f44336',
            fg='white',
            activebackground='#da190b',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state='disabled'
        )
        self.disconnect_button.pack(side=tk.LEFT, padx=5)
        
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
        self.log("MyOptum Activity Monitor initialized", "INFO")
        self.log(f"Client ID: {self.client_id}", "INFO")
        self.log(f"Ready to connect to: {server_url}", "INFO")
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log message to the GUI."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
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
    
    def start_connection(self):
        """Start connection to server."""
        if self.running:
            return
        
        self.server_url = self.url_entry.get()
        self.running = True
        self.connect_button.configure(state='disabled')
        self.disconnect_button.configure(state='normal')
        self.url_entry.configure(state='disabled')
        
        # Start async connection in background
        asyncio.run_coroutine_threadsafe(
            self._connect_to_server(),
            self.loop
        )
    
    def stop_connection(self):
        """Stop connection to server."""
        if not self.running:
            return
        
        self.running = False
        self.connect_button.configure(state='normal')
        self.disconnect_button.configure(state='disabled')
        self.url_entry.configure(state='normal')
        self.status_label.configure(text="● Disconnected", fg='#ff4444')
        
        self.log("Disconnecting from server...", "WARNING")
    
    async def _connect_to_server(self):
        """Connect to relay server and handle messages."""
        try:
            self.log(f"Connecting to {self.server_url}...", "INFO")
            
            async with websockets.connect(self.server_url) as websocket:
                self.websocket = websocket
                
                # Register as client
                await websocket.send(json.dumps({
                    'type': 'register_client',
                    'client_id': self.client_id
                }))
                
                # Wait for registration confirmation
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data.get('type') == 'registered':
                    self.root.after(0, lambda: self.status_label.configure(
                        text="● Connected", fg='#44ff44'
                    ))
                    self.root.after(0, lambda: self.log(
                        f"Connected to server as {self.client_id}", "SUCCESS"
                    ))
                    self.root.after(0, lambda: self.log(
                        "Waiting for commands...", "INFO"
                    ))
                    
                    # Listen for commands
                    while self.running:
                        try:
                            message_str = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=1.0
                            )
                            message = json.loads(message_str)
                            
                            # Handle command
                            self.root.after(0, lambda m=message: self._handle_command(m))
                            
                        except asyncio.TimeoutError:
                            continue
                        except websockets.exceptions.ConnectionClosed:
                            break
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Connection error: {e}", "ERROR"))
            self.root.after(0, lambda: self.status_label.configure(
                text="● Connection Failed", fg='#ff4444'
            ))
        finally:
            self.running = False
            self.root.after(0, lambda: self.connect_button.configure(state='normal'))
            self.root.after(0, lambda: self.disconnect_button.configure(state='disabled'))
            self.root.after(0, lambda: self.url_entry.configure(state='normal'))
    
    def _handle_command(self, message: dict):
        """Handle command from server."""
        action = message.get('action')
        self.log(f"Received command: {action}", "COMMAND")
        
        response = self._execute_command(message)
        
        # Send response back to server
        asyncio.run_coroutine_threadsafe(
            self.websocket.send(json.dumps(response)),
            self.loop
        )
        
        if response['status'] == 'success':
            self.log(f"✓ {response['message']}", "SUCCESS")
        else:
            self.log(f"✗ {response['message']}", "ERROR")
    
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
                    'type': 'response',
                    'status': 'error',
                    'message': f'Unknown action: {action}'
                }
        except Exception as e:
            return {
                'type': 'response',
                'status': 'error',
                'message': str(e)
            }
    
    def _move_cursor(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Move cursor to absolute position."""
        x = command.get('x')
        y = command.get('y')
        
        if x is None or y is None:
            return {'type': 'response', 'status': 'error', 'message': 'Missing x or y coordinates'}
        
        pyautogui.moveTo(x, y)
        current_pos = pyautogui.position()
        return {
            'type': 'response',
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
            return {'type': 'response', 'status': 'error', 'message': f'Invalid button: {button}'}
        
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
            message = f'Clicked {button} button at ({x}, {y})'
        else:
            pyautogui.click(button=button)
            pos = pyautogui.position()
            message = f'Clicked {button} button at current position ({pos.x}, {pos.y})'
        
        return {'type': 'response', 'status': 'success', 'message': message}
    
    def _move_relative(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Move cursor relative to current position."""
        x = command.get('x', 0)
        y = command.get('y', 0)
        
        pyautogui.moveRel(x, y)
        current_pos = pyautogui.position()
        return {
            'type': 'response',
            'status': 'success',
            'message': f'Moved cursor by ({x}, {y})',
            'data': {'x': current_pos.x, 'y': current_pos.y}
        }
    
    def _get_position(self) -> Dict[str, Any]:
        """Get current cursor position."""
        pos = pyautogui.position()
        screen_size = pyautogui.size()
        return {
            'type': 'response',
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
            self.stop_connection()
        self.root.quit()
    
    def run(self):
        """Start the GUI and async event loop."""
        # Create async event loop in background thread
        import threading
        
        def run_async_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        thread = threading.Thread(target=run_async_loop, daemon=True)
        thread.start()
        
        # Give loop time to start
        import time
        time.sleep(0.1)
        
        # Start GUI main loop
        self.root.mainloop()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows Remote Control Client (WebSocket)')
    parser.add_argument('--server', default=DEFAULT_SERVER_URL, help='WebSocket server URL')
    parser.add_argument('--client-id', default=None, help='Client ID (default: hostname)')
    
    args = parser.parse_args()
    
    client = WindowsClientWebSocket(server_url=args.server, client_id=args.client_id)
    client.run()


if __name__ == '__main__':
    main()
