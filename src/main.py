import time
import json
import os
import sys

# Добавляем путь к корню проекта, чтобы импорты работали везде
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collectors.news_collector import NewsCollector
from analytics.scoring_engine import ScoringEngine
from utils.reporter import TelegramReporter

def main():
    print("🚀 GTOE Roadmap 4.0: Starting Autonomous Cycle...")
    
    # Определение базовой директории (корень проекта)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_path = os.path.join(base_dir, 'config', 'api_keys.json')
    tg_config_path = os.path.join(base_dir, 'config', 'telegram_config.json')

    # Проверка наличия основного конфига
    if not os.path.exists(config_path):
        print(f"❌ ERROR: Configuration file not found at {config_path}")
        print("Please rename 'config/api_keys.json.example' to 'config/api_keys.json' and fill it.")
        return

    # Load config
    with open(config_path, 'r') as f:
        keys = json.load(f)
    
    # Initialize components
    collector = NewsCollector(api_key=keys.get('newsapi'))
    scorer = ScoringEngine()
    
    # Optional: Initialize reporter if token exists
    reporter = None
    if os.path.exists(tg_config_path):
        with open(tg_config_path, 'r') as f:
            tg_config = json.load(f)
            if tg_config.get('token'):
                reporter = TelegramReporter(tg_config['token'], tg_config['chat_id'])
                print("✅ Telegram Reporter initialized.")
            else:
                print("⚠️ Telegram token is empty. Alerts disabled.")
    else:
        print("ℹ️ telegram_config.json not found. Creating a template...")
        with open(tg_config_path, 'w') as f:
            json.dump({"token": "", "chat_id": ""}, f, indent=4)

    while True:
        print(f"\n--- [{time.strftime('%H:%M:%S')}] Fetching New Trends ---")
        try:
            raw_data = collector.fetch_latest()
            trends = scorer.analyze(raw_data)
            
            for trend in trends:
                if trend.get('score', 0) > 0.8:  # High priority threshold
                    alert = f"🚨 <b>High Priority Trend Detected!</b>\n\n"                             f"<b>Topic:</b> {trend['title']}\n"                             f"<b>Score:</b> {trend['score']}\n"                             f"<b>Source:</b> {trend['source']}\n"                             f"<b>Link:</b> {trend['url']}"
                    
                    print(f"🔥 ALERT: {trend['title']}")
                    if reporter:
                        reporter.send_alert(alert)
        except Exception as e:
            print(f"❌ ERROR during cycle: {str(e)}")
        
        print("Cycle complete. Next check in 15 minutes...")
        time.sleep(900)

if __name__ == "__main__":
    main()
