import sqlite3
import os

class DBManager:
    def __init__(self, db_path="/root/projects/global-trend-engine/data/trends.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                source TEXT,
                sentiment REAL,
                category TEXT,
                mentions_count INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()

    def save_trend(self, title, source, sentiment, category):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO trends (title, source, sentiment, category) VALUES (?, ?, ?, ?)",
                       (title, source, sentiment, category))
        self.conn.commit()

if __name__ == "__main__":
    db = DBManager()
    db.save_trend("AI Revolution", "TechCrunch", 0.85, "Technology")
    print("База данных инициализирована, тестовый тренд сохранен.")
