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
            self.bot = Bot(token=bot_token)
            self.chat_id = chat_id
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
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
            True if within limits, False if rate limited
        """
        if not self.state.last_notification_time:
            return True

        try:
            last_notification = datetime.fromisoformat(self.state.last_notification_time)
            time_since_last = datetime.now(timezone.utc) - last_notification

            # Check minimum interval between notifications
            min_interval = timedelta(seconds=self.config.monitoring.notification.rate_limit_seconds)
            if time_since_last < min_interval:
                self.state.rate_limit_violations += 1
                self._save_state()
                return False

            return True
        except (ValueError, TypeError):
            # If we can't parse the timestamp, allow the notification
            return True

    def _check_hourly_limit(self) -> bool:
        """Check if we're within hourly notification limits.

        Returns:
            True if within limits, False if exceeded
        """
        max_per_hour = self.config.monitoring.notification.max_notifications_per_hour

        # Count notifications in the last hour
        if self.state.last_notification_time:
            try:
                last_notification = datetime.fromisoformat(self.state.last_notification_time)
                one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

                # If last notification was more than an hour ago, reset counter
                if last_notification < one_hour_ago:
                    self.state.notification_count = 0
                    self._save_state()
                    return True
            except (ValueError, TypeError):
                pass

        # Check if we've exceeded the hourly limit
        if self.state.notification_count >= max_per_hour:
            logger.warning(f"Hourly notification limit reached: {max_per_hour}")
            return False

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

    async def send_notification(self, slot: ExamSlot) -> bool:
        """Send notification for a slot with rate limiting and error handling.

        Args:
            slot: ExamSlot to notify about

        Returns:
            True if notification was sent successfully, False otherwise
        """
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
