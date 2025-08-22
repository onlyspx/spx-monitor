import requests
import json
from datetime import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1408429479189151865/OxyU99MokLJ2-4LfTYwh42-O0DJ99SECgg4Jvt5vfMrho0Bz0dnCZ5euw6fsuXt1oRRA"

def test_discord_webhook():
    """Test the Discord webhook with a simple message"""
    print("Testing Discord webhook...")
    
    # Simple text message
    simple_payload = {
        "content": "🧪 Test message from SPX Monitor Bot!"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=simple_payload)
        print(f"Simple message status: {response.status_code}")
        
        if response.status_code == 204:
            print("✅ Simple message sent successfully!")
        else:
            print(f"❌ Simple message failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending simple message: {e}")
    
    # Rich embed message
    embed_payload = {
        "embeds": [{
            "title": "🎯 SPX Monitor Test",
            "description": "This is a test message to verify the Discord webhook is working correctly.",
            "color": 0x00ff00,
            "fields": [
                {
                    "name": "Test Status",
                    "value": "✅ Webhook connection successful",
                    "inline": True
                },
                {
                    "name": "Timestamp",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }
            ],

        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=embed_payload)
        print(f"Rich embed status: {response.status_code}")
        
        if response.status_code == 204:
            print("✅ Rich embed sent successfully!")
        else:
            print(f"❌ Rich embed failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending rich embed: {e}")

if __name__ == "__main__":
    test_discord_webhook()
