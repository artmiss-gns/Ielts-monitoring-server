"""Parser for detecting available IELTS exam slots."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ExamSlot:
    """Represents an IELTS exam slot."""
    
    date: str  # English date (e.g., "27 Oct 2025")
    farsi_date: str  # Farsi date (e.g., "۱۴۰۴/۰۸/۰۵")
    time_of_day: str  # Time of day (e.g., "صبح (۰۸:۳۰ - ۱۱:۳۰)")
    location: str  # Exam location (e.g., "اصفهان (ایده نواندیش)")
    exam_type: str  # Exam type (e.g., "cdielts - (Ac/Gt)")
    price: str  # Price (e.g., "۲۹۱,۱۱۵,۰۰۰ ریال")
    is_available: bool  # Whether the slot is available
    url: str  # URL of the page where this slot was found


class AvailabilityParser:
    """Parser for detecting available IELTS exam slots."""
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    def _extract_date(self, exam_item: BeautifulSoup) -> str:
        """Extract the English date from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            English date string
        """
        # Try the simulation server format first: time > span (first span is the date)
        time_elem = exam_item.select_one("time")
        if time_elem:
            spans = time_elem.select("span")
            if spans and len(spans) >= 1:
                # First span contains the date like "2025-11-10"
                date_text = spans[0].text.strip()
                if date_text and date_text != "":
                    return date_text
        
        # Fallback to original format: time date span
        date_spans = exam_item.select("time date span")
        if len(date_spans) >= 2:
            day_month = date_spans[0].text.strip()
            year = date_spans[1].text.strip()
            return f"{day_month} {year}"
        return "Unknown date"
    
    def _extract_farsi_date(self, exam_item: BeautifulSoup) -> str:
        """Extract the Farsi date from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Farsi date string
        """
        farsi_date = exam_item.select_one(".farsi_date")
        return farsi_date.text.strip() if farsi_date else "Unknown date"
    
    def _extract_time_of_day(self, exam_item: BeautifulSoup) -> str:
        """Extract the time of day from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Time of day string
        """
        # Try simulation server format: .exam__time
        time_elem = exam_item.select_one(".exam__time")
        if time_elem:
            time_text = time_elem.text.strip()
            if time_text and time_text != "":
                return time_text
        
        # Fallback to original format
        time_elem = exam_item.select_one("div[both] em")
        return time_elem.text.strip() if time_elem else "Unknown time"
    
    def _extract_location(self, exam_item: BeautifulSoup) -> str:
        """Extract the location from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Location string
        """
        # Try simulation server format: .exam__title h5
        location = exam_item.select_one(".exam__title h5")
        if location:
            location_text = location.text.strip()
            if location_text and location_text != "":
                return location_text
        
        # Fallback to original format
        location = exam_item.select_one("h5")
        return location.text.strip() if location else "Unknown location"
    
    def _extract_exam_type(self, exam_item: BeautifulSoup) -> str:
        """Extract the exam type from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Exam type string
        """
        # Try simulation server format: .exam__type
        exam_type = exam_item.select_one(".exam__type")
        if exam_type:
            type_text = exam_type.text.strip()
            if type_text and type_text != "":
                return type_text
        
        # Fallback to original format
        exam_type = exam_item.select_one(".exam_type")
        return exam_type.text.strip() if exam_type else "Unknown type"
    
    def _extract_price(self, exam_item: BeautifulSoup) -> str:
        """Extract the price from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Price string
        """
        # Try simulation server format: .exam__price
        price = exam_item.select_one(".exam__price")
        if price:
            price_text = price.text.strip()
            if price_text and price_text != "":
                return price_text
        
        # Fallback to original format
        price = exam_item.select_one("h6")
        return price.text.strip() if price else "Unknown price"
    
    def _is_available(self, exam_item: BeautifulSoup) -> bool:
        """Check if an exam slot is available.
        
        Based on the HTML analysis, an exam slot is considered available if:
        1. The <a> element does NOT have the "disabled" class
        2. The <a> element has the "available" class (simulation server format)
        3. The button inside does NOT have the "disable" class
        4. The button does NOT contain the text "تکمیل ظرفیت" (which means "full capacity")
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            True if the slot is available, False otherwise
        """
        classes = exam_item.get("class", [])
        
        # Simulation server format: check for "available" class and absence of "disabled"
        if "available" in classes and "disabled" not in classes:
            return True
        
        # If it has "filled" or "disabled" class, it's not available
        if "filled" in classes or "disabled" in classes:
            return False
        
        # Check if the button has the "disable" class or contains "تکمیل ظرفیت" text
        button = exam_item.select_one(".btn")
        if button:
            if "disable" in button.get("class", []):
                return False
            if "تکمیل ظرفیت" in button.text:
                return False
            
        # If none of the above conditions are met, the slot is available
        return True
    
    def parse_html(self, html: str, url: str) -> List[ExamSlot]:
        """Parse HTML content and extract available exam slots.
        
        Args:
            html: HTML content of the page
            url: URL of the page
            
        Returns:
            List of ExamSlot objects
        """
        if not html:
            logger.warning(f"Empty HTML content for URL: {url}")
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        exam_items = soup.select("a.exam__item.ielts")
        
        logger.info(f"Found {len(exam_items)} exam items on page: {url}")
        
        slots = []
        for item in exam_items:
            slot = ExamSlot(
                date=self._extract_date(item),
                farsi_date=self._extract_farsi_date(item),
                time_of_day=self._extract_time_of_day(item),
                location=self._extract_location(item),
                exam_type=self._extract_exam_type(item),
                price=self._extract_price(item),
                is_available=self._is_available(item),
                url=url
            )
            slots.append(slot)
            
            if slot.is_available:
                logger.info(f"Found available slot: {slot.date} at {slot.location}")
        
        return slots
    
    def find_available_slots(self, html_dict: Dict[str, Optional[str]]) -> List[ExamSlot]:
        """Find available exam slots in multiple HTML pages.
        
        Args:
            html_dict: Dictionary mapping URLs to their HTML content
            
        Returns:
            List of available ExamSlot objects
        """
        all_available_slots = []
        
        for url, html in html_dict.items():
            if html:
                slots = self.parse_html(html, url)
                available_slots = [slot for slot in slots if slot.is_available]
                all_available_slots.extend(available_slots)
        
        return all_available_slots