"""Logging configuration for the IELTS appointment monitoring application."""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "ielts_monitor", level: int = logging.INFO) -> logging.Logger:
    """Set up and configure a logger.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler if no handlers exist
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    return logger