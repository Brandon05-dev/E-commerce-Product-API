# E-commerce Product API - Complete Documentation

A production-ready Django REST Framework backend for an E-commerce platform with comprehensive user management, shopping cart, wishlist, and product catalog features.

## 🚀 Features

### Core Features
- **User Authentication & Management**
  - User registration with email validation
  - JWT-based authentication
  - Profile management
  - Password change functionality
  
- **Product Management**
  - Complete CRUD operations for products and categories
  - Advanced search and filtering
  - Stock management
  - Image support

- **Shopping Cart**
  - Add/update/remove items
  - Real-time quantity validation
  - Automatic cart creation on registration
  - Stock availability checking

- **Wishlist**
  - Save products for later
  - Easy add/remove operations
  - User-specific isolation

### Advanced Features
- **JWT Authentication** with token refresh and rotation
- **Role-Based Permissions** (Anonymous, User, Staff/Admin)
- **Advanced Filtering** by price, category, stock, date
- **Search Functionality** across multiple fields
- **Pagination** with metadata
- **CORS Support** for frontend integration
- **Production-Ready** deployment configuration

## 📋 Requirements

- Python 3.12+
- Django 5.2.5
- PostgreSQL (production) / SQLite (development)
- See `requirements.txt` for full dependencies

## 🛠️ Installation & Setup

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

### 4. Environment Configuration
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3  # Use PostgreSQL URL for production
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. (Optional) Load sample data
```bash
python manage.py load_sample_data
```

### 8. Run development server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication Endpoints

#### Register New User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-10-15T10:30:00Z",
    "last_login": null
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
```

#### Obtain JWT Token (Login)
```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "newuser",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Verify Token
```http
POST /api/auth/token/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### User Profile Endpoints

#### Get Profile
```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2025-10-15T10:30:00Z",
  "last_login": "2025-10-15T11:00:00Z"
}
```

#### Update Profile
```http
PATCH /api/auth/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com"
}
```

#### Change Password
```http
PUT /api/auth/password/change/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

### Product Endpoints

#### List Products
```http
GET /api/products/
```

**Query Parameters:**
- `search` - Search in name, description, category
- `category` - Filter by category ID or name
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `in_stock` - Filter by stock (true/false)
- `min_stock` - Minimum stock quantity
- `ordering` - Sort by field (price, -price, name, -name, created_date, -created_date)
- `page` - Page number
- `page_size` - Items per page

**Example:**
```http
GET /api/products/?search=laptop&min_price=500&max_price=2000&in_stock=true&ordering=-price&page=1
```

**Response (200):**
```json
{
  "count": 15,
  "total_pages": 2,
  "current_page": 1,
  "page_size": 10,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Gaming Laptop Pro",
      "price": "1599.99",
      "stock_quantity": 15,
      "image_url": "https://example.com/laptop.jpg",
      "category_name": "Electronics",
      "is_in_stock": true,
      "stock_status": "moderate_stock",
      "created_date": "2025-10-15T10:00:00Z"
    }
  ]
}
```

#### Create Product (Staff/Admin Only)
```http
POST /api/products/
Authorization: Bearer <staff_access_token>
Content-Type: application/json

{
  "name": "New Product",
  "description": "Product description",
  "price": "99.99",
  "stock_quantity": 50,
  "category": 1,
  "image_url": "https://example.com/image.jpg"
}
```

#### Get Single Product
```http
GET /api/products/1/
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Gaming Laptop Pro",
  "description": "High-performance gaming laptop",
  "price": "1599.99",
  "stock_quantity": 15,
  "image_url": "https://example.com/laptop.jpg",
  "created_date": "2025-10-15T10:00:00Z",
  "category": 1,
  "category_name": "Electronics",
  "category_details": {
    "id": 1,
    "name": "Electronics"
  },
  "is_in_stock": true,
  "stock_status": "moderate_stock",
  "inventory_value": 23998.85,
  "days_since_created": 0
}
```

#### Update Product (Staff/Admin Only)
```http
PUT /api/products/1/
Authorization: Bearer <staff_access_token>
Content-Type: application/json

{
  "name": "Updated Product Name",
  "description": "Updated description",
  "price": "199.99",
  "stock_quantity": 30,
  "category": 1
}
```

#### Delete Product (Staff/Admin Only)
```http
DELETE /api/products/1/
Authorization: Bearer <staff_access_token>
```

### Shopping Cart Endpoints

#### Get Cart
```http
GET /api/cart/
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "user": 1,
  "user_details": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "items": [
    {
      "id": 1,
      "product": 1,
      "product_details": {
        "id": 1,
        "name": "Gaming Laptop Pro",
        "price": "1599.99",
        "stock_quantity": 15,
        "image_url": "https://example.com/laptop.jpg",
        "category_name": "Electronics",
        "is_in_stock": true,
        "stock_status": "moderate_stock",
        "created_date": "2025-10-15T10:00:00Z"
      },
      "quantity": 2,
      "subtotal": 3199.98,
      "added_at": "2025-10-15T11:00:00Z"
    }
  ],
  "total_items": 2,
  "total_price": 3199.98,
  "created_at": "2025-10-15T10:30:00Z",
  "updated_at": "2025-10-15T11:00:00Z"
}
```

#### Add Item to Cart
```http
POST /api/cart/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product": 1,
  "quantity": 2
}
```

