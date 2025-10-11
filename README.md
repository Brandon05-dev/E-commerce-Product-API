# E-commerce Product API

A production-ready Django REST Framework backend for an E-commerce API with comprehensive CRUD operations for products and categories, featuring JWT authentication.

## Features

- **Django REST Framework** with ViewSets and Routers
- **JWT Authentication** with djangorestframework-simplejwt
- **Permission-based Access Control** (Read-only for anonymous, full access for authenticated)
- **Category and Product Models** with proper relationships
- **CRUD Operations** for both categories and products
- **Advanced Filtering** by category, price range, stock status, and search
- **Pagination** support for large datasets
- **Admin Interface** with custom configurations
- **Comprehensive Test Suite** with 30+ test cases including JWT authentication tests
- **Sample Data Management** command
- **Production-ready Structure** with proper validation

## Project Structure

```
E-commerce-Product-API/
├── ecommerce_api/          # Django project
│   ├── __init__.py
│   ├── settings.py         # Project settings with DRF config
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── api/                   # Django app
│   ├── models.py          # Category & Product models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # ViewSets with filtering
│   ├── urls.py            # API routes
│   ├── admin.py           # Admin configurations
│   ├── tests.py           # Comprehensive test suite
│   └── management/        # Custom management commands
│       └── commands/
│           └── load_sample_data.py
├── requirements.txt       # Dependencies
├── manage.py             # Django management script
└── README.md            # This file
```

## Models

### Category
- `id` (Primary Key)
- `name` (CharField, unique)

### Product
- `id` (Primary Key)
- `name` (CharField)
- `description` (TextField)
- `price` (DecimalField with validation)
- `stock_quantity` (PositiveIntegerField)
- `image_url` (URLField)
- `created_date` (DateTimeField, auto_now_add)
- `category` (ForeignKey to Category)

## API Endpoints

### Authentication (JWT)
- `POST /api/auth/token/` - Obtain JWT token pair (access & refresh)
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token validity

### Products
- `GET /api/products/` - List products (paginated) 🔓 *Public*
- `POST /api/products/` - Create product � *Staff/Admin Only*
- `GET /api/products/{id}/` - Retrieve single product 🔓 *Public*
- `PUT /api/products/{id}/` - Update product (full) � *Staff/Admin Only*
- `PATCH /api/products/{id}/` - Update product (partial) � *Staff/Admin Only*
- `DELETE /api/products/{id}/` - Delete product � *Staff/Admin Only*

### Categories
- `GET /api/categories/` - List categories (paginated) 🔓 *Public*
- `POST /api/categories/` - Create category � *Staff/Admin Only*
- `GET /api/categories/{id}/` - Retrieve single category 🔓 *Public*
- `PUT /api/categories/{id}/` - Update category (full) � *Staff/Admin Only*
- `PATCH /api/categories/{id}/` - Update category (partial) � *Staff/Admin Only*
- `DELETE /api/categories/{id}/` - Delete category � *Staff/Admin Only*

### Custom Actions
- `GET /api/products/low_stock/` - Get products with stock < 10 🔓 *Public*
- `POST /api/products/{id}/update_stock/` - Update product stock � *Staff/Admin Only*
- `GET /api/categories/{id}/products/` - Get products in category 🔓 *Public*

## Query Parameters & Advanced Filtering

### Product Filtering
- `?category=<id|name>` - Filter by category ID or name (case-insensitive)
- `?min_price=<value>` - Filter by minimum price
- `?max_price=<value>` - Filter by maximum price
- `?in_stock=<true|false>` - Filter products by stock status
- `?min_stock=<value>` - Filter by minimum stock quantity
- `?created_after=<ISO_date>` - Filter products created after date
- `?created_before=<ISO_date>` - Filter products created before date
- `?search=<term>` - Search in name, description, and category name
- `?ordering=<field>` - Order by field (prefix with `-` for descending)

### Category Filtering
- `?search=<term>` - Search categories by name
- `?ordering=<field>` - Order categories by field

### Pagination Parameters
- `?page=<number>` - Page number (default: 1)
- `?page_size=<number>` - Items per page (default: 20 for products, 10 for categories)

### Ordering Fields
**Products:**
- `name` - Product name
- `price` - Product price  
- `created_date` - Creation date
- `stock_quantity` - Stock quantity

**Categories:**
- `name` - Category name
- `id` - Category ID

### Enhanced Search Examples
```bash
# Search across name, description, and category
GET /api/products/?search=wireless headphones

# Multi-term search (finds products matching any term)
GET /api/products/?search=gaming laptop

# Search by category name
GET /api/products/?category=electronics

# Search categories
GET /api/categories/?search=book
```

