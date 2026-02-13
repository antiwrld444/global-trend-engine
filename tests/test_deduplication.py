from analytics.nlp_processor import NLPProcessor
from database.db_manager import DBManager
import os

def test_deduplication():
    print("=== Тест семантической группировки ===")
    
    # Удаляем старую базу для чистоты теста
    db_path = "/root/projects/global-trend-engine/data/test_trends.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = DBManager(db_path=db_path)
    
    # 1. Добавляем первый тренд
    title1 = "Apple reveals new AI features for iPhone 17"
    print(f"Добавление 1: {title1}")
    db.save_trend(title1, "http://link1.com", 0.8, "Tech")
    
    # 2. Добавляем похожий тренд (другая ссылка, немного другой текст)
    title2 = "New AI features for iPhone 17 announced by Apple"
    print(f"Добавление 2 (похожий): {title2}")
    db.save_trend(title2, "http://link2.com", 0.85, "Tech")
    
    # 3. Добавляем непохожий тренд
    title3 = "Oil prices dropping in 2026"
    print(f"Добавление 3 (непохожий): {title3}")
    db.save_trend(title3, "http://link3.com", 0.4, "Economy")
    
    # Проверка результатов
    cursor = db.conn.cursor()
    cursor.execute("SELECT title, mentions_count FROM trends")
    rows = cursor.fetchall()
    
    print("\nРезультаты в базе:")
    for title, count in rows:
        print(f"- {title} | Mentions: {count}")
        
    if len(rows) == 2 and rows[0][1] == 2:
        print("\n✅ УСПЕХ: Похожие тренды объединены!")
    else:
        print("\n❌ ОШИБКА: Ожидалось 2 тренда, первый с Mentions=2")

if __name__ == "__main__":
    test_deduplication()
