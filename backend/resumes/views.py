from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from resumes.models import Resume, Skill
from resumes.serializers import ResumeSerializer, SkillSerializer
from django.shortcuts import get_object_or_404
from resumes.tasks import analyze_resume
from accounts.models import User
from jobs.models import Job
from django.db.models import Q
from accounts.permissions import IsJobseeker, IsAdmin, IsOwnerOrAdmin

from resumes.models import Resume
from accounts.permissions import IsOwnerOrAdmin
from resume_analyzer.utils.mongodb import get_mongodb_db
from bson.objectid import ObjectId  

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Skill.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [IsJobseeker | IsAdmin]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.ADMIN:
            return Resume.objects.all()
        return Resume.objects.filter(user=user)
    
    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwnerOrAdmin]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Запуск анализа резюме"""
        resume = self.get_object()
        
        if resume.status == Resume.ANALYZING:
            return Response(
                {"error": "Резюме уже находится в процессе анализа"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resume.status = Resume.ANALYZING
        resume.save()
        
        analyze_resume.delay(resume.id)
        
        return Response({"status": "Анализ запущен"})
    
    @action(detail=True, methods=['get'])
    def analysis_results(self, request, pk=None):
        resume = self.get_object()
        
        if resume.status != Resume.COMPLETED:
            return Response(
                {"status": resume.status, "message": "Анализ еще не завершен"},
                status=status.HTTP_200_OK
            )
        
        # Здесь будет получение результатов из MongoDB
        # results = get_resume_analysis_from_mongodb(resume.mongodb_id)
        
        # Временно возвращаем заглушку
        results = {
            "skills_found": [skill.name for skill in resume.skills.all()],
            "format_quality": "good",
            "improvement_suggestions": [
                "Добавьте больше конкретных достижений",
                "Используйте активные глаголы в описании опыта"
            ]
        }
        
        return Response(results)
    
class AnalysisHistoryViewSet(viewsets.ViewSet):
    """API для просмотра истории анализа резюме"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        Получение списка всех анализов резюме пользователя
        """
        user = request.user
        
        try:
            db = get_mongodb_db()
            collection = db.resume_analysis
            
            # Поиск всех анализов пользователя
            results = list(collection.find(
                {"user_id": user.id}, 
                {"_id": 1, "resume_id": 1, "created_at": 1, 
                 "analysis_results.overall_score": 1}
            ))
            
            # Преобразование ObjectId в строку для JSON сериализации
            for result in results:
                result["_id"] = str(result["_id"])
                
            return Response(results)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """
        Получение деталей конкретного анализа
        """
        try:
            # Проверяем формат ID
            try:
                obj_id = ObjectId(pk)
            except:
                return Response(
                    {"error": "Неверный формат ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            db = get_mongodb_db()
            collection = db.resume_analysis
            
            # Поиск анализа по ID
            result = collection.find_one({"_id": obj_id})
            
            if not result:
                return Response(
                    {"error": "Анализ не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Проверяем, принадлежит ли анализ текущему пользователю
            if result["user_id"] != request.user.id and not request.user.role == 'admin':
                return Response(
                    {"error": "У вас нет доступа к этому анализу"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Преобразование ObjectId в строку для JSON сериализации
            result["_id"] = str(result["_id"])
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Получение статистики по всем анализам пользователя
        """
        user = request.user
        
        try:
            db = get_mongodb_db()
            collection = db.resume_analysis
            
            # Подсчет количества анализов
            total_count = collection.count_documents({"user_id": user.id})
            
            # Средний балл (если возможно)
            pipeline = [
                {"$match": {"user_id": user.id}},
                {"$group": {
                    "_id": None,
                    "avg_score": {"$avg": "$analysis_results.overall_score"}
                }}
            ]
            
            avg_result = list(collection.aggregate(pipeline))
            avg_score = avg_result[0]["avg_score"] if avg_result else None
            
            # Навыки из всех анализов
            pipeline = [
                {"$match": {"user_id": user.id}},
                {"$unwind": "$analysis_results.skills_found"},
                {"$group": {
                    "_id": "$analysis_results.skills_found",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            
            skills = list(collection.aggregate(pipeline))
            skills_summary = {item["_id"]: item["count"] for item in skills}
            
            return Response({
                "total_analyses": total_count,
                "average_score": avg_score,
                "skills_summary": skills_summary
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )