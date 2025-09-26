#!/usr/bin/env python3
"""
Real notification test script for IELTS monitoring system.
This script will actually attempt to send a notification to Telegram.
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
        location="Tehran (Test Center)",
        exam_type="cdielts - (Ac/Gt)",
        price="291,115,000 Rial",
        is_available=True,
        url="https://irsafam.org/ielts/timetable"
    )

async def test_telegram_connection():
    """Test the Telegram bot connection and send a test message."""
    print("🧪 Testing Real IELTS Notification System")
    print("=" * 50)
    
    # Check if environment variables are set
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        print("\n📋 To set up notifications:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your bot token")
        print("3. Set environment variable:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return False
        
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID environment variable not set")
        print("\n📋 To get your chat ID:")
        print("1. Start a chat with your bot")
        print("2. Send a message to your bot")
        print("3. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
        print("4. Look for 'chat':{'id': YOUR_CHAT_ID}")
        print("5. Set environment variable:")
        print("   export TELEGRAM_CHAT_ID='your_chat_id_here'")
        return False
    
    print(f"✅ Bot token found: {bot_token[:10]}...")
    print(f"✅ Chat ID found: {chat_id}")
    
    # Create notification service
    config = default_config
    config.monitoring.notification.enabled = True
    
    try:
        # Create notification service
        notification_service = NotificationService(config)
        
        # Check if bot was initialized
        if not notification_service.manager.bot:
            print("❌ Failed to initialize Telegram bot")
            print("Check your bot token and ensure python-telegram-bot is installed")
            print("Install with: pip install python-telegram-bot")
            return False
            
        print("✅ Telegram bot initialized successfully")
        
        # Create test slot
        test_slot = create_test_slot()
        print(f"\n📝 Test Slot: {test_slot.location} - {test_slot.date}")
        print(f"✅ Available: {test_slot.is_available}")
        
        # Test notification logic
        should_notify = notification_service.manager.should_notify(test_slot)
        print(f"🔔 Should notify: {should_notify}")
        
        if should_notify:
            # Try to send notification
            print("\n📤 Sending test notification...")
            success = await notification_service.manager.send_notification(test_slot)
            
            if success:
                print("✅ Test notification sent successfully!")
                print("🎉 Check your Telegram chat for the message")
            else:
                print("❌ Failed to send test notification")
                return False
        else:
            print("ℹ️  Notification already sent for this slot (check notification_state.json)")
            
        # Show notification stats
        stats = notification_service.get_notification_stats()
        print("\n📊 Notification Statistics:")
        print(f"   Total notifications: {stats['total_notifications']}")
        print(f"   Notified slots count: {stats['notified_slots_count']}")
        print(f"   Last check: {stats['last_check']}")
        print(f"   Last notification: {stats['last_notification']}")
        
        print("\n🎯 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function to run the test."""
    print("🚀 Starting Real Notification Test")
    print("This will attempt to send an actual Telegram message")
    print()
    
    # Check for required packages
    try:
        import telegram
        print("✅ python-telegram-bot package found")
    except ImportError:
        print("❌ python-telegram-bot package not installed")
        print("Install with: pip install python-telegram-bot")
        return
    
    success = await test_telegram_connection()
    
    if success:
        print("\n🎉 Notification system is working correctly!")
        print("You can now use the monitoring system with confidence.")
    else:
        print("\n⚠️  Notification system needs attention.")
        print("Please check the error messages above and fix the issues.")

if __name__ == "__main__":
    asyncio.run(main())