### Advanced Filtering Examples
```bash
# Get electronics products under $500
GET /api/products/?category=electronics&max_price=500

# Get products with low stock (less than 10 items)
GET /api/products/?max_stock=9

# Get products created in the last week
GET /api/products/?created_after=2025-10-04T00:00:00Z

# Get out-of-stock clothing items
GET /api/products/?category=clothing&in_stock=false

# Combine filters: expensive electronics in stock, ordered by price
GET /api/products/?category=1&min_price=1000&in_stock=true&ordering=price

# Get products with moderate to high stock, ordered by name
GET /api/products/?min_stock=20&ordering=name
```

### Pagination Examples
```bash
# Get first page with 10 items per page
GET /api/products/?page=1&page_size=10

# Get second page of categories
GET /api/categories/?page=2

# Large page size for bulk operations (max 100 for products)
GET /api/products/?page_size=50
```

### Combined Query Examples
```bash
# Search for laptops under $2000, in stock, ordered by price (desc)
GET /api/products/?search=laptop&max_price=2000&in_stock=true&ordering=-price

# Get electronics created this month with pagination
GET /api/products/?category=electronics&created_after=2025-10-01T00:00:00Z&page_size=5

# Search and filter category products
GET /api/categories/1/products/?search=gaming&min_price=100&ordering=name
```

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Brandon05-dev/E-commerce-Product-API.git
cd E-commerce-Product-API
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load sample data (optional)
```bash
python manage.py load_sample_data
```

### 6. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Start development server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## Testing

Run the comprehensive test suite:
```bash
python manage.py test api
```

### Test Coverage Includes:
- **Model validation tests** - Product and Category model validation
- **API endpoint tests** - CRUD operations for all endpoints
- **Search functionality** - Multi-term search, category search, description search
- **Advanced filtering** - Price range, stock status, date filtering, category filtering
- **Pagination tests** - Custom pagination metadata and page sizing
- **Ordering tests** - Sort by various fields in ascending/descending order
- **Combined filtering** - Multiple filters working together
- **Permission tests** - Role-based access control (Anonymous, Regular, Staff/Admin)
- **JWT authentication** - Token generation, validation, refresh, expiration
- **Error handling** - Invalid parameters, malformed requests, edge cases
- **Enhanced serializers** - Additional fields and computed values

### Test Categories:
1. **ProductModelTest** - Product model functionality
2. **CategoryModelTest** - Category model functionality  
3. **ProductAPITest** - Basic product API operations
4. **CategoryAPITest** - Basic category API operations
5. **SearchFilterPaginationTest** - ⭐ New comprehensive filtering tests
6. **JWTAuthenticationTest** - JWT token functionality
7. **AdminPermissionTest** - Role-based permissions

### Running Specific Test Categories:
```bash
# Run only the new search/filter/pagination tests
python manage.py test api.tests.SearchFilterPaginationTest

# Run permission tests
python manage.py test api.tests.AdminPermissionTest

# Run with verbose output
python manage.py test api --verbosity=2
```

## Admin Interface

Access the Django admin at `http://127.0.0.1:8000/admin/` to:
- Manage categories and products
- View product stock levels
- Filter products by various criteria
- Bulk edit operations

## API Documentation

The API uses Django REST Framework's browsable API. Visit any endpoint in your browser to see:
- Interactive API forms
- Request/response examples
- Available filters and parameters

Example: `http://127.0.0.1:8000/api/products/`

## Enhanced API Responses

### GET /api/products/ (Enhanced Pagination)
```json
{
  "count": 25,
  "total_pages": 2,
  "current_page": 1,
  "page_size": 20,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Smartphone XYZ",
      "price": "699.99",
      "stock_quantity": 50,
      "image_url": "https://example.com/smartphone.jpg",
      "category_name": "Electronics",
      "is_in_stock": true,
      "stock_status": "high_stock",
      "created_date": "2025-10-02T08:41:30.123456Z"
    }
  ]
}
```

### GET /api/products/1/ (Enhanced Detail)
```json
{
  "id": 1,
  "name": "Smartphone XYZ",
  "description": "Latest smartphone with advanced features",
  "price": "699.99",
  "stock_quantity": 50,
  "image_url": "https://example.com/smartphone.jpg",
  "created_date": "2025-10-02T08:41:30.123456Z",
  "category": 1,
  "category_name": "Electronics",
  "category_details": {
    "id": 1,
    "name": "Electronics"
  },
  "is_in_stock": true,
  "stock_status": "high_stock",
  "inventory_value": 34999.50,
  "days_since_created": 9
}
```

### GET /api/categories/ (Enhanced)
```json
{
  "count": 3,
  "total_pages": 1,
  "current_page": 1,
  "page_size": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Electronics",
      "products_count": 15,
      "in_stock_products_count": 12,
      "average_price": 456.78,
      "total_inventory_value": 125430.50
    }
  ]
}
```

### GET /api/categories/1/products/ (Enhanced Category Products)
```json
{
  "count": 15,
  "total_pages": 1,
  "current_page": 1,
  "page_size": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Smartphone XYZ",
      "price": "699.99",
      "stock_quantity": 50,
      "image_url": "https://example.com/smartphone.jpg",
      "category_name": "Electronics",
      "is_in_stock": true,
      "stock_status": "high_stock",
      "created_date": "2025-10-02T08:41:30.123456Z"
    }
  ]
}
```

