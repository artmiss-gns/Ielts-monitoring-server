#!/usr/bin/env python3
"""
Comprehensive Telegram bot debugging script.
This will help identify exactly what's wrong with the setup.
"""

import asyncio
import os
import json

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables")

async def debug_telegram_setup():
    """Debug Telegram bot setup step by step."""
    print("🔍 Telegram Bot Debug Tool")
    print("=" * 50)
    
    # Step 1: Check environment variables
    print("\n📋 Step 1: Checking Environment Variables")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        print("💡 Make sure your .env file contains:")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return False
    else:
        print(f"✅ TELEGRAM_BOT_TOKEN found: {bot_token[:10]}...{bot_token[-4:]}")
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found")
        print("💡 Make sure your .env file contains:")
        print("   TELEGRAM_CHAT_ID=your_chat_id_here")
        return False
    else:
        print(f"✅ TELEGRAM_CHAT_ID found: {chat_id}")
    
    # Step 2: Test bot token validity
    print("\n🤖 Step 2: Testing Bot Token Validity")
    try:
        from telegram import Bot
        bot = Bot(token=bot_token)
        
        # Test bot connection
        me = await bot.get_me()
        print(f"✅ Bot token is valid!")
        print(f"   🤖 Bot name: {me.first_name}")
        print(f"   📛 Bot username: @{me.username}")
        print(f"   🆔 Bot ID: {me.id}")
        
    except Exception as e:
        print(f"❌ Bot token is invalid or there's a connection issue: {e}")
        return False
    
    # Step 3: Test chat ID format
    print(f"\n💬 Step 3: Analyzing Chat ID Format")
    print(f"   Chat ID: {chat_id}")
    print(f"   Type: {type(chat_id)}")
    print(f"   Length: {len(str(chat_id))}")
    
    # Try to convert to int if it's a string
    try:
        chat_id_int = int(chat_id)
        print(f"   As integer: {chat_id_int}")
        
        if chat_id_int > 0:
            print("   💡 This looks like a user chat ID (positive number)")
        else:
            print("   💡 This looks like a group/channel chat ID (negative number)")
            
    except ValueError:
        print("   ⚠️  Chat ID is not a number - this might be the issue!")
        return False
    
    # Step 4: Test sending a message
    print(f"\n📤 Step 4: Testing Message Sending")
    try:
        # Try sending to the chat
        message = await bot.send_message(
            chat_id=chat_id,
            text="🧪 **Debug Test Message**\n\nIf you see this, your Telegram bot is working correctly! 🎉",
            parse_mode='Markdown'
        )
        print(f"✅ Message sent successfully!")
        print(f"   📨 Message ID: {message.message_id}")
        print(f"   📅 Sent at: {message.date}")
        print(f"   💬 Chat ID confirmed: {message.chat.id}")
        print(f"   📛 Chat title: {getattr(message.chat, 'title', 'Private Chat')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        
        # Provide specific troubleshooting based on error
        error_str = str(e).lower()
        
        if "chat not found" in error_str:
            print("\n🔧 Troubleshooting: Chat Not Found")
            print("   • Make sure the chat ID is correct")
            print("   • If using a group/channel, make sure the bot is added as a member")
            print("   • For channels, the bot needs to be an admin")
            
        elif "bot was blocked" in error_str:
            print("\n🔧 Troubleshooting: Bot Blocked")
            print("   • The user has blocked the bot")
            print("   • Start a conversation with the bot first")
            
        elif "forbidden" in error_str:
            print("\n🔧 Troubleshooting: Forbidden")
            print("   • Bot doesn't have permission to send messages")
            print("   • Make sure bot is added to the group/channel")
            print("   • For channels, bot needs admin rights")
            
        else:
            print(f"\n🔧 Troubleshooting: Unknown Error")
            print(f"   • Error: {e}")
            print("   • Check bot token and chat ID")
        
        return False

async def get_chat_id_helper():
    """Helper function to get the correct chat ID."""
    print("\n🆔 Chat ID Helper")
    print("=" * 30)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ Bot token not found")
        return
    
    try:
        from telegram import Bot
        bot = Bot(token=bot_token)
        
        print("📱 Getting recent updates to find your chat ID...")
        updates = await bot.get_updates(limit=10)
        
        if not updates:
            print("⚠️  No recent messages found.")
            print("💡 Send a message to your bot first, then run this script again.")
            return
        
        print(f"✅ Found {len(updates)} recent updates:")
        
        for i, update in enumerate(updates, 1):
            if update.message:
                chat = update.message.chat
                print(f"\n📨 Update {i}:")
                print(f"   💬 Chat ID: {chat.id}")
                print(f"   📛 Chat Title: {getattr(chat, 'title', 'Private Chat')}")
                print(f"   👤 Chat Type: {chat.type}")
                print(f"   📝 Message: {update.message.text[:50]}...")
                
                if chat.type == 'private':
                    print(f"   👤 User: {chat.first_name} {chat.last_name or ''}")
                
    except Exception as e:
        print(f"❌ Error getting updates: {e}")

async def main():
    """Main debug function."""
    print("🚀 Starting Telegram Debug Session")
    
    # First try the main debug
    success = await debug_telegram_setup()
    
    if not success:
        print("\n" + "="*50)
        print("🔧 Let's try to find the correct chat ID...")
        await get_chat_id_helper()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Telegram bot is working correctly!")
        print("You can now use the notification system with confidence.")
    else:
        print("⚠️  Issues found. Please check the troubleshooting tips above.")
        print("\n📋 Quick Checklist:")
        print("   1. ✅ Bot token is valid")
        print("   2. ❓ Chat ID is correct")
        print("   3. ❓ Bot has permission to send messages")
        print("   4. ❓ Bot is added to the group/channel (if applicable)")

if __name__ == "__main__":
    asyncio.run(main())
