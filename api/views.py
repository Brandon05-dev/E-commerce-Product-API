from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer
from .permissions import IsAdminOrReadOnly
from .pagination import StandardResultsSetPagination, SmallResultsSetPagination


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model providing CRUD operations with filtering
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = SmallResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'id']
    ordering = ['name']  # Default ordering
    
    def get_queryset(self):
        """Custom queryset filtering for categories"""
        queryset = Category.objects.all()
        
        # Only apply search filtering for list actions, not detail actions
        if self.action == 'list':
            search = self.request.query_params.get('search', None)
            if search is not None:
                queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in a specific category with pagination"""
        category = self.get_object()
        products = category.products.select_related('category').all()
        
        # Apply search and filtering to category products
        search = request.query_params.get('search', None)
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Apply price filtering
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass
                
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass
        
        # Apply stock filtering
        in_stock = request.query_params.get('in_stock', None)
        if in_stock is not None and in_stock.lower() == 'true':
            products = products.filter(stock_quantity__gt=0)
            
        # Paginate the results
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model providing CRUD operations with advanced filtering
    """
    queryset = Product.objects.select_related('category').all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_date', 'stock_quantity']
    ordering = ['-created_date']  # Default ordering
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Filter products based on query parameters"""
        queryset = Product.objects.select_related('category').all()
        
        # Filter by category (support both ID and name)
        category_param = self.request.query_params.get('category', None)
        if category_param is not None:
            try:
                # Try to filter by category ID first
                category_id = int(category_param)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                # If not an integer, try filtering by category name
                queryset = queryset.filter(category__name__icontains=category_param)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price is not None:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass  # Invalid price format, ignore filter
                
        if max_price is not None:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass  # Invalid price format, ignore filter
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None and in_stock.lower() == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        elif in_stock is not None and in_stock.lower() == 'false':
            queryset = queryset.filter(stock_quantity=0)
        
        # Filter by minimum stock quantity
        min_stock = self.request.query_params.get('min_stock', None)
        if min_stock is not None:
            try:
                queryset = queryset.filter(stock_quantity__gte=int(min_stock))
            except (ValueError, TypeError):
                pass
        
        # Filter by date range
        created_after = self.request.query_params.get('created_after', None)
        created_before = self.request.query_params.get('created_before', None)
        
        if created_after is not None:
            try:
                from datetime import datetime
                date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                queryset = queryset.filter(created_date__gte=date)
            except (ValueError, TypeError):
                pass
                
        if created_before is not None:
            try:
                from datetime import datetime
                date = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
                queryset = queryset.filter(created_date__lte=date)
            except (ValueError, TypeError):
                pass
        
        # Enhanced search functionality
        search = self.request.query_params.get('search', None)
        if search is not None:
            search_terms = search.split()
            query = Q()
            
            for term in search_terms:
                query |= (
                    Q(name__icontains=term) | 
                    Q(description__icontains=term) |
                    Q(category__name__icontains=term)
                )
            
            queryset = queryset.filter(query).distinct()
        
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
