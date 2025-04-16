import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

def send_welcome_email(user_id, email, first_name, last_name):
    """
    Асинхронная отправка приветственного письма новому пользователю.
    
    Args:
        user_id: ID пользователя
        email: Email пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
    """
    try:
        subject = f"Добро пожаловать в AI-CV Resume Analyzer!"
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'site_name': 'AI-CV Resume Analyzer',
            'domain': settings.SITE_DOMAIN if hasattr(settings, 'SITE_DOMAIN') else 'example.com',
        }
        html_message = render_to_string('accounts/email/welcome_email.html', context)
        plain_message = render_to_string('accounts/email/welcome_email.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=True
        )
        
        logger.info(f"Welcome email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")