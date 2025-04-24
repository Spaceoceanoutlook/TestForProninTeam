import idna
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Payment
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def safe_idna_encode(email):
    """Безопасное кодирование email с обработкой ошибок"""
    try:
        local, domain = email.split('@')
        # Кодируем только доменную часть
        return f"{local}@{idna.encode(domain).decode('ascii')}"
    except (idna.IDNAError, ValueError) as e:
        logger.warning(f"IDNA encoding failed for {email}: {str(e)}")
        return email  # Возвращаем оригинал в случае ошибки

@receiver(post_save, sender=Payment)
def payment_created_handler(sender, instance, created, **kwargs):
    if created:
        try:
            # Обновляем данные сбора
            collect = instance.collect
            collect.current_amount += instance.amount
            collect.contributors_count = Payment.objects.filter(
                collect=collect
            ).values('user').distinct().count()
            collect.save(update_fields=['current_amount', 'contributors_count'])
            
            # Отправляем письма
            send_payment_emails(instance)
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")

def send_payment_emails(payment):
    """Отправка писем с дополнительным логированием"""
    try:
        context = {
            'amount': payment.amount,
            'collect_title': payment.collect.title,
            'donator': payment.user.username,
            'current_amount': payment.collect.current_amount,
            'target_amount': payment.collect.target_amount
        }

        # Логируем информацию о письме
        logger.info(f"Attempting to send email from: 'noreply@example.com' to: {payment.collect.author.email}, {payment.user.email}")
        
        # Проверим валидность email адресов
        if not is_valid_email(payment.collect.author.email):
            logger.error(f"Invalid email (author): {payment.collect.author.email}")
            return
        if not is_valid_email(payment.user.email):
            logger.error(f"Invalid email (donator): {payment.user.email}")
            return

        # Письмо автору
        send_mail(
            subject=f'Новый платеж в сбор "{payment.collect.title}"',
            message=render_to_string('emails/payment_to_author.txt', context),
            from_email='noreply@example.com',  # Используем явно заданный email
            recipient_list=[payment.collect.author.email],
            fail_silently=False,
        )

        # Письмо донатеру
        send_mail(
            subject='Спасибо за ваш платеж!',
            message=render_to_string('emails/payment_to_donator.txt', context),
            from_email='noreply@example.com',  # Используем явно заданный email
            recipient_list=[payment.user.email],
            fail_silently=False,
        )

    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
