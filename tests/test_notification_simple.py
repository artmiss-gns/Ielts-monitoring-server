#!/usr/bin/env python3
"""
Test script for notification system without Telegram credentials.
This script simulates what would happen when appointments become available.
"""

import asyncio
import sys
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
        # Create notification service
        notification_service = NotificationService(config)

        # Create test slot
        test_slot = create_test_slot()

        print(f"📝 Test Slot: {test_slot.location} - {test_slot.date}")
        print(f"✅ Available: {test_slot.is_available}")

        # Test notification logic
        should_notify = notification_service.manager.should_notify(test_slot)
        print(f"🔔 Should notify: {should_notify}")

        # Try to send notification (will fail without bot credentials)
        print("\n📤 Attempting to send notification...")
        success = await notification_service.manager.send_notification(test_slot)

        if success:
            print("✅ Notification sent successfully!")
        else:
            print("❌ Notification failed (expected without bot credentials)")

        # Show notification stats
        stats = notification_service.get_notification_stats()
        print("\n📊 Notification Statistics:")
        print(f"   Total notifications: {stats['total_notifications']}")
        print(f"   Notified slots count: {stats['notified_slots_count']}")
        print(f"   Last check: {stats['last_check']}")
        print(f"   Last notification: {stats['last_notification']}")

        # Reset notifications for testing
        print("\n🔄 Resetting notification state...")
        notification_service.reset_notifications()
        print("✅ Notification state reset")

        print("\n🎯 Test completed!")
        print("\nTo enable real notifications:")
        print("1. Create a Telegram bot via @BotFather")
        print("2. Get your bot token")
        print("3. Get your chat ID")
        print("4. Set environment variables:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("   export TELEGRAM_CHAT_ID='your_chat_id'")
        print("5. Run: python -m src.ielts_monitor monitor")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Restore original environment variables
        if original_token:
            os.environ["TELEGRAM_BOT_TOKEN"] = original_token
        if original_chat_id:
            os.environ["TELEGRAM_CHAT_ID"] = original_chat_id

if __name__ == "__main__":
    import os
    asyncio.run(test_notification_system())
