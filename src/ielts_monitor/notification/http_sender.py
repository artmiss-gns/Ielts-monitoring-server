"""HTTP-based Telegram notification sender as fallback."""

import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HTTPTelegramSender:
    """HTTP-based Telegram message sender."""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """Initialize the HTTP sender."""
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
    def is_configured(self) -> bool:
        """Check if the sender is properly configured."""
        return bool(self.bot_token and self.chat_id)
    
    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send a message via HTTP API.
        
        Args:
            text: Message text to send
            parse_mode: Parse mode (Markdown or HTML)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("HTTP Telegram sender not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    logger.info(f"HTTP notification sent successfully: Message ID {data['result']['message_id']}")
                    return True
                else:
                    logger.error(f"Telegram API error: {data.get('description')}")
                    return False
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send HTTP notification: {e}")
            return False