### Stock Status Values
- `high_stock` - 50+ items in stock
- `moderate_stock` - 10-49 items in stock  
- `low_stock` - 1-9 items in stock
- `out_of_stock` - 0 items in stock

## Production Considerations

- **Database**: Switch from SQLite to PostgreSQL/MySQL for production
- **Environment Variables**: Use django-environ for sensitive settings
- **Static Files**: Configure proper static file serving
- **CORS**: Add django-cors-headers if needed for frontend
- **Authentication**: Implement JWT or session-based auth
- **Rate Limiting**: Add throttling for API endpoints
- **Logging**: Configure proper logging
- **Deployment**: Use Gunicorn/uWSGI with Nginx

## JWT Authentication

### How to authenticate:

1. **Obtain Token**:
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

2. **Use Token in Requests**:
```bash
curl -H "Authorization: Bearer your_access_token" \
  http://localhost:8000/api/products/
```

3. **Refresh Token**:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

### Permission Model:
- **Anonymous Users**: Can read all data (GET requests)
- **Regular Authenticated Users**: Can only read all data (GET requests)
- **Staff/Admin Users**: Can read and write all data (GET, POST, PUT, PATCH, DELETE)
- **Invalid/Expired Tokens**: Return 401 Unauthorized

### Token Configuration:
- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Token Rotation**: Enabled (new refresh token on each refresh)

## Demo Script

Run the included demo script to test JWT authentication:

```bash
# Make sure server is running
python manage.py runserver

# In another terminal
python demo_jwt_auth.py
```

This will demonstrate:
- Token obtaining and verification
- Public vs protected endpoints
- Authentication failure scenarios
- Token refresh workflow

## Role-Based Permissions 🛡️

The API implements role-based access control to ensure data security and proper authorization:

### Permission Levels

1. **🔓 Anonymous Users (Public Access)**
   - Can read all products and categories
   - Cannot create, update, or delete any data
   - No authentication required

2. **🔒 Regular Authenticated Users**
   - Can read all products and categories  
   - Cannot create, update, or delete any data
   - Must provide valid JWT token
   - Returns `403 Forbidden` for write operations

3. **👑 Staff/Admin Users**
   - Full access to all operations
   - Can create, read, update, and delete products and categories
   - Must provide valid JWT token
   - Must have `is_staff=True` or `is_superuser=True`

### How to Create Staff/Admin Users

#### Via Django Admin:
1. Access `/admin/` with superuser credentials
2. Go to Users section
3. Edit user and check "Staff status" or "Superuser status"

#### Via Django Shell:
```python
# Create staff user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='your_username')
>>> user.is_staff = True
>>> user.save()

# Or create superuser directly
python manage.py createsuperuser
```

### Testing Permissions

```bash
# 1. Create regular user and get token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "regular_user", "password": "password"}'

# 2. Try to create product (should fail with 403)
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <regular_user_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": "99.99", "category": 1}'

# 3. Same request with staff/admin token (should succeed)
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <staff_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": "99.99", "category": 1}'
```

### Implementation Details

The permission system uses a custom `IsAdminOrReadOnly` permission class that:
- Allows all users (including anonymous) to perform safe operations (GET, HEAD, OPTIONS)
- Restricts unsafe operations (POST, PUT, PATCH, DELETE) to staff and admin users only
- Returns appropriate HTTP status codes (403 Forbidden for unauthorized write attempts)

## Enhanced Features ✨

### 🔍 Advanced Search & Filtering
- **Multi-field search**: Search across product names, descriptions, and category names
- **Multi-term search**: Find products matching any of multiple search terms
- **Smart filtering**: Filter by category ID or name, price range, stock levels, creation date
- **Combined filters**: Mix and match multiple filters for precise results

### 📄 Enhanced Pagination
- **Custom pagination**: Detailed pagination metadata with page counts and navigation
- **Flexible page sizes**: Configurable page sizes with sensible defaults and limits
- **Context-aware**: Different pagination settings for different endpoints

### 📊 Rich API Responses  
- **Stock status indicators**: Human-readable stock levels (high/moderate/low/out)
- **Calculated fields**: Inventory values, days since creation, category statistics
- **Enhanced metadata**: Comprehensive category statistics including average prices

### ⚡ Performance Optimizations
- **Query optimization**: select_related() to minimize database queries
- **Efficient filtering**: Database-level filtering for better performance
- **Smart serializers**: Different serializers for list vs detail views

### 🎯 Flexible Ordering
- **Multiple sort fields**: Order by name, price, date, stock quantity
- **Ascending/descending**: Support for both sort directions
- **Default ordering**: Sensible defaults with newest products first

## Dependencies

- Django 5.2.5
- djangorestframework 3.15.2
- djangorestframework-simplejwt 5.3.0
- django-filter 24.3 (for advanced filtering)
- Pillow 10.0.0 (for ImageField support)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.