from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model providing CRUD operations
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in a specific category"""
        category = self.get_object()
        products = category.products.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model providing CRUD operations
    """
    queryset = Product.objects.select_related('category').all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Filter products based on query parameters"""
        queryset = Product.objects.select_related('category').all()
        
        # Filter by category
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None and in_stock.lower() == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        # Search by name or description
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock (less than 10 items)"""
        low_stock_products = self.get_queryset().filter(stock_quantity__lt=10)
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update stock quantity for a product"""
        product = self.get_object()
        quantity_change = request.data.get('quantity_change', 0)
        
        try:
            quantity_change = int(quantity_change)
            new_stock = product.stock_quantity + quantity_change
            
            if new_stock < 0:
                return Response(
                    {'error': 'Stock quantity cannot be negative'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product.stock_quantity = new_stock
            product.save()
            
            serializer = self.get_serializer(product)
            return Response(serializer.data)
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity_change value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
