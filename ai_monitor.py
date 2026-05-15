import os
import requests

# GitHub Secrets से आपकी चाबियां लेना
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
        print("✅ टेलीग्राम मैसेज सफलता से भेजा गया!")
    except Exception as e:
        print(f"❌ मैसेज भेजने में एरर: {e}")

if __name__ == "__main__":
    # यह आपका पहला टेस्ट मैसेज है
    test_message = (
        "🚀 **AI YouTube मैनेजर सिस्टम चालू!**\n\n"
        "नमस्ते गिरीशभाई! मुझे GitHub Secrets से Telegram और YouTube की चाबियां मिल गई हैं।\n"
        "मैं अब आपके सभी 10 चैनलों को ऑटोमैटिक तरीके से संभालने के लिए तैयार हूँ। ⚙️"
    )
    send_telegram(test_message)
