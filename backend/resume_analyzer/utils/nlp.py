import re
import nltk
from typing import List, Dict, Any, Set, Tuple

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
except ImportError:
    lemmatizer = None

def lemmatize_text(text: str) -> str:
    """
    Лемматизирует текст (приводит слова к базовой форме).
    Если NLTK не установлен, возвращает исходный текст.
    """
    if not lemmatizer:
        return text
        
    tokens = nltk.word_tokenize(text)
    return ' '.join([lemmatizer.lemmatize(token) for token in tokens])

def find_matching_terms(text: str, terms: List[str]) -> List[Dict[str, Any]]:
    """
    Находит совпадения между текстом и списком терминов.
    Возвращает список найденных совпадений с контекстом.
    """
    results = []
    text_lower = text.lower()
    
    for term in terms:
        term_lower = term.lower()
        pattern = r'\b' + re.escape(term_lower) + r'\b'
        
        for match in re.finditer(pattern, text_lower):
            start, end = match.span()
            
            # Получаем контекст вокруг найденного термина
            context_start = max(0, start - 30)
            context_end = min(len(text_lower), end + 30)
            context = text_lower[context_start:context_end]
            
            # Добавляем многоточия для обозначения обрезанного текста
            if context_start > 0:
                context = "..." + context
            if context_end < len(text_lower):
                context = context + "..."
            
            results.append({
                'term': term,
                'found': match.group(),
                'context': context,
                'start': start,
                'end': end
            })
    
    return results