import os
import json
import urllib.parse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

# GitHub Secrets से चाबियां लेना
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# आपका असली अमेज़ॉन अफिलिएट टैग
AMAZON_TAG = "girishbhut07-21"

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

def optimize_latest_video(youtube, channel_name):
    try:
        # चैनल की अपलोड प्लेलिस्ट खोजना
        request = youtube.channels().list(part="contentDetails", mine=True)
        response = request.execute()
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # सबसे नया वीडियो निकालना
        playlist_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=1
        )
        playlist_response = playlist_request.execute()
        
        if not playlist_response['items']:
            return f"⚠️ {channel_name} पर कोई वीडियो नहीं मिला।"

        video_id = playlist_response['items'][0]['snippet']['resourceId']['videoId']
        
        # वीडियो का पूरा डेटा लेना
        video_request = youtube.videos().list(part="snippet", id=video_id)
        video_response = video_request.execute()
        snippet = video_response['items'][0]['snippet']
        
        title = snippet.get('title', '')
        old_desc = snippet.get('description', '')
        
        # चेक करना कि लिंक पहले से तो नहीं है
        if AMAZON_TAG not in old_desc:
            # टाइटल से फालतू शब्द हटाकर सर्च कीवर्ड बनाना
            clean_title = title.replace('#shorts', '').replace('Best', '').replace('🤯', '').strip()
            search_query = urllib.parse.quote(clean_title)
            
            # आपका डायनामिक अमेज़ॉन लिंक बनाना
            dynamic_link = f"https://www.amazon.in/s?k={search_query}&tag={AMAZON_TAG}"
            
            affiliate_text = f"\n\n🔥 👉 यह शानदार गैजेट आउट ऑफ़ स्टॉक होने से पहले यहाँ से खरीदें!\n🔗 लिंक: {dynamic_link}"
            seo_tags = "\n#GBYoutuber #MysticUniverse #Trending #Viral #Gadgets"
            
            new_desc = old_desc + affiliate_text + seo_tags
            snippet['description'] = new_desc
            
            # यूट्यूब पर अपडेट करना
            update_request = youtube.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": snippet
                }
            )
            update_request.execute()
            return f"✅ **{channel_name}**: वीडियो '{title}' में आपका असली अमेज़ॉन लिंक लगा दिया गया है!"
        else:
            return f"⚡ **{channel_name}**: इस वीडियो में आपका अमेज़ॉन लिंक पहले से लगा हुआ है।"
            
    except Exception as e:
        return f"❌ **{channel_name}** में एरर: वीडियो अपडेट नहीं हो सका।"

def main():
    report = "🚀 **AI मैनेजर: अमेज़ॉन लिंक और SEO अपडेट रिपोर्ट**\n\n"
    tokens = ['YOUTUBE_REFRESH_TOKEN_1', 'YOUTUBE_REFRESH_TOKEN_2']
    
    for token_var in tokens:
        try:
            youtube = get_youtube_service(token_var)
            channel_req = youtube.channels().list(part="snippet", mine=True)
            channel_res = channel_req.execute()
            if channel_res['items']:
                channel_name = channel_res['items'][0]['snippet']['title']
                result = optimize_latest_video(youtube, channel_name)
                report += result + "\n\n"
        except Exception as e:
            report += f"❌ टोकन {token_var} कनेक्शन फेल।\n\n"
    
    send_telegram(report)

if __name__ == "__main__":
    main()
