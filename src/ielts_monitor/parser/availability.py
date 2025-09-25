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
        time_elem = exam_item.select_one("div[both] em")
        return time_elem.text.strip() if time_elem else "Unknown time"
    
    def _extract_location(self, exam_item: BeautifulSoup) -> str:
        """Extract the location from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Location string
        """
        location = exam_item.select_one("h5")
        return location.text.strip() if location else "Unknown location"
    
    def _extract_exam_type(self, exam_item: BeautifulSoup) -> str:
        """Extract the exam type from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Exam type string
        """
        exam_type = exam_item.select_one(".exam_type")
        return exam_type.text.strip() if exam_type else "Unknown type"
    
    def _extract_price(self, exam_item: BeautifulSoup) -> str:
        """Extract the price from an exam item.
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            Price string
        """
        price = exam_item.select_one("h6")
        return price.text.strip() if price else "Unknown price"
    
    def _is_available(self, exam_item: BeautifulSoup) -> bool:
        """Check if an exam slot is available.
        
        Based on the HTML analysis, an exam slot is considered available if:
        1. The <a> element does NOT have the "disabled" class
        2. The button inside does NOT have the "disable" class
        3. The button does NOT contain the text "تکمیل ظرفیت" (which means "full capacity")
        
        Args:
            exam_item: BeautifulSoup object representing an exam item
            
        Returns:
            True if the slot is available, False otherwise
        """
        # Check if the exam item has the "disabled" class
        if "disabled" in exam_item.get("class", []):
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