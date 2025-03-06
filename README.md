# YouTube Trend Analyzer

An AI-powered tool that analyzes trending YouTube content across multiple countries including US, India, UK, and more. Discover popular video formats, optimal durations, and emerging topics through interactive visualizations. Get strategic insights to inform your content strategy.

## Features

- **Trend Analysis**: Identify popular video formats, optimal durations, and trending topics
- **Multi-Region Support**: Compare trends across different countries (US, India, UK, Canada, etc.)
- **Interactive Visualizations**: Explore data through dynamic, interactive charts
- **AI-Powered Insights**: Generate strategic content recommendations using advanced AI

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YouTube-Trend-Analyzer.git
   cd YouTube-Trend-Analyzer
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `config.py` file with your API keys:
   ```python
   YouTube Data API key (required)
   YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
   
   Pollinations AI API URL (optional, for AI insights)
   POLLINATIONS_API_URL = "https://text.pollinations.ai/openai"
   
   Regions to track
   REGIONS = ['US', 'IN', 'GB', 'CA', 'AU', 'JP', 'KR', 'FR', 'DE', 'BR']
   
   Categories to track
   CATEGORIES = {
       '0': 'All',
       '10': 'Music',
       '20': 'Gaming',
       '23': 'Comedy',
       '24': 'Entertainment',
       '28': 'Science & Technology'
   }
   
   # Maximum results per API call
   MAX_RESULTS = 50
   ```

4. Create required directories:
   ```bash
   mkdir -p data/insights
   ```

## Usage

1. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

2. To collect data, analyze trends, and generate insights via command line:
   ```bash
   python main.py --collect --analyze --insights
   ```

3. For help with command line options:
   ```bash
   python main.py --help
   ```

## How It Works

1. Data Collection: The system connects to the YouTube API and collects metadata from trending videos across different categories and regions.

2. Pattern Analysis: Sophisticated algorithms analyze the collected data to identify patterns in video formats, durations, titles, and tags.

3. Visualization: The analyzed data is transformed into interactive visualizations that make it easy to understand complex trend patterns.

4. AI Insights: Advanced AI models analyze the trends to generate strategic insights and content recommendations.

## Project Structure

```
YouTube-Trend-Analyzer/
├── config.py               # Configuration and API keys
├── dashboard.py            # Streamlit dashboard interface
├── data_collector.py       # YouTube API interaction
├── trend_analyzer.py       # Trend analysis logic
├── llm_insights.py         # AI-powered insights
├── main.py                 # Command-line interface
├── requirements.txt        # Project dependencies
└── data/                   # Data storage directory
    └── insights/           # Generated AI insights
```

## Technical Details

This application is built using:
- **YouTube Data API** for trending video data collection
- **Python** for data processing and analysis
- **Streamlit** for the interactive dashboard
- **Plotly** for dynamic data visualizations
- **Pollinations AI** for generating content insights

The YouTube Data API has a daily quota limit of 10,000 units. Each data collection uses approximately 100 units, allowing for multiple collections per day.

## License

This project is licensed under the MIT License.
