import feedparser
import sys
import os
import requests
# Добавляем пути к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager
from analytics.nlp_processor import NLPProcessor
from utils.logger import setup_logger

logger = setup_logger("news_collector")

class NewsCollector:
    def __init__(self, api_key=None):
        self.db = DBManager()
        self.nlp = NLPProcessor()
        # Приоритет: переданный ключ > переменная окружения
        self.news_api_key = api_key or os.getenv("NEWS_API_KEY")
        self.feeds = {
            "Technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            "Fashion": "https://www.vogue.com/feed/rss",
            "TechCrunch": "https://techcrunch.com/feed/",
            "Wired": "https://www.wired.com/feed/rss",
            "BBC_Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
            "TheVerge": "https://www.theverge.com/rss/index.xml"
        }
        self.source_weights = {
            "Wired": 1.5,
            "TechCrunch": 1.4,
            "TheVerge": 1.3,
            "Technology": 1.2, 
            "Business": 1.1,
            "Global": 1.0
        }

    def fetch_from_news_api(self):
        if not self.news_api_key:
            logger.info("NewsAPI Key не найден, пропускаем...")
            return []
        
        logger.info("--- Сбор данных через NewsAPI ---")
        url = f"https://newsapi.org/v2/everything?q=trend+market&apiKey={self.news_api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            return data.get("articles", [])[:10]
        except Exception as e:
            logger.error(f"Ошибка NewsAPI: {e}")
            return []

    def fetch_latest(self):
        # Метод для внешнего вызова из main.py (Roadmap 4.0)
        logger.info("--- Запуск разового цикла сбора данных ---")
        results = []
        
        # RSS
        for category, url in self.feeds.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:
                    results.append({"title": entry.title, "url": entry.link, "source": category})
            except: pass
            
        # NewsAPI
        articles = self.fetch_from_news_api()
        for art in articles:
            results.append({"title": art["title"], "url": art["url"], "source": "NewsAPI"})
            
        return results

    def run(self):
        # Старый метод для обратной совместимости
        logger.info("--- Запуск сбора и NLP-анализа данных (Legacy Run) ---")
        data = self.fetch_latest()
        source_weight = 1.0
        for item in data:
            sentiment_score = self.nlp.analyze_text(item["title"])
            keywords = self.nlp.extract_keywords(item["title"])
            entities = self.nlp.extract_entities(item["title"])
            self.db.save_trend(item["title"], item["url"], sentiment_score, item["source"], keywords, source_weight, entities)
            logger.info(f"Сохранено: {item['title'][:50]}...")

if __name__ == "__main__":
    collector = NewsCollector()
    collector.run()
