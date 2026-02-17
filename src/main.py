import time
import json
import os
import sys

# Добавляем путь к корню проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collectors.news_collector import NewsCollector
from collectors.market_collector import MarketCollector
from analytics.scoring_engine import ScoringEngine

def main():
    print("🚀 GTOE Roadmap 4.0: Starting Autonomous Cycle...")
    
    # Определение базовой директории
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_path = os.path.join(base_dir, 'config', 'api_keys.json')

    # Проверка наличия основного конфига
    if not os.path.exists(config_path):
        print(f"❌ ERROR: Configuration file not found at {config_path}")
        return

    # Load config
    with open(config_path, 'r') as f:
        keys = json.load(f)
    
    # Initialize components
    news_collector = NewsCollector(api_key=keys.get('newsapi'))
    market_collector = MarketCollector(api_key=keys.get('alphavantage'))
    scorer = ScoringEngine()
    
    print("✅ System initialized. Monitoring News and Markets...")

    while True:
        print(f"\n--- [{time.strftime('%H:%M:%S')}] Fetching New Data ---")
        try:
            raw_data = []
            
            print("🔍 NewsAPI: Polling headlines...")
            raw_data.extend(news_collector.fetch_latest())
            
            print("📈 AlphaVantage: Syncing markets...")
            raw_data.extend(market_collector.fetch_latest())
            
            trends = scorer.analyze(raw_data)
            
            for trend in trends:
                if trend.get('score', 0) >= 0.5:
                    print(f"✅ Found: {trend['title']} | Source: {trend['source']}")
                    
        except Exception as e:
            print(f"❌ ERROR during cycle: {str(e)}")
        
        print("Cycle complete. Next check in 15 minutes...")
        time.sleep(900)

if __name__ == "__main__":
    main()
