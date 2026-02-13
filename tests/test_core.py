import unittest
import os
import sqlite3
import pandas as pd
import sys

# Добавляем путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.analytics.scoring_engine import ScoringEngine
from src.database.db_manager import DBManager
from src.analytics.anomaly_detector import AnomalyDetector

class TestGTOE(unittest.TestCase):
    def setUp(self):
        # Используем тестовую БД
        self.test_db = "/root/projects/global-trend-engine/data/test_trends.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = DBManager(db_path=self.test_db)
        
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_database_insertion(self):
        """Проверка корректности вставки данных и истории"""
        self.db.save_trend("Test Trend", "http://test.com", 0.5, "Testing", "test, unit")
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Проверка основной таблицы
        cursor.execute("SELECT title, mentions_count FROM trends WHERE title='Test Trend'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Test Trend")
        self.assertEqual(row[1], 1)
        
        # Проверка истории
        cursor.execute("SELECT score FROM trend_history")
        history_row = cursor.fetchone()
        self.assertIsNotNone(history_row)
        self.assertEqual(history_row[0], 0.5)
        conn.close()

    def test_scoring_calculation(self):
        """Проверка формулы скоринга"""
        # Скор = sentiment * 0.6 + mentions * 0.4
        # 0.8 * 0.6 + 1 * 0.4 = 0.48 + 0.4 = 0.88
        
        self.db.save_trend("High Score", "http://high.com", 0.8, "Tech")
        
        engine = ScoringEngine()
        engine.db_path = self.test_db # Переключаем на тестовую БД
        
        ranked_df = engine.calculate_opportunity_scores()
        score = ranked_df.iloc[0]['opportunity_score']
        
        self.assertAlmostEqual(score, 0.88)

    def test_anomaly_detection(self):
        """Проверка детектора аномалий"""
        data = {
            'title': ['Normal 1', 'Normal 2', 'Normal 3', 'Breakout!'],
            'opportunity_score': [0.1, 0.12, 0.11, 0.9]
        }
        df = pd.DataFrame(data)
        detector = AnomalyDetector(threshold=1.0)
        breakouts = detector.detect_breakouts(df)
        
        self.assertIn("Breakout!", breakouts)
        self.assertEqual(len(breakouts), 1)

if __name__ == '__main__':
    unittest.main()
