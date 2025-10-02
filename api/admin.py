from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model
    """
    list_display = ['id', 'name', 'products_count']
    search_fields = ['name']
    ordering = ['name']
    
    def products_count(self, obj):
        """Display number of products in category"""
        return obj.products.count()
    products_count.short_description = 'Products Count'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product model
    """
    list_display = [
        'id', 
        'name', 
        'category', 
        'price', 
        'stock_quantity', 
        'is_in_stock',
        'created_date'
    ]
    list_filter = ['category', 'created_date', 'stock_quantity']
    search_fields = ['name', 'description']
    ordering = ['-created_date']
    list_editable = ['price', 'stock_quantity']
    readonly_fields = ['created_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('Timestamps', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        }),
    )
    
    def is_in_stock(self, obj):
        """Display stock status"""
        return obj.is_in_stock
    is_in_stock.boolean = True
    is_in_stock.short_description = 'In Stock'
