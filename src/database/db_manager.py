import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import setup_logger
from analytics.nlp_processor import NLPProcessor

logger = setup_logger("db_manager")

class DBManager:
    def __init__(self, db_path="/root/projects/global-trend-engine/data/trends.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.nlp = None # Ленивая инициализация для избежания циклического импорта или лишней нагрузки
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
            
            # Проверка колонок (на случай, если таблица существовала)
            cursor.execute("PRAGMA table_info(trends)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'keywords' not in columns:
                cursor.execute("ALTER TABLE trends ADD COLUMN keywords TEXT")
            if 'source_weight' not in columns:
                cursor.execute("ALTER TABLE trends ADD COLUMN source_weight REAL DEFAULT 1.0")
            if 'entities' not in columns:
                cursor.execute("ALTER TABLE trends ADD COLUMN entities TEXT")
                
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")

    def save_trend(self, title, link, sentiment, category, keywords=None, source_weight=1.0, entities=None):
        cursor = self.conn.cursor()
        
        # 1. Семантическая группировка (Deduplication)
        if self.nlp is None:
            self.nlp = NLPProcessor()
            
        try:
            # Получаем последние тренды для сравнения (например, за последние 7 дней или просто последние 100)
            cursor.execute("SELECT id, title, mentions_count FROM trends ORDER BY timestamp DESC LIMIT 100")
            existing_trends = cursor.fetchall()
            
            for tid, t_title, m_count in existing_trends:
                similarity = self.nlp.calculate_similarity(title, t_title)
                if similarity > 0.85:
                    logger.info(f"Найден похожий тренд (Sim: {similarity:.2f}): '{t_title}'. Объединяем.")
                    cursor.execute("""
                        UPDATE trends 
                        SET mentions_count = mentions_count + 1, 
                            timestamp = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (tid,))
                    self.conn.commit()
                    self._record_history(tid, sentiment, source_weight)
                    return tid

        except Exception as e:
            logger.error(f"Ошибка при семантической проверке: {e}")

        # 2. Обычное сохранение, если похожих не найдено
        try:
            cursor.execute("INSERT INTO trends (title, link, sentiment, category, keywords, source_weight, entities) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (title, link, sentiment, category, keywords, source_weight, entities))
            trend_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # Если ссылка уже есть, увеличиваем счетчик упоминаний и получаем ID
            cursor.execute("UPDATE trends SET mentions_count = mentions_count + 1, timestamp = CURRENT_TIMESTAMP WHERE link = ?", (link,))
            cursor.execute("SELECT id FROM trends WHERE link = ?", (link,))
            trend_id = cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка при сохранении тренда: {e}")
            return
            
        self._record_history(trend_id, sentiment, source_weight)
        self.conn.commit()
        return trend_id

    def _record_history(self, trend_id, sentiment, source_weight):
        """Вспомогательный метод для записи в историю."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT mentions_count FROM trends WHERE id = ?", (trend_id,))
            mentions = cursor.fetchone()[0]
            score = sentiment * mentions * source_weight
            cursor.execute("INSERT INTO trend_history (trend_id, score) VALUES (?, ?)", (trend_id, score))
        except Exception as e:
            logger.error(f"Ошибка при записи истории тренда: {e}")

    def get_trend_timeseries(self, trend_id):
        """Возвращает историю изменений score для конкретного тренда."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT timestamp, score FROM trend_history WHERE trend_id = ? ORDER BY timestamp ASC", (trend_id,))
        return cursor.fetchall()

    def get_top_trends_timeseries(self, limit=5):
        """Возвращает историю изменений для топ-N трендов."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title FROM trends ORDER BY mentions_count DESC LIMIT ?", (limit,))
        top_trends = cursor.fetchall()
        
        history_data = {}
        for trend_id, title in top_trends:
            history_data[title] = self.get_trend_timeseries(trend_id)
        return history_data

    def get_brand_heatmap(self):
        """Извлекает сущности (ORGs) из базы для тепловой карты брендов."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT entities FROM trends WHERE entities IS NOT NULL AND entities != '[]'")
        rows = cursor.fetchall()
        
        brand_counts = {}
        import json
        for row in rows:
            try:
                entities = json.loads(row[0].replace("'", '"')) # На случай если там одинарные кавычки
                for entity, label in entities:
                    if label == 'ORG':
                        brand_counts[entity] = brand_counts.get(entity, 0) + 1
            except Exception:
                continue
        return brand_counts

if __name__ == "__main__":
    db = DBManager()
    db.save_trend("AI Revolution", "TechCrunch", 0.85, "Technology")
    print("База данных инициализирована, тестовый тренд сохранен.")
