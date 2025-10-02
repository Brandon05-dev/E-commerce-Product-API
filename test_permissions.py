#!/usr/bin/env python3
"""
Test script to verify role-based permissions are working correctly.
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_anonymous_access():
    """Test that anonymous users can read but not write"""
    print("🔓 Testing Anonymous User Access...")
    
    # Test reading products (should work)
    response = requests.get(f"{BASE_URL}/api/products/")
    if response.status_code == 200:
        print("✅ Anonymous user CAN read products")
    else:
        print(f"❌ Anonymous user CANNOT read products (status: {response.status_code})")
    
    # Test creating product (should fail)
    product_data = {
        "name": "Test Product",
        "description": "Should not be created",
        "price": "99.99",
        "stock_quantity": 10,
        "category": 1
    }
    response = requests.post(f"{BASE_URL}/api/products/", json=product_data)
    if response.status_code == 401:
        print("✅ Anonymous user CANNOT create products (401 Unauthorized)")
    else:
        print(f"❌ Anonymous user got unexpected status: {response.status_code}")

def get_token(username, password):
    """Get JWT token for user"""
    response = requests.post(f"{BASE_URL}/api/auth/token/", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access"]
    return None

def test_regular_user_access():
    """Test that regular authenticated users can read but not write"""
    print("\n🔒 Testing Regular User Access...")
    
    token = get_token("testuser", "testpass123")
    if not token:
        print("❌ Could not get token for regular user")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test reading products (should work)
    response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
    if response.status_code == 200:
        print("✅ Regular user CAN read products")
    else:
        print(f"❌ Regular user CANNOT read products (status: {response.status_code})")
    
    # Test creating product (should fail with 403)
    product_data = {
        "name": "Regular User Product",
        "description": "Should not be created",
        "price": "99.99",
        "stock_quantity": 10,
        "category": 1
    }
    response = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers)
    if response.status_code == 403:
        print("✅ Regular user CANNOT create products (403 Forbidden)")
    else:
        print(f"❌ Regular user got unexpected status: {response.status_code}")

def test_staff_user_access():
    """Test that staff users can read and write"""
    print("\n👑 Testing Staff User Access...")
    
    token = get_token("staffuser", "testpass123")
    if not token:
        print("❌ Could not get token for staff user")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test reading products (should work)
    response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
    if response.status_code == 200:
        print("✅ Staff user CAN read products")
    else:
        print(f"❌ Staff user CANNOT read products (status: {response.status_code})")
    
    # Test creating product (should work)
    product_data = {
        "name": "Staff Product",
        "description": "Created by staff user",
        "price": "149.99",
        "stock_quantity": 5,
        "category": 1
    }
    response = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers)
    if response.status_code == 201:
        print("✅ Staff user CAN create products")
        product_id = response.json()["id"]
        
        # Test updating the product
        update_data = {
            "name": "Updated Staff Product",
            "description": "Updated by staff user",
            "price": "199.99",
            "stock_quantity": 8,
            "category": 1
        }
        response = requests.put(f"{BASE_URL}/api/products/{product_id}/", json=update_data, headers=headers)
        if response.status_code == 200:
            print("✅ Staff user CAN update products")
        else:
            print(f"❌ Staff user CANNOT update products (status: {response.status_code})")
        
        # Test deleting the product
        response = requests.delete(f"{BASE_URL}/api/products/{product_id}/", headers=headers)
        if response.status_code == 204:
            print("✅ Staff user CAN delete products")
        else:
            print(f"❌ Staff user CANNOT delete products (status: {response.status_code})")
    else:
        print(f"❌ Staff user CANNOT create products (status: {response.status_code})")

def main():
    print("🧪 Testing Role-Based Permissions for E-commerce API")
    print("=" * 50)
    
    try:
        test_anonymous_access()
        test_regular_user_access()
        test_staff_user_access()
        
        print("\n🎉 Permission tests completed!")
        print("\nSummary:")
        print("- Anonymous users: Read-only access")
        print("- Regular authenticated users: Read-only access")
        print("- Staff/Admin users: Full CRUD access")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server at http://127.0.0.1:8000")
        print("Make sure the Django development server is running:")
        print("python manage.py runserver")
        sys.exit(1)

if __name__ == "__main__":
    main()