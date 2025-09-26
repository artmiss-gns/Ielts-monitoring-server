#!/usr/bin/env python3
"""
Test Telegram notifications using direct HTTP API calls.
This bypasses the python-telegram-bot library issues.
"""

import os
import requests
import json

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables")

def test_telegram_http():
    """Test Telegram bot using direct HTTP API."""
    print("🧪 Testing Telegram via HTTP API")
    print("=" * 40)
    
    # Get credentials
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found")
        return False
    
    print(f"✅ Bot token: {bot_token[:10]}...{bot_token[-4:]}")
    print(f"✅ Chat ID: {chat_id}")
    
    # Step 1: Test bot info
    print("\n🤖 Step 1: Getting bot info...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ Bot is valid!")
                print(f"   🤖 Name: {bot_info.get('first_name')}")
                print(f"   📛 Username: @{bot_info.get('username')}")
                print(f"   🆔 ID: {bot_info.get('id')}")
            else:
                print(f"❌ Bot API error: {data.get('description')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return False
    
    # Step 2: Test sending message
    print("\n📤 Step 2: Sending test message...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message_text = """🧪 **HTTP API Test Message**

✅ This message was sent using direct HTTP API calls!
🎉 Your Telegram bot is working correctly!

📋 **Test Details:**
• Bot Token: Valid ✅
• Chat ID: {chat_id}
• Method: Direct HTTP API
• Time: Now

If you see this message, the notification system should work! 🚀""".format(chat_id=chat_id)
        
        payload = {
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                message_info = data['result']
                print(f"✅ Message sent successfully!")
                print(f"   📨 Message ID: {message_info.get('message_id')}")
                print(f"   💬 Chat ID: {message_info.get('chat', {}).get('id')}")
                print(f"   📛 Chat Title: {message_info.get('chat', {}).get('title', 'Private Chat')}")
                print(f"   📅 Date: {message_info.get('date')}")
                
                print(f"\n🎉 SUCCESS! Check your Telegram for the test message!")
                return True
            else:
                error_desc = data.get('description', 'Unknown error')
                print(f"❌ Telegram API error: {error_desc}")
                
                # Provide specific troubleshooting
                if "chat not found" in error_desc.lower():
                    print("\n🔧 Troubleshooting: Chat Not Found")
                    print("   • Double-check your chat ID")
                    print("   • Make sure you've started a conversation with the bot")
                    print("   • For groups/channels, ensure the bot is a member")
                    
                elif "forbidden" in error_desc.lower():
                    print("\n🔧 Troubleshooting: Forbidden")
                    print("   • Bot doesn't have permission to send messages")
                    print("   • For groups/channels, make sure bot is added and has permissions")
                    
                elif "bot was blocked" in error_desc.lower():
                    print("\n🔧 Troubleshooting: Bot Blocked")
                    print("   • You may have blocked the bot")
                    print("   • Unblock the bot and try again")
                
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def get_chat_id_via_http():
    """Get chat ID using HTTP API."""
    print("\n🆔 Getting Chat ID via HTTP API")
    print("=" * 35)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ Bot token not found")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                updates = data.get('result', [])
                
                if not updates:
                    print("⚠️  No recent messages found.")
                    print("💡 Send a message to your bot first, then run this script again.")
                    return
                
                print(f"✅ Found {len(updates)} recent updates:")
                
                for i, update in enumerate(updates[-5:], 1):  # Show last 5 updates
                    print(f"\n📨 Update {i} (Raw): {json.dumps(update, indent=2)}")
                    
                    if 'message' in update:
                        message = update['message']
                        chat = message['chat']
                        
                        print(f"\n📨 Update {i} (Parsed):")
                        print(f"   💬 Chat ID: {chat['id']}")
                        print(f"   📛 Chat Title: {chat.get('title', 'Private Chat')}")
                        print(f"   👤 Chat Type: {chat['type']}")
                        print(f"   📝 Message: {message.get('text', 'No text')[:50]}...")
                        
                        if chat['type'] == 'private':
                            print(f"   👤 User: {chat.get('first_name', '')} {chat.get('last_name', '')}")
                            
                        print(f"\n💡 Use this Chat ID in your .env file:")
                        print(f"   TELEGRAM_CHAT_ID={chat['id']}")
                    elif 'channel_post' in update:
                        post = update['channel_post']
                        chat = post['chat']
                        
                        print(f"\n📨 Channel Update {i}:")
                        print(f"   💬 Chat ID: {chat['id']}")
                        print(f"   📛 Channel Title: {chat.get('title', 'Unknown Channel')}")
                        print(f"   👤 Chat Type: {chat['type']}")
                        
                        print(f"\n💡 Use this Chat ID in your .env file:")
                        print(f"   TELEGRAM_CHAT_ID={chat['id']}")
                    else:
                        print(f"\n📨 Other Update {i}: {list(update.keys())}")
            else:
                print(f"❌ API error: {data.get('description')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting updates: {e}")

def main():
    """Main function."""
    print("🚀 Telegram HTTP API Test")
    print("This bypasses python-telegram-bot library issues")
    print()
    
    success = test_telegram_http()
    
    if not success:
        print("\n" + "="*50)
        print("🔧 Let's try to find the correct chat ID...")
        get_chat_id_via_http()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Telegram is working via HTTP API!")
        print("We can now implement a HTTP-based notification system.")
    else:
        print("⚠️  Still having issues. Check the troubleshooting tips above.")

if __name__ == "__main__":
    main()
