from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.core.cache import cache
from django.db import transaction
from .models import Collect
from .serializers import CollectSerializer, CollectDetailSerializer


class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectDetailSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        cache_key = 'collects_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 5)
        return response

    def retrieve(self, request, *args, **kwargs):
        collect_id = self.kwargs['pk']
        cache_key = f'collect_detail_{collect_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 5)
        return response

    @transaction.atomic
    def perform_create(self, serializer):
        collect = serializer.save(author=self.request.user)
        self.clear_cache(collect.pk)

    @transaction.atomic
    def perform_update(self, serializer):
        collect = serializer.save()
        self.clear_cache(collect.pk)

    @transaction.atomic
    def perform_destroy(self, instance):
        self.clear_cache(instance.pk)
        instance.delete()

    def clear_cache(self, collect_id):
        keys_to_delete = [
            'collects_list',
            f'collect_detail_{collect_id}',
        ]
        for key in keys_to_delete:
            cache.delete(key)
