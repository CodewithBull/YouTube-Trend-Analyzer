# data_collector.py
# Functions to interact with YouTube API and collect data

import os
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
import time
import json
from config import YOUTUBE_API_KEY, CATEGORIES, REGIONS, MAX_RESULTS

# Initialize YouTube API client
def get_youtube_client():
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def parse_duration(duration_str):
    """Convert ISO 8601 duration to seconds"""
    try:
        return int(isodate.parse_duration(duration_str).total_seconds())
    except:
        return 0

def get_trending_videos(youtube, region_code='US', category_id=None, max_results=MAX_RESULTS):
    """Fetch trending videos with optional category filter"""
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=max_results,
            videoCategoryId=category_id if category_id else ""
        )
        
        response = request.execute()
        
        # Extract relevant information
        videos = []
        for item in response.get('items', []):
            video = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'channel_title': item['snippet']['channelTitle'],
                'channel_id': item['snippet']['channelId'],
                'publish_date': item['snippet']['publishedAt'],
                'tags': item['snippet'].get('tags', []),
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'like_count': int(item['statistics'].get('likeCount', 0)),
                'comment_count': int(item['statistics'].get('commentCount', 0)),
                'description': item['snippet']['description'],
                'category_id': item['snippet']['categoryId'],
                'duration': item['contentDetails']['duration'],
                'thumbnail_url': item['snippet']['thumbnails']['high']['url']
            }
            videos.append(video)
        
        df = pd.DataFrame(videos)
        if not df.empty:
            df['duration_seconds'] = df['duration'].apply(parse_duration)
        
        return df
    
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return pd.DataFrame()

def collect_all_trending_data():
    """Collect trending data for all configured regions and categories"""
    
    youtube = get_youtube_client()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    all_trends = {}
    
    for region in REGIONS:
        region_trends = {}
        
        for cat_id, cat_name in CATEGORIES.items():
            print(f"Collecting {cat_name} trends for {region}...")
            
            # Use empty string for "All" category
            df = get_trending_videos(youtube, region_code=region, category_id=cat_id if cat_id != '0' else "")
            
            if not df.empty:
                # Save raw data
                file_name = f'data/raw_{region}_{cat_name.lower().replace(" & ", "_")}_{today}.csv'
                df.to_csv(file_name, index=False)
                print(f"Saved {len(df)} videos to {file_name}")
                
                region_trends[cat_name] = df.to_dict('records')
            else:
                print(f"No data returned for {cat_name} in {region}")
            
            # Respect YouTube API quotas with a small delay
            time.sleep(1)
        
        all_trends[region] = region_trends
    
    # Save combined data
    with open(f'data/all_trending_{today}.json', 'w') as f:
        json.dump(all_trends, f)
    
    return all_trends