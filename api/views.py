from rest_framework import viewsets, status, filters, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Category, Product, Cart, CartItem, Wishlist
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    UserRegistrationSerializer, UserProfileSerializer, PasswordChangeSerializer,
    CartSerializer, CartItemSerializer, WishlistSerializer
)
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


# ==================== User Views ====================

class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create a new user and return user data with tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current authenticated user"""
        return self.request.user


class PasswordChangeView(generics.UpdateAPIView):
    """
    API endpoint for changing user password
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current authenticated user"""
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Change user password"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password updated successfully'
        }, status=status.HTTP_200_OK)


# ==================== Cart Views ====================

class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for managing shopping cart
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get current user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def create(self, request):
        """Add a product to cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        
        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {'error': 'Quantity must be at least 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if product is in stock
        if quantity > product.stock_quantity:
            return Response(
                {'error': f'Requested quantity ({quantity}) exceeds available stock ({product.stock_quantity})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                return Response(
                    {'error': f'Total quantity ({new_quantity}) would exceed available stock ({product.stock_quantity})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['put', 'patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """Update quantity of a cart item"""
        try:
            cart_item = CartItem.objects.get(
                pk=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'error': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {'error': 'Quantity must be at least 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check stock availability
        if quantity > cart_item.product.stock_quantity:
            return Response(
                {'error': f'Requested quantity ({quantity}) exceeds available stock ({cart_item.product.stock_quantity})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartSerializer(cart_item.cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove a product from cart"""
        try:
            cart_item = CartItem.objects.get(
                pk=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        cart_item.delete()
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


# ==================== Wishlist Views ====================

class WishlistViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user wishlist
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get current user's wishlist"""
        wishlists = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category')
        serializer = WishlistSerializer(wishlists, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Add a product to wishlist"""
        serializer = WishlistSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Check if product exists
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create wishlist item
        wishlist_item = Wishlist.objects.create(
            user=request.user,
            product=product
        )
        
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        """Remove a product from wishlist"""
        try:
            wishlist_item = Wishlist.objects.get(
                pk=pk,
                user=request.user
            )
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Wishlist item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        wishlist_item.delete()
        return Response(
            {'message': 'Product removed from wishlist'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['delete'], url_path='product/(?P<product_id>[^/.]+)')
    def remove_by_product(self, request, product_id=None):
        """Remove a product from wishlist by product ID"""
        try:
            wishlist_item = Wishlist.objects.get(
                product_id=product_id,
                user=request.user
            )
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Product not in wishlist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        wishlist_item.delete()
        return Response(
            {'message': 'Product removed from wishlist'},
            status=status.HTTP_204_NO_CONTENT
        )
