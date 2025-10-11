from rest_framework import serializers
from django.db.models import Count, Avg
from .models import Category, Product


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