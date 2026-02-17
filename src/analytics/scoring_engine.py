import sqlite3
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import setup_logger

logger = setup_logger("scoring_engine")

class ScoringEngine:
    def __init__(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.db_path = os.path.join(base_dir, 'data', 'trends.db')

    def analyze(self, raw_data):
        """Анализ входящих данных для основного цикла main.py."""
        scored_trends = []
        for item in raw_data:
            title_lower = item.get('title', '').lower()
            score = 0.5
            
            # Повышаем score за триггерные слова
            hot_keywords = ['breakthrough', 'surge', 'crash', 'ban', 'regulation', 'shortage', 'shocks', 'massive', 'growth']
            if any(kw in title_lower for kw in hot_keywords):
                score += 0.3
            
            # Вес источника
            if item.get('source') in ['Wired', 'TechCrunch', 'Bloomberg', 'AlphaVantage']:
                score += 0.2
                
            scored_trends.append({
                "title": item.get('title', 'No Title'),
                "url": item.get('url', '#'),
                "source": item.get('source', 'Unknown'),
                "score": round(min(score, 1.0), 2)
            })
        return scored_trends

    def calculate_opportunity_scores(self):
        """BI-скоринг для данных из базы."""
        try:
            if not os.path.exists(self.db_path): return pd.DataFrame()
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM trends", conn)
            conn.close()
            
            if df.empty: return pd.DataFrame()

            max_mentions = df['mentions_count'].max() if df['mentions_count'].max() > 0 else 1
            df['opportunity_score'] = (df['sentiment'] * 0.4) + \
                                     ((df['mentions_count'] / max_mentions) * 0.3) + \
                                     (df['source_weight'] * 0.3)
            
            return df.sort_values(by='opportunity_score', ascending=False)
        except Exception as e:
            logger.error(f"Ошибка скоринга: {e}")
            return pd.DataFrame()
