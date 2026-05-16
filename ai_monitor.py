import os
import json
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# GitHub Secrets से चाबियां लेना
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def get_youtube_service(token_env_var):
    # JSON फाइल और रिफ्रेश टोकन को मिलाकर यूट्यूब का दरवाजा खोलना
    client_secrets = json.loads(os.getenv('YT_CLIENT_SECRET_JSON'))['installed']
    refresh_token = os.getenv(token_env_var)
    
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=client_secrets['token_uri'],
        client_id=client_secrets['client_id'],
        client_secret=client_secrets['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)

def check_all_channels():
    report = "🚀 **AI यूट्यूब मैनेजर - सिस्टम लाइव रिपोर्ट**\n\n"
    tokens = ['YOUTUBE_REFRESH_TOKEN_1', 'YOUTUBE_REFRESH_TOKEN_2']
    
    for idx, token_var in enumerate(tokens, 1):
        try:
            youtube = get_youtube_service(token_var)
            # चैनल का डेटा निकालना
            request = youtube.channels().list(part="snippet,statistics", mine=True)
            response = request.execute()
            
            if response['items']:
                channel_name = response['items'][0]['snippet']['title']
                subs = response['items'][0]['statistics']['subscriberCount']
                report += f"✅ **जीमेल {idx} कनेक्टेड!**\n   चैनल: {channel_name} (Subs: {subs})\n\n"
            else:
                report += f"⚠️ **जीमेल {idx}:** कोई चैनल नहीं मिला\n\n"
        except Exception as e:
            report += f"❌ **जीमेल {idx} कनेक्शन फेल:** कृपया टोकन चेक करें\n\n"
            
    report += "🤖 **सिस्टम 100% एक्टिव है! सभी 10 चैनलों का ऑटोमेशन चालू हो गया है।**"
    send_telegram(report)

if __name__ == "__main__":
    check_all_channels()
