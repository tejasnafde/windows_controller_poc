"""High-level CV-5000 device controller"""

from typing import Optional, Dict, Any
from .protocol import CV5000Protocol
from .commands import CommandBuilder
from .exceptions import CV5000Error


class CV5000Device:
    """High-level controller for CV-5000 phoropter"""
    
    def __init__(self, port: str = "COM7", debug: bool = False):
        """
        Initialize device controller
        
        Args:
            port: Serial port
            debug: Enable debug output
        """
        self.protocol = CV5000Protocol(port=port)
        self.protocol.set_debug(debug)
        self.builder = CommandBuilder()
        
        # Current state cache
        self._state = {
            'r_sph': 0.0, 'r_cyl': 0.0, 'r_axis': 0,
            'l_sph': 0.0, 'l_cyl': 0.0, 'l_axis': 0,
            'pd': 64.0,
            'chart_line': 1,
            'chart_num': 1,
            'chart_mode': 1,
            'display_mode': 0,
            'connected': False,
            'initialized': False
        }
    
    def connect(self):
        """Connect to device"""
        self.protocol.connect()
        self._state['connected'] = True
    
    def initialize(self) -> Dict[str, str]:
        """
        Initialize device (send 'r' command at startup)
        
        Returns:
            Dict with initialization response
        """
        cmd = self.builder.build_init_command()
        response = self.protocol.send_command(*cmd, expect_response=True)
        
        result = {'status': 'unknown'}
        if response:
            decoded = response.decode('ascii', errors='ignore')
            if 'er' in decoded:
                result['status'] = 'initialized'
                # Extract response code (e.g., "01")
                parts = decoded.split('\r')
                if len(parts) >= 2:
                    result['code'] = parts[1].strip()
        
        self._state['initialized'] = True
        return result
    
    def disconnect(self):
        """Disconnect from device"""
        self.protocol.disconnect()
        self._state['connected'] = False
    
    def is_connected(self) -> bool:
        """Check connection status"""
        return self._state['connected'] and self.protocol.is_connected()
    
    # === Device Information ===
    
    def get_version(self) -> Dict[str, str]:
        """Get device version information"""
        versions = {}
        
        # Get software version
        cmd = self.builder.build_version_command("PS")
        response = self.protocol.send_command(*cmd, expect_response=True)
        if response:
            decoded = response.decode('ascii', errors='ignore')
            parts = decoded.split('\r')
            if len(parts) >= 3:
                versions['software'] = parts[2].strip()
        
        # Get controller version
        cmd = self.builder.build_version_command("CV")
        response = self.protocol.send_command(*cmd, expect_response=True)
        if response:
            decoded = response.decode('ascii', errors='ignore')
            parts = decoded.split('\r')
            if len(parts) >= 3:
                versions['controller'] = parts[2].strip()
        
        return versions
    
    def get_current_values(self) -> Dict[str, str]:
        """
        Get current device values (v CV command)
        
        Returns:
            Dict with current values from device
        """
        cmd = self.builder.build_version_command("CV")
        response = self.protocol.send_command(*cmd, expect_response=True)
        
        values = {}
        if response:
            decoded = response.decode('ascii', errors='ignore')
            parts = decoded.split('\r')
            if len(parts) >= 3:
                values['raw'] = parts[2].strip()
                # Parse value string like "4.00.50LP"
                # Format appears to be: VERSION.BUILD.VARIANT
                values['full_string'] = parts[2].strip()
        
        return values
    
    def reset(self):
        """Reset device"""
        cmd = self.builder.build_reset_command()
        self.protocol.send_command(*cmd)
        # Reset state cache
        self._state.update({
            'r_sph': 0.0, 'r_cyl': 0.0, 'r_axis': 0,
            'l_sph': 0.0, 'l_cyl': 0.0, 'l_axis': 0
        })
    
    # === Prescription Control ===
    
    def set_prescription(self,
                        r_sph: Optional[float] = None,
                        r_cyl: Optional[float] = None,
                        r_axis: Optional[int] = None,
                        l_sph: Optional[float] = None,
                        l_cyl: Optional[float] = None,
                        l_axis: Optional[int] = None,
                        chart: Optional[int] = None,
                        mode: Optional[int] = None,
                        display: Optional[int] = None) -> bool:
        """
        Set prescription values (only specified parameters)
        
        Args:
            r_sph: Right sphere
            r_cyl: Right cylinder
            r_axis: Right axis
            l_sph: Left sphere
            l_cyl: Left cylinder
            l_axis: Left axis
            chart: Chart number (1-7, default from state)
            mode: Mode parameter (1-2, default from state)
            display: Display mode (0=off, 2=on, default from state)
        
        Returns:
            True if successful
        """
        # Use current state for unspecified values
        params = {
            'r_sph': r_sph if r_sph is not None else self._state['r_sph'],
            'r_cyl': r_cyl if r_cyl is not None else self._state['r_cyl'],
            'r_axis': r_axis if r_axis is not None else self._state['r_axis'],
            'l_sph': l_sph if l_sph is not None else self._state['l_sph'],
            'l_cyl': l_cyl if l_cyl is not None else self._state['l_cyl'],
            'l_axis': l_axis if l_axis is not None else self._state['l_axis'],
            'mode1': chart if chart is not None else self._state['chart_num'],
            'mode2': mode if mode is not None else self._state['chart_mode'],
            'display': display if display is not None else self._state['display_mode'],
        }
        
        cmd = self.builder.build_prescription_command(**params)
        self.protocol.send_command(*cmd)
        
        # Update state cache
        self._state['r_sph'] = params['r_sph']
        self._state['r_cyl'] = params['r_cyl']
        self._state['r_axis'] = params['r_axis']
        self._state['l_sph'] = params['l_sph']
        self._state['l_cyl'] = params['l_cyl']
        self._state['l_axis'] = params['l_axis']
        if chart is not None:
            self._state['chart_num'] = chart
        if mode is not None:
            self._state['chart_mode'] = mode
        if display is not None:
            self._state['display_mode'] = display
        
        return True
    
    def set_sphere_both(self, value: float) -> bool:
        """Set sphere for both eyes"""
        return self.set_prescription(r_sph=value, l_sph=value)
    
    def set_cylinder_both(self, value: float) -> bool:
        """Set cylinder for both eyes"""
        return self.set_prescription(r_cyl=value, l_cyl=value)
    
    def reset_to_zero(self) -> bool:
        """Reset all prescription values to zero"""
        return self.set_prescription(
            r_sph=0.0, r_cyl=0.0, r_axis=0,
            l_sph=0.0, l_cyl=0.0, l_axis=0
        )
    
    # === PD Control ===
    
    def set_pd(self, value: float) -> bool:
        """Set pupillary distance"""
        cmd = self.builder.build_pd_command(value)
        self.protocol.send_command(*cmd)
        self._state['pd'] = value
        return True
    
    # === Chart Control ===
    
    def show_echart(self) -> bool:
        """Display E-chart"""
        cmd = self.builder.build_echart_command()
        self.protocol.send_command(*cmd)
        return True
    
    def set_chart_line(self, line: int) -> bool:
        """Select chart line"""
        cmd = self.builder.build_chart_line_command(line)
        self.protocol.send_command(*cmd)
        self._state['chart_line'] = line
        return True
    
    def switch_chart(self, chart_num: int) -> bool:
        """
        Switch to a specific chart (simple command)
        
        Args:
            chart_num: Chart number (1-9)
        
        Returns:
            True if successful
        """
        cmd = self.builder.build_chart_switch_command(chart_num)
        self.protocol.send_command(*cmd)
        self._state['chart_num'] = chart_num
        return True
    
    def set_chart_pattern(self, pattern_id: int) -> bool:
        """
        Set a specific chart pattern (complex command)
        
        Args:
            pattern_id: Chart pattern ID
                1, 6, 7, 8 = Basic charts
                12, 21, 22 = Chart + mode combinations
                47, 53, 54 = Specific patterns
        
        Returns:
            True if successful
        """
        cmd = self.builder.build_chart_pattern_command(pattern_id)
        self.protocol.send_command(*cmd)
        
        # Extract chart and mode from pattern_id
        # Pattern like 12 = chart 1, mode 2
        if pattern_id >= 10:
            chart = pattern_id // 10
            mode = pattern_id % 10
            self._state['chart_num'] = chart
            self._state['chart_mode'] = mode
        else:
            self._state['chart_num'] = pattern_id
        
        return True
    
    def set_axis_mode(self, eye: str, value: int, mode: int) -> bool:
        """
        Set axis with specific mode for an eye
        
        Args:
            eye: 'R' for right or 'L' for left
            value: Axis value (0-180)
            mode: Mode parameter (1-9)
        
        Returns:
            True if successful
        """
        cmd = self.builder.build_axis_mode_command(eye, value, mode)
        self.protocol.send_command(*cmd)
        
        # Update state
        if eye.upper() == 'R':
            self._state['r_axis'] = value
        else:
            self._state['l_axis'] = value
        
        return True
    
    # === State Queries ===
    
    def get_state(self) -> Dict[str, Any]:
        """Get current device state (cached)"""
        return self._state.copy()
    
    # === Context Manager ===
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

