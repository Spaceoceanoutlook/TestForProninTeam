from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Payment

@receiver(post_save, sender=Payment)
def update_contributors_on_payment(instance, created, **kwargs):
    if created:
        collect = instance.collect
        collect.contributors_count = Payment.objects.filter(
            collect=collect
        ).values('user').distinct().count()
        collect.save()

@receiver(post_save, sender=Payment)
def update_collected_amount(sender, instance, created, **kwargs):
    if created:  # Только для новых платежей
        collect = instance.collect
        collect.current_amount += instance.amount
        collect.save()

@receiver(post_delete, sender=Payment)
def deduct_collected_amount(sender, instance, **kwargs):
    collect = instance.collect
    collect.current_amount -= instance.amount
    collect.save()
