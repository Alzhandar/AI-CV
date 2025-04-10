from rest_framework import viewsets, status, permissions 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from django.db.models import Q
from jobs.models import Company, Job
from resumes.models import Skill, Resume
from jobs.serializers import CompanySerializer, JobSerializer
from accounts.models import User
from accounts.permissions import IsEmployer, IsAdmin, IsOwnerOrAdmin
from accounts.permissions import IsJobseeker, IsEmployer, IsAdmin, IsOwnerOrAdmin

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.EMPLOYER:
            return Company.objects.filter(user=user)
        elif user.role == User.ADMIN:
            return Company.objects.all()
        else:
            return Company.objects.filter(jobs__status=Job.ACTIVE).distinct()
    
    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsEmployer | IsAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwnerOrAdmin]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.EMPLOYER:
            return Job.objects.filter(company__user=user)
        elif user.role == User.ADMIN:
            return Job.objects.all()
        else:
            return Job.objects.filter(status=Job.ACTIVE)
    
    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsEmployer | IsAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwnerOrAdmin]
        elif self.action in ['matching', 'match_resume']:
            self.permission_classes = [IsJobseeker]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def matching(self, request):
        user = request.user
        
        if user.role != User.JOBSEEKER:
            return Response(
                {"error": "Эта функция доступна только для соискателей"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_skills = Skill.objects.filter(resume__user=user).distinct()
        
        if not user_skills:
            return Response(
                {"message": "У вас еще нет проанализированных резюме с навыками"},
                status=status.HTTP_200_OK
            )
        
        matching_jobs = Job.objects.filter(
            status=Job.ACTIVE,
            required_skills__in=user_skills
        ).distinct()
        
        serializer = self.get_serializer(matching_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def match_resume(self, request, pk=None):
        job = self.get_object()
        resume_id = request.query_params.get('resume_id')
        
        if not resume_id:
            return Response(
                {"error": "Необходимо указать ID резюме"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response(
                {"error": "Резюме не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if resume.status != Resume.COMPLETED:
            return Response(
                {"error": "Анализ резюме еще не завершен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resume_skills = set(resume.skills.all())
        job_skills = set(job.required_skills.all())
        
        matching_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        
        match_percentage = 0
        if job_skills:
            match_percentage = len(matching_skills) * 100 / len(job_skills)
        
        return Response({
            "match_percentage": round(match_percentage, 1),
            "matching_skills": [skill.name for skill in matching_skills],
            "missing_skills": [skill.name for skill in missing_skills],
        })