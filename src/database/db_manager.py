import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import setup_logger

logger = setup_logger("db_manager")

class DBManager:
    def __init__(self, db_path="/root/projects/global-trend-engine/data/trends.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    title TEXT,
                    link TEXT UNIQUE,
                    sentiment REAL,
                    category TEXT,
                    mentions_count INTEGER DEFAULT 1
                )
            """)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")

    def save_trend(self, title, link, sentiment, category):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO trends (title, link, sentiment, category) VALUES (?, ?, ?, ?)",
                           (title, link, sentiment, category))
        except sqlite3.IntegrityError:
            # Если ссылка уже есть, увеличиваем счетчик упоминаний
            cursor.execute("UPDATE trends SET mentions_count = mentions_count + 1 WHERE link = ?", (link,))
        except Exception as e:
            logger.error(f"Ошибка при сохранении тренда: {e}")
        self.conn.commit()

if __name__ == "__main__":
    db = DBManager()
    db.save_trend("AI Revolution", "TechCrunch", 0.85, "Technology")
    print("База данных инициализирована, тестовый тренд сохранен.")
