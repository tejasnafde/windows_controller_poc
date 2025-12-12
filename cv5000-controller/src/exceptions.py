"""Custom exceptions for CV-5000 controller"""

class CV5000Error(Exception):
    """Base exception for CV-5000 errors"""
    pass

class ConnectionError(CV5000Error):
    """Serial connection error"""
    pass

class CommandError(CV5000Error):
    """Command execution error"""
    pass

class ValidationError(CV5000Error):
    """Parameter validation error"""
    pass

class TimeoutError(CV5000Error):
    """Operation timeout"""
    pass

