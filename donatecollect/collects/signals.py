from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging
from .models import Collect

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Collect)
def send_collect_created_email(sender, instance, created, **kwargs):
    if created and instance.author.email:
        try:
            subject = f'Сбор "{instance.title}" успешно создан'
            context = {
                'user': instance.author,
                'title': instance.title,
                'description': instance.description,
                'target_amount': instance.target_amount,
                'end_datetime': instance.end_datetime,
                'id': instance.id
            }
            
            message = render_to_string('emails/collect_created.txt', context)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.author.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send collect creation email: {str(e)}")