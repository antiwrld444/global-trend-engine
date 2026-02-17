import time
import json
import os
import sys

# Добавляем путь к корню
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collectors.news_collector import NewsCollector
from collectors.market_collector import MarketCollector
from analytics.scoring_engine import ScoringEngine

def main():
    print("🚀 GTOE Intelligence: Starting Autonomous Pipeline...")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_path = os.path.join(base_dir, 'config', 'api_keys.json')

    if not os.path.exists(config_path):
        print(f"❌ ERROR: Config not found at {config_path}")
        return

    with open(config_path, 'r') as f:
        keys = json.load(f)
    
    news_col = NewsCollector(api_key=keys.get('newsapi'))
    market_col = MarketCollector(api_key=keys.get('alphavantage'))
    scorer = ScoringEngine()
    
    print("✅ System initialized. Monitoring News and Markets.")

    while True:
        print(f"\n--- [{time.strftime('%H:%M:%S')}] Data Fetching Cycle ---")
        try:
            raw_data = []
            print("🔍 News...")
            raw_data.extend(news_col.fetch_latest())
            print("📈 Markets...")
            raw_data.extend(market_col.fetch_latest())
            
            trends = scorer.analyze(raw_data)
            
            for trend in trends:
                if trend.get('score', 0) >= 0.6:
                    print(f"🔥 ALERT: {trend['title']} | Source: {trend['source']}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("Done. Waiting 15 min...")
        time.sleep(900)

if __name__ == "__main__":
    main()
