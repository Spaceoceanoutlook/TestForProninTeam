import traceback
import idna
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db import transaction
from .models import Payment


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def safe_idna_encode(email):
    try:
        local, domain = email.split('@')
        return f"{local}@{idna.encode(domain).decode('ascii')}"
    except (idna.IDNAError, ValueError) as e:
        return email

@receiver(post_save, sender=Payment)
def payment_created_handler(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():  # Гарантируем атомарность всех операций
                collect = instance.collect

                # Обновляем сбор
                collect.current_amount += instance.amount
                collect.contributors_count = Payment.objects.filter(
                    collect=collect
                ).values('user').distinct().count()
                collect.save(update_fields=['current_amount', 'contributors_count'])
                collect.refresh_from_db()

                # Чистим кэш сбора
                cache.delete('collects_list')
                cache.delete(f'collect_detail_{collect.pk}')

                # Отправляем письма
                send_payment_emails(instance)

        except Exception as e:
            print(f"Payment processing error: {str(e)}")
            print(traceback.format_exc())

def send_payment_emails(payment):
    try:
        author_email = payment.collect.author.email.strip()
        donator_email = payment.user.email.strip()

        if not is_valid_email(author_email):
            return
        if not is_valid_email(donator_email):
            return

        context = {
            'amount': payment.amount,
            'collect_title': payment.collect.title,
            'donator': getattr(payment.user, 'username', 'Аноним'),
            'current_amount': payment.collect.current_amount,
            'target_amount': payment.collect.target_amount
        }

        # Письмо автору сбора
        send_mail(
            subject=f'Новый платеж в сбор "{payment.collect.title}"',
            message=render_to_string('emails/payment_to_author.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[safe_idna_encode(author_email)],
            fail_silently=False,
        )

        # Письмо донатеру
        send_mail(
            subject='Спасибо за ваш платеж!',
            message=render_to_string('emails/payment_to_donator.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[safe_idna_encode(donator_email)],
            fail_silently=False,
        )

    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        print(traceback.format_exc())
