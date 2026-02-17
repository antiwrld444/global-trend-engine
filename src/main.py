import time
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collectors.news_collector import NewsCollector
from collectors.market_collector import MarketCollector
from collectors.deep_search import DeepSearchCollector
from analytics.scoring_engine import ScoringEngine

def main():
    print("🚀 GTOE Intelligence: Starting Autonomous Pipeline (Multi-Source)...")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_path = os.path.join(base_dir, 'config', 'api_keys.json')

    if not os.path.exists(config_path):
        print(f"❌ ERROR: Configuration file not found at {config_path}")
        return

    with open(config_path, 'r') as f:
        keys = json.load(f)
    
    news_collector = NewsCollector(api_key=keys.get('newsapi'))
    market_collector = MarketCollector(api_key=keys.get('alphavantage'))
    deep_collector = DeepSearchCollector(api_key=keys.get('tavily'))
    scorer = ScoringEngine()
    
    print("✅ System initialized. Sources: NewsAPI, AlphaVantage, Tavily Deep Search.")

    while True:
        print(f"\n--- [{time.strftime('%H:%M:%S')}] Global Intelligence Cycle ---")
        try:
            raw_data = []
            
            print("🔍 NewsAPI: Polling headlines...")
            raw_data.extend(news_collector.fetch_latest())
            
            print("📈 AlphaVantage: Syncing markets...")
            raw_data.extend(market_collector.fetch_latest())
            
            print("🧠 Tavily: Executing Deep Search for emerging trends...")
            raw_data.extend(deep_collector.fetch_latest())
            
            trends = scorer.analyze(raw_data)
            
            for trend in trends:
                if trend.get('score', 0) >= 0.7:
                    print(f"🔥 HOT SIGNAL: {trend['title']} | Source: {trend['source']}")
                    
        except Exception as e:
            print(f"❌ ERROR during cycle: {str(e)}")
        
        print("Cycle complete. Re-sync in 15 minutes...")
        time.sleep(900)

if __name__ == "__main__":
    main()
