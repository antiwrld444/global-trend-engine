from transformers import pipeline, AutoTokenizer, AutoModel
import re
import torch
import torch.nn.functional as F
from sklearn.feature_extraction.text import TfidfVectorizer

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
        
        # TF-IDF Векторизатор для извлечения ключевых слов
        self.tfidf = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )

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
        Извлекает ключевые слова из текста с использованием TF-IDF подхода.
        Для одиночного текста имитируем корпус, но в идеале TF-IDF обучается на всей базе.
        """
        if not text or len(text) < 10:
            return ""
            
        try:
            # Для одиночного документа TF-IDF выделит самые редкие/длинные слова
            # В будущем стоит перевести на извлечение из всей коллекции документов
            tfidf_matrix = self.tfidf.fit_transform([text])
            feature_names = self.tfidf.get_feature_names_out()
            
            # Получаем веса для первого (и единственного) документа
            scores = tfidf_matrix.toarray()[0]
            
            # Сортируем слова по весу
            keyword_data = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
            
            return ", ".join([kw[0] for kw in keyword_data[:limit]])
        except Exception:
            # Фолбэк на простую регулярку, если TF-IDF упал (например, слишком короткий текст)
            words = re.findall(r'\b\w{4,}\b', text.lower())
            return ", ".join(list(set(words))[:limit])

    def extract_entities(self, text):
        """
        Извлекает Сущности (Entities): слова с большой буквы, которые не в начале предложения.
        Использует простую регулярную логику.
        """
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
                    if first_word in found:
                        found.remove(first_word)
                
                for ent in found:
                    entities.add(ent)
        
        return ", ".join(list(entities)) if entities else None

if __name__ == "__main__":
    processor = NLPProcessor()
    test_text = "AI is the most promising technology of 2026, creating thousands of jobs. Artificial Intelligence will change the world."
    print(f"Текст: {test_text}")
    print(f"Оценка настроения: {processor.analyze_text(test_text)}")
    print(f"Ключевые слова (TF-IDF): {processor.extract_keywords(test_text)}")
