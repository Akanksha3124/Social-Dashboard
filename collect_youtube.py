import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = "AIzaSyDkqDLEkNRXH0yH5D1eRo1qv0g2ZeRJROY"


def get_channel_videos(channel_id, max_results=50):
    youtube = build("youtube", "v3", developerKey=API_KEY)

    print(f"Fetching videos for channel: {channel_id}")
    search_response = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]
    print(f"Found {len(video_ids)} videos. Fetching stats...")

    stats_response = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids)
    ).execute()

    rows = []
    for item in stats_response["items"]:
        s = item["statistics"]
        snip = item["snippet"]
        rows.append({
            "video_id":     item["id"],
            "title":        snip["title"],
            "published_at": snip["publishedAt"],
            "description":  snip.get("description", "")[:200],
            "views":        int(s.get("viewCount", 0)),
            "likes":        int(s.get("likeCount", 0)),
            "comments":     int(s.get("commentCount", 0)),
        })

    df = pd.DataFrame(rows)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/youtube_data.csv", index=False)
    print(f"Saved {len(df)} videos to data/raw/youtube_data.csv")
    return df


if __name__ == "__main__":
    CHANNEL_ID = "UCAov2BBv1ZJav0c_yHEciAw"
    df = get_channel_videos(CHANNEL_ID)
    print(df.head())
