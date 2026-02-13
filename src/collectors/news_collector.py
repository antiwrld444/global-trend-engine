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
    def __init__(self):
        self.db = DBManager()
        self.nlp = NLPProcessor()
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.feeds = {
            "Technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            "Fashion": "https://www.vogue.com/feed/rss",
            "TechCrunch": "https://techcrunch.com/feed/",
            "Wired": "https://www.wired.com/feed/rss",
            "BBC_Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
            "TheVerge": "https://www.theverge.com/rss/index.xml"
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

    def run(self):
        logger.info("--- Запуск сбора и NLP-анализа данных ---")
        
        # 1. RSS Feeds
        for category, url in self.feeds.items():
            logger.info(f"Обработка RSS категории: {category}")
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: 
                    sentiment_score = self.nlp.analyze_text(entry.title)
                    self.db.save_trend(entry.title, entry.link, sentiment_score, category)
                    logger.info(f"RSS Сохранено: {entry.title[:50]}... [Score: {sentiment_score:.2f}]")
            except Exception as e:
                logger.error(f"Ошибка при обработке RSS {category}: {e}")

        # 2. NewsAPI (если есть ключ)
        try:
            articles = self.fetch_from_news_api()
            for art in articles:
                sentiment_score = self.nlp.analyze_text(art["title"])
                self.db.save_trend(art["title"], art["url"], sentiment_score, "Global")
                logger.info(f"NewsAPI Сохранено: {art['title'][:50]}... [Score: {sentiment_score:.2f}]")
        except Exception as e:
            logger.error(f"Ошибка при обработке NewsAPI: {e}")

if __name__ == "__main__":
    collector = NewsCollector()
    collector.run()
