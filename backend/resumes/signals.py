import os
import logging
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.conf import settings

from resumes.models import Resume, Skill
from resumes.tasks import analyze_resume

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Resume)
def resume_delete_handler(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except Exception as e:
        logger.error(f"Ошибка при удалении файла резюме {instance.id}: {str(e)}")
    
    if instance.mongodb_id:
        try:
            from resume_analyzer.utils.mongodb import get_mongodb_db
            db = get_mongodb_db()
            collection = db.resume_analysis
            
            collection.delete_one({"_id": instance.mongodb_id})
            logger.info(f"Результаты анализа для резюме {instance.id} удалены из MongoDB")
        except Exception as e:
            logger.error(f"Ошибка при удалении результатов анализа из MongoDB для резюме {instance.id}: {str(e)}")


@receiver(post_save, sender=Resume)
def resume_file_changed_handler(sender, instance, created, **kwargs):
    update_fields = kwargs.get('update_fields')
    
    if created or (update_fields is None or 'file' in update_fields):
        if instance.status == Resume.PENDING:
            try:
                if 'celery' in settings.INSTALLED_APPS:
                    analyze_resume.delay(instance.id)
                    logger.info(f"Задача анализа резюме {instance.id} запущена")
            except Exception as e:
                logger.error(f"Ошибка при запуске задачи анализа резюме {instance.id}: {str(e)}")


@receiver(post_save, sender=Skill)
def skill_created_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Создан новый навык: {instance.name} (категория: {instance.category})")
        