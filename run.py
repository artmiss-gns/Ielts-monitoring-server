#!/usr/bin/env python3
"""
Runner script for the IELTS appointment monitoring application.
This script allows running the application without package installation.
"""

import argparse
import logging
import sys
import time
import os
import yaml
from typing import Dict, List, Optional
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ielts_monitor")

# Import required libraries
import ssl
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    logger.error("Required packages not found. Please install: requests, beautifulsoup4")
    sys.exit(1)

def read_config(config_path: str = 'config.yaml') -> dict:
    """Read configuration from YAML file."""
    if not os.path.exists(config_path):
        logging.warning(f"Config file {config_path} not found, using default settings")
        return {
            'cities': ['tehran', 'isfahan'],
            'exam_models': ['cdielts', 'pdielts'],
            'months': [10],
            'check_frequency': 3600,
            'show_unavailable': False,
            'no_ssl_verify': False
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
        # Ensure compatibility with both old and new config formats
        if 'monitoring' in config:
            # Legacy format with nested monitoring section
            monitoring_config = config.pop('monitoring')
            config.update(monitoring_config)
        
        return config

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="IELTS appointment monitoring application"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start continuous monitoring')
    monitor_parser.add_argument('--cities', nargs='+',
                               help='Cities to check for available slots (e.g., tehran isfahan)')
    monitor_parser.add_argument('--exam-models', nargs='+',
                               help='Exam models to check (e.g., cdielts pdielts)')
    monitor_parser.add_argument('--months', nargs='+', type=int,
                               help='Months to check (1-12, e.g., 10 11)')
    monitor_parser.add_argument('--check-frequency', type=int,
                               help='Check frequency in seconds')
    monitor_parser.add_argument('--verbose', action='store_true',
                               help='Enable verbose logging')
    monitor_parser.add_argument('--no-ssl-verify', action='store_true',
                               help='Disable SSL certificate verification')
    monitor_parser.add_argument('--show-unavailable', action='store_true',
                               help='Show unavailable/filled slots in the output')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for available slots once')
    scan_parser.add_argument('--cities', nargs='+',
                            help='Cities to check for available slots (e.g., tehran isfahan)')
    scan_parser.add_argument('--exam-models', nargs='+',
                            help='Exam models to check (e.g., cdielts pdielts)')
    scan_parser.add_argument('--months', nargs='+', type=int,
                            help='Months to check (1-12, e.g., 10 11)')
    scan_parser.add_argument('--verbose', action='store_true',
                            help='Enable verbose logging')
    scan_parser.add_argument('--no-ssl-verify', action='store_true',
                            help='Disable SSL certificate verification')
    scan_parser.add_argument('--show-unavailable', action='store_true',
                            help='Show unavailable/filled slots in the output')
    scan_parser.add_argument('--use-sample', action='store_true',
                            help='Use sample HTML data instead of making real requests (for testing)')
    
    # Default command if none specified
    parser.set_defaults(command='scan')
    return parser.parse_args()

class IELTSClient:
    """Client for fetching IELTS appointment data from the website."""
    
    BASE_URL = "https://irsafam.org/ielts/timetable"
    
    def __init__(self, no_ssl_verify: bool = False):
        """Initialize the client with improved SSL handling."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        })
        self.no_ssl_verify = no_ssl_verify
        
        # Configure SSL context for better handling
        if no_ssl_verify:
            # Create an SSL context that doesn't verify certificates
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            # Apply this context to the session
            self.session.verify = False
            # Disable urllib3 warnings about unverified HTTPS requests
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    
    def fetch_page(self, city: str, exam_model: str, month: Optional[str] = None) -> str:
        """Fetch a page for a specific city, exam model, and optional month."""
        # Construct URL with correct parameter formatting
        url = f"{self.BASE_URL}?city%5B%5D={city}&model%5B%5D={exam_model}"
        if month:
            url += f"&month%5B%5D={month}"
        
        logger.info(f"Fetching URL: {url}")
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                    return ""
    
    def fetch_all_pages(self, cities: List[str], exam_models: List[str], use_sample: bool = False) -> Dict[str, str]:
        """Fetch all pages for the specified cities and exam models."""
        results = {}
        
        if use_sample:
            # For testing purposes, use the sample HTML file instead of making real requests
            try:
                with open('sample-html-page.html', 'r', encoding='utf-8') as f:
                    sample_html = f.read()
                    
                for city in cities:
                    for exam_model in exam_models:
                        key = f"{city}_{exam_model}"
                        results[key] = sample_html
                        logger.info(f"Using sample HTML for {key}")
            except Exception as e:
                logger.error(f"Failed to read sample HTML file: {e}")
        else:
            # Make real requests
            for city in cities:
                for exam_model in exam_models:
                    key = f"{city}_{exam_model}"
                    html = self.fetch_page(city, exam_model)
                    
                    if html:
                        results[key] = html
                        # Be nice to the server
                        time.sleep(2)
        
        return results

def clean_persian_text(text: str) -> str:
    """Clean Persian text from logs, keeping only important information."""
    if not text:
        return text
        
    # Remove Farsi date and time indicators but keep times
    time_translations = {
        'صبح': 'AM',
        'ظهر': 'PM',
        'عصر': 'Afternoon'
    }
    
    # Normalize text by removing non-Latin and non-numeric characters
    # while preserving time format and parentheses
    cleaned_text = ''
    for char in text:
        if char.isalnum() or char in ' -:()':
            cleaned_text += char
    
    # Replace Persian time indicators
    for persian, english in time_translations.items():
        if persian in text:
            # Extract any time range in parentheses
            if '(' in text and ')' in text:
                time_range = text[text.find('('):text.rfind(')')+1]
                return f"{english} {time_range}"
            return english
    
    # Clean location by keeping only city name (first part before '(')
    if '(' in cleaned_text:
        return cleaned_text.split('(')[0].strip()
        
    return cleaned_text

class ExamSlot:
    """Represents an IELTS exam slot."""
    
    def __init__(self, date: str, farsi_date: str, time_of_day: str, 
                 location: str, exam_type: str, price: str, url: str, is_available: bool = True):
        self.date = date
        self.farsi_date = farsi_date
        self.time_of_day = clean_persian_text(time_of_day)
        self.location = clean_persian_text(location)
        self.exam_type = exam_type
        self.price = price
        self.url = url
        self.is_available = is_available

class AvailabilityParser:
    """Parser for detecting available and unavailable IELTS exam slots."""
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    def find_all_slots(self, html_dict: Dict[str, str]) -> Dict[str, List[ExamSlot]]:
        """Find all slots (both available and unavailable) in the provided HTML pages."""
        all_slots = {
            "available": [],
            "unavailable": []
        }
        
        for key, html in html_dict.items():
            city, exam_model = key.split("_")
            slots = self._parse_html(html, city, exam_model)
            
            # Separate available and unavailable slots
            for slot in slots:
                if slot.is_available:
                    all_slots["available"].append(slot)
                else:
                    all_slots["unavailable"].append(slot)
        
        return all_slots
    
    def _parse_html(self, html: str, city: str, exam_model: str) -> List[ExamSlot]:
        """Parse HTML to find all slots (both available and unavailable)."""
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        slots = []
        
        # Find all exam items (they are a tags, not div tags in the actual HTML)
        exam_items = soup.select("a.exam__item.ielts")
        
        for item in exam_items:
            # Determine if slot is available
            is_available = True
            if "disabled" in item.get("class", []):
                is_available = False
            
            # Check if "تکمیل ظرفیت" (capacity full) is present
            button = item.select_one("span.btn")
            if button and "تکمیل ظرفیت" in button.text:
                is_available = False
            
            # Extract slot details
            try:
                # Extract English date
                date_spans = item.select("time date span")
                date = ""
                if len(date_spans) >= 2:
                    date = f"{date_spans[0].text.strip()} {date_spans[1].text.strip()}"
                
                # Extract Farsi date
                farsi_date_elem = item.select_one("span.farsi_date")
                farsi_date = farsi_date_elem.text.strip() if farsi_date_elem else ""
                
                # Extract time of day
                time_elem = item.select_one("div[both] em")
                time_of_day = time_elem.text.strip() if time_elem else ""
                
                # Extract location
                location_elem = item.select_one("h5")
                location = location_elem.text.strip() if location_elem else ""
                
                # Extract exam type
                exam_type_elem = item.select_one("span.exam_type")
                exam_type = exam_type_elem.text.strip() if exam_type_elem else ""
                
                # Extract price
                price_elem = item.select_one("h6")
                price = price_elem.text.strip() if price_elem else ""
                
                # Create ExamSlot object with availability status
                slot = ExamSlot(
                    date=date,
                    farsi_date=farsi_date,
                    time_of_day=clean_persian_text(time_of_day),
                    location=clean_persian_text(location),
                    exam_type=exam_type,
                    price=price,
                    url=f"{IELTSClient.BASE_URL}?city%5B%5D={city}&model%5B%5D={exam_model}",
                    is_available=is_available
                )
                
                slots.append(slot)
            except Exception as e:
                logger.error(f"Error parsing slot: {e}")
                continue
        
        return slots

def format_month(month_num: int) -> str:
    """Format month number to YYYY-MM format required by the API."""
    current_year = datetime.now().year
    # If the month is in the past, use next year
    if month_num < datetime.now().month:
        current_year += 1
    return f"{current_year}-{month_num:02d}"

def run_monitor(cities: List[str], exam_models: List[str], months: List[str], check_frequency: int = 3600, once: bool = False, verbose: bool = False, no_ssl_verify: bool = False, use_sample: bool = False, show_unavailable: bool = False) -> None:
    """Run the monitoring application."""
    client = IELTSClient(no_ssl_verify=no_ssl_verify)
    parser = AvailabilityParser()
    
    logger.info(f"SSL verification bypassed: {no_ssl_verify}")
    logger.info(f"Show unavailable slots: {show_unavailable}")
    if not once:
        logger.info("🔍 Starting IELTS appointment monitoring")
    logger.info(f"Monitoring cities: {cities}")
    logger.info(f"Monitoring exam models: {exam_models}")
    if use_sample:
        logger.info("Using sample data: True")
    
    # Convert month numbers to YYYY-MM format
    formatted_months = []
    if months:
        for month in months:
            try:
                # Handle both integer months and strings
                month_num = int(month)
                formatted_month = format_month(month_num)
                formatted_months.append(formatted_month)
            except (ValueError, TypeError):
                # If it's already a string in YYYY-MM format, keep it
                formatted_months.append(month)
    
    logger.info(f"Monitoring months: {formatted_months or 'all available'}")
    
    try:
        while True:
            if not once:
                logger.info("\nChecking for available slots...")
            
            all_available_slots = []
            all_unavailable_slots = []
            
            for city in cities:
                for exam_model in exam_models:
                    for month in formatted_months:
                        try:
                            # Fetch page with month parameter
                            url = f"{IELTSClient.BASE_URL}?city%5B%5D={city}&model%5B%5D={exam_model}&month%5B%5D={month}"
                            logger.info(f"Fetching URL: {url}")
                            html_content = ""
                            
                            if use_sample:
                                try:
                                    with open('sample-html-page.html', 'r', encoding='utf-8') as f:
                                        html_content = f.read()
                                except Exception as e:
                                    logger.error(f"Failed to read sample HTML file: {e}")
                            else:
                                # Make real request with retry logic
                                max_retries = 3
                                retry_delay = 2
                                
                                for attempt in range(max_retries):
                                    try:
                                        response = client.session.get(url, timeout=30)
                                        response.raise_for_status()
                                        html_content = response.text
                                        break
                                    except requests.exceptions.RequestException as e:
                                        if attempt < max_retries - 1:
                                            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                                            time.sleep(retry_delay * (attempt + 1))
                                        else:
                                            logger.error(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                            
                            # Parse slots from HTML content
                            soup = BeautifulSoup(html_content, "html.parser")
                            exam_items = soup.select("a.exam__item.ielts")
                            
                            for item in exam_items:
                                # Determine if slot is available
                                is_available = True
                                if "disabled" in item.get("class", []):
                                    is_available = False
                                
                                # Check if "تکمیل ظرفیت" (capacity full) is present
                                button = item.select_one("span.btn")
                                if button and "تکمیل ظرفیت" in button.text:
                                    is_available = False
                                
                                # Extract slot details
                                try:
                                    # Extract English date
                                    date_spans = item.select("time date span")
                                    date = ""
                                    if len(date_spans) >= 2:
                                        date = f"{date_spans[0].text.strip()} {date_spans[1].text.strip()}"
                                    
                                    # Extract Farsi date
                                    farsi_date_elem = item.select_one("span.farsi_date")
                                    farsi_date = farsi_date_elem.text.strip() if farsi_date_elem else ""
                                    
                                    # Extract time of day
                                    time_elem = item.select_one("div[both] em")
                                    time_of_day = time_elem.text.strip() if time_elem else ""
                                    
                                    # Extract location
                                    location_elem = item.select_one("h5")
                                    location = location_elem.text.strip() if location_elem else ""
                                    
                                    # Extract exam type
                                    exam_type_elem = item.select_one("span.exam_type")
                                    exam_type = exam_type_elem.text.strip() if exam_type_elem else ""
                                    
                                    # Extract price
                                    price_elem = item.select_one("h6")
                                    price = price_elem.text.strip() if price_elem else ""
                                    
                                    # Create ExamSlot object
                                    slot = ExamSlot(
                                        date=date,
                                        farsi_date=farsi_date,
                                        time_of_day=time_of_day,
                                        location=location,
                                        exam_type=exam_type,
                                        price=price,
                                        url=url,
                                        is_available=is_available
                                    )
                                    
                                    if is_available:
                                        all_available_slots.append(slot)
                                    else:
                                        all_unavailable_slots.append(slot)
                                except Exception as e:
                                    logger.error(f"Error parsing slot: {e}")
                                    continue
                            
                            # Be nice to the server
                            if not use_sample:
                                time.sleep(2)
                        except Exception as e:
                            logger.error(f"Error processing {city}_{exam_model}_{month}: {str(e)}")
                            continue
            
            # Print summary first - concise output
            total_slots = len(all_available_slots) + len(all_unavailable_slots)
            if total_slots > 0:
                logger.info(f"\n📅 {total_slots} appointments found:")
                logger.info(f"  ✅ {len(all_available_slots)} Available")
                logger.info(f"  ❌ {len(all_unavailable_slots)} Unavailable")
            else:
                logger.info("\n📅 No appointments found.")
            
            # Print detailed available slots
            if all_available_slots:
                logger.info("\n--------------------------------------------------")
                logger.info("✅ Available slots:")
                logger.info("--------------------------------------------------")
                # Simple format - just show the essential information
                for slot in all_available_slots:
                    logger.info(f"  • {slot.date} | {slot.time_of_day} | {slot.location} | {slot.price}")
            else:
                logger.info("  No available slots found.")
            
            # Print detailed unavailable slots if requested
            if show_unavailable and all_unavailable_slots:
                logger.info("\n--------------------------------------------------")
                logger.info(f"❌ Unavailable slots:")
                logger.info("--------------------------------------------------")
                # Simple format for unavailable slots as well
                for slot in all_unavailable_slots:
                    logger.info(f"  • {slot.date} | {slot.time_of_day} | {slot.location}")
            
            if once:
                break
            
            # Show time in seconds if less than a minute, otherwise in minutes
            if check_frequency < 60:
                logger.info(f'\n⏳ Checking again in {check_frequency} seconds...\n')
            else:
                logger.info(f'\n⏳ Checking again in {check_frequency//60} minutes...\n')
            time.sleep(check_frequency)
    
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user")
    except Exception as e:
        logger.exception(f"Error during monitoring: {e}")
        sys.exit(1)

def main() -> None:
    """Main entry point."""
    args = parse_args()
    config = read_config()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Merge command line arguments with config file values
    cities = args.cities if hasattr(args, 'cities') and args.cities else config['cities']
    exam_models = args.exam_models if hasattr(args, 'exam_models') and args.exam_models else config['exam_models']
    months = args.months if hasattr(args, 'months') and args.months else config['months']
    
    # Determine check frequency based on command
    if args.command == 'monitor':
        check_frequency = args.check_frequency if hasattr(args, 'check_frequency') and args.check_frequency else config['monitoring']['check_frequency']
        once = False
    else:  # scan command
        check_frequency = 0
        once = True
    
    # Determine other flags
    no_ssl_verify = args.no_ssl_verify if hasattr(args, 'no_ssl_verify') else config['monitoring']['no_ssl_verify']
    show_unavailable = args.show_unavailable if hasattr(args, 'show_unavailable') else config['monitoring']['show_unavailable']
    
    # Use sample data only for scan command
    use_sample = args.use_sample if hasattr(args, 'use_sample') and args.use_sample else False
    
    run_monitor(
        cities=cities,
        exam_models=exam_models,
        months=months,
        check_frequency=check_frequency,
        once=once,
        verbose=args.verbose if hasattr(args, 'verbose') else False,
        no_ssl_verify=no_ssl_verify,
        use_sample=use_sample,
        show_unavailable=show_unavailable
    )

if __name__ == "__main__":
    main()