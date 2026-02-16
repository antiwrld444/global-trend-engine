import time
from collectors.news_collector import NewsCollector
from analytics.scoring_engine import ScoringEngine
from utils.reporter import TelegramReporter
import json
import os

def main():
    print("GTOE Roadmap 4.0: Starting Autonomous Cycle...")
    
    # Load config
    with open('config/api_keys.json', 'r') as f:
        keys = json.load(f)
    
    # Initialize components
    collector = NewsCollector(api_key=keys['newsapi'])
    scorer = ScoringEngine()
    
    # Optional: Initialize reporter if token exists
    reporter = None
    if os.path.exists('config/telegram_config.json'):
        with open('config/telegram_config.json', 'r') as f:
            tg_config = json.load(f)
            reporter = TelegramReporter(tg_config['token'], tg_config['chat_id'])

    while True:
        print("\n--- Fetching New Trends ---")
        raw_data = collector.fetch_latest()
        trends = scorer.analyze(raw_data)
        
        for trend in trends:
            if trend['score'] > 0.8:  # High priority threshold
                alert = f"🚨 <b>High Priority Trend Detected!</b>\n\n"                         f"<b>Topic:</b> {trend['title']}\n"                         f"<b>Score:</b> {trend['score']}\n"                         f"<b>Source:</b> {trend['source']}\n"                         f"<b>Link:</b> {trend['url']}"
                
                print(f"[ALERT] {trend['title']}")
                if reporter:
                    reporter.send_alert(alert)
        
        print("Cycle complete. Sleeping for 1 hour...")
        time.sleep(3600)

if __name__ == "__main__":
    main()
