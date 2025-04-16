import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import Group

from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    if created:
        try:
            if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
                from rest_framework.authtoken.models import Token
                Token.objects.create(user=instance)
        except Exception as e:
            logger.error(f"Failed to create token for user {instance.email}: {str(e)}")
        
        try:
            if instance.role == User.JOBSEEKER:
                group = Group.objects.get_or_create(name='Jobseekers')[0]
                instance.groups.add(group)
            elif instance.role == User.EMPLOYER:
                group = Group.objects.get_or_create(name='Employers')[0]
                instance.groups.add(group)
        except Exception as e:
            logger.error(f"Failed to add user {instance.email} to group: {str(e)}")
        
        try:
            if hasattr(settings, 'SITE_DOMAIN') and not settings.DEBUG:
                subject = f"Добро пожаловать в AI-CV Resume Analyzer!"
                context = {
                    'user': instance,
                    'site_name': 'AI-CV Resume Analyzer',
                    'domain': settings.SITE_DOMAIN,
                }
                html_message = render_to_string('accounts/email/welcome_email.html', context)
                plain_message = render_to_string('accounts/email/welcome_email.txt', context)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    html_message=html_message,
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {instance.email}: {str(e)}")
        
        logger.info(f"New user registered: {instance.email}, role: {instance.role}")


@receiver(post_save, sender=User)
def user_updated_handler(sender, instance, created, **kwargs):
    if not created:
        try:
            old_instance = None
            try:
                old_instance = User.objects.get(pk=instance.pk)
            except User.DoesNotExist:
                pass
            
            if old_instance and old_instance.role != instance.role:
                for group in Group.objects.filter(name__in=['Jobseekers', 'Employers']):
                    instance.groups.remove(group)
                
                if instance.role == User.JOBSEEKER:
                    group = Group.objects.get_or_create(name='Jobseekers')[0]
                    instance.groups.add(group)
                elif instance.role == User.EMPLOYER:
                    group = Group.objects.get_or_create(name='Employers')[0]
                    instance.groups.add(group)
                    
                logger.info(f"User {instance.email} role changed to {instance.role}")
        except Exception as e:
            logger.error(f"Failed to update groups for {instance.email}: {str(e)}")
        
        if hasattr(instance, 'last_activity'):
            instance.last_activity = timezone.now()
        
        logger.info(f"User profile updated: {instance.email}")


@receiver(pre_delete, sender=User)
def user_delete_handler(sender, instance, **kwargs):
    try:
        if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user=instance).delete()
    except Exception as e:
        logger.error(f"Failed to delete tokens for {instance.email}: {str(e)}")
    
    try:
        user_data = {
            'id': instance.id,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'role': instance.role,
            'date_joined': instance.date_joined.isoformat(),
            'deleted_at': timezone.now().isoformat(),
        }
        
        if hasattr(settings, 'ADMIN_EMAILS') and not settings.DEBUG:
            subject = f"Пользователь удален: {instance.email}"
            message = f"Пользователь {instance.get_full_name()} ({instance.email}) был удален из системы."
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ADMIN_EMAILS,
                fail_silently=True
            )
    except Exception as e:
        logger.error(f"Error archiving user data for {instance.email}: {str(e)}")
    
    logger.warning(f"User account deleted: {instance.email}, ID: {instance.id}")