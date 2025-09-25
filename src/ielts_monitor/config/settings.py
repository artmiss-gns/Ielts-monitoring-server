"""Configuration settings for the IELTS appointment monitoring application."""

from pydantic import BaseModel, Field
from typing import List, Optional


class ScraperConfig(BaseModel):
    """Configuration for the scraper."""
    
    # Base URL for the IELTS appointment website
    base_url: str = "https://irsafam.org/ielts/timetable"
    
    # User agent to mimic a real browser
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Delay between requests in seconds
    request_delay: float = 5.0
    
    # Timeout for requests in seconds
    request_timeout: int = 30
    
    # Maximum number of retries for failed requests
    max_retries: int = 3
    
    # Retry delay in seconds
    retry_delay: float = 2.0


class MonitoringConfig(BaseModel):
    """Configuration for the monitoring application."""
    
    # Cities to check for available slots
    cities: List[str] = Field(default_factory=lambda: ["tehran", "isfahan"])
    
    # Exam models to check (e.g., "cdielts", "pdielts")
    exam_models: List[str] = Field(default_factory=lambda: ["cdielts", "pdielts"])
    
    # Months to check (format: MM - just the month number 01-12)
    months: List[str] = Field(default_factory=lambda: [])
    
    # Check frequency in seconds
    check_frequency: int = 3600  # Default: check every hour
    
    # Notification settings
    notification_enabled: bool = True


class Config(BaseModel):
    """Main configuration for the application."""
    
    scraper: ScraperConfig = Field(default_factory=ScraperConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)


# Default configuration
default_config = Config()