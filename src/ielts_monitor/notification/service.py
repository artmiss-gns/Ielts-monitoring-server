"""Notification system for IELTS appointment monitoring."""

import asyncio
import logging
import os
import json
import hashlib
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, will use system environment variables
    pass

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    # Handle case where python-telegram-bot is not installed
    Bot = None
    TelegramError = Exception

from src.ielts_monitor.config import Config
from src.ielts_monitor.parser import ExamSlot
from .http_sender import HTTPTelegramSender

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class NotificationState:
    """Represents the state of notifications for tracking."""
    notified_slots: Set[str]  # Hash of notified slots
    last_check: Optional[str] = None  # ISO timestamp of last check
    notification_count: int = 0  # Total notifications sent
    last_notification_time: Optional[str] = None  # ISO timestamp of last notification
    rate_limit_violations: int = 0  # Number of rate limit violations

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "notified_slots": list(self.notified_slots),
            "last_check": self.last_check,
            "notification_count": self.notification_count,
            "last_notification_time": self.last_notification_time,
            "rate_limit_violations": self.rate_limit_violations
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'NotificationState':
        """Create from dictionary."""
        return cls(
            notified_slots=set(data.get("notified_slots", [])),
            last_check=data.get("last_check"),
            notification_count=data.get("notification_count", 0),
            last_notification_time=data.get("last_notification_time"),
            rate_limit_violations=data.get("rate_limit_violations", 0)
        )


