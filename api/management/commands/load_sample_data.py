from django.core.management.base import BaseCommand
from decimal import Decimal
from api.models import Category, Product


class Command(BaseCommand):
    help = 'Load sample data for testing the E-commerce API'

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")
        
        # Create categories
        categories_data = [
            "Electronics",
            "Books",
            "Clothing",
            "Home & Garden",
            "Sports & Outdoors"
        ]
        
        categories = []
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(name=cat_name)
            categories.append(category)
            if created:
                self.stdout.write(f"Created category: {cat_name}")
        
        # Create products
        products_data = [
            {
                "name": "Smartphone XYZ",
                "description": "Latest smartphone with advanced features",
                "price": Decimal("699.99"),
                "stock_quantity": 50,
                "image_url": "https://example.com/smartphone.jpg",
                "category": categories[0]  # Electronics
            },
            {
                "name": "Laptop Pro",
                "description": "High-performance laptop for professionals",
                "price": Decimal("1299.99"),
                "stock_quantity": 25,
                "image_url": "https://example.com/laptop.jpg",
                "category": categories[0]  # Electronics
            },
            {
                "name": "Python Programming Book",
                "description": "Learn Python programming from scratch",
                "price": Decimal("39.99"),
                "stock_quantity": 100,
                "image_url": "https://example.com/python-book.jpg",
                "category": categories[1]  # Books
            },
            {
                "name": "T-Shirt",
                "description": "Comfortable cotton t-shirt",
                "price": Decimal("19.99"),
                "stock_quantity": 200,
                "image_url": "https://example.com/tshirt.jpg",
                "category": categories[2]  # Clothing
            },
            {
                "name": "Garden Tools Set",
                "description": "Complete set of garden tools",
                "price": Decimal("89.99"),
                "stock_quantity": 30,
                "image_url": "https://example.com/garden-tools.jpg",
                "category": categories[3]  # Home & Garden
            },
            {
                "name": "Tennis Racket",
                "description": "Professional tennis racket",
                "price": Decimal("149.99"),
                "stock_quantity": 15,
                "image_url": "https://example.com/tennis-racket.jpg",
                "category": categories[4]  # Sports & Outdoors
            }
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults=product_data
            )
            if created:
                self.stdout.write(f"Created product: {product_data['name']}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created sample data: "
                f"{Category.objects.count()} categories, "
                f"{Product.objects.count()} products"
            )
        )