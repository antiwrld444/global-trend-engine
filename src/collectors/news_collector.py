import feedparser
import sys
import os
# Добавляем путь к БД
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager

class NewsCollector:
    def __init__(self):
        self.db = DBManager()
        self.feeds = {
            "Technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            "Fashion": "https://www.vogue.com/feed/rss"
        }

    def run(self):
        print("--- Запуск сбора реальных данных ---")
        for category, url in self.feeds.items():
            print(f"Обработка категории: {category}")
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # Берем последние 5 новостей для MVP
                # Здесь будет sentiment analysis, пока ставим 0.5
                self.db.save_trend(entry.title, entry.link, 0.5, category)
                print(f"Сохранено: {entry.title[:50]}...")

if __name__ == "__main__":
    collector = NewsCollector()
    collector.run()
