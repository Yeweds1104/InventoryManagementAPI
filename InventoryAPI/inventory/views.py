from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Item, ItemsLog
from .serializers import ItemSerializer, ItemLevelSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
# Create your views here.
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    def perform_update(self, serializer):
        instance = self.get_object()
        old_quantity = instance.quantity
        updated_item = serializer.save()
        
        if old_quantity != updated_item.quantity:
            ItemsLog.objects.create(
                item=updated_item,
                user=self.request.user,
                old_quantity=old_quantity,
                new_quantity=updated_item.quantity
            )
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='logs')
    def view_logs(self, request, pk=None):
        item = self.get_object()
        logs = item.logs.all().order_by('-timestamp')
        serializer = ItemsLogSerializer(logs, many=True)
        return Response(serializer.data)
        
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='low-stock')
    def item_levels(self, request):
        queryset = Item.objects.filter(owner=request.user, quantity__lt=10)
        category = request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category__name=category)
            
        price_min = request.query_params.get('price_min', None)
        price_max = request.query_params.get('price_max', None)
        if price_min is not None and price_max is not None:
            queryset = queryset.filter(price__gte=price_min, price__lte=price_max)
        low_stock = request.query_params.get('low_stock', None)
        if low_stock is not None:
            queryset = queryset.filter(quantity__lt=int(low_stock))
        serializer = ItemLevelSerializer(queryset, many=True)
        return Response(serializer.data)