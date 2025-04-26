from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
import logging
import traceback
from .models import Collect

logger = logging.getLogger(__name__)

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


@receiver(post_save, sender=Collect)
def send_collect_created_email(sender, instance, created, **kwargs):
    if created and instance.author.email:
        try:
            recipient_email = instance.author.email.strip()
            if not is_valid_email(recipient_email):
                logger.warning(f"Invalid email for collect author: {recipient_email}")
                return

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
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            logger.info(f"Email sent to collect author: {recipient_email}")

        except Exception as e:
            logger.error(f"Failed to send collect creation email: {str(e)}")
            logger.debug(traceback.format_exc())

    # Очистка кэша после сохранения объекта
    cache.delete('collections_cache_key')
    if created:
        logger.info(f"New collect created: {instance.title}")
    else:
        logger.info(f"Collect updated: {instance.title}")


@receiver(post_delete, sender=Collect)
def clear_cache_on_collect_delete(sender, instance, **kwargs):
    # Очистка кэша при удалении объекта
    cache.delete('collections_cache_key')
    logger.info(f"Collect deleted: {instance.title}")
