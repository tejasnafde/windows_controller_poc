"""Command builders and validators for CV-5000"""

from typing import Tuple
from .exceptions import ValidationError


class CommandBuilder:
    """Build and validate CV-5000 commands"""
    
    @staticmethod
    def validate_sphere(value: float) -> float:
        """Validate sphere value"""
        if not -20.0 <= value <= 20.0:
            raise ValidationError(f"Sphere {value} out of range (-20.00 to +20.00)")
        if round(value / 0.25) * 0.25 != value:
            raise ValidationError(f"Sphere {value} must be in 0.25 steps")
        return value
    
    @staticmethod
    def validate_cylinder(value: float) -> float:
        """Validate cylinder value"""
        if not -6.0 <= value <= 0.0:
            raise ValidationError(f"Cylinder {value} out of range (-6.00 to 0.00)")
        if round(value / 0.25) * 0.25 != value:
            raise ValidationError(f"Cylinder {value} must be in 0.25 steps")
        return value
    
    @staticmethod
    def validate_axis(value: int) -> int:
        """Validate axis value"""
        if not 0 <= value <= 180:
            raise ValidationError(f"Axis {value} out of range (0 to 180)")
        return value
    
    @staticmethod
    def validate_pd(value: float) -> float:
        """Validate PD value"""
        if not 50.0 <= value <= 80.0:
            raise ValidationError(f"PD {value} out of range (50.0 to 80.0)")
        return value
    
    @staticmethod
    def format_sphere_cyl(value: float) -> str:
        """Format sphere/cylinder value (6 chars with sign and spaces)"""
        if value >= 0:
            return f"  {value:.2f}"
        else:
            return f"- {abs(value):.2f}"
    
    @staticmethod
    def format_axis(value: int) -> str:
        """Format axis value (4 chars, space-padded)"""
        return f"{value:4d}"
    
    @staticmethod
    def build_prescription_command(
        r_sph: float = 0.0, r_cyl: float = 0.0, r_axis: int = 0,
        l_sph: float = 0.0, l_cyl: float = 0.0, l_axis: int = 0,
        mode1: int = 1, mode2: int = 1, display: int = 0
    ) -> Tuple:
        """
        Build prescription (B command) parameters
        
        Returns:
            Tuple of command parts ready to send
        """
        # Validate all values
        r_sph = CommandBuilder.validate_sphere(r_sph)
        r_cyl = CommandBuilder.validate_cylinder(r_cyl)
        r_axis = CommandBuilder.validate_axis(r_axis)
        l_sph = CommandBuilder.validate_sphere(l_sph)
        l_cyl = CommandBuilder.validate_cylinder(l_cyl)
        l_axis = CommandBuilder.validate_axis(l_axis)
        
        # Format values
        r_sph_str = CommandBuilder.format_sphere_cyl(r_sph)
        r_cyl_str = CommandBuilder.format_sphere_cyl(r_cyl)
        r_axis_str = CommandBuilder.format_axis(r_axis)
        l_sph_str = CommandBuilder.format_sphere_cyl(l_sph)
        l_cyl_str = CommandBuilder.format_sphere_cyl(l_cyl)
        l_axis_str = CommandBuilder.format_axis(l_axis)
        
        # Build command tuple
        return (
            "B",                    # Command
            "R", r_sph_str,        # Right eye
            r_cyl_str,
            r_axis_str,
            "L", l_sph_str,        # Left eye
            l_cyl_str,
            l_axis_str,
            f"{mode1:02d}",        # Modes
            f"{mode2:02d}",
            str(display)
        )
    
    @staticmethod
    def build_pd_command(pd_value: float) -> Tuple:
        """Build PD command parameters"""
        pd_value = CommandBuilder.validate_pd(pd_value)
        return ("D", f"{pd_value:.1f}")
    
    @staticmethod
    def build_chart_line_command(line: int) -> Tuple:
        """Build chart line selection command"""
        if not 1 <= line <= 20:
            raise ValidationError(f"Chart line {line} out of range (1-20)")
        return ("ln", str(line))
    
    @staticmethod
    def build_echart_command() -> Tuple:
        """Build E-chart display command"""
        return ("c", "E")
    
    @staticmethod
    def build_reset_command() -> Tuple:
        """Build reset command"""
        return ("r",)
    
    @staticmethod
    def build_version_command(query_type: str = "PS") -> Tuple:
        """Build version query command"""
        if query_type not in ["PS", "CV"]:
            raise ValidationError(f"Invalid version query type: {query_type}")
        return ("v", query_type)
    
    @staticmethod
    def build_chart_switch_command(chart_num: int) -> Tuple:
        """Build simple chart switch command (c 1, c 2, etc.)"""
        if not 1 <= chart_num <= 9:
            raise ValidationError(f"Chart number {chart_num} out of range (1-9)")
        return ("c", str(chart_num))
    
    @staticmethod
    def build_chart_pattern_command(pattern_id: int) -> Tuple:
        """Build complex chart pattern command (CE 12, CE 47, etc.)"""
        if not 1 <= pattern_id <= 99:
            raise ValidationError(f"Chart pattern {pattern_id} out of range (1-99)")
        return ("CE", str(pattern_id), "00")
    
    @staticmethod
    def build_axis_mode_command(eye: str, value: int, mode: int) -> Tuple:
        """Build axis mode command (c R A 25 2 or c L A 25 1)"""
        if eye.upper() not in ['R', 'L']:
            raise ValidationError(f"Eye must be 'R' or 'L', got {eye}")
        if not 0 <= value <= 180:
            raise ValidationError(f"Axis value {value} out of range (0-180)")
        if not 1 <= mode <= 9:
            raise ValidationError(f"Mode {mode} out of range (1-9)")
        return ("c", eye.upper(), "A", str(value), str(mode))
    
    @staticmethod
    def build_init_command() -> Tuple:
        """Build initialization command (sent at startup)"""
        return ("r",)

