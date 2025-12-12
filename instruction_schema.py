"""
Instruction Schema for Brain → Hands Communication

Defines the data structures for sending instructions from the brain (controller)
to the hands (Windows client).
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union


@dataclass
class ScreenshotConfig:
    """Configuration for screenshot capture."""
    before: bool = True
    after: bool = True
    
    @classmethod
    def from_value(cls, value: Union[bool, dict, None]):
        """Create ScreenshotConfig from various input types.
        
        Args:
            value: Can be:
                - bool: True = both, False = neither
                - dict: {"before": bool, "after": bool}
                - None: defaults to both True
        """
        if value is None:
            return cls(before=True, after=True)
        elif isinstance(value, bool):
            return cls(before=value, after=value)
        elif isinstance(value, dict):
            return cls(
                before=value.get('before', True),
                after=value.get('after', True)
            )
        else:
            raise ValueError(f"Invalid screenshot config: {value}")
    
    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary for JSON serialization."""
        return {
            'before': self.before,
            'after': self.after
        }


@dataclass
class Action:
    """A single action to execute on the remote client."""
    element: str  # Template name (e.g., "chart_e200")
    screenshot: ScreenshotConfig = field(default_factory=lambda: ScreenshotConfig())
    delay: float = 1.0  # Delay after action (seconds)
    
    def __init__(self, element: str, screenshot: Union[bool, dict, ScreenshotConfig, None] = None, delay: float = 1.0):
        self.element = element
        self.screenshot = screenshot if isinstance(screenshot, ScreenshotConfig) else ScreenshotConfig.from_value(screenshot)
        self.delay = delay
    
    def to_command(self) -> Dict[str, Any]:
        """Convert to command dictionary for sending to client."""
        return {
            'action': 'click_element',
            'element': self.element,
            'screenshot': self.screenshot.to_dict()
        }


@dataclass
class ActionResult:
    """Result of executing an action."""
    success: bool
    action: Action
    clicked_at: Optional[tuple] = None
    before_screenshot: Optional[str] = None  # base64 encoded
    after_screenshot: Optional[str] = None   # base64 encoded
    error: Optional[str] = None
    execution_time: float = 0.0  # seconds
    
    @classmethod
    def from_response(cls, response: Dict[str, Any], action: Action):
        """Create ActionResult from client response."""
        return cls(
            success=response.get('status') == 'success',
            action=action,
            clicked_at=tuple(response['data']['clicked_at'].values()) if 'data' in response and 'clicked_at' in response['data'] else None,
            before_screenshot=response['data'].get('before_screenshot') if 'data' in response else None,
            after_screenshot=response['data'].get('after_screenshot') if 'data' in response else None,
            error=response.get('message') if response.get('status') != 'success' else None
        )
    
    def __str__(self) -> str:
        """String representation."""
        status = "✓" if self.success else "✗"
        result = f"{status} {self.action.element}"
        if self.clicked_at:
            result += f" at {self.clicked_at}"
        if self.error:
            result += f" - Error: {self.error}"
        return result


# Example usage:
if __name__ == '__main__':
    # Create actions with different screenshot configs
    actions = [
        Action("chart_e200", screenshot=True),  # Both screenshots
        Action("chart_e100", screenshot={"before": True, "after": False}),  # Only before
        Action("chart_e70", screenshot=False),  # No screenshots
    ]
    
    # Print commands
    for action in actions:
        print(f"Action: {action.element}")
        print(f"Command: {action.to_command()}")
        print()
