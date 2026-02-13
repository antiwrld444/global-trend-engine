import sqlite3
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager

class ScoringEngine:
    """
    BI-движок для ранжирования трендов по их потенциалу.
    """
    def __init__(self):
        self.db_path = "/root/projects/global-trend-engine/data/trends.db"

    def calculate_opportunity_scores(self):
        print("--- Запуск BI-скоринга трендов ---")
        conn = sqlite3.connect(self.db_path)
        # Читаем данные в Pandas для аналитики
        df = pd.read_sql_query("SELECT * FROM trends", conn)
        
        if df.empty:
            print("Данные для анализа отсутствуют.")
            return pd.DataFrame()

        # Группируем по заголовкам (упрощенно) для поиска повторяющихся тем
        # В реальности тут был бы поиск по ключевым словам
        df['score'] = (df['sentiment'] * 0.6) + (df['mentions_count'] * 0.4)
        
        # Сортируем по убыванию "перспективности"
        ranked_df = df.sort_values(by='score', ascending=False)
        return ranked_df

if __name__ == "__main__":
    engine = ScoringEngine()
    ranked_opportunities = engine.calculate_opportunity_scores()
    if not ranked_opportunities.empty:
        print("Топ-3 рыночные возможности:")
        print(ranked_opportunities[['title', 'category', 'score']].head(3))
