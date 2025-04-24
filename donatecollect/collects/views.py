from rest_framework import viewsets, permissions
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
        
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)