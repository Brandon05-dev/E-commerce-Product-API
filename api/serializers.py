from rest_framework import serializers
from django.db.models import Count, Avg
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Category, Product, Cart, CartItem, Wishlist


class CategorySerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for Category model with additional statistics
    """
    products_count = serializers.SerializerMethodField()
    in_stock_products_count = serializers.SerializerMethodField()
    average_price = serializers.SerializerMethodField()
    total_inventory_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count', 'in_stock_products_count', 
                 'average_price', 'total_inventory_value']
        
    def get_products_count(self, obj):
        """Return the total number of products in this category"""
        return obj.products.count()
    
    def get_in_stock_products_count(self, obj):
        """Return the number of products in stock for this category"""
        return obj.products.filter(stock_quantity__gt=0).count()
    
    def get_average_price(self, obj):
        """Return the average price of products in this category"""
        avg = obj.products.aggregate(avg_price=Avg('price'))['avg_price']
        return round(float(avg), 2) if avg else 0.00
    
    def get_total_inventory_value(self, obj):
        """Return the total inventory value for this category"""
        total = 0
        for product in obj.products.all():
            total += product.price * product.stock_quantity
        return float(total)


class ProductSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for Product model with additional computed fields
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_details = serializers.SerializerMethodField()
    is_in_stock = serializers.ReadOnlyField()
    stock_status = serializers.SerializerMethodField()
    inventory_value = serializers.SerializerMethodField()
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'stock_quantity', 
            'image_url', 
            'created_date', 
            'category', 
            'category_name',
            'category_details',
            'is_in_stock',
            'stock_status',
            'inventory_value',
            'days_since_created'
        ]
        read_only_fields = ['created_date']
    
    def get_category_details(self, obj):
        """Return detailed category information"""
        return {
            'id': obj.category.id,
            'name': obj.category.name,
        }
    
    def get_stock_status(self, obj):
        """Return descriptive stock status"""
        if obj.stock_quantity == 0:
            return 'out_of_stock'
        elif obj.stock_quantity < 10:
            return 'low_stock'
        elif obj.stock_quantity < 50:
            return 'moderate_stock'
        else:
            return 'high_stock'
    
    def get_inventory_value(self, obj):
        """Return total inventory value for this product"""
        return float(obj.price * obj.stock_quantity)
    
    def get_days_since_created(self, obj):
        """Return number of days since product was created"""
        from django.utils import timezone
        return (timezone.now() - obj.created_date).days
    
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock_quantity(self, value):
        """Validate that stock quantity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for product list view with essential fields
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'price', 
            'stock_quantity', 
            'image_url', 
            'category_name',
            'is_in_stock',
            'stock_status',
            'created_date'
        ]
    
    def get_stock_status(self, obj):
        """Return descriptive stock status"""
        if obj.stock_quantity == 0:
            return 'out_of_stock'
        elif obj.stock_quantity < 10:
            return 'low_stock'
        elif obj.stock_quantity < 50:
            return 'moderate_stock'
        else:
            return 'high_stock'


class CategorySummarySerializer(serializers.ModelSerializer):
    """
    Minimal serializer for category references in other serializers
    """
    class Meta:
        model = Category
        fields = ['id', 'name']


# ==================== User Serializers ====================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password validation
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }
    
    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Create cart for user automatically
        Cart.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile viewing and updating
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']
    
    def validate_email(self, value):
        """Ensure email is unique when updating"""
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for nested representations
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs
    
    def save(self, **kwargs):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# ==================== Cart & Wishlist Serializers ====================

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items with product details
    """
    product_details = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_details', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
    
    def validate(self, attrs):
        """Validate quantity doesn't exceed available stock"""
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)
        
        # For updates, get the product from instance if not in attrs
        if not product and self.instance:
            product = self.instance.product
        
        if product and quantity > product.stock_quantity:
            raise serializers.ValidationError({
                "quantity": f"Requested quantity ({quantity}) exceeds available stock ({product.stock_quantity})."
            })
        
        return attrs


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping cart with all items
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_details', 'items', 'total_items', 
                  'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for wishlist items with product details
    """
    product_details = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_details', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def validate_product(self, value):
        """Ensure product exists and is not already in wishlist"""
        user = self.context['request'].user
        if Wishlist.objects.filter(user=user, product=value).exists():
            raise serializers.ValidationError("This product is already in your wishlist.")
        return value