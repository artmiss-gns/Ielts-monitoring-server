"""Enhanced logging configuration for the IELTS appointment monitoring application."""

import logging
import sys
from typing import Optional
from pathlib import Path

try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False

try:
    import colorama
    colorama.init()  # Initialize colorama for Windows compatibility
except ImportError:
    pass


def setup_enhanced_logger(
    name: str = "ielts_monitor", 
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> "loguru_logger":
    """Set up and configure an enhanced logger using loguru.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        use_colors: Whether to use colored output
        
    Returns:
        Configured loguru logger
    """
    if not LOGURU_AVAILABLE:
        # Fallback to basic logging if loguru is not available
        return setup_basic_logger(name, getattr(logging, level.upper(), logging.INFO))
    
    # Remove default handler
    loguru_logger.remove()
    
    # Console format with colors and emojis
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Add console handler with enhanced formatting
    loguru_logger.add(
        sys.stdout,
        format=console_format,
        level=level,
        colorize=use_colors,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Make it thread-safe
    )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File format without colors
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
        
        loguru_logger.add(
            log_file,
            format=file_format,
            level=level,
            rotation="10 MB",  # Rotate when file reaches 10MB
            retention="7 days",  # Keep logs for 7 days
            compression="zip",  # Compress old logs
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )
    
    return loguru_logger


def setup_basic_logger(name: str = "ielts_monitor", level: int = logging.INFO) -> logging.Logger:
    """Fallback basic logger setup when loguru is not available.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured basic logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler if no handlers exist
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Enhanced formatter with colors (if supported)
        try:
            import colorama
            from colorama import Fore, Style
            
            class ColoredFormatter(logging.Formatter):
                """Custom formatter with colors."""
                
                COLORS = {
                    'DEBUG': Fore.CYAN,
                    'INFO': Fore.GREEN,
                    'WARNING': Fore.YELLOW,
                    'ERROR': Fore.RED,
                    'CRITICAL': Fore.MAGENTA,
                }
                
                def format(self, record):
                    color = self.COLORS.get(record.levelname, '')
                    record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
                    return super().format(record)
            
            formatter = ColoredFormatter(
                "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        except ImportError:
            # Fallback to basic formatter
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def setup_logger(name: str = "ielts_monitor", level: str = "INFO", **kwargs) -> "loguru_logger":
    """Main logger setup function with enhanced features.
    
    Args:
        name: Logger name
        level: Logging level
        **kwargs: Additional arguments for enhanced logger
        
    Returns:
        Configured logger (loguru if available, otherwise basic logging)
    """
    return setup_enhanced_logger(name, level, **kwargs)


# Create some helper functions for common logging patterns
def log_slot_info(logger, slot, slot_number: int = None):
    """Log slot information in a structured way."""
    prefix = f"Slot {slot_number}" if slot_number else "Slot"
    
    if hasattr(logger, 'info'):  # loguru logger
        logger.info(f"🎯 {prefix} Found:")
        logger.info(f"   📅 Date: {slot.date} ({slot.farsi_date})")
        logger.info(f"   🕐 Time: {slot.time_of_day}")
        logger.info(f"   📍 Location: {slot.location}")
        logger.info(f"   📝 Exam Type: {slot.exam_type}")
        logger.info(f"   💰 Price: {slot.price}")
        logger.info(f"   🔗 URL: {slot.url}")
    else:  # basic logger
        logger.info(f"🎯 {prefix} Found:")
        logger.info(f"   📅 Date: {slot.date} ({slot.farsi_date})")
        logger.info(f"   🕐 Time: {slot.time_of_day}")
        logger.info(f"   📍 Location: {slot.location}")
        logger.info(f"   📝 Exam Type: {slot.exam_type}")
        logger.info(f"   💰 Price: {slot.price}")
        logger.info(f"   🔗 URL: {slot.url}")


def log_monitoring_start(logger, config):
    """Log monitoring start information."""
    if hasattr(logger, 'info'):  # loguru logger
        logger.info("🚀 Starting IELTS appointment monitoring")
        logger.info(f"🏙️  Monitoring cities: {', '.join(config.monitoring.cities)}")
        logger.info(f"📚 Monitoring exam models: {', '.join(config.monitoring.exam_models)}")
        logger.info(f"📅 Monitoring months: {', '.join(config.monitoring.months) if config.monitoring.months else 'all available'}")
        logger.info(f"🔔 Notifications enabled: {'✅' if config.monitoring.notification.enabled else '❌'}")
        logger.info(f"⏱️  Check frequency: {config.monitoring.check_frequency} seconds")
    else:  # basic logger
        logger.info("🚀 Starting IELTS appointment monitoring")
        logger.info(f"🏙️  Monitoring cities: {', '.join(config.monitoring.cities)}")
        logger.info(f"📚 Monitoring exam models: {', '.join(config.monitoring.exam_models)}")
        logger.info(f"📅 Monitoring months: {', '.join(config.monitoring.months) if config.monitoring.months else 'all available'}")
        logger.info(f"🔔 Notifications enabled: {'✅' if config.monitoring.notification.enabled else '❌'}")
        logger.info(f"⏱️  Check frequency: {config.monitoring.check_frequency} seconds")


def log_check_results(logger, available_count: int, unavailable_count: int = 0):
    """Log the results of a slot check with enhanced formatting.
    
    Args:
        logger: Logger instance
        available_count: Number of available slots found
        unavailable_count: Number of unavailable slots found
    """
    # Create a visual separator
    logger.info("=" * 60)
    
    if available_count > 0:
        logger.info(f"🎉 SLOTS FOUND: {available_count} available appointment{'s' if available_count != 1 else ''}")
        if hasattr(logger, 'success'):
            logger.success(f"✨ {available_count} slot{'s' if available_count != 1 else ''} ready for immediate booking!")
        else:
            logger.info(f"✨ {available_count} slot{'s' if available_count != 1 else ''} ready for immediate booking!")
    else:
        logger.warning("😔 NO AVAILABLE SLOTS: All appointments are currently filled")
    
    if unavailable_count > 0:
        logger.info(f"📋 UNAVAILABLE: {unavailable_count} filled appointment{'s' if unavailable_count != 1 else ''}")
    
    logger.info("=" * 60)


def log_new_slot_detected(logger, slot_count: int = 1):
    """Log when new slots are detected.
    
    Args:
        logger: Logger instance
        slot_count: Number of new slots detected
    """
    if hasattr(logger, 'success'):
        logger.success(f"🆕 NEW SLOT ALERT: {slot_count} new appointment{'s' if slot_count != 1 else ''} just became available!")
    else:
        logger.info(f"🆕 NEW SLOT ALERT: {slot_count} new appointment{'s' if slot_count != 1 else ''} just became available!")


def log_notification_sent(logger, slot_date: str, location: str, success: bool = True):
    """Log when a notification is sent.
    
    Args:
        logger: Logger instance
        slot_date: Date of the slot
        location: Location of the slot
        success: Whether notification was successful
    """
    if success:
        if hasattr(logger, 'success'):
            logger.success(f"📤 NOTIFICATION SENT: Alert delivered for {slot_date} at {location}")
        else:
            logger.info(f"📤 NOTIFICATION SENT: Alert delivered for {slot_date} at {location}")
    else:
        logger.error(f"❌ NOTIFICATION FAILED: Could not send alert for {slot_date} at {location}")


def log_monitoring_status(logger, status: str, details: str = ""):
    """Log monitoring status updates.
    
    Args:
        logger: Logger instance
        status: Status message
        details: Additional details
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    if details:
        logger.info(f"🔄 [{timestamp}] {status} - {details}")
    else:
        logger.info(f"🔄 [{timestamp}] {status}")