from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    """
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']
        
    def get_products_count(self, obj):
        """Return the number of products in this category"""
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    
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
            'is_in_stock'
        ]
        read_only_fields = ['created_date']
    
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
    Simplified serializer for product list view
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'price', 
            'stock_quantity', 
            'image_url', 
            'category_name',
            'is_in_stock'
        ]