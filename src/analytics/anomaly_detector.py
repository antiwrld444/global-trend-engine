import numpy as np
import pandas as pd

class AnomalyDetector:
    """
    Класс для обнаружения аномального роста трендов.
    Использует Z-score для выявления всплесков упоминаний или резкого улучшения сентимента.
    """
    def __init__(self, threshold=2.0):
        self.threshold = threshold

    def detect_breakouts(self, df):
        if df.empty or len(df) < 3:
            return []

        # Рассчитываем среднее и стандартное отклонение для скоров
        mean_score = df['opportunity_score'].mean()
        std_score = df['opportunity_score'].std()

        if std_score == 0:
            return []

        # Находим тренды, чей скор выше (mean + threshold * std)
        breakouts = df[df['opportunity_score'] > (mean_score + self.threshold * std_score)]
        
        return breakouts['title'].tolist()

if __name__ == "__main__":
    # Тестовый запуск
    data = {'title': ['A', 'B', 'C', 'D'], 'opportunity_score': [0.1, 0.2, 0.15, 0.9]}
    df = pd.DataFrame(data)
    detector = AnomalyDetector()
    print(f"Обнаружены прорывные тренды: {detector.detect_breakouts(df)}")
