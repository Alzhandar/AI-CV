import os
import tempfile
from celery import shared_task
from django.conf import settings
import logging
import docx
import PyPDF2
import io

from resume_analyzer.utils.mongodb import get_mongodb_db
from resumes.models import Resume, Skill
from resume_analyzer.utils import ai_analyzer
logger = logging.getLogger(__name__)

@shared_task
def analyze_resume(resume_id):
    """
    Фоновая задача для анализа загруженного резюме
    """
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        logger.error(f"Resume with id {resume_id} not found.")
        return
    
    try:
        # Извлечем текст из документа
        extracted_text = extract_text_from_file(resume.file.path, resume.file_type)
        
        # Анализируем текст с использованием AI
        analysis_results = ai_analyzer.analyze_resume(extracted_text)
        
        # Сохраняем результаты в MongoDB
        db = get_mongodb_db()
        collection = db.resume_analysis
        
        # Сохраняем данные в MongoDB
        mongo_data = {
            'resume_id': resume_id,
            'user_id': resume.user.id,
            'extracted_text': extracted_text,
            'analysis_results': analysis_results,
            'created_at': resume.created_at
        }
        
        result = collection.insert_one(mongo_data)
        
        # Обновляем запись о резюме с ID из MongoDB
        resume.mongodb_id = str(result.inserted_id)
        
        # Добавляем выявленные навыки
        for skill_name in analysis_results.get('skills_found', []):
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            resume.skills.add(skill)
        
        # Устанавливаем статус "завершено"
        resume.status = Resume.COMPLETED
        resume.save()
        
    except Exception as e:
        logger.error(f"Error analyzing resume {resume_id}: {str(e)}")
        resume.status = Resume.FAILED
        resume.save()

def extract_text_from_file(file_path, file_type):
    text = ""
    
    try:
        if file_type == 'pdf':
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
        
        elif file_type == 'docx':
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_type}")
        
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        raise

def simple_resume_analysis(text):
    """
    Простой анализ резюме без использования AI
    В будущем заменим на интеграцию с AI API
    """
    common_skills = [
        "Python", "Java", "JavaScript", "React", "Vue", "Angular", "Node.js",
        "Django", "Flask", "SQL", "PostgreSQL", "MongoDB", "MySQL", "Redis",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "CI/CD",
        "HTML", "CSS", "REST API", "GraphQL", "TDD", "Agile", "Scrum",
        "Machine Learning", "Data Analysis", "TensorFlow", "PyTorch"
    ]
    
    found_skills = []
    for skill in common_skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)
    
    format_quality = "needs_improvement"
    if len(text) > 1000 and text.count('\n') > 10:
        format_quality = "good"
    
    suggestions = ["Убедитесь, что резюме содержит ваши актуальные контактные данные",
                  "Добавьте количественные показатели достижений"]
    
    if len(found_skills) < 5:
        suggestions.append("Рекомендуется расширить список технических навыков")
    
    return {
        "skills_found": found_skills,
        "format_quality": format_quality,
        "improvement_suggestions": suggestions
    }