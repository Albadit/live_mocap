"""
Logging utilities for the addon.
"""

import logging
import sys


class AddonLogger:
    """Custom logger for the addon."""
    
    def __init__(self, name="LiveMocap", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)
            
            # Format: [LiveMocap] INFO: message
            formatter = logging.Formatter('[%(name)s] %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
    
    def debug(self, msg):
        """Log debug message."""
        self.logger.debug(msg)
    
    def info(self, msg):
        """Log info message."""
        self.logger.info(msg)
    
    def warning(self, msg):
        """Log warning message."""
        self.logger.warning(msg)
    
    def error(self, msg):
        """Log error message."""
        self.logger.error(msg)
    
    def critical(self, msg):
        """Log critical message."""
        self.logger.critical(msg)


# Global logger instance
_logger = None


def get_logger():
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = AddonLogger()
    return _logger


def set_debug_mode(enabled):
    """Enable or disable debug logging."""
    logger = get_logger()
    level = logging.DEBUG if enabled else logging.INFO
    logger.logger.setLevel(level)
    for handler in logger.logger.handlers:
        handler.setLevel(level)
