from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db import transaction
from django.core.cache import cache
from .models import Payment
from .serializers import PaymentSerializer



class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.select_related('collect', 'user')
        if user.is_staff or user.is_superuser:
            return queryset
        return queryset.filter(user=user)

    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = f'payments_list_{user.id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 5)
        return response

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        cache_key = f'payment_detail_{pk}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 5)
        return response

    @transaction.atomic
    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        collect = payment.collect
        collect.current_amount += payment.amount
        collect.contributors_count = Payment.objects.filter(
            collect=collect
        ).values('user').distinct().count()
        collect.save(update_fields=['current_amount', 'contributors_count'])

        self.clear_cache(collect.pk, payment.user.id)

    @transaction.atomic
    def perform_destroy(self, instance):
        """
        Удаление объекта и очистка кэша.
        """
        collect_id = instance.collect.pk
        user_id = instance.user.id
        # Удаляем кэш после удаления объекта
        self.clear_cache(collect_id, user_id)
        instance.delete()

    def clear_cache(self, collect_id, user_id):
        """
        Удаление кэша при изменении платежа.
        """
        keys_to_delete = [
            'collects_list',
            f'collect_detail_{collect_id}',
            f'payments_list_{user_id}',
        ]
        for key in keys_to_delete:
            cache.delete(key)
