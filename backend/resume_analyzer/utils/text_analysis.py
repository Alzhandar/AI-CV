import re
import logging
from typing import Dict, Any, List, Set, Tuple

logger = logging.getLogger(__name__)

def analyze_resume_text(text: str) -> Dict[str, Any]:
    """
    Анализирует текст резюме и возвращает результаты анализа.
    """
    results = {}
    
    # Базовые метрики текста
    results['word_count'] = len(text.split())
    
    # Поиск контактной информации
    emails = extract_emails(text)
    phones = extract_phone_numbers(text)
    results['contact_info'] = {
        'emails': emails,
        'phones': phones
    }
    
    # Оценка общего качества резюме
    results['overall_score'] = calculate_resume_score(text, emails, phones)
    
    # Рекомендации для улучшения
    results['recommendations'] = generate_recommendations(text, results)
    
    # Анализ структуры
    results['structure_analysis'] = analyze_resume_structure(text)
    
    # Детали анализа
    results['analysis_details'] = {
        'content_score': calculate_content_score(text),
        'format_score': calculate_format_score(text),
        'completeness_score': calculate_completeness_score(text, emails, phones)
    }
    
    return results

def extract_emails(text: str) -> List[str]:
    """Извлекает email адреса из текста."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """Извлекает номера телефонов из текста."""
    # Упрощенный паттерн для поиска телефонов
    phone_pattern = r'(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'
    return re.findall(phone_pattern, text)

def calculate_resume_score(text: str, emails: List[str], phones: List[str]) -> float:
    """
    Рассчитывает общую оценку резюме на основе различных факторов.
    Возвращает значение от 0 до 100.
    """
    # Базовый скор
    score = 50.0
    
    # Длина текста
    word_count = len(text.split())
    if word_count < 100:
        score -= 15
    elif word_count < 300:
        score -= 5
    elif word_count > 500:
        score += 10
    
    # Наличие контактной информации
    if emails:
        score += 5
    if phones:
        score += 5
        
    # Ключевые секции резюме
    if re.search(r'образование|education|обучение|учеба', text.lower()):
        score += 10
    if re.search(r'опыт работы|experience|стаж', text.lower()):
        score += 15
    if re.search(r'навыки|skills|умения', text.lower()):
        score += 10
        
    # Ограничиваем значение между 0 и 100
    return max(0, min(100, score))

def calculate_content_score(text: str) -> float:
    """Рассчитывает оценку содержимого резюме."""
    # Упрощенная реализация для примера
    return min(100, len(text.split()) / 10)

def calculate_format_score(text: str) -> float:
    """Рассчитывает оценку форматирования резюме."""
    # Упрощенная реализация для примера
    score = 50.0
    
    # Проверяем наличие заголовков и разделов
    if re.search(r'образование|education', text.lower()):
        score += 10
    if re.search(r'опыт работы|experience', text.lower()):
        score += 10
    if re.search(r'навыки|skills', text.lower()):
        score += 10
        
    # Проверяем наличие маркированных списков
    if re.search(r'•|\*|–|-', text):
        score += 10
        
    # Ограничиваем значение между 0 и 100
    return max(0, min(100, score))

def calculate_completeness_score(text: str, emails: List[str], phones: List[str]) -> float:
    """Рассчитывает оценку полноты резюме."""
    # Упрощенная реализация для примера
    score = 0.0
    
    # Проверяем наличие контактной информации
    if emails:
        score += 20
    if phones:
        score += 20
        
    # Проверяем наличие основных разделов
    if re.search(r'образование|education', text.lower()):
        score += 20
    if re.search(r'опыт работы|experience', text.lower()):
        score += 20
    if re.search(r'навыки|skills', text.lower()):
        score += 20
        
    # Ограничиваем значение между 0 и 100
    return max(0, min(100, score))

def analyze_resume_structure(text: str) -> Dict[str, Any]:
    """Анализирует структуру резюме."""
    structure = {
        'has_contact_info': bool(extract_emails(text) or extract_phone_numbers(text)),
        'has_education': bool(re.search(r'образование|education', text.lower())),
        'has_experience': bool(re.search(r'опыт работы|experience', text.lower())),
        'has_skills': bool(re.search(r'навыки|skills', text.lower())),
    }
    
    return structure

def generate_recommendations(text: str, analysis_results: Dict[str, Any]) -> List[str]:
    """Генерирует рекомендации для улучшения резюме."""
    recommendations = []
    
    # Рекомендации по длине
    if analysis_results['word_count'] < 200:
        recommendations.append('Добавьте больше содержания в резюме, оптимальная длина - 300-600 слов')
    elif analysis_results['word_count'] > 1000:
        recommendations.append('Резюме слишком длинное, сократите его для лучшего восприятия')
    
    # Рекомендации по контактной информации
    if not analysis_results['contact_info']['emails']:
        recommendations.append('Добавьте email адрес для связи')
    if not analysis_results['contact_info']['phones']:
        recommendations.append('Добавьте номер телефона для связи')
    
    # Рекомендации по структуре
    if not re.search(r'образование|education', text.lower()):
        recommendations.append('Добавьте раздел с информацией об образовании')
    if not re.search(r'опыт работы|experience', text.lower()):
        recommendations.append('Добавьте раздел с описанием опыта работы')
    if not re.search(r'навыки|skills', text.lower()):
        recommendations.append('Добавьте раздел, перечисляющий ваши навыки')
    
    return recommendations