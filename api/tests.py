from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Category, Product


class ProductModelTest(TestCase):
    """Test cases for Product model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            stock_quantity=10,
            category=self.category
        )
    
    def test_product_creation(self):
        """Test product is created correctly"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.stock_quantity, 10)
        self.assertEqual(self.product.category, self.category)
    
    def test_product_str_method(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), "Test Product")
    
    def test_is_in_stock_property(self):
        """Test is_in_stock property"""
        self.assertTrue(self.product.is_in_stock)
        
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)


class CategoryModelTest(TestCase):
    """Test cases for Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
    
    def test_category_creation(self):
        """Test category is created correctly"""
        self.assertEqual(self.category.name, "Electronics")
    
    def test_category_str_method(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), "Electronics")


class ProductAPITest(APITestCase):
    """Test cases for Product API endpoints"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            stock_quantity=10,
            category=self.category
        )
        self.products_url = reverse('product-list')
        self.product_detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})
    
    def test_get_products_list(self):
        """Test GET /api/products/ endpoint"""
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Product')
    
    def test_get_single_product(self):
        """Test GET /api/products/{id}/ endpoint"""
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['category_name'], 'Electronics')
    
    def test_create_product(self):
        """Test POST /api/products/ endpoint"""
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '149.99',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Product')
    
    def test_create_product_invalid_price(self):
        """Test creating product with invalid price"""
        data = {
            'name': 'Invalid Product',
            'price': '-10.00',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_product(self):
        """Test PUT /api/products/{id}/ endpoint"""
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': '199.99',
            'stock_quantity': 15,
            'category': self.category.pk
        }
        response = self.client.put(self.product_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(self.product.price, Decimal('199.99'))
    
    def test_delete_product(self):
        """Test DELETE /api/products/{id}/ endpoint"""
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
    
    def test_product_search(self):
        """Test product search functionality"""
        response = self.client.get(f"{self.products_url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_filter_by_category(self):
        """Test filtering products by category"""
        response = self.client.get(f"{self.products_url}?category={self.category.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CategoryAPITest(APITestCase):
    """Test cases for Category API endpoints"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.categories_url = reverse('category-list')
    
    def test_get_categories_list(self):
        """Test GET /api/categories/ endpoint"""
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Electronics')
    
    def test_create_category(self):
        """Test POST /api/categories/ endpoint"""
        data = {'name': 'Books'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Books')
