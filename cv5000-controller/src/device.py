"""High-level CV-5000 device controller"""

from typing import Optional, Dict, Any
from .protocol import CV5000Protocol
from .commands import CommandBuilder
from .exceptions import CV5000Error


class CV5000Device:
    """High-level controller for CV-5000 phoropter"""
    
    def __init__(self, port: str = "COM4", debug: bool = False):
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
            'connected': False
        }
    
    def connect(self):
        """Connect to device"""
        self.protocol.connect()
        self._state['connected'] = True
    
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
                        l_axis: Optional[int] = None) -> bool:
        """
        Set prescription values (only specified parameters)
        
        Args:
            r_sph: Right sphere
            r_cyl: Right cylinder
            r_axis: Right axis
            l_sph: Left sphere
            l_cyl: Left cylinder
            l_axis: Left axis
        
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
        }
        
        cmd = self.builder.build_prescription_command(**params)
        self.protocol.send_command(*cmd)
        
        # Update state cache
        self._state.update(params)
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

