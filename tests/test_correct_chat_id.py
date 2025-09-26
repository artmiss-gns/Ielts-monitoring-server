#!/usr/bin/env python3
"""
Test with the correct chat ID we found.
"""

import os
import requests

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_with_correct_chat_id():
    """Test with the correct chat ID."""
    print("🧪 Testing with Correct Chat ID")
    print("=" * 40)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    correct_chat_id = "-1003117398974"  # The correct chat ID from the update
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    print(f"✅ Bot token: {bot_token[:10]}...{bot_token[-4:]}")
    print(f"✅ Using correct Chat ID: {correct_chat_id}")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message_text = """🎉 **SUCCESS!** 

✅ Found the correct Chat ID!
🔧 Your .env file should use: `-1003117398974`

📋 **What was wrong:**
• Old Chat ID: `3117398974` ❌
• Correct Chat ID: `-1003117398974` ✅

The difference:
• Channel/Group IDs are negative
• They often have a `100` prefix
• Your original ID was missing the `-100` prefix

🚀 **Next Steps:**
1. Update your .env file with the correct Chat ID
2. Run the notification tests again
3. Enjoy working notifications! 🎊"""
        
        payload = {
            'chat_id': correct_chat_id,
            'text': message_text,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"🎉 SUCCESS! Message sent to your channel!")
                print(f"📨 Message ID: {data['result']['message_id']}")
                print(f"💬 Channel: {data['result']['chat']['title']}")
                
                print(f"\n🔧 **ACTION REQUIRED:**")
                print(f"Update your .env file:")
                print(f"TELEGRAM_CHAT_ID=-1003117398974")
                
                return True
            else:
                print(f"❌ API error: {data.get('description')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_with_correct_chat_id()
    
    if success:
        print("\n🎊 NOTIFICATION SYSTEM FIXED!")
        print("Update your .env file and you're good to go!")
    else:
        print("\n⚠️ Still having issues...")
