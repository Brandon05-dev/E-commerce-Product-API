from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from .models import Category, Product, Cart, CartItem, Wishlist


# ==================== User Registration and Profile Tests ====================

class UserRegistrationTest(APITestCase):
    """Test cases for user registration"""
    
    def setUp(self):
        self.register_url = reverse('user-register')
        self.valid_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Verify cart was created
        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'cart'))
    
    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        data = self.valid_user_data.copy()
        data['password_confirm'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', str(response.data))
    
    def test_user_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        User.objects.create_user(
            username='existing',
            email='newuser@example.com',
            password='pass123'
        )
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(response.data))
    
    def test_user_registration_weak_password(self):
        """Test registration fails with weak password"""
        data = self.valid_user_data.copy()
        data['password'] = 'weak'
        data['password_confirm'] = 'weak'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_missing_required_fields(self):
        """Test registration fails with missing required fields"""
        # Missing email
        data = {'username': 'test', 'password': 'Pass123!', 'password_confirm': 'Pass123!'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing username
        data = {'email': 'test@test.com', 'password': 'Pass123!', 'password_confirm': 'Pass123!'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTest(APITestCase):
    """Test cases for user profile management"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile_url = reverse('user-profile')
        self.token = str(RefreshToken.for_user(self.user).access_token)
    
    def test_get_profile_authenticated(self):
        """Test authenticated user can view their profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_get_profile_unauthenticated(self):
        """Test unauthenticated user cannot view profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile_success(self):
        """Test user can update their profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
    
    def test_update_profile_duplicate_email(self):
        """Test profile update fails with duplicate email"""
        User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {'email': 'other@example.com'}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cannot_update_username(self):
        """Test user cannot change username"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {'username': 'newusername'}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')  # Should remain unchanged


# ==================== Cart Tests ====================

class CartTest(APITestCase):
    """Test cases for shopping cart functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            name='Product 1',
            price=Decimal('100.00'),
            stock_quantity=10,
            category=self.category
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            price=Decimal('50.00'),
            stock_quantity=5,
            category=self.category
        )
        self.cart_url = reverse('cart-list')
        self.token = str(RefreshToken.for_user(self.user).access_token)
    
    def test_get_cart_authenticated(self):
        """Test authenticated user can view their cart"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertIn('total_items', response.data)
        self.assertIn('total_price', response.data)
    
    def test_get_cart_unauthenticated(self):
        """Test unauthenticated user cannot access cart"""
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_product_to_cart(self):
        """Test adding a product to cart"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {'product': self.product1.id, 'quantity': 2}
        response = self.client.post(self.cart_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_items'], 2)
        
        # Verify cart item was created
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)
    
    def test_add_product_exceeds_stock(self):
        """Test adding more items than available stock fails"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {'product': self.product1.id, 'quantity': 100}
        response = self.client.post(self.cart_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', str(response.data))
    
    def test_add_same_product_twice(self):
        """Test adding same product twice updates quantity"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Add product first time
        data = {'product': self.product1.id, 'quantity': 2}
        self.client.post(self.cart_url, data)
        
        # Add same product again
        data = {'product': self.product1.id, 'quantity': 3}
        response = self.client.post(self.cart_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_items'], 5)
        
        # Verify only one cart item exists
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 5)
    
    def test_update_cart_item_quantity(self):
        """Test updating quantity of cart item"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Add product to cart
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        
        # Update quantity
        url = f'/api/cart/items/{cart_item.id}/'
        data = {'quantity': 5}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
    
    def test_update_cart_item_invalid_quantity(self):
        """Test updating cart item with invalid quantity fails"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        
        url = f'/api/cart/items/{cart_item.id}/'
        
        # Test zero quantity
        data = {'quantity': 0}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test exceeding stock
        data = {'quantity': 100}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_remove_product_from_cart(self):
        """Test removing a product from cart"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        
        url = f'/api/cart/items/{cart_item.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify item was deleted
        self.assertEqual(cart.items.count(), 0)
    
    def test_clear_cart(self):
        """Test clearing all items from cart"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=cart, product=self.product2, quantity=1)
        
        url = '/api/cart/clear/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 0)
        
        # Verify all items were deleted
        self.assertEqual(cart.items.count(), 0)
    
    def test_cart_total_calculation(self):
        """Test cart total price calculation"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=cart, product=self.product2, quantity=3)
        
        response = self.client.get(self.cart_url)
        expected_total = (self.product1.price * 2) + (self.product2.price * 3)
        self.assertEqual(float(response.data['total_price']), float(expected_total))


# ==================== Wishlist Tests ====================

class WishlistTest(APITestCase):
    """Test cases for wishlist functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            name='Product 1',
            price=Decimal('100.00'),
            stock_quantity=10,
            category=self.category
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            price=Decimal('50.00'),
            stock_quantity=5,
            category=self.category
        )
        self.wishlist_url = reverse('wishlist-list')
        self.token = str(RefreshToken.for_user(self.user).access_token)
    
    def test_get_wishlist_authenticated(self):
        """Test authenticated user can view their wishlist"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_wishlist_unauthenticated(self):
        """Test unauthenticated user cannot access wishlist"""
        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_product_to_wishlist(self):
        """Test adding a product to wishlist"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {'product': self.product1.id}
        response = self.client.post(self.wishlist_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify wishlist item was created
        self.assertTrue(Wishlist.objects.filter(user=self.user, product=self.product1).exists())
    
    def test_add_duplicate_product_to_wishlist(self):
        """Test adding duplicate product to wishlist fails"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Add product first time
        Wishlist.objects.create(user=self.user, product=self.product1)
        
        # Try to add same product again
        data = {'product': self.product1.id}
        response = self.client.post(self.wishlist_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_nonexistent_product_to_wishlist(self):
        """Test adding non-existent product fails"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {'product': 9999}
        response = self.client.post(self.wishlist_url, data)
        # Should return 400 or 404 - DRF returns 400 for invalid foreign key
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
    
    def test_remove_product_from_wishlist(self):
        """Test removing a product from wishlist"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        wishlist_item = Wishlist.objects.create(user=self.user, product=self.product1)
        
        url = reverse('wishlist-detail', kwargs={'pk': wishlist_item.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify item was deleted
        self.assertFalse(Wishlist.objects.filter(pk=wishlist_item.id).exists())
    
    def test_remove_product_from_wishlist_by_product_id(self):
        """Test removing product from wishlist by product ID"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        Wishlist.objects.create(user=self.user, product=self.product1)
        
        url = f'/api/wishlist/product/{self.product1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify item was deleted
        self.assertFalse(Wishlist.objects.filter(user=self.user, product=self.product1).exists())
    
    def test_list_wishlist_items(self):
        """Test listing all wishlist items"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        Wishlist.objects.create(user=self.user, product=self.product1)
        Wishlist.objects.create(user=self.user, product=self.product2)
        
        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_wishlist_isolation_between_users(self):
        """Test that users can only see their own wishlist"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create another user with wishlist items
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        Wishlist.objects.create(user=other_user, product=self.product1)
        Wishlist.objects.create(user=self.user, product=self.product2)
        
        # Current user should only see their own items
        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product'], self.product2.id)
