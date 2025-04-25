import idna
import logging
import traceback
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Payment

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
        return f"{local}@{idna.encode(domain).decode('ascii')}"
    except (idna.IDNAError, ValueError) as e:
        logger.warning(f"IDNA encoding failed for {email}: {str(e)}")
        return email


@receiver(post_save, sender=Payment)
def payment_created_handler(sender, instance, created, **kwargs):
    if created:
        try:
            # Обновляем сбор
            collect = instance.collect
            collect.current_amount += instance.amount
            collect.contributors_count = Payment.objects.filter(
                collect=collect
            ).values('user').distinct().count()
            collect.save(update_fields=['current_amount', 'contributors_count'])
            collect.refresh_from_db()  # Обновляем объект после сохранения

            # Отправляем письма
            send_payment_emails(instance)
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            logger.debug(traceback.format_exc())


def send_payment_emails(payment):
    """Отправка писем с логированием"""
    try:
        author_email = payment.collect.author.email.strip()
        donator_email = payment.user.email.strip()

        context = {
            'amount': payment.amount,
            'collect_title': payment.collect.title,
            'donator': getattr(payment.user, 'username', 'Аноним'),
            'current_amount': payment.collect.current_amount,
            'target_amount': payment.collect.target_amount
        }

        logger.debug(f"Email context: {context}")
        logger.info(f"Sending emails to: author={author_email}, donator={donator_email}")

        if not is_valid_email(author_email):
            logger.error(f"Invalid author email: {author_email}")
            return
        if not is_valid_email(donator_email):
            logger.error(f"Invalid donator email: {donator_email}")
            return

        # Письмо автору сбора
        send_mail(
            subject=f'Новый платеж в сбор "{payment.collect.title}"',
            message=render_to_string('emails/payment_to_author.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author_email],
            fail_silently=False,
        )
        logger.info(f"Email sent to author: {author_email}")

        # Письмо донатеру
        send_mail(
            subject='Спасибо за ваш платеж!',
            message=render_to_string('emails/payment_to_donator.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[donator_email],
            fail_silently=False,
        )
        logger.info(f"Email sent to donator: {donator_email}")

    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        logger.debug(traceback.format_exc())
