import logging
from rest_framework import viewsets, permissions
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.db import transaction
from rest_framework.response import Response

from .models import Collect
from .serializers import CollectSerializer, CollectDetailSerializer

logger = logging.getLogger(__name__)

class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectDetailSerializer
        return super().get_serializer_class()

    @method_decorator(cache_page(60 * 5, key_prefix='collects-list'))
    def list(self, request, *args, **kwargs):
        cache_key = "collects_list"  # Простой ключ
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 5)
        return response

    @method_decorator(cache_page(60 * 5, key_prefix='collect-detail'))
    def retrieve(self, request, *args, **kwargs):
        """
        Возвращает детали одной коллекции.
        Кэшируется на 5 минут.
        """
        collect_id = kwargs['pk']
        logger.debug(f"Retrieving collect {collect_id} (cache miss)...")
        response = super().retrieve(request, *args, **kwargs)
        logger.debug(f"Collect {collect_id} cached.")
        return response

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создает новую коллекцию и инвалидирует кэш.
        """
        collect = serializer.save(author=self.request.user)
        
        # Удаляем кэшированные данные
        cache_keys_to_delete = [
            'collects-list',  # Кэш списка
            f'collect-detail-{collect.id}',  # Кэш деталей (если есть)
        ]
        
        for key in cache_keys_to_delete:
            if cache.delete(key):
                logger.debug(f"Cache deleted: {key}")
            else:
                logger.debug(f"Cache key not found: {key}")

    # Аналогично для update и destroy
    def perform_update(self, serializer):
        collect = serializer.save()
        cache.delete('collects-list')
        cache.delete(f'collect-detail-{collect.id}')

    def perform_destroy(self, instance):
        cache.delete('collects-list')
        cache.delete(f'collect-detail-{instance.id}')
        instance.delete()
        
