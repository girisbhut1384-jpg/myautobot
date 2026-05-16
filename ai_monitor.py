import os
import json
import urllib.parse
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 🔐 Telegram Settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

AMAZON_TAG = "girishbhut07-21"
GUMROAD_LINK = "https://your_store.gumroad.com/l/ai-setup" 

# 🎯 10-चैनल स्मार्ट रणनीति (सही चैनलों पर सही लिंक)
CHANNEL_STRATEGIES = {
    "GIRISH AI GADGET": "AMAZON",         
    "FACELESS AI WEALTH": "GUMROAD", 
    "AI AUTO PILOT EMPIRE": "GUMROAD",  
    "ZEROTOUCH AI CREATOR": "GUMROAD"     
}

# 🔑 सभी 10 टोकन्स की लिस्ट
ALL_TOKENS = [
    'TOKEN_GBYOUTUBER', 'TOKEN_HEALTH', 'TOKEN_SUCCESS', 'TOKEN_SANATAN', 
    'TOKEN_BOOK', 'TOKEN_MYSTERY', 'TOKEN_WEALTH', 'TOKEN_GADGET', 
    'TOKEN_EMPIRE', 'TOKEN_ZEROTOUCH'
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def get_youtube_service(token_env_var):
    client_secrets_json = os.getenv('YT_CLIENT_SECRET_JSON')
    refresh_token = os.getenv(token_env_var)
    if not refresh_token or not client_secrets_json:
        return None 
    client_secrets = json.loads(client_secrets_json)['installed']
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
        video_data = youtube.videos().list(part="snippet,statistics", id=video_id).execute()['items'][0]
        snippet = video_data['snippet']
        stats = video_data.get('statistics', {})
        
        title = snippet.get('title', '')
        old_desc = snippet.get('description', '')
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        
        # 🚨 सख्त डिलीट कमांड
        if views > 100 and likes == 0:
            youtube.videos().delete(id=video_id).execute()
            return f"🚨 **ALERT ({channel_name})** 🚨\n❌ क्वालिटी फेल! (Views: {views}, Likes: 0)।\nमैंने इस वीडियो को हमेशा के लिए **DELETE** कर दिया है।"
        
        health_msg = f"👁️ Views: {views} | ❤️ Likes: {likes}\n"
        strategy = CHANNEL_STRATEGIES.get(channel_name, "NONE")
        
        if strategy == "AMAZON" and AMAZON_TAG not in old_desc:
            query = urllib.parse.quote(title.replace('#shorts', '').strip())
            link = f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}"
            snippet['description'] = old_desc + f"\n\n🔥 गैजेट खरीदें: {link}"
            youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()
            add_top_comment(youtube, video_id, f"🔥 शानदार गैजेट यहाँ से खरीदें: {link}")
            return f"🎬 **{channel_name}**\n{health_msg}✅ अमेज़ॉन लिंक लग गया।"
            
        elif strategy == "GUMROAD" and GUMROAD_LINK not in old_desc:
            snippet['description'] = old_desc + f"\n\n🤖 100% ऑटोमेटेड AI सेटअप खरीदें: {GUMROAD_LINK}"
            youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()
            add_top_comment(youtube, video_id, f"🤖 हमारा ऑटोमेटेड AI सेटअप यहाँ से खरीदें: {GUMROAD_LINK}")
            return f"🎬 **{channel_name}**\n{health_msg}💰 गमरोड लिंक लग गया।"
            
        return f"🎬 **{channel_name}**\n{health_msg}⚡ सेफ है, कोई नया बदलाव ज़रूरी नहीं।"
            
    except Exception as e:
        return f"❌ **{channel_name}** में एरर: {e}"

def main():
    report = "🚀 **AI मास्टर मैनेजर: फुल 10-चैनल ऑडिट रिपोर्ट** 🚀\n\n"
    channels_found = 0
    
    for token_var in ALL_TOKENS:
        youtube = get_youtube_service(token_var)
        if youtube:
            try:
                channels = youtube.channels().list(part="snippet,contentDetails", mine=True, maxResults=50).execute().get('items', [])
                for ch in channels:
                    channels_found += 1
                    report += advanced_delete_manager(youtube, ch['snippet']['title'], ch['contentDetails']['relatedPlaylists']['uploads']) + "\n\n"
            except Exception:
                pass
                
    if channels_found == 0:
        report += "⚠️ कोई चैनल स्कैन नहीं हुआ। कृपया GitHub Secrets में टोकन चेक करें।"
        
    send_telegram(report)

if __name__ == "__main__":
    main()
