# main.py - updated version
# Main execution script for YouTube Trend Analyzer

import argparse
import os
import subprocess
import sys
from datetime import datetime
from data_collector import collect_all_trending_data
from trend_analyzer import analyze_all_trending_data
from llm_insights import generate_all_insights

def run_dashboard_properly():
    """Run the dashboard using streamlit run command"""
    print("Starting dashboard...")
    # Use subprocess to run streamlit properly
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])

def main():
    """Main function to run the YouTube Trend Analyzer"""
    
    parser = argparse.ArgumentParser(description='YouTube Trend Analyzer')
    parser.add_argument('--collect', action='store_true', help='Collect trending data')
    parser.add_argument('--analyze', action='store_true', help='Analyze collected data')
    parser.add_argument('--insights', action='store_true', help='Generate AI insights')
    parser.add_argument('--dashboard', action='store_true', help='Run the dashboard')
    parser.add_argument('--date', type=str, help='Date to analyze (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help and run dashboard
    if not any(vars(args).values()):
        parser.print_help()
        print("\nRunning dashboard by default...\n")
        run_dashboard_properly()
        return
    
    # Collect data
    if args.collect:
        print("Collecting trending data...")
        collect_all_trending_data()
        print("Data collection complete!")
    
    # Analyze data
    if args.analyze:
        print("Analyzing trending data...")
        date = args.date or datetime.now().strftime('%Y-%m-%d')
        analysis = analyze_all_trending_data(date)
        
        if analysis:
            print(f"Analysis complete! Results saved to data/analysis_{date}.json")
        else:
            print(f"No data found for {date}")
    
    # Generate insights
    if args.insights:
        print("Generating AI insights with Pollinations AI...")
        date = args.date or datetime.now().strftime('%Y-%m-%d')
        
        try:
            with open(f'data/analysis_{date}.json', 'r') as f:
                import json
                analysis_data = json.load(f)
                
                insights = generate_all_insights(analysis_data)
                print("Insights generation complete!")
        
        except FileNotFoundError:
            print(f"No analysis data found for {date}")
    
    # Run dashboard
    if args.dashboard:
        run_dashboard_properly()

if __name__ == "__main__":
    main()