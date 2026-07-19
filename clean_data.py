import os
import pandas as pd
from sqlalchemy import create_engine

os.makedirs("data/cleaned", exist_ok=True)


def clean_youtube():
    path = "data/raw/youtube_data.csv"
    if not os.path.exists(path):
        print("YouTube raw data not found. Run collect_youtube.py first.")
        return None

    df = pd.read_csv(path)
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["hour"]         = df["published_at"].dt.hour
    df["day_of_week"]  = df["published_at"].dt.day_name()
    df["month"]        = df["published_at"].dt.month_name()
    df["engagement_rate"] = (
        (df["likes"] + df["comments"]) / df["views"].replace(0, 1)
    ).round(4)
    df["like_ratio"]   = (df["likes"] / df["views"].replace(0, 1)).round(4)

    df.to_csv("data/cleaned/youtube_clean.csv", index=False)
    print(f"YouTube: cleaned {len(df)} rows → data/cleaned/youtube_clean.csv")
    return df


def save_to_database(yt_df):
    engine = create_engine("sqlite:///data/engagement.db")
    if yt_df is not None:
        yt_df.to_sql("youtube", engine, if_exists="replace", index=False)
        print("YouTube data saved to SQLite database.")
    print("Database ready at: data/engagement.db")


if __name__ == "__main__":
    yt = clean_youtube()
    save_to_database(yt)
