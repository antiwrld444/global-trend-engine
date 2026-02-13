import os
import sys
import time

# Добавляем корневую директорию проекта в пути
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.collectors.news_collector import NewsCollector
from src.analytics.scoring_engine import ScoringEngine
from src.utils.reporter import BIReporter
from src.utils.logger import setup_logger

logger = setup_logger("auto_worker")

class AutoWorker:
    def __init__(self):
        self.collector = NewsCollector()
        self.scoring = ScoringEngine()
        self.reporter = BIReporter()

    def run_full_cycle(self):
        logger.info("=== НАЧАЛО ПОЛНОГО ЦИКЛА GTOE ===")
        
        # 1. Сбор данных
        logger.info("Шаг 1: Сбор новостей и NLP-анализ...")
        self.collector.run()
        
        # 2. Анализ и скоринг
        logger.info("Шаг 2: Расчет рыночных возможностей...")
        ranked_trends = self.scoring.calculate_opportunity_scores()
        
        if ranked_trends.empty:
            logger.warning("Анализ не дал результатов. Возможно, база пуста.")
            return

        # 3. Генерация отчета
        logger.info("Шаг 3: Генерация PDF/Markdown отчета...")
        # Предполагаем, что reporter.generate_report принимает DataFrame
        # В текущей реализации reporter может работать иначе, проверим его позже.
        # Для начала просто выведем топ в лог и создадим файл.
        
        top_trends = ranked_trends.head(10)
        report_path = "/root/projects/global-trend-engine/DEEP_INTEL.md"
        
        with open(report_path, "w") as f:
            f.write("# 🕵️ GTOE Deep Intel Report\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 🚀 Top Market Opportunities\n\n")
            f.write("| Title | Category | Score | Mentions |\n")
            f.write("|-------|----------|-------|----------|\n")
            for _, row in top_trends.iterrows():
                f.write(f"| {row['title']} | {row['category']} | {row['opportunity_score']:.2f} | {row['mentions_count']} |\n")
            
            f.write("\n## 📈 Summary Statistics\n\n")
            f.write(f"- Total Trends Analyzed: {len(ranked_trends)}\n")
            f.write(f"- Average Sentiment: {ranked_trends['sentiment'].mean():.2f}\n")
            
        logger.info(f"Отчет сохранен в {report_path}")
        logger.info("=== ЦИКЛ ЗАВЕРШЕН УСПЕШНО ===")

if __name__ == "__main__":
    worker = AutoWorker()
    worker.run_full_cycle()
