from rest_framework import serializers
from django.db import transaction
from jobs.models import Company, Job
from resumes.serializers import SkillSerializer
from resumes.models import Skill
from typing import Dict, Any, List


class CompanySerializer(serializers.ModelSerializer):
    active_jobs_count = serializers.IntegerField(read_only=True)
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'website', 'logo',
            'logo_url', 'user', 'active_jobs_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'slug', 'active_jobs_count']
    
    def get_logo_url(self, obj) -> str:
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return ''
    
    def validate_name(self, value: str) -> str:
        user = self.context['request'].user
        if Company.objects.filter(name=value, user=user).exists():
            if self.instance and self.instance.name == value:
                return value
            raise serializers.ValidationError("У вас уже есть компания с таким названием.")
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> Company:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JobListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.SerializerMethodField()
    salary_display = serializers.CharField(read_only=True)
    skills_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 'company_name', 'company_logo',
            'location', 'salary_display', 'skills_count', 
            'status', 'created_at'
        ]
        read_only_fields = ['created_at', 'slug']
    
    def get_company_logo(self, obj) -> str:
        request = self.context.get('request')
        if obj.company.logo and request:
            return request.build_absolute_uri(obj.company.logo.url)
        return ''
    
    def get_skills_count(self, obj) -> int:
        return obj.required_skills.count()


class JobDetailSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.SerializerMethodField()
    company_website = serializers.URLField(source='company.website', read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    required_skills_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='required_skills'
    )
    salary_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 'company_name', 'company_logo', 'company_website',
            'description', 'requirements', 'salary_min', 'salary_max', 'salary_display',
            'location', 'required_skills', 'required_skills_ids',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'slug']
    
    def get_company_logo(self, obj) -> str:
        request = self.context.get('request')
        if obj.company.logo and request:
            return request.build_absolute_uri(obj.company.logo.url)
        return ''
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError({
                "salary_min": "Минимальная зарплата не может быть больше максимальной."
            })
            
        company = data.get('company')
        user = self.context['request'].user
        
        if company and company.user != user and not user.is_staff:
            raise serializers.ValidationError({
                "company": "Вы можете создавать вакансии только для своих компаний."
            })
            
        return data
    
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Job:
        skills_data = validated_data.pop('required_skills', [])
        job = Job.objects.create(**validated_data)
        
        if skills_data:
            job.required_skills.set(skills_data)
            
        return job
    
    @transaction.atomic
    def update(self, instance: Job, validated_data: Dict[str, Any]) -> Job:
        skills_data = validated_data.pop('required_skills', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if skills_data is not None:
            instance.required_skills.set(skills_data)
            
        instance.save()
        return instance