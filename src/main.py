import time
import json
import os
import sys

# Добавляем путь к корню проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collectors.news_collector import NewsCollector
from analytics.scoring_engine import ScoringEngine

def main():
    print("🚀 GTOE Roadmap 4.0: Starting Autonomous Cycle (Lite Mode)...")
    
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
    collector = NewsCollector(api_key=keys.get('newsapi'))
    scorer = ScoringEngine()
    
    print("✅ System initialized. Monitoring global trends...")

    while True:
        print(f"\n--- [{time.strftime('%H:%M:%S')}] Fetching New Trends ---")
        try:
            raw_data = collector.fetch_latest()
            trends = scorer.analyze(raw_data)
            
            for trend in trends:
                if trend.get('score', 0) > 0.8:
                    print(f"🔥 HIGH PRIORITY: {trend['title']} ({trend['score']})")
                    print(f"🔗 Source: {trend['source']} | URL: {trend['url']}")
        except Exception as e:
            print(f"❌ ERROR during cycle: {str(e)}")
        
        print("Cycle complete. Next check in 15 minutes...")
        time.sleep(900)

if __name__ == "__main__":
    main()
