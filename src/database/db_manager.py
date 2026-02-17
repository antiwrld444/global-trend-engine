import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import setup_logger
from analytics.nlp_processor import NLPProcessor

logger = setup_logger("db_manager")

class DBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            db_path = os.path.join(base_dir, 'data', 'trends.db')
            
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.nlp = None 
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
                    keywords TEXT,
                    source_weight REAL DEFAULT 1.0,
                    entities TEXT
                )
            """)
            cursor.execute("CREATE TABLE IF NOT EXISTS trend_history (id INTEGER PRIMARY KEY AUTOINCREMENT, trend_id INTEGER, score REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")

    def save_trend(self, title, link, sentiment, category, keywords=None, source_weight=1.0, entities=None):
        cursor = self.conn.cursor()
        if self.nlp is None: self.nlp = NLPProcessor()
            
        try:
            cursor.execute("SELECT id, title FROM trends ORDER BY timestamp DESC LIMIT 100")
            for tid, t_title in cursor.fetchall():
                if self.nlp.calculate_similarity(title, t_title) > 0.85:
                    cursor.execute("UPDATE trends SET mentions_count = mentions_count + 1, timestamp = CURRENT_TIMESTAMP WHERE id = ?", (tid,))
                    self.conn.commit()
                    return tid
        except: pass

        try:
            cursor.execute("INSERT INTO trends (title, link, sentiment, category, keywords, source_weight, entities) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (title, link, sentiment, category, keywords, source_weight, entities))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE trends SET mentions_count = mentions_count + 1 WHERE link = ?", (link,))
            self.conn.commit()
