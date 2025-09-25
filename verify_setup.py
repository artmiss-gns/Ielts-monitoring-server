#!/usr/bin/env python3
"""
Quick verification script for Telegram credentials.
Run this after setting up your .env file to test the connection.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ielts_monitor.config import default_config
from src.ielts_monitor.notification import NotificationService

async def verify_credentials():
    """Verify that Telegram credentials are properly configured."""
    print("🔍 Verifying Telegram Credentials")
    print("=" * 40)

    # Load environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or bot_token == "your_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN not set or still using placeholder")
        print("   Please edit the .env file with your actual bot token")
        return False

    if not chat_id or chat_id == "your_chat_id_here":
        print("❌ TELEGRAM_CHAT_ID not set or still using placeholder")
        print("   Please edit the .env file with your actual chat ID")
        return False

    print(f"✅ Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"✅ Chat ID: {chat_id}")

    # Test notification service initialization
    try:
        config = default_config
        config.monitoring.notification.enabled = True

        service = NotificationService(config)

        if service.manager.bot:
            print("✅ Telegram bot initialized successfully!")
            print("✅ Notification system is ready!")

            # Show current stats
            stats = service.get_notification_stats()
            print(f"📊 Current stats: {stats}")

            return True
        else:
            print("❌ Failed to initialize Telegram bot")
            print("   Check your credentials and try again")
            return False

    except Exception as e:
        print(f"❌ Error initializing bot: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_credentials())
    if success:
        print("\n🎉 Setup complete! You can now run the monitoring system:")
        print("python -m src.ielts_monitor monitor")
    else:
        print("\n⚠️  Please fix the issues above and run this script again")
