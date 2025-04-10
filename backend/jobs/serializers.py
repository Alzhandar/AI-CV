from rest_framework import serializers
from jobs.models import Company, Job
from resumes.serializers import SkillSerializer

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'website', 'logo', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'company_name', 'description', 'requirements',
                 'salary_min', 'salary_max', 'location', 'required_skills',
                 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']