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
GUMROAD_LINK = "https://your_store.gumroad.com/l/ai-setup" # ⚠️ अपना असली गमरोड लिंक डालें

# 🎯 10-चैनल मास्टर रणनीति
CHANNEL_STRATEGIES = {
    "Gadget Pro": "AMAZON",         
    "AI Automation Hub": "GUMROAD", 
    "Creator AI Setup": "GUMROAD",  
    "Future Tech AI": "GUMROAD"     
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def get_youtube_service(token_env_var):
    client_secrets = json.loads(os.getenv('YT_CLIENT_SECRET_JSON'))['installed']
    refresh_token = os.getenv(token_env_var)
    creds = Credentials(token=None, refresh_token=refresh_token, token_uri=client_secrets['token_uri'], client_id=client_secrets['client_id'], client_secret=client_secrets['client_secret'])
    return build('youtube', 'v3', credentials=creds)

def add_top_comment(youtube, video_id, comment_text):
    try:
        youtube.commentThreads().insert(part="snippet", body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": comment_text}}}}).execute()
    except Exception:
        pass

def advanced_delete_manager(youtube, channel_name, playlist_id):
    try:
        playlist_res = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=1).execute()
        if not playlist_res.get('items'): return f"⚠️ **{channel_name}**: कोई वीडियो नहीं है।"
        
        video_id = playlist_res['items'][0]['snippet']['resourceId']['videoId']
        
        # वीडियो का पूरा डेटा निकालना
        video_data = youtube.videos().list(part="snippet,statistics", id=video_id).execute()['items'][0]
        snippet = video_data['snippet']
        stats = video_data.get('statistics', {})
        
        title = snippet.get('title', '')
        old_desc = snippet.get('description', '')
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        
        # 🚨 सबसे सख्त क्वालिटी कंट्रोल: खराब वीडियो को हमेशा के लिए डिलीट करना
        # नियम: अगर 100 से ज़्यादा लोगों ने देखा, लेकिन लाइक 0 हैं (मतलब क्वालिटी खराब है)
        if views > 100 and likes == 0:
            print(f"🗑️ Deleting bad quality video from {channel_name}...")
            youtube.videos().delete(id=video_id).execute()
            return f"🚨 **ALERT ({channel_name})** 🚨\n❌ वीडियो क्वालिटी फेल! लोग इसे नापसंद कर रहे थे (Views: {views}, Likes: 0)।\nमैंने तुरंत एक्शन लेते हुए इस वीडियो को **यूट्यूब से हमेशा के लिए डिलीट (DELETE)** कर दिया है।"
        
        # 📈 सही वीडियो होने पर लिंक अपडेट करना
        health_msg = f"👁️ Views: {views} | ❤️ Likes: {likes}\n"
        strategy = CHANNEL_STRATEGIES.get(channel_name, "NONE")
        
        if strategy == "AMAZON" and AMAZON_TAG not in old_desc:
            query = urllib.parse.quote(title.replace('#shorts', '').strip())
            link = f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}"
            snippet['description'] = old_desc + f"\n\n🔥 गैजेट खरीदें: {link}"
            youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()
            add_top_comment(youtube, video_id, f"🔥 गैजेट यहाँ से खरीदें: {link}")
            return f"🎬 **{channel_name}**\n{health_msg}✅ वीडियो सेफ है! अमेज़ॉन लिंक और कमेंट लग गया।"
            
        elif strategy == "GUMROAD" and GUMROAD_LINK not in old_desc:
            snippet['description'] = old_desc + f"\n\n🤖 AI सेटअप खरीदें: {GUMROAD_LINK}"
            youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()
            add_top_comment(youtube, video_id, f"🤖 हमारा AI सेटअप खरीदें: {GUMROAD_LINK}")
            return f"🎬 **{channel_name}**\n{health_msg}💰 वीडियो सेफ है! गमरोड लिंक और कमेंट लग गया।"
            
        return f"🎬 **{channel_name}**\n{health_msg}⚡ वीडियो सेफ है, कोई नया बदलाव ज़रूरी नहीं।"
            
    except Exception as e:
        return f"❌ **{channel_name}** में एरर: {e}"

def main():
    report = "🚀 **AI मास्टर मैनेजर: क्वालिटी ऑडिट और सेल्स रिपोर्ट** 🚀\n\n"
    for token_var in ['YOUTUBE_REFRESH_TOKEN_1', 'YOUTUBE_REFRESH_TOKEN_2']:
        try:
            youtube = get_youtube_service(token_var)
            channels = youtube.channels().list(part="snippet,contentDetails", mine=True, maxResults=50).execute().get('items', [])
            for ch in channels:
                report += advanced_delete_manager(youtube, ch['snippet']['title'], ch['contentDetails']['relatedPlaylists']['uploads']) + "\n\n"
        except Exception:
            pass
            
    send_telegram(report)

if __name__ == "__main__":
    main()