**Notes:**
- If item already exists in cart, quantity is added to existing quantity
- Validates stock availability
- Returns updated cart

#### Update Cart Item Quantity
```http
PUT /api/cart/items/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 5
}
```

#### Remove Item from Cart
```http
DELETE /api/cart/items/1/
Authorization: Bearer <access_token>
```

#### Clear Cart
```http
DELETE /api/cart/clear/
Authorization: Bearer <access_token>
```

### Wishlist Endpoints

#### Get Wishlist
```http
GET /api/wishlist/
Authorization: Bearer <access_token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "product": 2,
    "product_details": {
      "id": 2,
      "name": "Wireless Headphones",
      "price": "299.99",
      "stock_quantity": 25,
      "image_url": "https://example.com/headphones.jpg",
      "category_name": "Electronics",
      "is_in_stock": true,
      "stock_status": "moderate_stock",
      "created_date": "2025-10-14T10:00:00Z"
    },
    "added_at": "2025-10-15T12:00:00Z"
  }
]
```

#### Add to Wishlist
```http
POST /api/wishlist/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product": 2
}
```

#### Remove from Wishlist
```http
DELETE /api/wishlist/1/
Authorization: Bearer <access_token>
```

#### Remove by Product ID
```http
DELETE /api/wishlist/product/2/
Authorization: Bearer <access_token>
```

### Category Endpoints

#### List Categories
```http
GET /api/categories/
```

**Response (200):**
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

#### Create Category (Staff/Admin Only)
```http
POST /api/categories/
Authorization: Bearer <staff_access_token>
Content-Type: application/json

{
  "name": "New Category"
}
```

#### Get Category Products
```http
GET /api/categories/1/products/
```

**Supports all product filtering parameters**

## 🔐 Authentication & Permissions

### Permission Levels

1. **Anonymous Users** 🔓
   - Can view products and categories
   - Cannot access cart, wishlist, or profile
   - Cannot create/update/delete any data

2. **Authenticated Users** 🔒
   - All anonymous permissions
   - Can manage own cart and wishlist
   - Can view and update own profile
   - Cannot create/update/delete products or categories

3. **Staff/Admin Users** 👑
   - All authenticated user permissions
   - Can create, update, and delete products and categories
   - Full API access

### Using JWT Tokens

Include the access token in the Authorization header:
```http
Authorization: Bearer <your_access_token>
```

### Token Lifecycle
- **Access Token**: 60 minutes (configurable)
- **Refresh Token**: 7 days (configurable)
- Tokens rotate on refresh for security

## 🧪 Testing

Run all tests:
```bash
python manage.py test
```

Run specific test modules:
```bash
# Test products and categories
python manage.py test api.tests

# Test new features (registration, cart, wishlist)
python manage.py test api.test_new_features
```

Run with verbose output:
```bash
python manage.py test --verbosity=2
```

### Test Coverage
- ✅ User registration and validation
- ✅ Profile management
- ✅ JWT authentication
- ✅ Shopping cart operations
- ✅ Wishlist management
- ✅ Product CRUD operations
- ✅ Category management
- ✅ Permission-based access control
- ✅ Search and filtering
- ✅ Pagination
- ✅ Edge cases and error handling

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Heroku
- Render
- Railway
- DigitalOcean
- AWS/GCP

### Quick Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS`
- [ ] Configure PostgreSQL database
- [ ] Set up CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Run `collectstatic`
- [ ] Set up regular backups

## 📁 Project Structure

```
E-commerce-Product-API/
├── api/
│   ├── models.py              # Product, Category, Cart, CartItem, Wishlist
│   ├── serializers.py         # All API serializers
│   ├── views.py               # ViewSets and API views
│   ├── urls.py                # API routes
│   ├── permissions.py         # Custom permissions
│   ├── pagination.py          # Custom pagination
│   ├── tests.py               # Original tests
│   ├── test_new_features.py   # Tests for new features
│   └── management/
│       └── commands/
│           └── load_sample_data.py
├── ecommerce_api/
│   ├── settings.py            # Django settings with env vars
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI configuration
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku/Render deployment
├── runtime.txt                # Python version
├── render.yaml                # Render deployment config
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

## 🛠️ Technologies Used

- **Django 5.2.5** - Web framework
- **Django REST Framework 3.15.2** - REST API framework
- **djangorestframework-simplejwt 5.3.0** - JWT authentication
- **django-filter 24.3** - Advanced filtering
- **django-cors-headers 4.3.1** - CORS support
- **python-decouple 3.8** - Environment variable management
- **Gunicorn 21.2.0** - WSGI HTTP server
- **WhiteNoise 6.6.0** - Static file serving
- **PostgreSQL** - Production database (via psycopg2-binary)

## 📖 API Examples with cURL

### Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "SecurePass123!"}'
```

### Add to Cart
```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product": 1, "quantity": 2}'
```

### Search Products
```bash
curl "http://localhost:8000/api/products/?search=laptop&min_price=500&in_stock=true&ordering=-price"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**Brandon**
- GitHub: [@Brandon05-dev](https://github.com/Brandon05-dev)

## 🙏 Acknowledgments

- Django REST Framework documentation
- Django documentation
- Community contributors

---

**Need Help?** Open an issue on GitHub or contact the maintainer.

**Found a Bug?** Please open an issue with detailed reproduction steps.

**Want a Feature?** Open an issue to discuss it first!
