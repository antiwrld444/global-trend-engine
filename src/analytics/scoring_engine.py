import sqlite3
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager
from utils.logger import setup_logger

logger = setup_logger("scoring_engine")

class ScoringEngine:
    """
    BI-движок для ранжирования трендов по их потенциалу.
    """
    def __init__(self):
        self.db_path = "/root/projects/global-trend-engine/data/trends.db"

    def calculate_opportunity_scores(self):
        logger.info("--- Запуск BI-скоринга трендов ---")
        try:
            conn = sqlite3.connect(self.db_path)
            # Читаем данные в Pandas для аналитики
            df = pd.read_sql_query("SELECT * FROM trends", conn)
            
            if df.empty:
                logger.info("Данные для анализа отсутствуют.")
                return pd.DataFrame()

            # Обновленная формула: учитываем вес источника
            # opportunity_score = (sentiment * 0.4) + (mentions_count * 0.3) + (source_weight * 0.3)
            # Мы нормализуем mentions_count и sentiment (уже 0-1), source_weight обычно 1.0-1.5
            
            df['opportunity_score'] = (df['sentiment'] * 0.4) + (df['mentions_count'] * 0.3) + (df['source_weight'] * 0.3)
            
            # Сортируем по убыванию "перспективности"
            ranked_df = df.sort_values(by='opportunity_score', ascending=False)
            return ranked_df
        except Exception as e:
            logger.error(f"Ошибка при расчете скоринга: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    engine = ScoringEngine()
    ranked_opportunities = engine.calculate_opportunity_scores()
    if not ranked_opportunities.empty:
        print("Топ-3 рыночные возможности:")
        print(ranked_opportunities[['title', 'category', 'opportunity_score']].head(3))
