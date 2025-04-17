import os
import io
import re
import logging
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from bson import ObjectId

from resume_analyzer.utils.mongodb import get_mongodb_db
from resumes.models import Resume, Skill
from resume_analyzer.utils import ai_analyzer

logger = logging.getLogger(__name__)

try:
    import PyPDF2
    import docx
    from pdfminer.high_level import extract_text as pdf_extract_text
except ImportError:
    logger.warning("Не удалось импортировать необходимые библиотеки для обработки файлов")


@shared_task(bind=True, max_retries=3)
def analyze_resume(self, resume_id: int) -> Dict[str, Any]:
    logger.info(f"Начат анализ резюме {resume_id}")
    
    try:
        resume = Resume.objects.get(id=resume_id)
        
        resume.status = Resume.ANALYZING
        resume.save(update_fields=['status'])
        
        file_path = resume.file.path
        file_type = resume.file_type
        
        extracted_text = extract_text_from_file(file_path, file_type)
        
        if not extracted_text:
            raise ValueError("Не удалось извлечь текст из файла")
        
        analysis_result = analyze_resume_text(extracted_text)
        
        mongodb_id = save_analysis_to_mongodb(resume_id, resume.user_id, extracted_text, analysis_result)
        
        update_resume_skills(resume, analysis_result)
        
        resume.status = Resume.COMPLETED
        resume.mongodb_id = mongodb_id
        resume.save(update_fields=['status', 'mongodb_id'])
        
        logger.info(f"Анализ резюме {resume_id} успешно завершен")
        return {
            'resume_id': resume_id,
            'status': 'success',
            'mongodb_id': mongodb_id
        }
        
    except Resume.DoesNotExist:
        logger.error(f"Резюме с ID {resume_id} не существует")
        return {
            'resume_id': resume_id,
            'status': 'error',
            'error': 'Resume does not exist'
        }
    except Exception as e:
        logger.error(f"Ошибка при анализе резюме {resume_id}: {str(e)}", exc_info=True)
        try:
            resume = Resume.objects.get(id=resume_id)
            resume.status = Resume.FAILED
            resume.save(update_fields=['status'])
        except:
            pass
            
        try:
            self.retry(countdown=60 * 5, exc=e)  
        except:
            pass
            
        return {
            'resume_id': resume_id,
            'status': 'error',
            'error': str(e)
        }


def extract_text_from_file(file_path: str, file_type: str) -> str:
    text = ""
    
    try:
        if file_type == 'pdf':
            text = pdf_extract_text(file_path)
            
            if not text.strip():
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(len(pdf_reader.pages)):
                        text += pdf_reader.pages[page_num].extract_text() or ""
        
        elif file_type == 'docx':
            doc = docx.Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            text = "\n".join(paragraphs)
        
        else:
            raise ValueError(f"Неподдерживаемый тип файла: {file_type}")
    
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста из файла: {str(e)}", exc_info=True)
        raise
    
    return text.strip()


def analyze_resume_text(text: str) -> Dict[str, Any]:
    if hasattr(settings, 'USE_AI_ANALYSIS') and settings.USE_AI_ANALYSIS:
        try:
            return ai_analyzer.analyze_resume(text)
        except Exception as e:
            logger.error(f"Ошибка при анализе через AI: {str(e)}")
            return simple_resume_analysis(text)
    
    return simple_resume_analysis(text)


def simple_resume_analysis(text: str) -> Dict[str, Any]:
    skills_in_db = list(Skill.objects.values_list('name', flat=True))
    
    skills_regex = {
        skill: re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE) 
        for skill in skills_in_db
    }
    
    skills_found = []
    for skill, pattern in skills_regex.items():
        if pattern.search(text):
            skills_found.append(skill)
    
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    phone_pattern = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    
    emails = email_pattern.findall(text)
    phones = phone_pattern.findall(text)
    
    word_count = len(text.split())
    
    skill_score = min(len(skills_found) / 5, 1) * 50  # максимум 50 баллов за навыки
    volume_score = min(word_count / 500, 1) * 50  # максимум 50 баллов за объем
    overall_score = (skill_score + volume_score) / 2
    
    result = {
        'overall_score': overall_score,
        'skills_found': skills_found,
        'skill_count': len(skills_found),
        'word_count': word_count,
        'contact_info': {
            'emails': emails,
            'phones': phones
        },
        'recommendations': generate_recommendations(skills_found, word_count),
        'analysis_details': {
            'skill_score': skill_score,
            'volume_score': volume_score,
            'missing_key_skills': find_missing_key_skills(skills_found),
        }
    }
    
    return result


def find_missing_key_skills(found_skills: List[str]) -> List[str]:
    key_programming_skills = ["Python", "Java", "JavaScript", "C++", "C#"]
    key_framework_skills = ["Django", "React", "Angular", "Vue.js", "Spring"]
    key_database_skills = ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis"]
    
    all_key_skills = key_programming_skills + key_framework_skills + key_database_skills
    
    missing_skills = [skill for skill in all_key_skills if skill not in found_skills]
    
    return missing_skills[:5]


def generate_recommendations(skills_found: List[str], word_count: int) -> List[str]:
    recommendations = []
    
    if word_count < 300:
        recommendations.append("Добавьте больше информации о вашем опыте работы и проектах.")
    elif word_count > 1000:
        recommendations.append("Рекомендуем сократить объем резюме, сфокусировавшись на ключевых достижениях.")
    
    if len(skills_found) < 5:
        recommendations.append("Включите больше технических навыков, соответствующих позиции.")
    
    recommendations.append("Используйте конкретные цифры и результаты для описания ваших достижений.")
    recommendations.append("Адаптируйте резюме под конкретную вакансию, выделяя релевантные навыки.")
    
    return recommendations


def save_analysis_to_mongodb(resume_id: int, user_id: int, 
                            extracted_text: str, analysis_result: Dict[str, Any]) -> str:
    try:
        db = get_mongodb_db()
        collection = db.resume_analysis
        
        document = {
            "resume_id": resume_id,
            "user_id": user_id,
            "extracted_text": extracted_text,
            "analysis_results": analysis_result,
            "created_at": datetime.now()
        }
        
        result = collection.insert_one(document)
        
        return str(result.inserted_id)
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении результатов анализа в MongoDB: {str(e)}", exc_info=True)
        raise


def update_resume_skills(resume: Resume, analysis_result: Dict[str, Any]) -> None:
    try:
        skills_found = analysis_result.get('skills_found', [])
        
        if not skills_found:
            return
        
        skills = Skill.objects.filter(name__in=skills_found)
        
        resume.skills.clear()
        resume.skills.add(*skills)
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении навыков резюме: {str(e)}", exc_info=True)
        raise