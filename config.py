# config.py
# Store your API keys and configuration settings

# YouTube Data API key
YOUTUBE_API_KEY = "AIzaSyBfn5vJpNM_-xtprmXTBVz_YL-ldE04lyM"

# Pollinations AI API URL
POLLINATIONS_API_URL = "https://text.pollinations.ai/openai"  # Using OpenAI-compatible endpoint

# Categories to track
CATEGORIES = {
    '0': 'All',
    '10': 'Music',
    '20': 'Gaming',
    '23': 'Comedy',
    '24': 'Entertainment',
    '28': 'Science & Technology'
}

# Regions to track (ISO 3166-1 alpha-2 country codes)
REGIONS = ['US', 'IN', 'GB', 'CA', 'AU', 'JP', 'KR', 'FR', 'DE', 'BR']  

# Maximum results per API call
MAX_RESULTS = 50  # Maximum allowed is 50