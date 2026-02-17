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
        scored_trends = []
        for item in raw_data:
            # Улучшенная логика базового скоринга
            title_lower = item['title'].lower()
            score = 0.5
            
            # Триггеры важности
            hot_keywords = ['breakthrough', 'surge', 'crash', 'ban', 'regulation', 'shortage', 'shocks', 'massive']
            if any(kw in title_lower for kw in hot_keywords):
                score += 0.3
            
            if item['source'] in ['Wired', 'TechCrunch', 'Bloomberg']:
                score += 0.2
                
            scored_trends.append({
                "title": item['title'],
                "url": item['url'],
                "source": item['source'],
                "score": round(min(score, 1.0), 2)
            })
        return scored_trends

    def get_market_sentiment_stats(self):
        """Агрегированная статистика по новостям для графиков."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT category, sentiment, timestamp FROM trends", conn)
            conn.close()
            if df.empty: return pd.DataFrame()
            return df
        except: return pd.DataFrame()
