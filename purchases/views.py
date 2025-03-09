from rest_framework import viewsets, permissions
from .models import Purchase, TaskName
from .serializers import PurchaseSerializer, TaskNameSerializer

class TaskNameViewSet(viewsets.ModelViewSet):
    queryset = TaskName.objects.all()
    serializer_class = TaskNameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        