class NotificationManager:
    """Manages notifications and state tracking for IELTS slots."""

    def __init__(self, config: Config):
        """Initialize the notification manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.state_file = Path("notification_state.json")
        self.state = self._load_state()

        # Initialize Telegram bot if credentials are available
        self.bot = None
        self.http_sender = HTTPTelegramSender()
        self._init_telegram_bot()

    def _init_telegram_bot(self):
        """Initialize Telegram bot with credentials from environment."""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            logger.warning("Telegram credentials not found in environment variables")
            logger.info("To set up notifications:")
            logger.info("1. Create a bot with @BotFather on Telegram")
            logger.info("2. Create a .env file with:")
            logger.info("   TELEGRAM_BOT_TOKEN=your_bot_token")
            logger.info("   TELEGRAM_CHAT_ID=your_chat_id")
            logger.info("3. Add the bot as an admin to your channel")
            return

        if Bot is None:
            logger.error("python-telegram-bot package not installed")
            logger.info("Install it with: pip install python-telegram-bot")
            return

        try:
            # Try to initialize bot with different configurations to handle version issues
            try:
                # First try with default settings
                self.bot = Bot(token=bot_token)
            except Exception as init_error:
                if "proxy" in str(init_error).lower() or "AsyncClient" in str(init_error):
                    logger.debug("Telegram library compatibility issue, trying alternative method")
                    # Try creating bot with custom request configuration
                    try:
                        # Import the specific classes we need
                        from telegram.request import HTTPXRequest
                        import httpx
                        
                        # Create a custom HTTPXRequest without proxy settings
                        request = HTTPXRequest(
                            connection_pool_size=1,
                            read_timeout=30,
                            write_timeout=30,
                            connect_timeout=30,
                            pool_timeout=30
                        )
                        self.bot = Bot(token=bot_token, request=request)
                        logger.info("Bot initialized with custom HTTP request handler")
                    except Exception as custom_error:
                        logger.debug(f"Custom request handler failed: {custom_error}")
                        # Final fallback: try the simplest possible initialization
                        try:
                            # Use the most basic Bot initialization possible
                            from telegram import Bot as TelegramBot
                            self.bot = TelegramBot(token=bot_token)
                            logger.info("Bot initialized with basic configuration")
                        except Exception as basic_error:
                            logger.info("📡 Using HTTP fallback for reliable Telegram delivery")
                            logger.debug(f"All Telegram library methods failed: {basic_error}")
                            # Use HTTP fallback instead of failing
                            self.bot = None
                            self.http_sender = HTTPTelegramSender(bot_token, chat_id)
                else:
                    raise init_error
            
            self.chat_id = chat_id
            logger.info("Telegram bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            logger.error("This might be due to version compatibility issues.")
            logger.info("Try updating dependencies with:")
            logger.info("  pip install --upgrade python-telegram-bot httpx")
            logger.info("Or install compatible versions with:")
            logger.info("  pip install 'python-telegram-bot>=20.0.0,<21.0.0' 'httpx>=0.24.0,<0.28.0'")
            self.bot = None

    def _load_state(self) -> NotificationState:
        """Load notification state from file."""
        if not self.state_file.exists():
            return NotificationState(notified_slots=set())

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return NotificationState.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load notification state: {e}")
            return NotificationState(notified_slots=set())

    def _save_state(self):
        """Save notification state to file."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save notification state: {e}")

    def _generate_slot_hash(self, slot: ExamSlot) -> str:
        """Generate a unique hash for a slot to track notifications.

        Args:
            slot: ExamSlot to hash

        Returns:
            Unique hash string
        """
        # Create a unique identifier based on key slot attributes
        slot_key = f"{slot.date}_{slot.time_of_day}_{slot.location}_{slot.exam_type}"
        return hashlib.md5(slot_key.encode()).hexdigest()

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits.

        Returns:
            Always True (rate limiting disabled for IELTS monitoring)
        """
        # Rate limiting disabled - IELTS slots can appear in batches
        # and users want to be notified about all available slots immediately
        return True

    def _check_hourly_limit(self) -> bool:
        """Check if we're within hourly notification limits.

        Returns:
            Always True (hourly limit disabled for IELTS monitoring)
        """
        # Hourly limit disabled - IELTS slots are rare and valuable
        # Users want to be notified about every available slot
        return True

    def _format_slot_message(self, slot: ExamSlot) -> str:
        """Format a slot for notification message.

        Args:
            slot: ExamSlot to format

        Returns:
            Formatted message string
        """
        return (
            f"🎯 *New IELTS Slot Available!*\n\n"
            f"📅 **Date:** {slot.date}\n"
            f"🕐 **Time:** {slot.time_of_day}\n"
            f"📍 **Location:** {slot.location}\n"
            f"📝 **Exam Type:** {slot.exam_type}\n"
            f"💰 **Price:** {slot.price}\n"
            f"🔗 **URL:** {slot.url}\n\n"
            f"_Don't miss this opportunity!_"
        )

    async def _send_http_notification(self, slot: ExamSlot) -> bool:
        """Send notification using HTTP fallback method.
        
        Args:
            slot: ExamSlot to notify about
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        # Check rate limits
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded, skipping HTTP notification")
            return False

        if not self._check_hourly_limit():
            logger.warning("Hourly limit exceeded, skipping HTTP notification")
            return False

        try:
            slot_hash = self._generate_slot_hash(slot)
            message = self._format_slot_message(slot)

            success = await self.http_sender.send_message(message)
            
            if success:
                # Update state
                self.state.notified_slots.add(slot_hash)
                self.state.notification_count += 1
                self.state.last_notification_time = datetime.now(timezone.utc).isoformat()
                self.state.last_check = datetime.now(timezone.utc).isoformat()
                self._save_state()

                logger.info(f"HTTP notification sent for slot: {slot.date} at {slot.location}")
                return True
            else:
                logger.error(f"Failed to send HTTP notification for: {slot.date} at {slot.location}")
                return False

        except Exception as e:
            logger.error(f"Unexpected error sending HTTP notification: {e}")
            return False

    async def send_notification(self, slot: ExamSlot) -> bool:
        """Send notification for a slot with rate limiting and error handling.

        Args:
            slot: ExamSlot to notify about

        Returns:
            True if notification was sent successfully, False otherwise
        """
        # Try HTTP sender first if bot is not available
        if not self.bot and self.http_sender.is_configured():
            logger.info("Using HTTP fallback for notification")
            return await self._send_http_notification(slot)
        
        if not self.bot:
            logger.warning("Telegram bot not initialized, skipping notification")
            return False

        # Check rate limits
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded, skipping notification")
            return False

        if not self._check_hourly_limit():
            logger.warning("Hourly limit exceeded, skipping notification")
            return False

        try:
            slot_hash = self._generate_slot_hash(slot)
            message = self._format_slot_message(slot)

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )

            # Update state
            self.state.notified_slots.add(slot_hash)
            self.state.notification_count += 1
            self.state.last_notification_time = datetime.now(timezone.utc).isoformat()
            self.state.last_check = datetime.now(timezone.utc).isoformat()
            self._save_state()

            logger.info(f"Notification sent for slot: {slot.date} at {slot.location}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            # Handle specific Telegram errors
            if "retry after" in str(e).lower():
                logger.warning("Telegram rate limit hit, will retry later")
            elif "bot was blocked" in str(e).lower():
                logger.error("Bot was blocked by user, disabling notifications")
                self.bot = None
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending notification: {e}")
            return False

    def should_notify(self, slot: ExamSlot) -> bool:
        """Check if a slot should trigger a notification.

        Args:
            slot: ExamSlot to check

        Returns:
            True if notification should be sent, False if already notified
        """
        if not slot.is_available:
            return False

        slot_hash = self._generate_slot_hash(slot)
        return slot_hash not in self.state.notified_slots

    def mark_slot_filled(self, slot: ExamSlot):
        """Mark a previously notified slot as filled (remove from notified set).

        Args:
            slot: ExamSlot that was previously notified but is now filled
        """
        slot_hash = self._generate_slot_hash(slot)
        if slot_hash in self.state.notified_slots:
            self.state.notified_slots.remove(slot_hash)
            self._save_state()
            logger.info(f"Removed slot from notified list: {slot.date} at {slot.location}")

    def get_stats(self) -> Dict:
        """Get notification statistics.

        Returns:
            Dictionary with notification statistics
        """
        return {
            "total_notifications": self.state.notification_count,
            "notified_slots_count": len(self.state.notified_slots),
            "last_check": self.state.last_check,
            "last_notification": self.state.last_notification_time,
            "rate_limit_violations": self.state.rate_limit_violations
        }

    def reset_notifications(self):
        """Reset all notification state (for testing or manual reset)."""
        self.state = NotificationState(notified_slots=set())
        self._save_state()
        logger.info("Notification state reset")


class NotificationService:
    """Service for handling notifications in the main application."""

    def __init__(self, config: Config):
        """Initialize the notification service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.manager = NotificationManager(config)

    async def process_slots(self, slots: List[ExamSlot]):
        """Process a list of slots and send notifications for new ones.

        Args:
            slots: List of ExamSlot objects to process
        """
        if not self.config.monitoring.notification.enabled:
            return

        available_slots = [slot for slot in slots if slot.is_available]

        if not available_slots:
            logger.debug("No available slots to process")
            return

        logger.info(f"Processing {len(available_slots)} available slots for notifications")

        # Send notifications for new slots
        for slot in available_slots:
            if self.manager.should_notify(slot):
                success = await self.manager.send_notification(slot)
                if success:
                    logger.info(f"Sent notification for: {slot.date} at {slot.location}")
                else:
                    logger.error(f"Failed to send notification for: {slot.date} at {slot.location}")

    def get_notification_stats(self) -> Dict:
        """Get notification statistics.

        Returns:
            Dictionary with notification statistics
        """
        return self.manager.get_stats()

    def reset_notifications(self):
        """Reset all notification state."""
        self.manager.reset_notifications()
