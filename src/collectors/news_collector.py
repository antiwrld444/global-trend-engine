import feedparser
import sys
import os
# Добавляем пути к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager
from analytics.nlp_processor import NLPProcessor

class NewsCollector:
    def __init__(self):
        self.db = DBManager()
        self.nlp = NLPProcessor()
        self.feeds = {
            "Technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            "Fashion": "https://www.vogue.com/feed/rss"
        }

    def run(self):
        print("--- Запуск сбора и NLP-анализа реальных данных ---")
        for category, url in self.feeds.items():
            print(f"Обработка категории: {category}")
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: 
                # Реальный анализ настроения заголовка
                sentiment_score = self.nlp.analyze_text(entry.title)
                self.db.save_trend(entry.title, entry.link, sentiment_score, category)
                print(f"Сохранено: {entry.title[:50]}... [Score: {sentiment_score:.2f}]")

if __name__ == "__main__":
    collector = NewsCollector()
    collector.run()
