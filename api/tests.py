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
    
    def test_create_product_as_regular_user_forbidden(self):
        """Test POST /api/products/ endpoint fails for regular users"""
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)  # Only the initial product
    
    def test_create_product_invalid_price_as_regular_user_forbidden(self):
        """Test creating product with invalid price fails for regular users"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Invalid Product',
            'price': '-10.00',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_product_as_regular_user_forbidden(self):
        """Test PUT /api/products/{id}/ endpoint fails for regular users"""
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Test Product')  # Should remain unchanged
    
    def test_delete_product_as_regular_user_forbidden(self):
        """Test DELETE /api/products/{id}/ endpoint fails for regular users"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)  # Should remain unchanged
    
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


class SearchFilterPaginationTest(APITestCase):
    """Test cases for enhanced search, filtering, and pagination features"""
    
    def setUp(self):
        # Create test categories
        self.electronics = Category.objects.create(name="Electronics")
        self.books = Category.objects.create(name="Books")
        self.clothing = Category.objects.create(name="Clothing")
        
        # Create test products with varied data
        self.products = [
            Product.objects.create(
                name="Smartphone Pro",
                description="Latest flagship smartphone with advanced features",
                price=Decimal('999.99'),
                stock_quantity=25,
                category=self.electronics
            ),
            Product.objects.create(
                name="Laptop Gaming",
                description="High-performance gaming laptop",
                price=Decimal('1599.99'),
                stock_quantity=5,
                category=self.electronics
            ),
            Product.objects.create(
                name="Python Programming Book",
                description="Comprehensive guide to Python programming",
                price=Decimal('49.99'),
                stock_quantity=100,
                category=self.books
            ),
            Product.objects.create(
                name="T-Shirt Cotton",
                description="Premium cotton t-shirt",
                price=Decimal('29.99'),
                stock_quantity=0,
                category=self.clothing
            ),
            Product.objects.create(
                name="Wireless Headphones",
                description="Noise-cancelling wireless headphones",
                price=Decimal('299.99'),
                stock_quantity=15,
                category=self.electronics
            ),
        ]
        
        self.products_url = reverse('product-list')
        self.categories_url = reverse('category-list')
    
    def test_enhanced_search_functionality(self):
        """Test enhanced search with multiple terms"""
        # Search by product name
        response = self.client.get(f"{self.products_url}?search=smartphone")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Smartphone Pro')
        
        # Search by description
        response = self.client.get(f"{self.products_url}?search=gaming")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop Gaming')
        
        # Search by category name
        response = self.client.get(f"{self.products_url}?search=electronics")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Multi-term search
        response = self.client.get(f"{self.products_url}?search=python programming")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Python Programming Book')
    
    def test_price_range_filtering(self):
        """Test filtering by price range"""
        # Filter by minimum price
        response = self.client.get(f"{self.products_url}?min_price=100")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(float(product['price']) >= 100 for product in results))
        
        # Filter by maximum price  
        response = self.client.get(f"{self.products_url}?max_price=100")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(float(product['price']) <= 100 for product in results))
        
        # Filter by price range
        response = self.client.get(f"{self.products_url}?min_price=50&max_price=500")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(50 <= float(product['price']) <= 500 for product in results))
    
    def test_category_filtering(self):
        """Test filtering by category ID and name"""
        # Filter by category ID
        response = self.client.get(f"{self.products_url}?category={self.electronics.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Filter by category name
        response = self.client.get(f"{self.products_url}?category=books")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category_name'], 'Books')
    
    def test_stock_filtering(self):
        """Test filtering by stock status"""
        # Filter in-stock products
        response = self.client.get(f"{self.products_url}?in_stock=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(product['is_in_stock'] for product in results))
        
        # Filter out-of-stock products
        response = self.client.get(f"{self.products_url}?in_stock=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(not product['is_in_stock'] for product in results))
        
        # Filter by minimum stock quantity
        response = self.client.get(f"{self.products_url}?min_stock=20")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(product['stock_quantity'] >= 20 for product in results))
    
    def test_ordering_functionality(self):
        """Test ordering by different fields"""
        # Order by price ascending
        response = self.client.get(f"{self.products_url}?ordering=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        prices = [float(product['price']) for product in results]
        self.assertEqual(prices, sorted(prices))
        
        # Order by price descending
        response = self.client.get(f"{self.products_url}?ordering=-price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        prices = [float(product['price']) for product in results]
        self.assertEqual(prices, sorted(prices, reverse=True))
        
        # Order by name
        response = self.client.get(f"{self.products_url}?ordering=name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        names = [product['name'] for product in results]
        self.assertEqual(names, sorted(names))
    
    def test_combined_filtering(self):
        """Test combining multiple filters"""
        response = self.client.get(
            f"{self.products_url}?category={self.electronics.pk}&min_price=200&in_stock=true&ordering=price"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        
        # Check all filters are applied
        for product in results:
            self.assertEqual(product['category_name'], 'Electronics')
            self.assertGreaterEqual(float(product['price']), 200)
            self.assertTrue(product['is_in_stock'])
        
        # Check ordering
        if len(results) > 1:
            prices = [float(product['price']) for product in results]
            self.assertEqual(prices, sorted(prices))
    
    def test_pagination_metadata(self):
        """Test custom pagination response format"""
        response = self.client.get(f"{self.products_url}?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination metadata
        self.assertIn('count', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('current_page', response.data)
        self.assertIn('page_size', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Check page size is respected
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['page_size'], 2)
        self.assertEqual(response.data['current_page'], 1)
    
    def test_category_products_endpoint_with_filtering(self):
        """Test category products endpoint with filtering"""
        category_products_url = reverse('category-products', kwargs={'pk': self.electronics.pk})
        
        # Test basic endpoint
        response = self.client.get(category_products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # We have 3 electronics products in the test data
        self.assertEqual(len(response.data['results']), 3)
        
        # Test with price filtering
        response = self.client.get(f"{category_products_url}?min_price=500")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(float(product['price']) >= 500 for product in results))
        
        # Test with search
        response = self.client.get(f"{category_products_url}?search=gaming")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop Gaming')
    
    def test_invalid_filter_parameters(self):
        """Test handling of invalid filter parameters"""
        # Invalid price format
        response = self.client.get(f"{self.products_url}?min_price=invalid")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all products (filter ignored)
        
        # Invalid category ID
        response = self.client.get(f"{self.products_url}?category=999")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
        # Invalid stock quantity
        response = self.client.get(f"{self.products_url}?min_stock=invalid")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all products (filter ignored)
    
    def test_empty_search_results(self):
        """Test search with no matching results"""
        response = self.client.get(f"{self.products_url}?search=nonexistent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)
    
    def test_category_search_and_ordering(self):
        """Test category search and ordering"""
        # Test category search
        response = self.client.get(f"{self.categories_url}?search=book")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Books')
        
        # Test category ordering
        response = self.client.get(f"{self.categories_url}?ordering=name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        names = [category['name'] for category in results]
        self.assertEqual(names, sorted(names))
    
    def test_enhanced_serializer_fields(self):
        """Test enhanced serializer fields in responses"""
        # Test product detail serializer
        product = self.products[0]
        product_detail_url = reverse('product-detail', kwargs={'pk': product.pk})
        response = self.client.get(product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check enhanced fields
        self.assertIn('stock_status', response.data)
        self.assertIn('inventory_value', response.data)
        self.assertIn('days_since_created', response.data)
        self.assertIn('category_details', response.data)
        
        # Test category detail serializer
        category_detail_url = reverse('category-detail', kwargs={'pk': self.electronics.pk})
        response = self.client.get(category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check enhanced fields
        self.assertIn('products_count', response.data)
        self.assertIn('in_stock_products_count', response.data)
        self.assertIn('average_price', response.data)
        self.assertIn('total_inventory_value', response.data)


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
    
    def test_create_category_as_regular_user_forbidden(self):
        """Test POST /api/categories/ endpoint fails for regular users"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Books'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(), 1)  # Only the initial category


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
    
    def test_regular_authenticated_user_cannot_create_product(self):
        """Test that regular authenticated users cannot create products"""
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)  # Only the initial product
    
    def test_regular_authenticated_user_cannot_update_product(self):
        """Test that regular authenticated users cannot update products"""
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Test Product')  # Should remain unchanged
    
    def test_regular_authenticated_user_cannot_delete_product(self):
        """Test that regular authenticated users cannot delete products"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)  # Should remain unchanged
    
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
    
    def test_regular_authenticated_user_cannot_create_category(self):
        """Test that regular authenticated users cannot create categories"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Books'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(), 1)  # Only the initial category


class AdminPermissionTest(APITestCase):
    """Test cases for admin/staff role-based permissions"""
    
    def setUp(self):
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpass123',
            email='regular@example.com'
        )
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='testpass123',
            email='staff@example.com',
            is_staff=True
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='testpass123',
            email='admin@example.com',
            is_superuser=True,
            is_staff=True
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
        self.categories_url = reverse('category-list')
        self.product_detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})
        self.category_detail_url = reverse('category-detail', kwargs={'pk': self.category.pk})
    
    def get_jwt_token(self, user):
        """Helper method to get JWT token for any user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_anonymous_user_can_read_products(self):
        """Test that anonymous users can read products"""
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_anonymous_user_can_read_categories(self):
        """Test that anonymous users can read categories"""
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_anonymous_user_cannot_create_product(self):
        """Test that anonymous users cannot create products"""
        data = {
            'name': 'Unauthorized Product',
            'description': 'Should not be created',
            'price': '99.99',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_anonymous_user_cannot_create_category(self):
        """Test that anonymous users cannot create categories"""
        data = {'name': 'Unauthorized Category'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_regular_user_cannot_create_product(self):
        """Test that regular authenticated users cannot create products"""
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Regular User Product',
            'description': 'Should not be created',
            'price': '99.99',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_regular_user_cannot_create_category(self):
        """Test that regular authenticated users cannot create categories"""
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Regular User Category'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_regular_user_cannot_update_product(self):
        """Test that regular authenticated users cannot update products"""
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': '199.99',
            'stock_quantity': 15,
            'category': self.category.pk
        }
        response = self.client.put(self.product_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_regular_user_cannot_update_category(self):
        """Test that regular authenticated users cannot update categories"""
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Updated Category'}
        response = self.client.put(self.category_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_regular_user_cannot_delete_product(self):
        """Test that regular authenticated users cannot delete products"""
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_regular_user_cannot_delete_category(self):
        """Test that regular authenticated users cannot delete categories"""
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_staff_user_can_create_product(self):
        """Test that staff users can create products"""
        token = self.get_jwt_token(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Staff Product',
            'description': 'Created by staff',
            'price': '149.99',
            'stock_quantity': 5,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
    
    def test_staff_user_can_create_category(self):
        """Test that staff users can create categories"""
        token = self.get_jwt_token(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Staff Category'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
    
    def test_staff_user_can_update_product(self):
        """Test that staff users can update products"""
        token = self.get_jwt_token(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Staff Updated Product',
            'description': 'Updated by staff',
            'price': '199.99',
            'stock_quantity': 15,
            'category': self.category.pk
        }
        response = self.client.put(self.product_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Staff Updated Product')
    
    def test_staff_user_can_update_category(self):
        """Test that staff users can update categories"""
        token = self.get_jwt_token(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Staff Updated Category'}
        response = self.client.put(self.category_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Staff Updated Category')
    
    def test_staff_user_can_delete_product(self):
        """Test that staff users can delete products"""
        token = self.get_jwt_token(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
    
    def test_staff_user_can_delete_category(self):
        """Test that staff users can delete categories"""
        # First delete the product that references this category
        self.product.delete()
        
        token = self.get_jwt_token(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)
    
    def test_admin_user_can_create_product(self):
        """Test that admin users can create products"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Admin Product',
            'description': 'Created by admin',
            'price': '299.99',
            'stock_quantity': 20,
            'category': self.category.pk
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
    
    def test_admin_user_can_create_category(self):
        """Test that admin users can create categories"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Admin Category'}
        response = self.client.post(self.categories_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
    
    def test_admin_user_can_update_product(self):
        """Test that admin users can update products"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Admin Updated Product',
            'description': 'Updated by admin',
            'price': '399.99',
            'stock_quantity': 25,
            'category': self.category.pk
        }
        response = self.client.put(self.product_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Admin Updated Product')
    
    def test_admin_user_can_update_category(self):
        """Test that admin users can update categories"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'name': 'Admin Updated Category'}
        response = self.client.put(self.category_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Admin Updated Category')
    
    def test_admin_user_can_delete_product(self):
        """Test that admin users can delete products"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
    
    def test_admin_user_can_delete_category(self):
        """Test that admin users can delete categories"""
        # First delete the product that references this category
        self.product.delete()
        
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)
