"""Main entry point for the IELTS appointment monitoring application."""

import argparse
import logging
import sys
import time
from typing import List, Optional

from src.ielts_monitor.config import Config, default_config
from src.ielts_monitor.scraper import IELTSClient
from src.ielts_monitor.parser import AvailabilityParser
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
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    return config


def run_monitor(config: Config, run_once: bool = False) -> None:
    """Run the monitoring application.
    
    Args:
        config: Application configuration
        run_once: Whether to run once and exit
    """
    client = IELTSClient(config)
    parser = AvailabilityParser()
    
    logger.info("Starting IELTS appointment monitoring")
    logger.info(f"Monitoring cities: {config.monitoring.cities}")
    logger.info(f"Monitoring exam models: {config.monitoring.exam_models}")
    logger.info(f"Monitoring months: {config.monitoring.months or 'all available'}")
    
    try:
        while True:
            logger.info("Checking for available slots...")
            
            # Fetch all pages
            html_dict = client.fetch_all_pages()
            
            # Find available slots
            available_slots = parser.find_available_slots(html_dict)
            
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
            else:
                logger.info("No available slots found.")
            
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
    run_monitor(config, args.once)


if __name__ == "__main__":
    main()