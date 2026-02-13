import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import setup_logger

logger = setup_logger("anomaly_detector")

class AnomalyDetector:
    """
    Класс для обнаружения аномального роста трендов.
    Использует Z-score для выявления всплесков упоминаний или резкого улучшения сентимента.
    """
    def __init__(self, threshold=2.0):
        self.threshold = threshold

    def detect_breakouts(self, df):
        logger.info("--- Запуск поиска аномалий ---")
        try:
            if df.empty or len(df) < 3:
                logger.info("Недостаточно данных для поиска аномалий.")
                return []

            # Рассчитываем среднее и стандартное отклонение для скоров
            mean_score = df['opportunity_score'].mean()
            std_score = df['opportunity_score'].std()

            if std_score == 0:
                return []

            # Находим тренды, чей скор выше (mean + threshold * std)
            breakouts = df[df['opportunity_score'] > (mean_score + self.threshold * std_score)]
            
            logger.info(f"Найдено аномалий: {len(breakouts)}")
            return breakouts['title'].tolist()
        except Exception as e:
            logger.error(f"Ошибка при поиске аномалий: {e}")
            return []

if __name__ == "__main__":
    # Тестовый запуск
    data = {'title': ['A', 'B', 'C', 'D'], 'opportunity_score': [0.1, 0.2, 0.15, 0.9]}
    df = pd.DataFrame(data)
    detector = AnomalyDetector()
    print(f"Обнаружены прорывные тренды: {detector.detect_breakouts(df)}")
