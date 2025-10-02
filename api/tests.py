from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
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
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
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
    
    def get_jwt_token(self):
        """Helper method to get JWT token for test user"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)
    
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
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
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
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
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
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
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
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
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
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.category = Category.objects.create(name="Electronics")
        self.categories_url = reverse('category-list')
    
    def get_jwt_token(self):
        """Helper method to get JWT token for test user"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)
    
    def test_get_categories_list(self):
        """Test GET /api/categories/ endpoint"""
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Electronics')
    
    def test_create_category(self):
        """Test POST /api/categories/ endpoint"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Books'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Books')


class JWTAuthenticationTest(APITestCase):
    """Test cases for JWT Authentication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            stock_quantity=10,
            category=self.category
        )
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.verify_url = reverse('token_verify')
        self.products_url = reverse('product-list')
        self.categories_url = reverse('category-list')
        self.product_detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})
    
    def get_jwt_token(self):
        """Helper method to get JWT token for test user"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)
    
    def test_obtain_jwt_token(self):
        """Test JWT token obtain endpoint"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_obtain_token_invalid_credentials(self):
        """Test JWT token obtain with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_jwt_token(self):
        """Test JWT token refresh endpoint"""
        # First get a token
        refresh = RefreshToken.for_user(self.user)
        data = {'refresh': str(refresh)}
        
        response = self.client.post(self.refresh_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_verify_jwt_token(self):
        """Test JWT token verify endpoint"""
        token = self.get_jwt_token()
        data = {'token': token}
        
        response = self.client.post(self.verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_verify_invalid_jwt_token(self):
        """Test JWT token verify with invalid token"""
        data = {'token': 'invalid_token'}
        
        response = self.client.post(self.verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_can_read_products(self):
        """Test that unauthenticated users can read products"""
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthenticated_user_cannot_create_product(self):
        """Test that unauthenticated users cannot create products"""
        data = {
            'name': 'Unauthorized Product',
            'description': 'Should not be created',
            'price': '99.99',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_update_product(self):
        """Test that unauthenticated users cannot update products"""
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': '199.99',
            'stock_quantity': 15,
            'category': self.category.pk
        }
        response = self.client.put(self.product_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_cannot_delete_product(self):
        """Test that unauthenticated users cannot delete products"""
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_create_product(self):
        """Test that authenticated users can create products"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
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
    
    def test_authenticated_user_can_update_product(self):
        """Test that authenticated users can update products"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
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
    
    def test_authenticated_user_can_delete_product(self):
        """Test that authenticated users can delete products"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
    
    def test_expired_token_returns_401(self):
        """Test that expired JWT token returns 401 Unauthorized"""
        # Create an expired token (this is a simplified test)
        # In a real test, you'd need to manipulate the token's expiry time
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjA5NDU5MjAwLCJqdGkiOiJmZDJmOWQ1ZTNlN2Q0NmU4OGVhNTVmYzhmYWIyZDdkOSIsInVzZXJfaWQiOjF9.NHlztMGER7UADHZJlxNG0WSi3974NMbvd5MvF0XykWY"
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_token}')
        
        data = {
            'name': 'Should Fail',
            'description': 'Should not be created',
            'price': '99.99',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_invalid_token_returns_401(self):
        """Test that invalid JWT token returns 401 Unauthorized"""
        invalid_token = "invalid.jwt.token"
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {invalid_token}')
        
        data = {
            'name': 'Should Fail',
            'description': 'Should not be created',
            'price': '99.99',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_can_read_categories(self):
        """Test that unauthenticated users can read categories"""
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthenticated_user_cannot_create_category(self):
        """Test that unauthenticated users cannot create categories"""
        data = {'name': 'Unauthorized Category'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_create_category(self):
        """Test that authenticated users can create categories"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Books'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
