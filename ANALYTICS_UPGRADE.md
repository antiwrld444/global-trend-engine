# Analytics Upgrade Report (Sprint)

## 1. NLP Processor Upgrade
- Добавлен метод `extract_keywords(text, limit=5)` в `src/analytics/nlp_processor.py`.
- Реализована базовая логика извлечения ключевых слов с фильтрацией стоп-слов и пунктуации (без внешних зависимостей типа NLTK для стабильности).

## 2. Database Schema Update
- Таблица `trends`: добавлено поле `keywords` (TEXT).
- Создана новая таблица `trend_history` для отслеживания изменений во времени:
  - `id` (INTEGER PRIMARY KEY)
  - `trend_id` (INTEGER, FOREIGN KEY)
  - `score` (REAL)
  - `timestamp` (DATETIME)

## 3. Pipeline Integration
- `NewsCollector` обновлен: теперь при каждом проходе извлекаются ключевые слова.
- `DBManager` обновлен: метод `save_trend` теперь автоматически записывает текущее состояние в `trend_history` при каждом упоминании тренда. Это позволяет строить графики популярности.

## 4. Git Push
- Изменения зафиксированы и отправлены в удаленный репозиторий.
