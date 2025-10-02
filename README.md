# E-commerce Product API

A production-ready Django REST Framework backend for an E-commerce API with comprehensive CRUD operations for products and categories.

## Features

- **Django REST Framework** with ViewSets and Routers
- **Category and Product Models** with proper relationships
- **CRUD Operations** for both categories and products
- **Advanced Filtering** by category, price range, stock status, and search
- **Pagination** support for large datasets
- **Admin Interface** with custom configurations
- **Comprehensive Test Suite** with 15+ test cases
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

### Products
- `GET /api/products/` - List products (paginated)
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Retrieve single product
- `PUT /api/products/{id}/` - Update product (full)
- `PATCH /api/products/{id}/` - Update product (partial)
- `DELETE /api/products/{id}/` - Delete product

### Categories
- `GET /api/categories/` - List categories (paginated)
- `POST /api/categories/` - Create category
- `GET /api/categories/{id}/` - Retrieve single category
- `PUT /api/categories/{id}/` - Update category (full)
- `PATCH /api/categories/{id}/` - Update category (partial)
- `DELETE /api/categories/{id}/` - Delete category

### Custom Actions
- `GET /api/products/low_stock/` - Get products with stock < 10
- `POST /api/products/{id}/update_stock/` - Update product stock
- `GET /api/categories/{id}/products/` - Get products in category

## Query Parameters

### Product Filtering
- `?category=<id>` - Filter by category ID
- `?min_price=<value>` - Filter by minimum price
- `?max_price=<value>` - Filter by maximum price
- `?in_stock=true` - Filter products in stock
- `?search=<term>` - Search in name and description

### Examples
```bash
# Get products in category 1
GET /api/products/?category=1

# Get products between $50-$200
GET /api/products/?min_price=50&max_price=200

# Search for "laptop"
GET /api/products/?search=laptop

# Get in-stock electronics
GET /api/products/?category=1&in_stock=true
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

The test suite includes:
- Model validation tests
- API endpoint tests (GET, POST, PUT, DELETE)
- Filtering and search tests
- Error handling tests
- Edge case tests

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

## Sample API Responses

### GET /api/products/
```json
{
  "count": 6,
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
      "is_in_stock": true
    }
  ]
}
```

### GET /api/products/1/
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
  "is_in_stock": true
}
```

## Production Considerations

- **Database**: Switch from SQLite to PostgreSQL/MySQL for production
- **Environment Variables**: Use django-environ for sensitive settings
- **Static Files**: Configure proper static file serving
- **CORS**: Add django-cors-headers if needed for frontend
- **Authentication**: Implement JWT or session-based auth
- **Rate Limiting**: Add throttling for API endpoints
- **Logging**: Configure proper logging
- **Deployment**: Use Gunicorn/uWSGI with Nginx

## Dependencies

- Django 5.2.5
- djangorestframework 3.15.2
- Pillow 10.0.0 (for ImageField support)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.