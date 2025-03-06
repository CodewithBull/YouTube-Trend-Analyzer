# trend_analyzer.py
# Functions to analyze trending video data

import pandas as pd
import numpy as np
import re
from collections import Counter
import json
from datetime import datetime
import os
from config import CATEGORIES, REGIONS

def extract_title_patterns(titles):
    """Extract common patterns from video titles"""
    
    patterns = {
        'question': sum(1 for t in titles if re.search(r'\?|\bwhy\b|\bhow\b|\bwhat\b', t, re.I)),
        'all_caps': sum(1 for t in titles if t.isupper()),
        'emoji': sum(1 for t in titles if any(c for c in t if ord(c) > 0x1F000)),
        'number_in_title': sum(1 for t in titles if re.search(r'\d+', t)),
        'exclamation': sum(1 for t in titles if '!' in t),
        'parentheses': sum(1 for t in titles if '(' in t and ')' in t),
        'brackets': sum(1 for t in titles if '[' in t and ']' in t),
    }
    
    # Video formats
    formats = {
        'listicle': sum(1 for t in titles if re.search(r'^\d+\s|\s\d+\s|top\s\d+', t, re.I)),
        'reaction': sum(1 for t in titles if re.search(r'reacting|reaction', t, re.I)),
        'tutorial': sum(1 for t in titles if re.search(r'how to|tutorial|guide', t, re.I)),
        'review': sum(1 for t in titles if re.search(r'review|unboxing', t, re.I)),
        'challenge': sum(1 for t in titles if re.search(r'challenge', t, re.I)),
        'day_in_life': sum(1 for t in titles if re.search(r'day in|day of|day in the life', t, re.I)),
        'asmr': sum(1 for t in titles if re.search(r'asmr', t, re.I)),
        'shorts': sum(1 for t in titles if re.search(r'#shorts|shorts', t, re.I)),
        'live': sum(1 for t in titles if re.search(r'live|stream', t, re.I)),
        'podcast': sum(1 for t in titles if re.search(r'podcast|episode', t, re.I)),
    }
    
    return {"patterns": patterns, "formats": formats}

def extract_common_words(titles, min_length=4, stop_words=None):
    """Extract common words from titles after removing stop words"""
    if stop_words is None:
        stop_words = {'the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were', 'be', 'this', 'that', 'my', 'your', 'our', 'their'}
    
    # Combine titles and lowercase
    text = ' '.join(titles).lower()
    
    # Remove special characters and split into words
    words = re.findall(r'\b[a-z]{' + str(min_length) + r',}\b', text)
    
    # Filter out stop words
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count occurrences
    word_counts = Counter(filtered_words)
    
    return dict(word_counts.most_common(30))

def analyze_trending_videos(df):
    """Analyze trending videos to extract insights"""
    
    if df.empty:
        return {"error": "No data to analyze"}
    
    # Basic stats
    stats = {
        'total_videos': len(df),
        'avg_views': int(df['view_count'].mean()),
        'avg_likes': int(df['like_count'].mean()),
        'avg_comments': int(df['comment_count'].mean()),
        'avg_duration': int(df['duration_seconds'].mean()),
    }
    
    # Duration distribution
    duration_bins = [0, 60, 300, 600, 1200, 1800, 3600, float('inf')]
    duration_labels = ['<1 min', '1-5 min', '5-10 min', '10-20 min', '20-30 min', '30-60 min', '>60 min']
    
    duration_counts = pd.cut(df['duration_seconds'], bins=duration_bins, labels=duration_labels)
    duration_distribution = duration_counts.value_counts().to_dict()
    
    # Extract title patterns
    titles = df['title'].tolist()
    title_analysis = extract_title_patterns(titles)
    
    # Extract common words
    common_words = extract_common_words(titles)
    
    # Extract common tags
    all_tags = [tag for tags_list in df['tags'] for tag in tags_list if tags_list]
    tag_counts = Counter(all_tags).most_common(20)
    
    # Channel analysis
    channel_counts = df['channel_title'].value_counts().head(10).to_dict()
    
    return {
        'stats': stats,
        'duration_distribution': duration_distribution,
        'title_patterns': title_analysis['patterns'],
        'video_formats': title_analysis['formats'],
        'common_words': common_words,
        'top_tags': dict(tag_counts),
        'top_channels': channel_counts
    }

def analyze_all_trending_data(date=None):
    """Analyze all trending data for a specific date"""
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Load combined data
        with open(f'data/all_trending_{date}.json', 'r') as f:
            all_data = json.load(f)
        
        analysis_results = {}
        
        for region, region_data in all_data.items():
            region_analysis = {}
            
            for category, videos in region_data.items():
                df = pd.DataFrame(videos)
                if not df.empty:
                    region_analysis[category] = analyze_trending_videos(df)
            
            analysis_results[region] = region_analysis
        
        # Save analysis results
        with open(f'data/analysis_{date}.json', 'w') as f:
            json.dump(analysis_results, f)
        
        return analysis_results
    
    except FileNotFoundError:
        print(f"No data found for {date}")
        return None