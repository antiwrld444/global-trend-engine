import sys
import os
from collectors.news_collector import NewsCollector
from analytics.scoring_engine import ScoringEngine
from analytics.anomaly_detector import AnomalyDetector
from utils.logger import setup_logger

logger = setup_logger("main")

def run_pipeline():
    logger.info("=== GLOBAL TREND ENGINE: ЗАПУСК ПАЙПЛАЙНА ===")
    
    try:
        # 1. Сбор и NLP анализ
        collector = NewsCollector()
        collector.run()
        
        # 2. BI Скоринг
        engine = ScoringEngine()
        results = engine.calculate_opportunity_scores()
        
        # 3. Детектор аномалий (усложнение логики)
        detector = AnomalyDetector(threshold=1.5)
        breakouts = detector.detect_breakouts(results)
        
        if not results.empty:
            logger.info("\n--- ИТОГОВЫЙ ОТЧЕТ BI ---")
            top_3 = results.head(3)
            for i, row in top_3.iterrows():
                is_breakout = " [🚀 BREAKOUT]" if row['title'] in breakouts else ""
                logger.info(f"[{i+1}]{is_breakout} {row['title']} | Категория: {row['category']} | Скоринг: {row['opportunity_score']:.2f}")
    except Exception as e:
        logger.error(f"Критическая ошибка пайплайна: {e}")
    
    logger.info("\n=== ПАЙПЛАЙН ЗАВЕРШЕН ===")

if __name__ == "__main__":
    run_pipeline()
