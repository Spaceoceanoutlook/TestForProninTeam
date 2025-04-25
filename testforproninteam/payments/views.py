from rest_framework import viewsets, permissions
from django.db import transaction
from django.core.cache import cache

from .models import Payment
from .serializers import PaymentSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('collect')

    @transaction.atomic
    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        collect = payment.collect
        collect.current_amount += payment.amount
        collect.contributors_count = Payment.objects.filter(
            collect=collect
        ).values('user').distinct().count()
        collect.save(update_fields=['current_amount', 'contributors_count'])

        # Инвалидация кэша
        cache.delete('collects-list')
        cache.delete(f'collect-detail.{collect.pk}')
