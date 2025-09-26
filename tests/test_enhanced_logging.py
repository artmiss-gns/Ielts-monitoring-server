#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced logging system.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ielts_monitor.utils.logger import setup_logger, log_monitoring_start, log_slot_info, log_check_results
from src.ielts_monitor.config import default_config
from src.ielts_monitor.parser import ExamSlot

def test_enhanced_logging():
    """Test the enhanced logging system."""
    print("🧪 Testing Enhanced Logging System")
    print("=" * 50)
    
    # Set up enhanced logger
    logger = setup_logger("test_logger", "INFO", log_file="logs/test.log")
    
    # Test startup logging
    logger.info("🚀 Testing enhanced logging system...")
    
    # Test monitoring start logging
    config = default_config
    config.monitoring.cities = ["tehran", "isfahan"]
    config.monitoring.exam_models = ["cdielts"]
    config.monitoring.months = ["10", "11"]
    
    log_monitoring_start(logger, config)
    
    # Test slot logging
    test_slot = ExamSlot(
        date="27 Oct 2025",
        farsi_date="۱۴۰۴/۰۸/۰۵",
        time_of_day="Morning (08:30 - 11:30)",
        location="Tehran (Test Center)",
        exam_type="cdielts - (Ac/Gt)",
        price="291,115,000 Rial",
        is_available=True,
        url="https://irsafam.org/ielts/timetable"
    )
    
    log_slot_info(logger, test_slot, 1)
    
    # Test check results logging
    log_check_results(logger, 2, 5)
    log_check_results(logger, 0, 3)
    
    # Test different log levels
    logger.debug("🐛 This is a debug message")
    logger.info("ℹ️  This is an info message")
    logger.warning("⚠️  This is a warning message")
    logger.error("❌ This is an error message")
    
    # Test success method if available (loguru)
    if hasattr(logger, 'success'):
        logger.success("✅ This is a success message")
    else:
        logger.info("✅ This is a success message")
    
    # Test notification-style messages
    logger.info("📤 Processing notifications...")
    logger.info("🔔 Notification sent successfully!")
    logger.info("⏰ Next check in 3600 seconds")
    logger.info("🛑 Monitoring stopped by user")
    
    print("\n" + "=" * 50)
    print("✅ Enhanced logging test completed!")
    print("📁 Check the 'logs/test.log' file for file output")
    print("🎨 Notice the colored and emoji-enhanced console output")

if __name__ == "__main__":
    test_enhanced_logging()
