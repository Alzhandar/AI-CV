from rest_framework import viewsets, status, permissions, filters 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404

from jobs.models import Company, Job
from resumes.models import Skill, Resume
from jobs.serializers import (
    CompanySerializer, 
    JobListSerializer,
    JobDetailSerializer
)
from accounts.models import User
from accounts.permissions import IsEmployer, IsAdmin, IsOwnerOrAdmin, ReadOnly


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Company.objects.annotate(
            active_jobs_count=Count('jobs', filter=Q(jobs__status=Job.ACTIVE))
        )
        
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(user=user)
            
        return queryset
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated & (IsEmployer | IsAdmin)]
        else:
            permission_classes = [IsAuthenticated & IsOwnerOrAdmin]
            
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, slug=None):
        company = self.get_object()
        jobs = Job.objects.filter(company=company)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            jobs = jobs.filter(status=status_filter)
            
        serializer = JobListSerializer(jobs, many=True, context={'request': request})
        return Response(serializer.data)


class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company__name', 'location']
    ordering_fields = ['created_at', 'title', 'company__name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.select_related('company')
        
        if self.action != 'list':
            queryset = queryset.prefetch_related('required_skills')
        
        if user.is_staff or user.is_superuser:
            return queryset
            
        if user.role == User.EMPLOYER:
            return queryset.filter(company__user=user)
            
        return queryset.filter(status=Job.ACTIVE)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated & (IsEmployer | IsAdmin)]
        else:
            permission_classes = [IsAuthenticated & IsOwnerOrAdmin]
            
        return [permission() for permission in permission_classes]
        
    def perform_create(self, serializer):
        company = serializer.validated_data.get('company')
        user = self.request.user
        
        if not user.is_staff and company.user != user:
            raise permissions.PermissionDenied(
                "Вы можете создавать вакансии только для своих компаний."
            )
            
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def matching_resumes(self, request, slug=None):
        job = self.get_object()
        
        if not request.user.is_staff and job.company.user != request.user:
            return Response(
                {"detail": "У вас нет прав для просмотра этой информации."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        job_skills = job.required_skills.values_list('id', flat=True)
        
        matching_resumes = Resume.objects.filter(
            skills__in=job_skills
        ).annotate(
            matching_skills_count=Count('skills', filter=Q(skills__in=job_skills))
        ).order_by('-matching_skills_count')
        
        from resumes.serializers import ResumeListSerializer
        
        serializer = ResumeListSerializer(
            matching_resumes, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'count': matching_resumes.count(),
            'results': serializer.data
        })