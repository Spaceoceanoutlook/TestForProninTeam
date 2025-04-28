import traceback
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Collect


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

        except Exception as e:
            print(f"Ошибка при отправке письма: {str(e)}")
            print(traceback.format_exc())

    # Очистка кэша после создания или обновления сбора
    cache.delete('collects_list')
    cache.delete(f'collect_detail_{instance.id}')

@receiver(post_delete, sender=Collect)
def clear_cache_on_collect_delete(sender, instance, **kwargs):
    # Очистка кэша при удалении сбора
    cache.delete('collects_list')
    cache.delete(f'collect_detail_{instance.id}')

