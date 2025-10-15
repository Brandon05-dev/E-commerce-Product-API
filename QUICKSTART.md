# 🚀 Quick Start Guide

This guide will get your E-commerce API up and running in minutes!

## Prerequisites

- Python 3.12+ installed
- pip and virtualenv
- Git (optional)

## Installation (5 minutes)

### Step 1: Clone or Download
```bash
cd /path/to/your/projects
# If using git:
git clone https://github.com/Brandon05-dev/E-commerce-Product-API.git
cd E-commerce-Product-API

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment
```bash
# Copy the example environment file
cp .env.example .env

# The default values work for development, but you can customize:
# - SECRET_KEY (use a secure random string for production)
# - DEBUG (set to False for production)
# - ALLOWED_HOSTS (add your domain for production)
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Create Admin User
```bash
python manage.py createsuperuser
# Follow the prompts to create your admin account
```

### Step 7: (Optional) Load Sample Data
```bash
python manage.py load_sample_data
```

### Step 8: Start Development Server
```bash
python manage.py runserver
```

**🎉 Done! Your API is now running at http://localhost:8000/api/**

---

## First API Calls

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Save the access token from the response!**

### 2. View Products
```bash
curl http://localhost:8000/api/products/
```

### 3. View Your Cart
```bash
curl http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Add Product to Cart
```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product": 1, "quantity": 2}'
```

---

## Access the Admin Panel

1. Go to http://localhost:8000/admin/
2. Login with your superuser credentials
3. You can now manage:
   - Users
   - Products
   - Categories
   - Carts
   - Wishlists

---

## Browse the API

Visit http://localhost:8000/api/ in your browser to see the browsable API interface where you can:
- View all available endpoints
- Test API calls directly from the browser
- See request/response examples

---

## Available Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/token/` - Login (get JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - View/update profile

### Products & Categories
- `GET /api/products/` - List products (with filtering & search)
- `GET /api/products/{id}/` - Get product details
- `GET /api/categories/` - List categories
- `GET /api/categories/{id}/products/` - Get category products

### Shopping Cart (Requires Authentication)
- `GET /api/cart/` - View cart
- `POST /api/cart/` - Add to cart
- `PUT /api/cart/items/{id}/` - Update quantity
- `DELETE /api/cart/items/{id}/` - Remove item
- `DELETE /api/cart/clear/` - Clear cart

### Wishlist (Requires Authentication)
- `GET /api/wishlist/` - List wishlist items
- `POST /api/wishlist/` - Add to wishlist
- `DELETE /api/wishlist/{id}/` - Remove from wishlist

---

## Testing

Run the test suite:
```bash
python manage.py test
```

Run specific tests:
```bash
# Test new features
python manage.py test api.test_new_features

# Test original features
python manage.py test api.tests
```

---

## Next Steps

1. **Read the Documentation**
   - See `README_COMPLETE.md` for full API documentation
   - Check `API_TESTING_GUIDE.md` for testing examples
   - Review `DEPLOYMENT.md` for production deployment

2. **Explore the API**
   - Use the browsable API at http://localhost:8000/api/
   - Try different filters and search queries
   - Test all cart and wishlist operations

3. **Customize**
   - Add your own products and categories
   - Modify the models to fit your needs
   - Customize serializers for additional fields

4. **Deploy**
   - Follow `DEPLOYMENT.md` for production deployment
   - Choose from Heroku, Render, Railway, or others
   - Set up PostgreSQL database
   - Configure domain and SSL

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Database errors
```bash
python manage.py migrate
```

### "Authentication credentials were not provided"
Make sure to include the JWT token:
```bash
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Can't create admin products
Make sure your user is a staff/admin:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='your_username')
>>> user.is_staff = True
>>> user.save()
```

---

## Getting Help

- **Documentation**: See `README_COMPLETE.md`
- **API Testing**: See `API_TESTING_GUIDE.md`
- **Deployment**: See `DEPLOYMENT.md`
- **Issues**: Open an issue on GitHub
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`

---

## Quick Command Reference

```bash
# Development
python manage.py runserver          # Start server
python manage.py test              # Run tests
python manage.py makemigrations    # Create migrations
python manage.py migrate           # Apply migrations
python manage.py createsuperuser   # Create admin user
python manage.py load_sample_data  # Load sample data
python manage.py shell             # Django shell

# Production
gunicorn ecommerce_api.wsgi:application    # Production server
python manage.py collectstatic --noinput   # Collect static files
python manage.py check --deploy            # Check deployment readiness
```

---

**🎉 You're all set! Start building your e-commerce application!**

For detailed documentation, see `README_COMPLETE.md`
