from transformers import pipeline
import re

class NLPProcessor:
    """
    Класс для анализа текста: определение настроения и извлечение сути.
    """
    def __init__(self):
        # Загружаем легковесную модель для анализа настроений
        print("--- Загрузка NLP моделей ---")
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        # Список стоп-слов для базового извлечения ключевых слов
        self.stopwords = {
            "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
            "at", "by", "from", "for", "in", "of", "on", "to", "with", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
            "did", "will", "would", "shall", "should", "can", "could", "may", "might",
            "must", "this", "that", "these", "those", "it", "its", "they", "their",
            "them", "we", "our", "us", "you", "your", "he", "she", "his", "her",
            "about", "above", "across", "after", "against", "along", "among", "around",
            "as", "at", "before", "behind", "below", "beneath", "beside", "between",
            "beyond", "during", "except", "for", "from", "in", "inside", "into", "near",
            "of", "off", "on", "onto", "out", "outside", "over", "past", "since", "through",
            "throughout", "to", "toward", "under", "until", "up", "upon", "with", "within", "without"
        }

    def analyze_text(self, text):
        # Ограничиваем длину текста для модели
        result = self.sentiment_analyzer(text[:512])[0]
        # Преобразуем POSITIVE/NEGATIVE в число от 0 до 1
        score = result['score'] if result['label'] == 'POSITIVE' else 1 - result['score']
        return score

    def extract_keywords(self, text, limit=5):
        """
        Извлекает ключевые слова из текста, очищая от стоп-слов и пунктуации.
        """
        # Очистка текста от спецсимволов и приведение к нижнему регистру
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Фильтрация: убираем стоп-слова и короткие слова (< 3 символов)
        filtered_words = [w for w in words if w not in self.stopwords and len(w) > 2]
        
        # Подсчет частоты
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        # Сортировка по частоте и выбор топ-слов
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return ", ".join([kw[0] for kw in sorted_keywords[:limit]])

if __name__ == "__main__":
    processor = NLPProcessor()
    test_text = "AI is the most promising technology of 2026, creating thousands of jobs. AI will change the world."
    print(f"Текст: {test_text}")
    print(f"Оценка настроения: {processor.analyze_text(test_text)}")
    print(f"Ключевые слова: {processor.extract_keywords(test_text)}")
