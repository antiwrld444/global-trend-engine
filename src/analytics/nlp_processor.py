from transformers import pipeline, AutoTokenizer, AutoModel
import re
import torch
import torch.nn.functional as F

class NLPProcessor:
    """
    Класс для анализа текста: определение настроения, извлечение сути и вычисление эмбеддингов.
    """
    def __init__(self):
        # Загружаем легковесную модель для анализа настроений
        print("--- Загрузка NLP моделей ---")
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        # Модель для эмбеддингов (используем ту же distilbert для экономии памяти или sentence-transformers)
        self.embed_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.embed_model_name)
        self.model = AutoModel.from_pretrained(self.embed_model_name)
        
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

    def get_embedding(self, text):
        """Вычисляет эмбеддинг для текста."""
        inputs = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
        with torch.no_grad():
            model_output = self.model(**inputs)
        # mean pooling
        embeddings = model_output[0].mean(dim=1)
        # normalization
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings

    def calculate_similarity(self, text1, text2):
        """Вычисляет косинусное сходство между двумя текстами."""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        similarity = torch.mm(emb1, emb2.transpose(0, 1))
        return similarity.item()

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

    def extract_entities(self, text):
        """
        Извлекает Сущности (Entities): слова с большой буквы, которые не в начале предложения.
        Использует простую регулярную логику.
        """
        # Ищем слова с большой буквы, которые не в начале строки и не после точки
        # Упрощенно: ищем заглавную букву, перед которой нет знаков препинания конца предложения
        # Или просто все слова с большой буквы, кроме первого слова в предложениях.
        
        # Разделяем на предложения
        sentences = re.split(r'(?<=[.!?])\s+', text)
        entities = set()
        
        for sentence in sentences:
            if not sentence:
                continue
            # Ищем слова с большой буквы
            found = re.findall(r'\b[A-Z][a-z]+\b', sentence)
            if found:
                # Убираем первое слово, если оно с большой буквы
                first_word_match = re.match(r'^\s*([A-Z][a-z]+)\b', sentence)
                if first_word_match:
                    first_word = first_word_match.group(1)
                    # Если первое слово встретилось в списке found, убираем одно вхождение
                    if first_word in found:
                        found.remove(first_word)
                
                for ent in found:
                    entities.add(ent)
        
        return ", ".join(list(entities)) if entities else None

if __name__ == "__main__":
    processor = NLPProcessor()
    test_text = "AI is the most promising technology of 2026, creating thousands of jobs. AI will change the world."
    print(f"Текст: {test_text}")
    print(f"Оценка настроения: {processor.analyze_text(test_text)}")
    print(f"Ключевые слова: {processor.extract_keywords(test_text)}")
