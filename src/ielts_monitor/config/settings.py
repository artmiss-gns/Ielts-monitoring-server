"""Configuration settings for the IELTS appointment monitoring application."""

import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


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


class NotificationConfig(BaseModel):
    """Configuration for notifications."""
    
    # Enable notifications
    enabled: bool = True
    
    # Telegram bot token (from environment variable)
    bot_token: Optional[str] = None
    
    # Telegram chat ID (from environment variable)
    chat_id: Optional[str] = None
    
    # Notification message format
    message_format: str = "markdown"
    
    # Rate limiting: minimum seconds between notifications
    rate_limit_seconds: int = 60
    
    # Maximum notifications per hour
    max_notifications_per_hour: int = 50


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
    
    # Show unavailable/filled slots in output
    show_unavailable: bool = False
    
    # Notification settings
    notification: NotificationConfig = Field(default_factory=NotificationConfig)


class Config(BaseModel):
    """Main configuration for the application."""
    
    scraper: ScraperConfig = Field(default_factory=ScraperConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)


def load_config_from_yaml(config_path: str = "config.yaml") -> Config:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Config object with values from YAML file
    """
    config_file = Path(config_path)
    
    # Start with default config
    config = Config()
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data:
                # Update scraper config
                if 'base_url' in yaml_data:
                    config.scraper.base_url = yaml_data['base_url']
                
                # Update monitoring config
                if 'cities' in yaml_data:
                    config.monitoring.cities = yaml_data['cities']
                
                if 'exam_models' in yaml_data:
                    config.monitoring.exam_models = yaml_data['exam_models']
                
                if 'months' in yaml_data:
                    # Convert to strings if they're integers
                    config.monitoring.months = [str(m) for m in yaml_data['months']]
                
                if 'check_frequency' in yaml_data:
                    config.monitoring.check_frequency = yaml_data['check_frequency']
                
                if 'show_unavailable' in yaml_data:
                    config.monitoring.show_unavailable = yaml_data['show_unavailable']
                
                if 'no_ssl_verify' in yaml_data:
                    config.scraper.request_timeout = 60 if yaml_data['no_ssl_verify'] else 30
                    
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration")
    
    return config


# Default configuration (loads from config.yaml if available)
default_config = load_config_from_yaml()