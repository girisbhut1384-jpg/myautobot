import os
import json
import urllib.parse
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 🔐 Telegram Settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 🛒 Affiliate & Sales Links
AMAZON_TAG = "girishbhut07-21"
GUMROAD_LINK = "https://your_store.gumroad.com/l/ai-setup" # ⚠️ यहाँ अपना असली गमरोड लिंक ज़रूर डालें

# 🎯 10-चैनल मास्टर रणनीति
# ध्यान दें: यहाँ अपने गैजेट और AI चैनलों के बिल्कुल सही नाम (जैसे यूट्यूब पर दिखते हैं) लिखें।
# जिन चैनलों का नाम इस लिस्ट में नहीं होगा, सिस्टम उन्हें सुरक्षित (NONE) रखेगा और वहाँ कोई लिंक नहीं लगाएगा।
CHANNEL_STRATEGIES = {
    "Gadget Pro": "AMAZON",         # गैजेट चैनल का नाम 
    "AI Automation Hub": "GUMROAD", # पहले AI चैनल का नाम
    "Creator AI Setup": "GUMROAD",  # दूसरे AI चैनल का नाम
    "Future Tech AI": "GUMROAD"     # तीसरे AI चैनल का नाम
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def get_youtube_service(token_env_var):
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

def add_top_comment(youtube, video_id, comment_text, channel_name):
    try:
        youtube.commentThreads().insert(
            part="snippet", 
            body={
                "snippet": {
                    "videoId": video_id, 
                    "topLevelComment": {"snippet": {"textOriginal": comment_text}}
                }
            }
        ).execute()
    except Exception as e:
        print(f"Comment Error on {channel_name}: {e}")

def optimize_latest_video(youtube, channel_name, playlist_id):
    try:
        # सबसे नया वीडियो निकालना
        playlist_res = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=1).execute()
        if not playlist_res.get('items'): 
            return f"⚠️ **{channel_name}**: कोई नया वीडियो नहीं मिला।"
        
        video_id = playlist_res['items'][0]['snippet']['resourceId']['videoId']
        snippet = youtube.videos().list(part="snippet", id=video_id).execute()['items'][0]['snippet']
        
        title = snippet.get('title', '')
        old_desc = snippet.get('description', '')
        strategy = CHANNEL_STRATEGIES.get(channel_name, "NONE")
        
        # 1. Amazon Strategy (गैजेट्स के लिए)
        if strategy == "AMAZON" and AMAZON_TAG not in old_desc:
            clean_title = title.replace('#shorts', '').replace('Best', '').replace('🤯', '').strip()
            query = urllib.parse.quote(clean_title)
            link = f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}"
            
            snippet['description'] = old_desc + f"\n\n🔥 👉 शानदार गैजेट आउट ऑफ़ स्टॉक होने से पहले खरीदें!\n🔗 लिंक: {link}\n#Gadgets #Trending #Viral"
            youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()
            add_top_comment(youtube, video_id, f"🔥 गैजेट खरीदने का लिंक: {link}", channel_name)
            
            return f"✅ **{channel_name}**: अमेज़ॉन लिंक और कमेंट सफलता से लगा दिया गया!"
            
        # 2. Gumroad Strategy (AI चैनलों के लिए)
        elif strategy == "GUMROAD" and GUMROAD_LINK not in old_desc:
            snippet['description'] = old_desc + f"\n\n🤖 100% ऑटोमेटेड AI यूट्यूब सेटअप आज ही खरीदें और पैसिव इनकम शुरू करें!\n👉 यहाँ क्लिक करें: {GUMROAD_LINK}\n#AIAutomation #YouTubeAutomation #MakeMoneyOnline"
            youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()
            add_top_comment(youtube, video_id, f"🤖 हमारा ऑटोमेटेड AI सेटअप यहाँ से खरीदें: {GUMROAD_LINK}", channel_name)
            
            return f"💰 **{channel_name}**: गमरोड लिंक और कमेंट सफलता से लगा दिया गया!"
            
        # 3. None Strategy (भक्ति, रहस्य आदि चैनलों के लिए)
        else:
            if strategy == "NONE":
                return f"🛡️ **{channel_name}**: इस चैनल पर लिंक लगाना मना है (सुरक्षित)।"
            return f"⚡ **{channel_name}**: इस वीडियो में लिंक पहले से लगा हुआ है।"
            
    except Exception as e:
        return f"❌ **{channel_name}** में एरर: अपडेट फेल हो गया। ({e})"

def main():
    report = "🚀 **AI मास्टर मैनेजर: 10-चैनल लाइव रिपोर्ट** 🚀\n\n"
    tokens = ['YOUTUBE_REFRESH_TOKEN_1', 'YOUTUBE_REFRESH_TOKEN_2']
    
    for idx, token_var in enumerate(tokens, 1):
        report += f"📁 **जीमेल अकाउंट {idx} स्कैनिंग:**\n"
        try:
            youtube = get_youtube_service(token_var)
            # maxResults=50 सुनिश्चित करता है कि कोई भी चैनल न छूटे
            channels_res = youtube.channels().list(part="snippet,contentDetails", mine=True, maxResults=50).execute()
            
            if 'items' in channels_res:
                for channel in channels_res['items']:
                    channel_name = channel['snippet']['title']
                    uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
                    
                    result = optimize_latest_video(youtube, channel_name, uploads_playlist_id)
                    report += result + "\n"
            else:
                report += f"⚠️ इस अकाउंट में कोई चैनल नहीं मिला।\n"
        except Exception as e:
            report += f"❌ इस अकाउंट का कनेक्शन फेल हो गया। कृपया टोकन चेक करें।\n"
        report += "\n"
        
    report += "🤖 **सभी चैनलों का स्कैन पूरा हुआ!**"
    send_telegram(report)

if __name__ == "__main__":
    main()
