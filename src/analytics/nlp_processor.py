from transformers import pipeline

class NLPProcessor:
    """
    Класс для анализа текста: определение настроения и извлечение сути.
    """
    def __init__(self):
        # Загружаем легковесную модель для анализа настроений
        print("--- Загрузка NLP моделей ---")
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze_text(self, text):
        # Ограничиваем длину текста для модели
        result = self.sentiment_analyzer(text[:512])[0]
        # Преобразуем POSITIVE/NEGATIVE в число от 0 до 1
        score = result['score'] if result['label'] == 'POSITIVE' else 1 - result['score']
        return score

if __name__ == "__main__":
    processor = NLPProcessor()
    test_text = "AI is the most promising technology of 2026, creating thousands of jobs."
    print(f"Текст: {test_text}")
    print(f"Оценка настроения: {processor.analyze_text(test_text)}")
