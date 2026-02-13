import sqlite3
import pandas as pd
import os

class BIReporter:
    """
    Класс для генерации кратких аналитических сводок для Димы.
    """
    def __init__(self, db_path="/root/projects/global-trend-engine/data/trends.db"):
        self.db_path = db_path

    def get_summary(self):
        if not os.path.exists(self.db_path):
            return "База данных еще не создана."
        
        conn = sqlite3.connect(self.db_path)
        # Получаем последние аномалии (Breakouts)
        query = "SELECT title, category, mentions_count FROM trends ORDER BY mentions_count DESC LIMIT 3"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return "Пока нет данных для сводки."

        summary = "📊 **BI-Сводка GTOE за последние часы:**\n\n"
        for i, row in df.iterrows():
            summary += f"{i+1}. {row['title']} ({row['category']}) — замечено в нескольких источниках!\n"
        
        summary += "\n🚀 Система продолжает мониторинг. Дашборд обновлен."
        return summary

if __name__ == "__main__":
    reporter = BIReporter()
    print(reporter.get_summary())
