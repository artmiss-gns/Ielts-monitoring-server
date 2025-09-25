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
from src.ielts_monitor.utils import setup_logger

# Set up logger
logger = setup_logger()


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
        help="Run once and exit (default: run continuously)"
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
    
    if args.verbose:
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
    
    logger.info("Starting IELTS appointment monitoring")
    logger.info(f"Monitoring cities: {config.monitoring.cities}")
    logger.info(f"Monitoring exam models: {config.monitoring.exam_models}")
    logger.info(f"Monitoring months: {config.monitoring.months or 'all available'}")
    logger.info(f"Notifications enabled: {config.monitoring.notification.enabled}")
    
    try:
        while True:
            logger.info("Checking for available slots...")
            
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
            
            if available_slots:
                logger.info(f"Found {len(available_slots)} available slots!")
                
                # Print available slots
                for i, slot in enumerate(available_slots, 1):
                    logger.info(f"Slot {i}:")
                    logger.info(f"  Date: {slot.date} ({slot.farsi_date})")
                    logger.info(f"  Time: {slot.time_of_day}")
                    logger.info(f"  Location: {slot.location}")
                    logger.info(f"  Exam Type: {slot.exam_type}")
                    logger.info(f"  Price: {slot.price}")
                    logger.info(f"  URL: {slot.url}")
                
                # Send notifications for new slots
                await notification_service.process_slots(all_slots)
            else:
                logger.info("No available slots found.")
            
            # Print unavailable slots if requested
            if config.monitoring.show_unavailable and unavailable_slots:
                logger.info(f"Found {len(unavailable_slots)} unavailable slots")
                for slot in unavailable_slots:
                    logger.info(f"  Unavailable: {slot.date} | {slot.time_of_day} | {slot.location}")
            
            if run_once:
                break
            
            # Wait for the next check
            next_check = time.time() + config.monitoring.check_frequency
            logger.info(f"Next check in {config.monitoring.check_frequency} seconds")
            time.sleep(config.monitoring.check_frequency)
    
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.exception(f"Error during monitoring: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    args = parse_args()
    config = update_config_from_args(default_config, args)
    
    # Run the async monitoring function
    asyncio.run(run_monitor(config, args.once))


if __name__ == "__main__":
    main()