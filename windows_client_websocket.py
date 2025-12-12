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
from typing import Dict, Any, Optional, Tuple
import websockets
import socket
import os
import base64
import io
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Configuration
DEFAULT_SERVER_URL = 'ws://34.63.226.183:8765' #gcp uri given by vinay
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
        
        # Template matching setup
        # When running as PyInstaller bundle, use _MEIPASS for bundled resources
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running as normal Python script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.templates_dir = os.path.join(base_path, "templates")
        self.templates_cache = {}  # Cache loaded templates
        

        
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
        self.log(f"Templates directory: {self.templates_dir}", "INFO")
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
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(response)),
                self.loop
            )
            # Wait for send to complete (with timeout matching brain's 10s timeout)
            future.result(timeout=10.0)
        except Exception as e:
            self.log(f"Failed to send response: {e}", "ERROR")
            return
        
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
            elif action == 'take_screenshot':
                return self._take_screenshot()
            elif action == 'click_element':
                return self._click_element(command)
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
    
    def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot of the screen."""
        import base64
        import io
        
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert to PNG bytes
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            
            # Encode to base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return {
                'type': 'response',
                'status': 'success',
                'message': 'Screenshot captured',
                'data': {
                    'screenshot': img_base64,
                    'width': screenshot.width,
                    'height': screenshot.height
                }
            }
        except Exception as e:
            return {
                'type': 'response',
                'status': 'error',
                'message': f'Failed to take screenshot: {str(e)}'
            }
    
    def _find_element_by_orb(self, template_name: str) -> Optional[Tuple[int, int]]:
        """Find element using ORB feature matching.
        
        ORB (Oriented FAST and Rotated BRIEF) is robust to:
        - Scale changes
        - Rotation
        - Low-resolution templates
        - Brightness/contrast variations
        
        Args:
            template_name: Name of template (e.g., 'chart_e200')
        
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        if not OPENCV_AVAILABLE:
            raise RuntimeError("OpenCV not installed. Run: pip install opencv-python-headless")
        
        # Load template from cache or file
        if template_name not in self.templates_cache:
            template_path = os.path.join(self.templates_dir, f"{template_name}.png")
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
            
            self.templates_cache[template_name] = template
        
        template = self.templates_cache[template_name]
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale for feature detection
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
        
        # Initialize ORB detector with increased features for better matching
        orb = cv2.ORB_create(
            nfeatures=5000,
            scaleFactor=1.2,
            nlevels=8,
            edgeThreshold=15,
            firstLevel=0,
            WTA_K=2,
            scoreType=cv2.ORB_HARRIS_SCORE,
            patchSize=31
        )
        
        # Detect keypoints and compute descriptors
        kp_template, des_template = orb.detectAndCompute(template_gray, None)
        kp_screenshot, des_screenshot = orb.detectAndCompute(screenshot_gray, None)
        
        # Check if enough keypoints were found
        if des_template is None or des_screenshot is None:
            self.log(f"ORB: Not enough features found (template={len(kp_template) if kp_template else 0}, screen={len(kp_screenshot) if kp_screenshot else 0})", "WARNING")
            return None
        
        if len(kp_template) < 10:
            self.log(f"ORB: Template has too few keypoints ({len(kp_template)}), falling back to template matching", "WARNING")
            return None
        
        # Create BFMatcher with Hamming distance
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        
        # Match descriptors using KNN (k=2 for ratio test)
        matches = bf.knnMatch(des_template, des_screenshot, k=2)
        
        # Apply Lowe's ratio test to filter good matches
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                # Ratio threshold: 0.75 is standard
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
        
        # Need at least 10 good matches for reliable detection
        MIN_MATCH_COUNT = 10
        if len(good_matches) < MIN_MATCH_COUNT:
            self.log(f"ORB: Not enough good matches ({len(good_matches)}/{MIN_MATCH_COUNT})", "WARNING")
            return None
        
        # Sort by distance and use best matches
        good_matches = sorted(good_matches, key=lambda x: x.distance)
        
        # Check if best match quality is reasonable
        if good_matches[0].distance > 50:
            self.log(f"ORB: Best match distance too high ({good_matches[0].distance})", "WARNING")
            return None
        
        # Extract location of good matches (use top 20)
        top_matches = good_matches[:min(20, len(good_matches))]
        src_pts = np.float32([kp_template[m.queryIdx].pt for m in top_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_screenshot[m.trainIdx].pt for m in top_matches]).reshape(-1, 1, 2)
        
        # Check if matches are clustered (not scattered across screen)
        screen_points = np.array([kp_screenshot[m.trainIdx].pt for m in top_matches])
        std_x = np.std(screen_points[:, 0])
        std_y = np.std(screen_points[:, 1])
        
        if std_x > 100 or std_y > 100:
            self.log(f"ORB: Matches too scattered (std_x={std_x:.1f}, std_y={std_y:.1f})", "WARNING")
            return None
        
        # Find homography matrix using RANSAC
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if M is None:
            self.log("ORB: Failed to compute homography", "WARNING")
            return None
        
        # Get template dimensions
        h, w = template_gray.shape
        
        # Transform template corners to screenshot coordinates
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        
        # Calculate center of transformed template
        center_x = int(np.mean(dst[:, 0, 0]))
        center_y = int(np.mean(dst[:, 0, 1]))
        
        # Verify the match is reasonable (within screen bounds)
        screen_h, screen_w = screenshot_gray.shape
        if not (0 <= center_x < screen_w and 0 <= center_y < screen_h):
            self.log(f"ORB: Match outside screen bounds ({center_x}, {center_y})", "WARNING")
            return None
        
        # Count inliers (matches that fit the homography)
        inliers = np.sum(mask)
        inlier_ratio = inliers / len(good_matches)
        
        # Require at least 60% inliers for reliable match
        if inlier_ratio < 0.6:
            self.log(f"ORB: Low inlier ratio ({inlier_ratio:.2%})", "WARNING")
            return None
        
        self.log(f"ORB: Found match with {len(good_matches)} matches, {inliers} inliers ({inlier_ratio:.2%})", "SUCCESS")
        return (center_x, center_y)
    
    def _find_element_by_template(self, template_name: str) -> Optional[Tuple[int, int]]:
        """Find element on screen using template matching.
        
        Robust to low-resolution templates by using upscaling and edge detection.
        This is a fallback method when ORB feature matching fails.
        
        Args:
            template_name: Name of template (e.g., 'chart_e200')
        
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        if not OPENCV_AVAILABLE:
            raise RuntimeError("OpenCV not installed. Run: pip install opencv-python-headless")
        
        # Load template from cache or file
        if template_name not in self.templates_cache:
            template_path = os.path.join(self.templates_dir, f"{template_name}.png")
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
            
            # Preprocess low-res template: upscale with quality enhancement
            # This helps when template is lower quality than screen
            if template.shape[0] < 100 or template.shape[1] < 100:
                # Upscale small templates using high-quality interpolation
                scale_factor = 2.0
                template = cv2.resize(
                    template,
                    None,
                    fx=scale_factor,
                    fy=scale_factor,
                    interpolation=cv2.INTER_CUBIC
                )
                
                # Apply bilateral filter to reduce noise while preserving edges
                # This helps with low-quality/compressed templates
                template = cv2.bilateralFilter(template, 9, 75, 75)
            
            self.templates_cache[template_name] = template
        
        template = self.templates_cache[template_name]
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        best_match = None
        best_score = 0.0
        
        # Multi-scale template matching with multiple methods for robustness
        # Wider scale range to handle upscaled templates
        for scale in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]:
            # Resize template
            scaled_template = cv2.resize(
                template,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )
            
            # Skip if template is larger than screenshot
            if (scaled_template.shape[0] > screenshot_bgr.shape[0] or 
                scaled_template.shape[1] > screenshot_bgr.shape[1]):
                continue
            
            # Method 1: Normalized correlation (good for color/brightness variations)
            result = cv2.matchTemplate(screenshot_bgr, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Update best match if this is better
            if max_val > best_score:
                best_score = max_val
                best_match = (max_loc, scaled_template.shape)
            
            # Method 2: Edge-based matching (VERY robust to quality differences)
            # Convert to grayscale
            screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(scaled_template, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding to handle varying brightness
            # This is especially good for low-res templates
            screenshot_thresh = cv2.adaptiveThreshold(
                screenshot_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            template_thresh = cv2.adaptiveThreshold(
                template_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Edge detection
            screenshot_edges = cv2.Canny(screenshot_gray, 50, 150)
            template_edges = cv2.Canny(template_gray, 50, 150)
            
            # Match using edges
            edge_result = cv2.matchTemplate(screenshot_edges, template_edges, cv2.TM_CCOEFF_NORMED)
            edge_min_val, edge_max_val, edge_min_loc, edge_max_loc = cv2.minMaxLoc(edge_result)
            
            # Match using thresholded images (good for low-res)
            thresh_result = cv2.matchTemplate(screenshot_thresh, template_thresh, cv2.TM_CCOEFF_NORMED)
            thresh_min_val, thresh_max_val, thresh_min_loc, thresh_max_loc = cv2.minMaxLoc(thresh_result)
            
            # Combine all three scores with weights optimized for low-res templates
            # 50% color, 30% edges, 20% threshold
            combined_score = (max_val * 0.5) + (edge_max_val * 0.3) + (thresh_max_val * 0.2)
            
            if combined_score > best_score:
                best_score = combined_score
                # Use the location from the best individual method
                if max_val >= edge_max_val and max_val >= thresh_max_val:
                    best_match = (max_loc, scaled_template.shape)
                elif edge_max_val >= thresh_max_val:
                    best_match = (edge_max_loc, scaled_template.shape)
                else:
                    best_match = (thresh_max_loc, scaled_template.shape)
        
        # Lower threshold for low-res templates (0.6 instead of 0.6)
        if best_score < 0.6:
            self.log(f"Template matching: Best score {best_score:.3f} below threshold", "WARNING")
            return None
        
        # Calculate center coordinates
        top_left, (h, w, _) = best_match
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        
        self.log(f"Template matching: Found match with score {best_score:.3f}", "SUCCESS")
        return (center_x, center_y)
    
    def _find_element_by_edges(self, template_name: str) -> Optional[Tuple[int, int]]:
        """Find element using edge-based matching (robust to lighting changes).
        
        This method is very robust to:
        - Brightness/contrast differences
        - Color variations
        - Slight quality differences
        
        Args:
            template_name: Name of template (e.g., 'chart_e200')
        
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        if not OPENCV_AVAILABLE:
            raise RuntimeError("OpenCV not installed. Run: pip install opencv-python-headless")
        
        # Load template from cache
        if template_name not in self.templates_cache:
            template_path = os.path.join(self.templates_dir, f"{template_name}.png")
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
            
            self.templates_cache[template_name] = template
        
        template = self.templates_cache[template_name]
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        template_edges = cv2.Canny(template_gray, 50, 150)
        screenshot_edges = cv2.Canny(screenshot_gray, 50, 150)
        
        # Dilate edges slightly to handle small shifts
        kernel = np.ones((3, 3), np.uint8)
        template_edges = cv2.dilate(template_edges, kernel, iterations=1)
        screenshot_edges = cv2.dilate(screenshot_edges, kernel, iterations=1)
        
        best_match = None
        best_score = 0.0
        
        # Try multiple scales
        for scale in [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]:
            scaled = cv2.resize(template_edges, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            
            if scaled.shape[0] > screenshot_edges.shape[0] or scaled.shape[1] > screenshot_edges.shape[1]:
                continue
            
            result = cv2.matchTemplate(screenshot_edges, scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                h, w = scaled.shape[:2]
                best_match = (max_loc[0] + w // 2, max_loc[1] + h // 2)
        
        # Lower threshold for edge matching (edges are less precise)
        if best_score < 0.45:
            self.log(f"Edge matching: Best score {best_score:.3f} below threshold", "WARNING")
            return None
        
        self.log(f"Edge matching: Found match with score {best_score:.3f}", "SUCCESS")
        return best_match
    
    def _find_all_elements_by_template(self, template_name: str, threshold: float = 0.6) -> list:
        """Find ALL instances of a template on screen.
        
        This is useful for templates that appear multiple times (e.g., arrows, buttons).
        Returns all matches sorted by position (left-to-right, then top-to-bottom).
        
        Args:
            template_name: Name of template (e.g., 'navigate_chart_arrows')
            threshold: Minimum match score (0.0-1.0)
        
        Returns:
            List of (x, y) coordinates, sorted by position
        """
        if not OPENCV_AVAILABLE:
            raise RuntimeError("OpenCV not installed. Run: pip install opencv-python-headless")
        
        # Load template
        if template_name not in self.templates_cache:
            template_path = os.path.join(self.templates_dir, f"{template_name}.png")
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
            
            self.templates_cache[template_name] = template
        
        template = self.templates_cache[template_name]
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Get template dimensions
        template_h, template_w = template.shape[:2]
        
        # Perform template matching
        result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
        
        # Find all locations above threshold
        locations = np.where(result >= threshold)
        
        # Convert to list of (x, y, score) tuples
        matches = []
        for pt in zip(*locations[::-1]):  # Switch x and y
            score = result[pt[1], pt[0]]
            center_x = pt[0] + template_w // 2
            center_y = pt[1] + template_h // 2
            matches.append((center_x, center_y, score))
        
        if not matches:
            self.log(f"Template matching (all): No matches found above threshold {threshold}", "WARNING")
            return []
        
        # Remove overlapping matches (keep highest score)
        # Two matches are considered overlapping if their centers are within template_w/2
        filtered_matches = []
        matches_sorted_by_score = sorted(matches, key=lambda x: x[2], reverse=True)
        
        for match in matches_sorted_by_score:
            x, y, score = match
            # Check if this match overlaps with any already accepted match
            is_duplicate = False
            for accepted in filtered_matches:
                ax, ay, _ = accepted
                distance = ((x - ax)**2 + (y - ay)**2)**0.5
                if distance < max(template_w, template_h) * 0.5:  # Within half template size
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_matches.append(match)
        
        # Sort by position: left-to-right, then top-to-bottom
        # Determine if layout is more horizontal or vertical
        if len(filtered_matches) > 1:
            x_coords = [m[0] for m in filtered_matches]
            y_coords = [m[1] for m in filtered_matches]
            x_range = max(x_coords) - min(x_coords)
            y_range = max(y_coords) - min(y_coords)
            
            if x_range > y_range:
                # Horizontal layout - sort by x (left to right)
                filtered_matches.sort(key=lambda m: m[0])
                self.log(f"Found {len(filtered_matches)} matches (horizontal layout, sorted left-to-right)", "SUCCESS")
            else:
                # Vertical layout - sort by y (top to bottom)
                filtered_matches.sort(key=lambda m: m[1])
                self.log(f"Found {len(filtered_matches)} matches (vertical layout, sorted top-to-bottom)", "SUCCESS")
        else:
            self.log(f"Found {len(filtered_matches)} match(es)", "SUCCESS")
        
        # Return just coordinates (without scores)
        return [(x, y) for x, y, _ in filtered_matches]
    
    def _find_element_hybrid(self, template_name: str) -> Optional[Tuple[int, int]]:
        """Find element using hybrid approach: ORB → Template → Edges.
        
        This combines three complementary methods:
        - ORB: Best for complex elements with distinctive features
        - Template matching: Good for exact pixel matches
        - Edge matching: Robust to lighting/color changes
        
        Args:
            template_name: Name of template (e.g., 'chart_e200')
        
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        # Try ORB first (most robust for complex elements)
        self.log(f"Trying ORB feature matching for '{template_name}'...", "INFO")
        coords = self._find_element_by_orb(template_name)
        
        if coords is not None:
            return coords
        
        # Fall back to template matching
        self.log(f"ORB failed, trying template matching for '{template_name}'...", "INFO")
        coords = self._find_element_by_template(template_name)
        
        if coords is not None:
            return coords
        
        # Final fallback: edge-based matching
        self.log(f"Template matching failed, trying edge matching for '{template_name}'...", "INFO")
        coords = self._find_element_by_edges(template_name)
        
        return coords
    
    def _click_element(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Click element by template name.
        
        Args:
            command: {
                'element': 'chart_e200',
                'screenshot': {'before': True, 'after': False} or bool,
                'index': 0,  # Which match to click if multiple found (0-based)
                'button': 'left'  # Mouse button: 'left', 'right', or 'middle'
            }
        """
        element = command.get('element')
        screenshot_config = command.get('screenshot', {})
        match_index = command.get('index', 0)  # Default to first match
        button = command.get('button', 'left')  # Default to left click
        offset = command.get('offset', {'x': 0, 'y': 0})  # Offset from matched position
        
        # Validate button
        if button not in ['left', 'right', 'middle']:
            return {
                'type': 'response',
                'status': 'error',
                'message': f'Invalid button: {button}. Must be "left", "right", or "middle"'
            }
        
        # Support both boolean (legacy) and object format
        if isinstance(screenshot_config, bool):
            screenshot_config = {
                'before': screenshot_config,
                'after': screenshot_config
            }
        
        try:
            # Take before screenshot if requested
            before_screenshot = None
            if screenshot_config.get('before', False):
                screenshot_result = self._take_screenshot()
                if screenshot_result['status'] == 'success':
                    before_screenshot = screenshot_result['data']['screenshot']
            
            # Strategy: Try to find all matches first if index > 0
            # This allows us to select specific instances
            coords = None
            
            if match_index > 0:
                # User wants a specific instance, so find all matches
                self.log(f"Looking for match #{match_index} of '{element}'...", "INFO")
                all_matches = self._find_all_elements_by_template(element)
                
                if all_matches and match_index < len(all_matches):
                    coords = all_matches[match_index]
                    self.log(f"Selected match #{match_index} out of {len(all_matches)} total matches", "SUCCESS")
                elif all_matches:
                    return {
                        'type': 'response',
                        'status': 'error',
                        'message': f'Index {match_index} out of range. Found {len(all_matches)} matches (indices 0-{len(all_matches)-1})',
                        'data': {
                            'before_screenshot': before_screenshot,
                            'after_screenshot': None
                        }
                    }
            
            # If index is 0 or find-all failed, use hybrid approach (single match)
            if coords is None:
                if match_index == 0:
                    self.log(f"Looking for first match of '{element}'...", "INFO")
                coords = self._find_element_hybrid(element)
            
            if coords is None:
                return {
                    'type': 'response',
                    'status': 'error',
                    'message': f'Element not found: {element}',
                    'data': {
                        'before_screenshot': before_screenshot,
                        'after_screenshot': None
                    }
                }
            
            # Apply offset to coordinates
            # Support both pixel offsets and percentage offsets
            offset_x = offset.get('x', 0)
            offset_y = offset.get('y', 0)
            
            # Check if offset is percentage-based (values between -1.0 and 1.0)
            # Percentage offsets are relative to screen dimensions
            if isinstance(offset_x, float) and -1.0 <= offset_x <= 1.0:
                screen_size = pyautogui.size()
                offset_x = int(offset_x * screen_size.width)
                self.log(f"Converting percentage offset X ({offset.get('x', 0):.2%}) to pixels ({offset_x}px)", "INFO")
            
            if isinstance(offset_y, float) and -1.0 <= offset_y <= 1.0:
                screen_size = pyautogui.size()
                offset_y = int(offset_y * screen_size.height)
                self.log(f"Converting percentage offset Y ({offset.get('y', 0):.2%}) to pixels ({offset_y}px)", "INFO")
            
            click_x = coords[0] + offset_x
            click_y = coords[1] + offset_y
            
            # Log offset if non-zero
            if offset_x != 0 or offset_y != 0:
                self.log(f"Applying offset ({offset_x}, {offset_y}) to click position", "INFO")
            
            # Click at coordinates with specified button
            pyautogui.click(click_x, click_y, button=button)
            
            # Take after screenshot if requested
            after_screenshot = None
            if screenshot_config.get('after', False):
                screenshot_result = self._take_screenshot()
                if screenshot_result['status'] == 'success':
                    after_screenshot = screenshot_result['data']['screenshot']
            
            button_text = f" ({button} click)" if button != 'left' else ""
            offset_text = f" with offset ({offset['x']}, {offset['y']})" if (offset.get('x', 0) != 0 or offset.get('y', 0) != 0) else ""
            return {
                'type': 'response',
                'status': 'success',
                'message': f'Clicked element: {element}{button_text}{offset_text}' + (f' (match #{match_index})' if match_index > 0 else ''),
                'data': {
                    'clicked_at': {'x': click_x, 'y': click_y},
                    'before_screenshot': before_screenshot,
                    'after_screenshot': after_screenshot
                }
            }
            
        except Exception as e:
            return {
                'type': 'response',
                'status': 'error',
                'message': f'Failed to click element: {str(e)}'
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
