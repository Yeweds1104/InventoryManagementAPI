from django.shortcuts import render
from rest_framework import viewSets, permissions
from .models import Item
from .serializers import ItemSerializer
from .permissions import IsOwnerOrReadOnly

# Create your views here.
class ItemViewSet(viewSets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)