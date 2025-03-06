# dashboard.py - simplified version with native Streamlit components
import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px
from datetime import datetime
import time
from data_collector import collect_all_trending_data
from trend_analyzer import analyze_all_trending_data
from llm_insights import generate_insights
from config import REGIONS, CATEGORIES

# Set page configuration
st.set_page_config(
    page_title="YouTube Trend Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    
    h1, h2, h3 {
        color: #FF0000;
    }
    
    .stProgress .st-bo {
        background-color: #FF0000;
    }
</style>
""", unsafe_allow_html=True)

def load_available_dates():
    """Load available analysis dates"""
    analysis_files = glob.glob('data/analysis_*.json')
    dates = [f.split('analysis_')[1].split('.json')[0] for f in analysis_files]
    dates.sort(reverse=True)
    return dates

def run_dashboard():
    """Run the Streamlit dashboard"""
    
    st.title("YouTube Trend Analyzer")
    st.subheader("Discover what's trending and why")
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png", width=100)
        st.title("Navigation")
        
        selected_tab = st.radio(
            "Go to",
            ["Dashboard", "Collect New Data", "About"],
            key="navigation"
        )
    
    # Main content based on selected tab
    if selected_tab == "Dashboard":
        display_dashboard()
    elif selected_tab == "Collect New Data":
        collect_data_page()
    else:
        about_page()

def display_dashboard():
    """Display the main dashboard with visualizations"""
    
    # Get available dates
    dates = load_available_dates()
    
    if not dates:
        st.warning("No analysis data available. Please collect data first.")
        
        # Show sample visualization for first-time users
        st.subheader("Sample Preview (Collect data to see real trends)")
        
        # Sample data for preview
        sample_formats = {'Tutorial': 42, 'Reaction': 35, 'Listicle': 28, 'Review': 25, 'Challenge': 18}
        sample_df = pd.DataFrame({
            'Format': list(sample_formats.keys()),
            'Count': list(sample_formats.values())
        })
        
        # Sample plotly chart
        fig = px.bar(
            sample_df, 
            x='Count', 
            y='Format',
            orientation='h',
            color='Count',
            color_continuous_scale='Reds',
            title="Popular Video Formats (Sample)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("👆 This is a preview. Collect real data to see actual YouTube trends.")
        
        # CTA button
        st.button("Collect YouTube Trends Now", on_click=lambda: st.session_state.update({"navigation": "Collect New Data"}))
        
        return
    
    # Date selection with animation
    selected_date = st.selectbox(
        "Select Date", 
        dates,
        key="date_selector"
    )
    
    try:
        # Load analysis data
        with open(f'data/analysis_{selected_date}.json', 'r') as f:
            analysis_data = json.load(f)
        
        # Region and category selection
        col1, col2 = st.columns(2)
        
        with col1:
            available_regions = list(analysis_data.keys())
            selected_region = st.selectbox("Select Region", available_regions)
        
        with col2:
            available_categories = list(analysis_data[selected_region].keys())
            selected_category = st.selectbox("Select Category", available_categories)
        
        # Display analysis
        category_data = analysis_data[selected_region][selected_category]
        
        # Stats overview
        st.header("Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Videos",
                value=category_data['stats']['total_videos']
            )
        
        with col2:
            st.metric(
                label="Average Views",
                value=f"{category_data['stats']['avg_views']:,}"
            )
        
        with col3:
            st.metric(
                label="Average Likes",
                value=f"{category_data['stats']['avg_likes']:,}"
            )
        
        with col4:
            st.metric(
                label="Avg. Duration",
                value=f"{category_data['stats']['avg_duration'] // 60} min"
            )
        
        # Video formats visualization with Plotly
        st.header("Video Formats")
        
        formats_df = pd.DataFrame({
            'Format': list(category_data['video_formats'].keys()),
            'Count': list(category_data['video_formats'].values())
        }).sort_values('Count', ascending=False)
        
        # Create interactive bar chart
        fig = px.bar(
            formats_df, 
            x='Count', 
            y='Format',
            orientation='h',
            color='Count',
            color_continuous_scale='Reds',
            text='Count'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Number of Videos",
            yaxis_title="",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Duration distribution visualization
        st.header("Video Duration Distribution")
        
        duration_df = pd.DataFrame({
            'Duration': list(category_data['duration_distribution'].keys()),
            'Count': list(category_data['duration_distribution'].values())
        })
        
        # Create interactive duration chart
        fig = px.bar(
            duration_df,
            x='Duration',
            y='Count',
            color='Count',
            color_continuous_scale='Blues',
            text='Count'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="",
            yaxis_title="Number of Videos",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Common words and tags in two columns with interactive charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Common Words in Titles")
            
            words_df = pd.DataFrame({
                'Word': list(category_data['common_words'].keys()),
                'Count': list(category_data['common_words'].values())
            }).head(15).sort_values('Count', ascending=False)
            
            # Create treemap for words
            fig = px.treemap(
                words_df,
                path=['Word'],
                values='Count',
                color='Count',
                color_continuous_scale='Reds',
                hover_data=['Count']
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.header("Top Tags")
            
            tags_df = pd.DataFrame({
                'Tag': list(category_data['top_tags'].keys()),
                'Count': list(category_data['top_tags'].values())
            }).head(15).sort_values('Count', ascending=False)
            
            # Create horizontal bar chart for tags
            fig = px.bar(
                tags_df,
                x='Count',
                y='Tag',
                orientation='h',
                color='Count',
                color_continuous_scale='Greens',
                text='Count'
            )
            
            fig.update_layout(
                height=500,
                xaxis_title="Frequency",
                yaxis_title="",
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Channel analysis with bubble chart
        st.header("Top Channels")
        
        # Create channel dataframe
        channel_df = pd.DataFrame({
            'Channel': list(category_data['top_channels'].keys()),
            'Videos': list(category_data['top_channels'].values())
        }).head(10).sort_values('Videos', ascending=False)
        
        # Create bar chart for channels
        fig = px.bar(
            channel_df,
            x='Videos',
            y='Channel',
            orientation='h',
            color='Videos',
            color_continuous_scale='Viridis',
            text='Videos'
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="Number of Trending Videos",
            yaxis_title="",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Insights
        st.header("AI-Powered Insights")
        
        insights_file = f'data/insights/{selected_date}_{selected_region}_{selected_category.replace(" & ", "_")}.txt'
        
        if os.path.exists(insights_file):
            with open(insights_file, 'r') as f:
                insights = f.read()
            
            # Display insights in an expander
            with st.expander("View AI Insights", expanded=True):
                st.markdown(insights)
        else:
            # Button for generating insights
            if st.button("Generate AI Insights", key="generate_insights"):
                with st.spinner("Analyzing YouTube trends with AI..."):
                    # Generate insights
                    insights = generate_insights(analysis_data, selected_region, selected_category)
                    st.markdown(insights)
    
    except Exception as e:
        st.error(f"Error loading analysis data: {e}")
        st.warning("""
        Troubleshooting Tips:
        - Make sure you've collected data first
        - Check that your YouTube API key is valid
        - Verify the data directory exists and is writable
        - Try collecting data again
        """)

def collect_data_page():
    """Page for collecting new data"""
    
    st.header("Collect Trending Data")
    st.subheader("Fetch the latest trending videos from YouTube")
    
    # API key status check
    try:
        from config import YOUTUBE_API_KEY
        api_key_status = "✅ Configured" if YOUTUBE_API_KEY and YOUTUBE_API_KEY != "YOUR_YOUTUBE_API_KEY" else "❌ Not configured"
    except:
        api_key_status = "❌ Not configured"
    
    # Display API status
    st.info(f"API Key Status: {api_key_status}")
    
    # Collection options
    st.subheader("Collection Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_regions = st.multiselect(
            "Select Regions",
            ["US", "GB", "CA", "AU", "IN", "JP", "KR", "FR", "DE", "BR", "RU"],
            default=["US" , "IN"]
        )
    
    with col2:
        selected_categories = st.multiselect(
            "Select Categories",
            ["All", "Music", "Gaming", "Entertainment", "Comedy", "Science & Technology"],
            default=["All"]
        )
    
    # Collection button
    if st.button("Collect YouTube Trends Now", key="collect_button"):
        # Check if API key is configured
        if "❌" in api_key_status:
            st.error("YouTube API key is not configured. Please add your API key to config.py")
            return
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate collection process
        for i in range(101):
            # Update progress bar
            progress_bar.progress(i)
            
            # Update status text based on progress
            if i < 20:
                status_text.write("Connecting to YouTube API...")
            elif i < 40:
                status_text.write(f"Fetching trending videos for {selected_regions}...")
            elif i < 60:
                status_text.write("Processing video metadata...")
            elif i < 80:
                status_text.write("Analyzing content patterns...")
            else:
                status_text.write("Finalizing results...")
            
            # Actual data collection happens here
            if i == 1:
                try:
                    all_data = collect_all_trending_data()
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Error collecting data: {e}")
                    return
            
            # Actual analysis happens here
            if i == 60:
                try:
                    analysis = analyze_all_trending_data()
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Error analyzing data: {e}")
                    return
            
            time.sleep(0.05)  # Simulate processing time
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Show success message
        st.success("YouTube trending data has been successfully collected and analyzed!")
        
        # Show view results button
        if st.button("View Analysis Results"):
            st.session_state.navigation = "Dashboard"
            st.rerun()

def about_page():
    """About page with information about the project"""
    
    st.header("About YouTube Trend Analyzer")
    
    st.write("""
    YouTube Trend Analyzer is a powerful tool that helps content creators, marketers, and researchers 
    understand what types of videos are trending on YouTube. By analyzing metadata from trending videos, 
    it identifies patterns, popular formats, and content opportunities.
    """)
    
    # Features section
    st.subheader("Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📊 Trend Analysis", expanded=True):
            st.write("""
            - Identify popular video formats
            - Analyze optimal video durations
            - Discover common topics and keywords
            - Track top performing channels
            """)
        
        with st.expander("🌐 Multi-Region Support", expanded=True):
            st.write("""
            - Compare trends across different countries
            - Identify regional content preferences
            - Discover global trend patterns
            - Target specific geographic audiences
            """)
    
    with col2:
        with st.expander("🧠 AI-Powered Insights", expanded=True):
            st.write("""
            - Generate advanced content recommendations
            - Identify emerging trends early
            - Discover content gaps and opportunities
            - Get actionable strategic advice
            """)
        
        with st.expander("📈 Interactive Visualizations", expanded=True):
            st.write("""
            - Explore data through dynamic charts
            - Filter and sort trend information
            - Visualize patterns and relationships
            - Export insights for presentations
            """)
    
    # How it works section
    st.subheader("How It Works")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 1. Data Collection")
        st.write("""
        The system connects to the YouTube API and collects metadata from trending videos 
        across different categories and regions.
        """)
        
        st.markdown("#### 2. Pattern Analysis")
        st.write("""
        Sophisticated algorithms analyze the collected data to identify patterns in video 
        formats, durations, titles, and tags.
        """)
    
    with col2:
        st.markdown("#### 3. Visualization")
        st.write("""
        The analyzed data is transformed into interactive visualizations that make it 
        easy to understand complex trend patterns.
        """)
        
        st.markdown("#### 4. AI Insights")
        st.write("""
        Advanced AI models analyze the trends to generate strategic insights and content 
        recommendations tailored to your needs.
        """)
    
    # Technical details
    st.subheader("Technical Details")
    
    with st.expander("Technology Stack", expanded=True):
        st.write("""
        This application is built using:
        - **YouTube Data API** for trending video data collection
        - **Python** for data processing and analysis
        - **Streamlit** for the interactive dashboard
        - **Plotly** for dynamic data visualizations
        - **Pollinations AI** for generating content insights
        
        The YouTube Data API has a daily quota limit of 10,000 units. Each data collection 
        uses approximately 100 units, allowing for multiple collections per day.
        """)
    
    # Get started section
    st.subheader("Get Started")
    
    if st.button("Start Collecting Trends Now", key="start_collecting"):
        st.session_state.navigation = "Collect New Data"
        st.rerun()

if __name__ == "__main__":
    run_dashboard()