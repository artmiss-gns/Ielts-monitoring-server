#!/usr/bin/env python3
"""
Simple Telegram bot test to isolate the initialization issue.
"""

import asyncio
import os

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def test_simple_telegram():
    """Test Telegram bot with the simplest possible approach."""
    print("🧪 Simple Telegram Bot Test")
    print("=" * 30)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ Missing environment variables")
        return
    
    print(f"✅ Bot token: {bot_token[:10]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    try:
        # Try the most basic import and initialization
        print("\n🔄 Importing telegram...")
        from telegram import Bot
        print("✅ Import successful")
        
        print("🔄 Creating bot instance...")
        # Try creating bot without any custom configuration
        bot = Bot(token=bot_token)
        print("✅ Bot instance created")
        
        print("🔄 Testing bot connection...")
        # Test getting bot info (this doesn't require httpx async client)
        me = await bot.get_me()
        print(f"✅ Bot connected: @{me.username}")
        
        print("🔄 Sending test message...")
        message = await bot.send_message(
            chat_id=chat_id,
            text="🧪 Test message from IELTS monitoring system!\n\nIf you see this, the notification system is working! 🎉"
        )
        print(f"✅ Message sent successfully! Message ID: {message.message_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Let's try to get more specific error information
        if "AsyncClient" in str(e):
            print("\n🔍 This appears to be an httpx AsyncClient issue.")
            print("Let's try a different approach...")
            
            try:
                # Try importing and checking httpx version
                import httpx
                print(f"httpx version: {httpx.__version__}")
                
                # Try creating a simple AsyncClient to see what fails
                print("Testing httpx AsyncClient creation...")
                client = httpx.AsyncClient()
                print("✅ httpx AsyncClient created successfully")
                await client.aclose()
                
            except Exception as httpx_error:
                print(f"❌ httpx error: {httpx_error}")
                
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_telegram())
    if success:
        print("\n🎉 Telegram bot is working!")
    else:
        print("\n⚠️ Telegram bot needs fixing.")
