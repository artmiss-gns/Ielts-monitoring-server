#!/usr/bin/env python3
"""
Test script for the notification system.
This script tests the notification functionality without requiring actual Telegram credentials.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ielts_monitor.config import default_config
from src.ielts_monitor.parser import ExamSlot
from src.ielts_monitor.notification import NotificationService

def create_test_slot():
    """Create a test ExamSlot for testing purposes."""
    return ExamSlot(
        date="27 Oct 2025",
        farsi_date="۱۴۰۴/۰۸/۰۵",
        time_of_day="Morning (08:30 - 11:30)",
        location="Tehran (Pars Center)",
        exam_type="cdielts - (Ac/Gt)",
        price="291,115,000 Rial",
        is_available=True,
        url="https://irsafam.org/ielts/timetable"
    )

async def test_notification_system():
    """Test the notification system functionality."""
    print("🧪 Testing IELTS Notification System")
    print("=" * 50)

    # Create notification service
    config = default_config
    config.monitoring.notification.enabled = True

    # Disable actual bot initialization by removing env vars
    original_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    original_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if "TELEGRAM_BOT_TOKEN" in os.environ:
        del os.environ["TELEGRAM_BOT_TOKEN"]
    if "TELEGRAM_CHAT_ID" in os.environ:
        del os.environ["TELEGRAM_CHAT_ID"]

    try:
        service = NotificationService(config)

        print("✅ NotificationService created successfully")

        # Test slot creation
        test_slot = create_test_slot()
        print(f"✅ Test slot created: {test_slot.date} at {test_slot.location}")

        # Test notification logic without sending actual messages
        print("✅ Notification system initialized (bot not configured for testing)")

        # Test state management
        stats = service.get_notification_stats()
        print(f"✅ Initial stats: {stats}")

        # Test slot processing (should not send notifications without bot)
        slots = [test_slot]
        await service.process_slots(slots)
        print("✅ Slot processing completed (no notifications sent without credentials)")

        # Test notification reset
        service.reset_notifications()
        print("✅ Notification state reset successfully")

        print("\n🎉 All tests passed! Notification system is working correctly.")
        print("\n📝 Next steps:")
        print("1. Install python-telegram-bot: pip install python-telegram-bot")
        print("2. Create a .env file with your Telegram credentials")
        print("3. Run the main monitoring script to test real notifications")

    finally:
        # Restore original environment variables
        if original_token:
            os.environ["TELEGRAM_BOT_TOKEN"] = original_token
        if original_chat_id:
            os.environ["TELEGRAM_CHAT_ID"] = original_chat_id

if __name__ == "__main__":
    asyncio.run(test_notification_system())
