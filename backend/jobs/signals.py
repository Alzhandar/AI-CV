import logging
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from jobs.models import Company, Job

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Company)
def company_created_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Создана новая компания: {instance.name} (ID: {instance.id}), владелец: {instance.user.email}")
        
        if hasattr(settings, 'ADMIN_EMAILS') and not settings.DEBUG:
            try:
                subject = f"Новая компания: {instance.name}"
                message = f"Пользователь {instance.user.email} создал новую компанию: {instance.name}"
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.ADMIN_EMAILS,
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления о новой компании: {e}")


@receiver(post_save, sender=Job)
def job_created_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Создана новая вакансия: {instance.title} (ID: {instance.id}), "
            f"компания: {instance.company.name}, статус: {instance.status}"
        )
        
        if instance.status == Job.ACTIVE:
            try:
                from resumes.models import Resume, Skill
                from django.db.models import Count, Q
                
                job_skills_ids = instance.required_skills.values_list('id', flat=True)
                
                if job_skills_ids:
                    matching_resumes = Resume.objects.filter(
                        skills__id__in=job_skills_ids
                    ).annotate(
                        matching_skills=Count('skills', filter=Q(skills__id__in=job_skills_ids))
                    ).filter(
                        matching_skills__gte=1
                    ).distinct().order_by('-matching_skills')
                    
                    logger.info(f"Найдено {matching_resumes.count()} подходящих резюме для вакансии {instance.title}")
                    
            except Exception as e:
                logger.error(f"Ошибка при поиске кандидатов для вакансии {instance.id}: {e}")


@receiver(post_save, sender=Job)
def job_status_changed_handler(sender, instance, created, **kwargs):
    if not created:
        try:
            old_instance = Job.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                logger.info(f"Статус вакансии {instance.title} (ID: {instance.id}) изменен с {old_instance.status} на {instance.status}")
                
                if instance.status == Job.ACTIVE and old_instance.status != Job.ACTIVE:
                    logger.info(f"Вакансия {instance.title} стала активной, запускаем поиск кандидатов")
                    
                if instance.status == Job.CLOSED and old_instance.status != Job.CLOSED:
                    logger.info(f"Вакансия {instance.title} закрыта")
                    
        except Job.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Ошибка при обработке изменения статуса вакансии: {e}")


@receiver(m2m_changed, sender=Job.required_skills.through)
def job_skills_changed_handler(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and pk_set and not reverse:
        logger.info(f"К вакансии {instance.title} (ID: {instance.id}) добавлены новые требуемые навыки")
        
        if instance.status == Job.ACTIVE:
            logger.info(f"Обновление списка кандидатов для вакансии {instance.title} после изменения требуемых навыков")


@receiver(pre_delete, sender=Company)
def company_delete_handler(sender, instance, **kwargs):
    logger.warning(f"Удаление компании {instance.name} (ID: {instance.id}), владелец: {instance.user.email}")
    
    active_jobs = instance.jobs.filter(status=Job.ACTIVE).count()
    if active_jobs > 0:
        logger.warning(f"При удалении компании {instance.name} будут удалены {active_jobs} активных вакансий")
    
