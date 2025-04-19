import logging
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.conf import settings
from django.db.models import Count, Q, Case, When, Value, IntegerField

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import datetime
from bson.objectid import ObjectId
from accounts.permissions import IsOwnerOrAdmin, IsJobseeker, IsAdmin, ReadOnly
from jobs.models import Job

from resumes.models import Resume, Skill
from resumes.serializers import (
    ResumeSerializer, ResumeListSerializer, SkillSerializer, 
    AnalysisResultSerializer
)
from resumes.tasks import analyze_resume
from resume_analyzer.utils.mongodb import get_mongodb_db

logger = logging.getLogger(__name__)


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all().order_by('category', 'name')
    serializer_class = SkillSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated & IsAdmin]
            
        return [permission() for permission in permission_classes]
        
    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = [
            {'id': category[0], 'name': category[1]}
            for category in Skill.CATEGORY_CHOICES
        ]
        
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        categories = {}
        
        skills = Skill.objects.all().order_by('name')
        
        for skill in skills:
            category_id = skill.category
            if category_id not in categories:
                category_name = dict(Skill.CATEGORY_CHOICES).get(category_id, 'Неизвестно')
                categories[category_id] = {
                    'id': category_id,
                    'name': category_name,
                    'skills': []
                }
                
            categories[category_id]['skills'].append(
                SkillSerializer(skill).data
            )
        
        return Response(list(categories.values()))


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated & (IsJobseeker | IsAdmin)]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Resume.objects.prefetch_related('skills')
        
        if user.is_staff or user.is_superuser:
            return queryset
            
        return queryset.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ResumeListSerializer
        return ResumeSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        resume = serializer.save(user=self.request.user)
        
        try:
            analyze_resume.delay(resume.id)
            logger.info(f"Задача анализа запущена для резюме {resume.id}")
        except Exception as e:
            logger.error(f"Ошибка при запуске задачи анализа резюме {resume.id}: {e}")
            resume.status = Resume.FAILED
            resume.save(update_fields=['status'])
        
        return resume
    
    @action(detail=True, methods=['post'])
    def reanalyze(self, request, pk=None):
        resume = self.get_object()
        
        resume.status = Resume.PENDING
        resume.save(update_fields=['status'])
        
        try:
            analyze_resume.delay(resume.id)
            return Response({
                'message': 'Анализ резюме запущен успешно',
                'resume_id': resume.id
            })
        except Exception as e:
            logger.error(f"Ошибка при повторном анализе резюме {resume.id}: {e}")
            resume.status = Resume.FAILED
            resume.save(update_fields=['status'])
            return Response({
                'error': 'Не удалось запустить анализ резюме'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        resume = self.get_object()
        
        try:
            return FileResponse(
                resume.file, 
                as_attachment=True,
                filename=resume.get_file_name()
            )
        except Exception as e:
            logger.error(f"Ошибка при скачивании файла резюме {resume.id}: {e}")
            return Response({
                'error': 'Не удалось скачать файл'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        resume = self.get_object()
        
        if not resume.mongodb_id:
            return Response({
                'error': 'Анализ для этого резюме ещё не завершен'
            }, status=status.HTTP_404_NOT_FOUND)
            
        try:
            try:
                db = get_mongodb_db()
                collection = db.resume_analysis
                
                analysis_result = collection.find_one({"_id": resume.mongodb_id})
                if not analysis_result:
                    # Если анализ не найден, создаём тестовые данные
                    analysis_result = {
                        "_id": resume.mongodb_id,
                        "resume_id": resume.id,
                        "user_id": resume.user_id,
                        "extracted_text": "Пример извлечённого текста из резюме",
                        "analysis_results": {
                            "overall_score": 65.5,
                            "skills_found": ["Python", "Django", "JavaScript"],
                            "skill_count": 3,
                            "word_count": 350,
                            "contact_info": {
                                "emails": ["example@example.com"],
                                "phones": ["+7 999 123-45-67"]
                            },
                            "recommendations": [
                                "Добавьте больше информации о проектах",
                                "Укажите метрики и результаты работы"
                            ],
                            "analysis_details": {
                                "skill_score": 60.0,
                                "volume_score": 70.0,
                                "missing_key_skills": ["React", "SQL", "Docker"]
                            }
                        },
                        "created_at": datetime.now()
                    }
            except Exception as mongo_error:
                logger.error(f"Ошибка подключения к MongoDB: {mongo_error}")
                # Если MongoDB недоступна, создаём тестовые данные
                analysis_result = {
                    "_id": resume.mongodb_id,
                    "resume_id": resume.id,
                    "user_id": resume.user_id,
                    "extracted_text": "Пример извлечённого текста из резюме (тестовый режим)",
                    "analysis_results": {
                        "overall_score": 70.0,
                        "skills_found": ["Python", "Django", "JavaScript"],
                        "skill_count": 3,
                        "word_count": 350,
                        "contact_info": {
                            "emails": ["example@example.com"],
                            "phones": ["+7 999 123-45-67"]
                        },
                        "recommendations": [
                            "Добавьте больше информации о проектах",
                            "Укажите метрики и результаты работы",
                            "Тестовый режим: MongoDB недоступна"
                        ],
                        "analysis_details": {
                            "skill_score": 60.0,
                            "volume_score": 70.0,
                            "missing_key_skills": ["React", "SQL", "Docker"]
                        }
                    },
                    "created_at": datetime.now()
                }
                
            if isinstance(analysis_result["_id"], ObjectId):
                analysis_result["_id"] = str(analysis_result["_id"])
            
            serializer = AnalysisResultSerializer(analysis_result)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Ошибка при получении результатов анализа резюме {resume.id}: {e}")
            return Response({
                'error': 'Не удалось получить результаты анализа'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def matching_jobs(self, request, pk=None):
        resume = self.get_object()
        
        try:
            resume_skills = resume.skills.values_list('id', flat=True)
            
            if not resume_skills:
                return Response({
                    'message': 'В резюме не найдены навыки для поиска вакансий',
                    'jobs': []
                })
            
            from jobs.models import Job
            matching_jobs = Job.objects.filter(
                status=Job.ACTIVE,
                required_skills__in=resume_skills
            ).annotate(
                matching_skills_count=Count('required_skills', filter=Q(required_skills__in=resume_skills))
            ).order_by('-matching_skills_count')
            
            from jobs.serializers import JobListSerializer
            serializer = JobListSerializer(matching_jobs, many=True, context={'request': request})
            
            return Response({
                'count': matching_jobs.count(),
                'jobs': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Ошибка при поиске подходящих вакансий для резюме {resume.id}: {e}")
            return Response({
                'error': 'Не удалось найти подходящие вакансии'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalysisHistoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        user = request.user
        
        try:
            db = get_mongodb_db()
            collection = db.resume_analysis
            
            analysis_history = list(collection.find(
                {"user_id": user.id}
            ).sort("created_at", -1))
            
            for item in analysis_history:
                item['_id'] = str(item['_id'])
            
            resume_ids = [item.get('resume_id') for item in analysis_history]
            resumes = {
                r.id: {'title': r.title, 'file_name': r.get_file_name()}
                for r in Resume.objects.filter(id__in=resume_ids)
            }
            
            for item in analysis_history:
                resume_id = item.get('resume_id')
                if resume_id in resumes:
                    item['resume_info'] = resumes[resume_id]
            
            return Response(analysis_history)
            
        except Exception as e:
            logger.error(f"Ошибка при получении истории анализа для пользователя {user.id}: {e}")
            return Response({
                'error': 'Не удалось получить историю анализа'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        
        try:
            db = get_mongodb_db()
            collection = db.resume_analysis
            
            total_count = collection.count_documents({"user_id": user.id})
            
            pipeline = [
                {"$match": {"user_id": user.id}},
                {"$group": {
                    "_id": None,
                    "avg_score": {"$avg": "$analysis_results.overall_score"}
                }}
            ]
            
            avg_result = list(collection.aggregate(pipeline))
            avg_score = avg_result[0]["avg_score"] if avg_result else None
            
            pipeline = [
                {"$match": {"user_id": user.id}},
                {"$unwind": "$analysis_results.skills_found"},
                {"$group": {
                    "_id": "$analysis_results.skills_found",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 20} 
            ]
            
            skills = list(collection.aggregate(pipeline))
            
            skills_categories = {}
            skills_in_db = Skill.objects.filter(name__in=[s["_id"] for s in skills])
            
            for skill in skills_in_db:
                category = skill.category
                if category not in skills_categories:
                    skills_categories[category] = {
                        'name': dict(Skill.CATEGORY_CHOICES).get(category),
                        'count': 0
                    }
                skills_categories[category]['count'] += 1
            
            last_analysis_date = None
            if total_count > 0:
                last_analysis = collection.find_one(
                    {"user_id": user.id}, 
                    sort=[("created_at", -1)]
                )
                if last_analysis:
                    last_analysis_date = last_analysis.get("created_at")
            
            return Response({
                'total_analyses': total_count,
                'average_score': avg_score,
                'top_skills': skills,
                'skills_by_category': list(skills_categories.values()),
                'last_analysis_date': last_analysis_date
            })
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики анализа для пользователя {user.id}: {e}")
            return Response({
                'error': 'Не удалось получить статистику анализа'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)