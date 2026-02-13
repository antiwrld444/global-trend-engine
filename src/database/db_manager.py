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
                    mentions_count INTEGER DEFAULT 1,
                    keywords TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trend_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trend_id INTEGER,
                    score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trend_id) REFERENCES trends(id)
                )
            """)
            
            # Проверка, есть ли уже колонка keywords (на случай, если таблица существовала)
            cursor.execute("PRAGMA table_info(trends)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'keywords' not in columns:
                cursor.execute("ALTER TABLE trends ADD COLUMN keywords TEXT")
                
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")

    def save_trend(self, title, link, sentiment, category, keywords=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO trends (title, link, sentiment, category, keywords) VALUES (?, ?, ?, ?, ?)",
                           (title, link, sentiment, category, keywords))
            trend_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # Если ссылка уже есть, увеличиваем счетчик упоминаний и получаем ID
            cursor.execute("UPDATE trends SET mentions_count = mentions_count + 1 WHERE link = ?", (link,))
            cursor.execute("SELECT id FROM trends WHERE link = ?", (link,))
            trend_id = cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка при сохранении тренда: {e}")
            return
            
        # Запись в историю
        try:
            # В качестве score используем sentiment для примера отслеживания популярности/настроения
            cursor.execute("INSERT INTO trend_history (trend_id, score) VALUES (?, ?)", (trend_id, sentiment))
        except Exception as e:
            logger.error(f"Ошибка при записи истории тренда: {e}")
            
        self.conn.commit()

if __name__ == "__main__":
    db = DBManager()
    db.save_trend("AI Revolution", "TechCrunch", 0.85, "Technology")
    print("База данных инициализирована, тестовый тренд сохранен.")
