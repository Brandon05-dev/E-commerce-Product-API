# API Testing Guide

This guide provides step-by-step instructions for testing all API endpoints.

## Setup

1. Start the development server:
```bash
python manage.py runserver
```

2. Base URL: `http://localhost:8000/api/`

## Testing Workflow

### 1. User Registration

**Request:**
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

**Expected Response:** 201 Created with user data and JWT tokens

**Save the access token for subsequent requests!**

### 2. Login (Get Token)

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123!"}'
```

**Expected Response:** 200 OK with access and refresh tokens

### 3. View Profile

**Request:**
```bash
curl http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:** 200 OK with user profile data

### 4. List Products (No Auth Required)

**Request:**
```bash
curl http://localhost:8000/api/products/
```

**Expected Response:** 200 OK with paginated product list

### 5. Search and Filter Products

**Request:**
```bash
curl "http://localhost:8000/api/products/?search=laptop&min_price=500&max_price=2000&in_stock=true&ordering=-price"
```

**Expected Response:** 200 OK with filtered results

### 6. Get Single Product

**Request:**
```bash
curl http://localhost:8000/api/products/1/
```

**Expected Response:** 200 OK with detailed product information

### 7. View Cart

**Request:**
```bash
curl http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:** 200 OK with cart data (initially empty)

### 8. Add Product to Cart

**Request:**
```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product": 1, "quantity": 2}'
```

**Expected Response:** 201 Created with updated cart

### 9. Update Cart Item Quantity

**Request:**
```bash
curl -X PUT http://localhost:8000/api/cart/items/CART_ITEM_ID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 3}'
```

**Expected Response:** 200 OK with updated cart

### 10. View Wishlist

**Request:**
```bash
curl http://localhost:8000/api/wishlist/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:** 200 OK with wishlist items (initially empty)

### 11. Add to Wishlist

**Request:**
```bash
curl -X POST http://localhost:8000/api/wishlist/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product": 2}'
```

**Expected Response:** 201 Created with wishlist item

### 12. List Categories

**Request:**
```bash
curl http://localhost:8000/api/categories/
```

**Expected Response:** 200 OK with category list and statistics

### 13. Create Product (Staff Only)

First, create a staff user:
```bash
python manage.py createsuperuser
```

Then login and get token, then:

**Request:**
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer STAFF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Test product",
    "price": "99.99",
    "stock_quantity": 10,
    "category": 1
  }'
```

**Expected Response:** 201 Created with new product

### 14. Update Profile

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name",
    "email": "updated@example.com"
  }'
```

**Expected Response:** 200 OK with updated profile

### 15. Refresh Token

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

**Expected Response:** 200 OK with new access token

## Testing with Postman/Insomnia

1. Import the collection (you can create one using the examples above)
2. Set environment variable: `BASE_URL = http://localhost:8000`
3. After login, save the access_token in environment variables
4. Use `{{BASE_URL}}` and `{{access_token}}` in requests

## Common Test Scenarios

### Test 1: Anonymous User Restrictions
```bash
# Try to add to cart without authentication
curl -X POST http://localhost:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"product": 1, "quantity": 1}'
```
**Expected:** 401 Unauthorized

### Test 2: Regular User Cannot Create Products
```bash
# Try to create product with regular user token
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer REGULAR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "price": "10.00", "stock_quantity": 1, "category": 1}'
```
**Expected:** 403 Forbidden

### Test 3: Stock Validation
```bash
# Try to add more items than available in stock
curl -X POST http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product": 1, "quantity": 99999}'
```
**Expected:** 400 Bad Request with error message

### Test 4: Duplicate Email Registration
```bash
# Try to register with existing email
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }'
```
**Expected:** 400 Bad Request with email error

## Automated Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test api.tests
python manage.py test api.test_new_features

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Performance Testing

Use Apache Bench or similar tools:
```bash
# Test product listing performance
ab -n 1000 -c 10 http://localhost:8000/api/products/

# Test with authentication
ab -n 100 -c 5 -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/cart/
```

## Troubleshooting

### "Authentication credentials were not provided"
- Ensure you're including the Authorization header
- Check token hasn't expired (60 minutes default)
- Use token refresh endpoint if expired

### "Invalid token" errors
- Token may be expired
- Use the refresh endpoint to get a new access token
- Verify token is properly formatted in header

### 404 Not Found
- Check the URL is correct
- Ensure server is running
- Verify the endpoint exists

### 400 Bad Request
- Check request body format
- Ensure all required fields are included
- Verify data types match API expectations

## Next Steps

1. Test all endpoints systematically
2. Verify error handling works correctly
3. Check permission restrictions
4. Test edge cases (empty cart, out of stock, etc.)
5. Validate data persistence across requests
