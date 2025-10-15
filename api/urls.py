from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet,
    UserRegistrationView, UserProfileView, PasswordChangeView,
    CartViewSet, WishlistViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    # User authentication and profile
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
    
    # Include router URLs
    path('', include(router.urls)),
]