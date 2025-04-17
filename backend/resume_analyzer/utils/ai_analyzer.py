import os
import logging
import requests
import json
import openai
from django.conf import settings

logger = logging.getLogger(__name__)

class AIResumeAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        openai.api_key = self.api_key
    
    def analyze_resume(self, resume_text, job_description=None):
        try:
            if not self.api_key:
                logger.warning("OpenAI API key is not set. Using simple analysis.")
                return self._simple_analysis(resume_text)
            
            prompt = self._create_analysis_prompt(resume_text, job_description)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert resume analyzer. Analyze the resume and provide detailed feedback in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    logger.warning("Failed to extract JSON from AI response. Using simple analysis.")
                    result = self._simple_analysis(resume_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON. Using simple analysis.")
                result = self._simple_analysis(resume_text)
                
            return result
            
        except Exception as e:
            logger.error(f"Error in AI resume analysis: {str(e)}")
            return self._simple_analysis(resume_text)
    
    def _create_analysis_prompt(self, resume_text, job_description=None):
        prompt = f"""
        Please analyze the following resume and return your analysis in JSON format:
        
        Resume text:
        ```
        {resume_text}
        ```
        
        Please return a JSON object with the following structure:
        {{
            "skills_found": [list of technical and soft skills found in resume],
            "format_quality": "good"|"average"|"needs_improvement",
            "structure_analysis": {{
                "has_contact_info": true|false,
                "has_professional_summary": true|false,
                "has_work_experience": true|false,
                "has_education": true|false,
                "has_skills_section": true|false
            }},
            "improvement_suggestions": [list of specific suggestions],
            "overall_score": 1-10 rating
        }}
        
        Only return the JSON, no additional explanations.
        """
        
        if job_description:
            prompt += f"""
            
            Additionally, compare the resume with the following job description:
            ```
            {job_description}
            ```
            
            Add these fields to the JSON:
            {{
                "job_match_percentage": percentage as number (0-100),
                "matching_skills": [skills that match job requirements],
                "missing_skills": [important skills from job description not found in resume],
                "tailoring_suggestions": [suggestions to better tailor resume for this job]
            }}
            """
        
        return prompt
    
    def _simple_analysis(self, text):
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
        
        structure_analysis = {
            "has_contact_info": "email" in text.lower() or "телефон" in text.lower(),
            "has_professional_summary": len(text) > 200,
            "has_work_experience": "опыт" in text.lower() or "experience" in text.lower(),
            "has_education": "образование" in text.lower() or "education" in text.lower(),
            "has_skills_section": "навыки" in text.lower() or "skills" in text.lower()
        }
        
        format_quality = "needs_improvement"
        if len(text) > 1000 and text.count('\n') > 10:
            format_quality = "good"
        elif len(text) > 500 and text.count('\n') > 5:
            format_quality = "average"
        
        suggestions = ["Убедитесь, что резюме содержит ваши актуальные контактные данные",
                      "Добавьте количественные показатели достижений"]
        
        if len(found_skills) < 5:
            suggestions.append("Рекомендуется расширить список технических навыков")
        
        overall_score = min(5 + len(found_skills) // 2, 10)
        
        return {
            "skills_found": found_skills,
            "format_quality": format_quality,
            "structure_analysis": structure_analysis,
            "improvement_suggestions": suggestions,
            "overall_score": overall_score
        }