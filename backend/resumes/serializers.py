from rest_framework import serializers
from django.db import transaction
from django.core.validators import FileExtensionValidator

from resumes.models import Resume, Skill
from typing import Dict, Any, List


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'slug', 'description']
        read_only_fields = ['slug']
        
    def validate_name(self, value: str) -> str:
        if Skill.objects.filter(name__iexact=value).exists():
            if not self.instance or self.instance.name.lower() != value.lower():
                raise serializers.ValidationError("Навык с таким названием уже существует.")
        return value


class ResumeSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    skills_list = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        required=True
    )
    
    class Meta:
        model = Resume
        fields = [
            'id', 'title', 'file', 'file_name', 'file_type',
            'status', 'mongodb_id', 'skills', 'skills_list',
            'created_at', 'updated_at', 'is_analyzed'
        ]
        read_only_fields = ['status', 'mongodb_id', 'skills', 'created_at', 'updated_at', 'is_analyzed']
        
    def get_skills_list(self, obj: Resume) -> List[str]:
        return obj.get_skills_list()
    
    def get_file_name(self, obj: Resume) -> str:
        return obj.get_file_name()
    
    def validate_file(self, value: Any) -> Any:
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Размер файла не должен превышать 5MB.")
            
        file_ext = value.name.split('.')[-1].lower()
        if file_ext not in ['pdf', 'docx']:
            raise serializers.ValidationError("Поддерживаются только файлы PDF и DOCX.")
            
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> Resume:
        validated_data['user'] = self.context['request'].user
        
        file_ext = validated_data['file'].name.split('.')[-1].lower()
        validated_data['file_type'] = 'pdf' if file_ext == 'pdf' else 'docx'
        
        return super().create(validated_data)


class ResumeListSerializer(serializers.ModelSerializer):
    skills_count = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = ['id', 'title', 'file_name', 'status', 'skills_count', 'created_at', 'is_analyzed']
        read_only_fields = ['status', 'skills_count', 'created_at', 'is_analyzed']
    
    def get_skills_count(self, obj: Resume) -> int:
        return obj.skills.count()
    
    def get_file_name(self, obj: Resume) -> str:
        return obj.get_file_name()


class AnalysisResultSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    resume_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    analysis_results = serializers.DictField(read_only=True)
    extracted_text = serializers.CharField(read_only=True)
    
    class Meta:
        fields = ['_id', 'resume_id', 'user_id', 'created_at', 'analysis_results', 'extracted_text']