from rest_framework import serializers
from resumes.models import Resume, Skill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']

class ResumeSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Resume
        fields = ['id', 'user', 'title', 'file', 'file_type', 'status', 
                 'skills', 'created_at', 'updated_at']
        read_only_fields = ['user', 'status', 'skills', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        file = validated_data.get('file')
        if file:
            file_name = file.name.lower()
            if file_name.endswith('.pdf'):
                validated_data['file_type'] = 'pdf'
            elif file_name.endswith('.docx'):
                validated_data['file_type'] = 'docx'
            else:
                raise serializers.ValidationError(
                    "Неподдерживаемый формат файла. Поддерживаются только PDF и DOCX."
                )
        
        return super().create(validated_data)