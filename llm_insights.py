# llm_insights.py
# Generate AI insights from trend analysis using Pollinations AI

import json
import os
import requests
from datetime import datetime
from config import POLLINATIONS_API_URL

def generate_basic_insights(category_data):
    """Generate basic insights without using an API (fallback method)"""
    
    # Calculate the most popular format
    formats = category_data['video_formats']
    most_popular_format = max(formats.items(), key=lambda x: x[1])[0]
    
    # Calculate most common duration
    durations = category_data['duration_distribution']
    most_common_duration = max(durations.items(), key=lambda x: x[1])[0]
    
    # Generate basic insights
    insights = f"""
    # YouTube Trend Analysis
    
    ## Video Format Trends
    The most popular video format is **{most_popular_format}** with {formats[most_popular_format]} videos.
    
    ## Duration Trends
    Most trending videos are **{most_common_duration}** in length.
    
    ## Common Topics
    Common words in titles include: {', '.join(list(category_data['common_words'].keys())[:5])}.
    
    ## Popular Tags
    Top tags include: {', '.join(list(category_data['top_tags'].keys())[:5])}.
    """
    
    return insights

def generate_insights(analysis_data, region, category):
    """Generate insights from analysis data using Pollinations AI"""
    
    try:
        # Extract relevant data
        category_data = analysis_data[region][category]
        
        # Create prompt for the API
        prompt = f"""
        Analyze these YouTube trends for {category} videos in {region} and identify:
        1. Emerging video formats or styles
        2. Rising topics or themes
        3. Content opportunities (gaps in the market)
        4. Unusual patterns or outliers
        
        Trend data:
        - Total videos analyzed: {category_data['stats']['total_videos']}
        - Average views: {category_data['stats']['avg_views']}
        - Average duration: {category_data['stats']['avg_duration']} seconds
        
        Popular video formats:
        {json.dumps(category_data['video_formats'], indent=2)}
        
        Common title patterns:
        {json.dumps(category_data['title_patterns'], indent=2)}
        
        Most common words in titles:
        {json.dumps(category_data['common_words'], indent=2)}
        
        Top tags:
        {json.dumps(category_data['top_tags'], indent=2)}
        
        Duration distribution:
        {json.dumps(category_data['duration_distribution'], indent=2)}
        
        Top channels:
        {json.dumps(category_data['top_channels'], indent=2)}
        
        Provide your analysis in a structured format with clear sections for each category.
        Focus on actionable insights for content creators.
        """
        
        # System message to guide the AI
        system_message = "You are a YouTube trend analysis expert."
        
        # Prepare the request to Pollinations AI
        payload = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Make the POST request to Pollinations AI
        response = requests.post(POLLINATIONS_API_URL, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            
            # Extract the generated text (adjust based on actual API response format)
            if "choices" in result and len(result["choices"]) > 0:
                insights = result["choices"][0]["message"]["content"]
            else:
                insights = result.get("content", "No insights generated")
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return generate_basic_insights(category_data)
        
        # Save insights
        insights_dir = 'data/insights'
        if not os.path.exists(insights_dir):
            os.makedirs(insights_dir)
            
        date = datetime.now().strftime('%Y-%m-%d')
        with open(f'{insights_dir}/{date}_{region}_{category.replace(" & ", "_")}.txt', 'w') as f:
            f.write(insights)
        
        return insights
    
    except Exception as e:
        print(f"Error generating insights: {e}")
        print("Falling back to basic insights generation...")
        return generate_basic_insights(category_data)

def generate_all_insights(analysis_data):
    """Generate insights for all regions and categories"""
    
    all_insights = {}
    
    for region in analysis_data.keys():
        region_insights = {}
        
        for category in analysis_data[region].keys():
            print(f"Generating insights for {category} in {region}...")
            insights = generate_insights(analysis_data, region, category)
            region_insights[category] = insights
        
        all_insights[region] = region_insights
    
    return all_insights