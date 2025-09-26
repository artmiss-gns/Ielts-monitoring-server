"""Main entry point for the IELTS appointment monitoring application."""

import argparse
import logging
import sys
import time
import asyncio
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, will use system environment variables
    pass

from src.ielts_monitor.config import Config, default_config
from src.ielts_monitor.scraper import IELTSClient
from src.ielts_monitor.parser import AvailabilityParser
from src.ielts_monitor.notification import NotificationService
from src.ielts_monitor.utils import setup_logger, log_monitoring_start, log_slot_info, log_check_results, log_new_slot_detected, log_notification_sent, log_monitoring_status

# Set up enhanced logger with file logging
logger = setup_logger("ielts_monitor", "INFO", log_file="logs/ielts_monitor.log")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="IELTS appointment monitoring application"
    )
    
    parser.add_argument(
        "--cities",
        nargs="+",
        help="Cities to check for available slots (e.g., tehran isfahan)"
    )
    
    parser.add_argument(
        "--exam-models",
        nargs="+",
        help="Exam models to check (e.g., cdielts pdielts)"
    )
    
    parser.add_argument(
        "--months",
        nargs="+",
        help="Months to check in YYYY-MM format (e.g., 2025-10 2025-11)"
    )
    
    parser.add_argument(
        "--check-frequency",
        type=int,
        help="Check frequency in seconds (default: 3600)"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single scan and exit (replaces old 'scan' command)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--no-notifications",
        action="store_true",
        help="Disable notifications"
    )
    
    parser.add_argument(
        "--clear-notifications",
        action="store_true",
        help="Clear notification state (allows re-notification of all slots)"
    )
    
    parser.add_argument(
        "--show-unavailable",
        action="store_true",
        help="Show unavailable/filled slots in output"
    )
    
    return parser.parse_args()


def update_config_from_args(config: Config, args: argparse.Namespace) -> Config:
    """Update configuration from command line arguments.
    
    Args:
        config: Default configuration
        args: Command line arguments
        
    Returns:
        Updated configuration
    """
    if args.cities:
        config.monitoring.cities = args.cities
    
    if args.exam_models:
        config.monitoring.exam_models = args.exam_models
    
    if args.months:
        config.monitoring.months = args.months
    
    if args.check_frequency:
        config.monitoring.check_frequency = args.check_frequency
    
    if args.no_notifications:
        config.monitoring.notification.enabled = False
    
    if args.show_unavailable:
        config.monitoring.show_unavailable = True
    
    if args.verbose:
        # For loguru logger, we need to reconfigure it
        if hasattr(logger, 'remove'):
            logger.remove()
            logger.add(sys.stdout, level="DEBUG", colorize=True)
            logger.add("logs/ielts_monitor.log", level="DEBUG", rotation="10 MB")
        else:
            logger.setLevel(logging.DEBUG)
    
    return config


async def run_monitor(config: Config, run_once: bool = False) -> None:
    """Run the monitoring application.
    
    Args:
        config: Application configuration
        run_once: Whether to run once and exit
    """
    client = IELTSClient(config)
    parser = AvailabilityParser()
    notification_service = NotificationService(config)
    
    # Use enhanced logging function for startup
    log_monitoring_start(logger, config)
    
    try:
        while True:
            log_monitoring_status(logger, "SCANNING", "Checking IELTS appointment availability...")
            
            # Show URLs being monitored
            urls = client.get_urls()
            logger.info("🌐 Monitoring URLs:")
            for i, url in enumerate(urls, 1):
                logger.info(f"   {i}. {url}")
            
            # Fetch all pages
            html_dict = client.fetch_all_pages()
            
            # Find available slots
            all_slots = []
            for url, html in html_dict.items():
                if html:
                    slots = parser.parse_html(html, url)
                    all_slots.extend(slots)
            
            # Separate available and unavailable slots
            available_slots = [slot for slot in all_slots if slot.is_available]
            unavailable_slots = [slot for slot in all_slots if not slot.is_available]
            
            # Check for new slots by comparing with notification service state
            new_slots = []
            for slot in available_slots:
                if notification_service.manager.should_notify(slot):
                    new_slots.append(slot)
            
            # Enhanced logging for results
            log_check_results(logger, len(available_slots), len(unavailable_slots))
            
            # Alert about new slots
            if new_slots:
                log_new_slot_detected(logger, len(new_slots))
            
            if available_slots:
                # Print available slots using enhanced logging
                for i, slot in enumerate(available_slots, 1):
                    log_slot_info(logger, slot, i)
                
                # Send notifications for new slots
                log_monitoring_status(logger, "NOTIFICATIONS", f"Processing alerts for {len(available_slots)} available slots...")
                
                # Process each slot individually to log notification results
                for slot in available_slots:
                    if notification_service.manager.should_notify(slot):
                        success = await notification_service.manager.send_notification(slot)
                        log_notification_sent(logger, slot.date, slot.location, success)
            
            # Mark unavailable slots as filled (so they can be re-notified when available again)
            if unavailable_slots:
                logger.debug("🔄 Marking filled slots for potential re-notification...")
                for slot in unavailable_slots:
                    notification_service.manager.mark_slot_filled(slot)
            
            # Print unavailable slots if requested
            if config.monitoring.show_unavailable and unavailable_slots:
                logger.info(f"📋 Showing {len(unavailable_slots)} unavailable slots:")
                for slot in unavailable_slots:
                    logger.info(f"   ❌ {slot.date} | {slot.time_of_day} | {slot.location}")
            
            if run_once:
                break
            
            # Wait for the next check
            if not run_once:
                log_monitoring_status(logger, "WAITING", f"Next scan in {config.monitoring.check_frequency} seconds")
                time.sleep(config.monitoring.check_frequency)
    
    except KeyboardInterrupt:
        log_monitoring_status(logger, "STOPPED", "Monitoring terminated by user")
        logger.info("🛑 IELTS monitoring service stopped")
    except Exception as e:
        log_monitoring_status(logger, "ERROR", f"Critical error occurred: {str(e)}")
        if hasattr(logger, 'exception'):
            logger.exception(f"💥 SYSTEM ERROR: {e}")
        else:
            logger.error(f"💥 SYSTEM ERROR: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    args = parse_args()
    config = update_config_from_args(default_config, args)
    
    # Handle clear notifications command
    if args.clear_notifications:
        import os
        try:
            if os.path.exists("notification_state.json"):
                os.remove("notification_state.json")
                logger.info("✅ Notification state cleared successfully")
            else:
                logger.info("ℹ️  No notification state file found")
        except Exception as e:
            logger.error(f"❌ Failed to clear notification state: {e}")
        return
    
    # Run the async monitoring function
    asyncio.run(run_monitor(config, args.once))


if __name__ == "__main__":
    main()