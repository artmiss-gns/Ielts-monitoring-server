#!/usr/bin/env python3
"""
Setup script to help configure Telegram bot for IELTS notifications.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with Telegram credentials."""
    env_file = Path(".env")
    
    print("🤖 Telegram Bot Setup")
    print("=" * 30)
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📋 Follow these steps to set up your Telegram bot:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Start a chat with @BotFather")
    print("3. Send /newbot command")
    print("4. Follow the instructions to create your bot")
    print("5. Copy the bot token when provided")
    print()
    
    bot_token = input("Enter your bot token: ").strip()
    if not bot_token:
        print("❌ Bot token is required")
        return
    
    print("\n📱 To get your chat ID:")
    print("1. Start a chat with your bot (search for your bot's username)")
    print("2. Send any message to your bot")
    print("3. Open this URL in your browser:")
    print(f"   https://api.telegram.org/bot{bot_token}/getUpdates")
    print("4. Look for 'chat':{'id': YOUR_CHAT_ID} in the response")
    print("5. Copy the chat ID (it's usually a negative number for groups)")
    print()
    
    chat_id = input("Enter your chat ID: ").strip()
    if not chat_id:
        print("❌ Chat ID is required")
        return
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration for IELTS Monitoring
TELEGRAM_BOT_TOKEN={bot_token}
TELEGRAM_CHAT_ID={chat_id}

# Optional: Add other environment variables here
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"📁 Location: {env_file.absolute()}")
        print("\n🧪 You can now test your setup by running:")
        print("   python test_notification_real.py")
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def check_existing_setup():
    """Check if Telegram credentials are already configured."""
    print("🔍 Checking existing setup...")
    
    # Check environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Check .env file
    env_file = Path(".env")
    env_exists = env_file.exists()
    
    print(f"Environment variables:")
    print(f"  TELEGRAM_BOT_TOKEN: {'✅ Set' if bot_token else '❌ Not set'}")
    print(f"  TELEGRAM_CHAT_ID: {'✅ Set' if chat_id else '❌ Not set'}")
    print(f".env file: {'✅ Exists' if env_exists else '❌ Not found'}")
    
    if bot_token and chat_id:
        print("\n🎉 Telegram credentials are configured!")
        print("You can test them by running:")
        print("   python test_notification_real.py")
        return True
    else:
        print("\n⚠️  Telegram credentials need to be configured.")
        return False

def main():
    """Main function."""
    print("🚀 IELTS Monitoring - Telegram Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_existing_setup()
        return
    
    # Check if already configured
    if check_existing_setup():
        reconfigure = input("\nDo you want to reconfigure? (y/N): ").lower().strip()
        if reconfigure != 'y':
            print("Setup cancelled.")
            return
    
    print("\n" + "=" * 40)
    create_env_file()

if __name__ == "__main__":
    main()
