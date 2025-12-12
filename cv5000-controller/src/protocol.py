"""Low-level CV-5000 serial protocol implementation"""

import serial
import time
from typing import Optional, List
from .exceptions import ConnectionError, CommandError, TimeoutError


class CV5000Protocol:
    """Low-level ASCII protocol handler for CV-5000"""
    
    # Protocol constants
    SOH = b'\x01'  # Start of Header
    CR = b'\x0d'   # Carriage Return (delimiter)
    EOT = b'\x04'  # End of Transmission
    
    def __init__(self, port: str = "COM4", baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialize serial connection
        
        Args:
            port: Serial port (e.g., COM4, /dev/ttyUSB0)
            baudrate: Communication speed (default 9600)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self._debug = False
    
    def connect(self):
        """Establish serial connection"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            time.sleep(0.2)  # Let port stabilize
            
            if self._debug:
                print(f"✅ Connected to {self.port} at {self.baudrate} baud")
            
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            if self._debug:
                print(f"✅ Disconnected from {self.port}")
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.ser is not None and self.ser.is_open
    
    def build_packet(self, *parts) -> bytes:
        """
        Build a protocol packet from parts
        
        Args:
            *parts: Command parts (will be converted to ASCII and delimited)
        
        Returns:
            Complete packet bytes
        """
        packet = self.SOH
        for part in parts:
            packet += str(part).encode('ascii') + self.CR
        packet += self.EOT
        return packet
    
    def send_packet(self, packet: bytes, expect_response: bool = False) -> Optional[bytes]:
        """
        Send a packet and optionally wait for response
        
        Args:
            packet: Raw packet bytes
            expect_response: Whether to wait for and return response
        
        Returns:
            Response bytes if expect_response=True, else None
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
        
        try:
            # Send packet
            self.ser.write(packet)
            self.ser.flush()
            
            if self._debug:
                print(f"TX: {packet.hex(' ').upper()}")
                print(f"    {self._format_ascii(packet)}")
            
            # Wait for device to process
            time.sleep(0.05)
            
            # Read response if expected
            if expect_response:
                response = self.ser.read(256)  # Read up to 256 bytes
                
                if self._debug and response:
                    print(f"RX: {response.hex(' ').upper()}")
                    print(f"    {self._format_ascii(response)}")
                
                return response if response else None
            
            return None
            
        except serial.SerialException as e:
            raise CommandError(f"Communication error: {e}")
    
    def send_command(self, *parts, expect_response: bool = False) -> Optional[bytes]:
        """
        Build and send a command
        
        Args:
            *parts: Command parts
            expect_response: Whether to wait for response
        
        Returns:
            Response bytes if expect_response=True
        """
        packet = self.build_packet(*parts)
        return self.send_packet(packet, expect_response)
    
    def _format_ascii(self, data: bytes) -> str:
        """Format bytes as readable ASCII with special chars shown"""
        result = []
        for b in data:
            if b == 0x01:
                result.append('<SOH>')
            elif b == 0x0d:
                result.append('<CR>')
            elif b == 0x04:
                result.append('<EOT>')
            elif 32 <= b <= 126:
                result.append(chr(b))
            else:
                result.append(f'<{b:02X}>')
        return ''.join(result)
    
    def set_debug(self, enabled: bool):
        """Enable/disable debug output"""
        self._debug = enabled
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

