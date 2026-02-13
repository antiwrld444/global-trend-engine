import sys
import os
from collectors.news_collector import NewsCollector
from analytics.scoring_engine import ScoringEngine

def run_pipeline():
    print("=== GLOBAL TREND ENGINE: ЗАПУСК ПАЙПЛАЙНА ===")
    
    # 1. Сбор и NLP анализ
    collector = NewsCollector()
    collector.run()
    
    # 2. BI Скоринг
    engine = ScoringEngine()
    results = engine.calculate_opportunity_scores()
    
    if not results.empty:
        print("\n--- ИТОГОВЫЙ ОТЧЕТ BI ---")
        top_3 = results.head(3)
        for i, row in top_3.iterrows():
            print(f"[{i+1}] {row['title']} | Категория: {row['category']} | Скоринг: {row['score']:.2f}")
    
    print("\n=== ПАЙПЛАЙН ЗАВЕРШЕН ===")

if __name__ == "__main__":
    run_pipeline()
