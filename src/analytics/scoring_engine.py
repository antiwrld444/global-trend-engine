import sqlite3
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager
from utils.logger import setup_logger

logger = setup_logger("scoring_engine")

class ScoringEngine:
    def __init__(self):
        # Базовая директория для путей
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.db_path = os.path.join(self.base_dir, 'data', 'trends.db')

    def analyze(self, raw_data):
        """
        Метод для интеграции с Roadmap 4.0: анализирует пачку входящих данных (raw_data).
        Каждый элемент в raw_data: {'title': ..., 'url': ..., 'source': ...}
        """
        scored_trends = []
        for item in raw_data:
            # Базовый скоринг для новых данных (пока не в БД)
            # В идеале здесь должен быть NLP анализ, но для работы пайплайна возвращаем структуру
            score = 0.5 # Значение по умолчанию
            scored_trends.append({
                "title": item['title'],
                "url": item['url'],
                "source": item['source'],
                "score": score
            })
        return scored_trends

    def calculate_opportunity_scores(self):
        """Расчет скоринга для данных, уже сохраненных в БД."""
        logger.info("--- Запуск BI-скоринга трендов ---")
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM trends", conn)
            conn.close()
            
            if df.empty:
                return pd.DataFrame()

            max_mentions = df['mentions_count'].max() if df['mentions_count'].max() > 0 else 1
            df['opportunity_score'] = (df['sentiment'] * 0.4) +                                      ((df['mentions_count'] / max_mentions) * 0.3) +                                      (df['source_weight'] * 0.3)
            
            return df.sort_values(by='opportunity_score', ascending=False)
        except Exception as e:
            logger.error(f"Ошибка при расчете скоринга: {e}")
            return pd.DataFrame()
