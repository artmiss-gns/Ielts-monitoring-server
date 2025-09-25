"""HTTP client for fetching IELTS appointment data."""

import time
import logging
from typing import Dict, Optional

import requests
from requests.exceptions import RequestException

from src.ielts_monitor.config import Config, default_config

# Configure logging
logger = logging.getLogger(__name__)


class IELTSClient:
    """Client for fetching IELTS appointment data from the website."""

    def __init__(self, config: Config = default_config):
        """Initialize the client with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.scraper.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        })
        
    def _construct_url(self, city: str, exam_model: str, month: Optional[str] = None) -> str:
        """Construct the URL for the IELTS appointment page.
        
        Args:
            city: City name
            exam_model: Exam model (e.g., "cdielts", "pdielts")
            month: Month in YYYY-MM format (optional)
            
        Returns:
            URL for the IELTS appointment page
        """
        url = f"{self.config.scraper.base_url}/{city}/{exam_model}"
        if month:
            url = f"{url}/{month}"
        return url
    
    def fetch_page(self, city: str, exam_model: str, month: Optional[str] = None) -> Optional[str]:
        """Fetch the HTML content of the IELTS appointment page.
        
        Args:
            city: City name
            exam_model: Exam model (e.g., "cdielts", "pdielts")
            month: Month in YYYY-MM format (optional)
            
        Returns:
            HTML content of the page or None if the request failed
        """
        url = self._construct_url(city, exam_model, month)
        retries = 0
        
        while retries <= self.config.scraper.max_retries:
            try:
                logger.info(f"Fetching URL: {url}")
                response = self.session.get(
                    url, 
                    timeout=self.config.scraper.request_timeout
                )
                response.raise_for_status()
                return response.text
            except RequestException as e:
                retries += 1
                logger.warning(f"Request failed (attempt {retries}/{self.config.scraper.max_retries}): {e}")
                
                if retries <= self.config.scraper.max_retries:
                    time.sleep(self.config.scraper.retry_delay)
                else:
                    logger.error(f"Failed to fetch {url} after {self.config.scraper.max_retries} attempts")
                    return None
        
        return None
    
    def fetch_all_pages(self) -> Dict[str, Optional[str]]:
        """Fetch all configured pages.
        
        Returns:
            Dictionary mapping URLs to their HTML content
        """
        results = {}
        
        for city in self.config.monitoring.cities:
            for exam_model in self.config.monitoring.exam_models:
                if self.config.monitoring.months:
                    for month in self.config.monitoring.months:
                        url = self._construct_url(city, exam_model, month)
                        html = self.fetch_page(city, exam_model, month)
                        results[url] = html
                        # Add delay between requests
                        time.sleep(self.config.scraper.request_delay)
                else:
                    url = self._construct_url(city, exam_model)
                    html = self.fetch_page(city, exam_model)
                    results[url] = html
                    # Add delay between requests
                    time.sleep(self.config.scraper.request_delay)
        
        return results