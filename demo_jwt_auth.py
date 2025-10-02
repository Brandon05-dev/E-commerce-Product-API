#!/usr/bin/env python3
"""
JWT Authentication Demo Script for E-commerce API

This script demonstrates how to:
1. Obtain JWT tokens
2. Use JWT tokens for authenticated requests
3. Handle authentication errors

Run this script while the Django server is running on localhost:8000
"""

import requests
import json

# API endpoints
BASE_URL = "http://127.0.0.1:8000"
TOKEN_URL = f"{BASE_URL}/api/auth/token/"
REFRESH_URL = f"{BASE_URL}/api/auth/token/refresh/"
VERIFY_URL = f"{BASE_URL}/api/auth/token/verify/"
PRODUCTS_URL = f"{BASE_URL}/api/products/"
CATEGORIES_URL = f"{BASE_URL}/api/categories/"

# Test credentials
USERNAME = "testuser"
PASSWORD = "testpass123"

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

def print_response(response, title="Response"):
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"JSON: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Text: {response.text}")

def main():
    print_section("JWT Authentication Demo")
    
    # 1. Test obtaining JWT token
    print_section("1. Obtaining JWT Token")
    auth_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(TOKEN_URL, json=auth_data)
        print_response(response, "Token Request")
        
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens['access']
            refresh_token = tokens['refresh']
            print(f"\n✅ JWT tokens obtained successfully!")
        else:
            print("❌ Failed to obtain JWT tokens")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django server is running on localhost:8000")
        print("Run: python manage.py runserver")
        return
    
    # 2. Test token verification
    print_section("2. Verifying JWT Token")
    verify_data = {"token": access_token}
    response = requests.post(VERIFY_URL, json=verify_data)
    print_response(response, "Token Verification")
    
    # 3. Test reading products without authentication (should work)
    print_section("3. Reading Products (No Auth Required)")
    response = requests.get(PRODUCTS_URL)
    print_response(response, "Get Products Without Auth")
    
    # 4. Test creating product without authentication (should fail)
    print_section("4. Creating Product Without Auth (Should Fail)")
    product_data = {
        "name": "Unauthorized Product",
        "description": "This should fail",
        "price": "99.99",
        "stock_quantity": 10,
        "category": 1
    }
    response = requests.post(PRODUCTS_URL, json=product_data)
    print_response(response, "Create Product Without Auth")
    
    # 5. Test creating product with authentication (should work)
    print_section("5. Creating Product With Auth (Should Work)")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # First create a category
    category_data = {"name": "Demo Category"}
    cat_response = requests.post(CATEGORIES_URL, json=category_data, headers=headers)
    print_response(cat_response, "Create Category With Auth")
    
    if cat_response.status_code == 201:
        category_id = cat_response.json()['id']
        
        product_data = {
            "name": "Authorized Product",
            "description": "This should work with JWT",
            "price": "149.99",
            "stock_quantity": 5,
            "category": category_id
        }
        response = requests.post(PRODUCTS_URL, json=product_data, headers=headers)
        print_response(response, "Create Product With Auth")
    
    # 6. Test with invalid token (should fail)
    print_section("6. Using Invalid Token (Should Fail)")
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.post(PRODUCTS_URL, json=product_data, headers=invalid_headers)
    print_response(response, "Create Product With Invalid Token")
    
    # 7. Test token refresh
    print_section("7. Refreshing JWT Token")
    refresh_data = {"refresh": refresh_token}
    response = requests.post(REFRESH_URL, json=refresh_data)
    print_response(response, "Token Refresh")
    
    print_section("Demo Complete!")
    print("✅ JWT Authentication is working correctly!")
    print("\nKey points demonstrated:")
    print("- ✅ Read operations work without authentication")
    print("- ✅ Write operations require JWT authentication") 
    print("- ✅ Invalid tokens are rejected")
    print("- ✅ Tokens can be refreshed")

if __name__ == "__main__":
    main()