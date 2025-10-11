#!/usr/bin/env python3
"""
Demo script for E-commerce Product API - Enhanced Features
Demonstrates search, filtering, pagination, and enhanced responses
"""

import requests
import json
from datetime import datetime, timedelta


BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_response(url, response):
    """Print formatted API response"""
    print(f"\n🔗 GET {url}")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Print pagination info if available
        if 'count' in data and 'results' in data:
            print(f"📄 Pagination: {data.get('current_page', 1)}/{data.get('total_pages', 1)} " +
                  f"(showing {len(data['results'])}/{data['count']} items)")
        
        # Print results
        if 'results' in data:
            print(f"📝 Results ({len(data['results'])} items):")
            for i, item in enumerate(data['results'][:3], 1):  # Show first 3 items
                if 'name' in item:
                    stock_info = f" [Stock: {item.get('stock_quantity', 'N/A')} - {item.get('stock_status', 'N/A')}]" if 'stock_quantity' in item else ""
                    print(f"  {i}. {item['name']} - ${item.get('price', 'N/A')}{stock_info}")
                else:
                    print(f"  {i}. {json.dumps(item, indent=2)}")
            
            if len(data['results']) > 3:
                print(f"  ... and {len(data['results']) - 3} more items")
        else:
            print(f"📝 Response: {json.dumps(data, indent=2)[:200]}...")
    else:
        print(f"❌ Error: {response.text}")


def demo_search_functionality():
    """Demo enhanced search functionality"""
    print_section("🔍 ENHANCED SEARCH FUNCTIONALITY")
    
    # Basic search
    response = requests.get(f"{BASE_URL}/products/?search=smartphone")
    print_response("/products/?search=smartphone", response)
    
    # Multi-term search
    response = requests.get(f"{BASE_URL}/products/?search=gaming laptop")
    print_response("/products/?search=gaming laptop", response)
    
    # Search by category name
    response = requests.get(f"{BASE_URL}/products/?search=electronics")
    print_response("/products/?search=electronics", response)
    
    # Category search
    response = requests.get(f"{BASE_URL}/categories/?search=book")
    print_response("/categories/?search=book", response)


def demo_advanced_filtering():
    """Demo advanced filtering options"""
    print_section("🎯 ADVANCED FILTERING")
    
    # Price range filtering
    response = requests.get(f"{BASE_URL}/products/?min_price=100&max_price=500")
    print_response("/products/?min_price=100&max_price=500", response)
    
    # Stock status filtering
    response = requests.get(f"{BASE_URL}/products/?in_stock=true&min_stock=20")
    print_response("/products/?in_stock=true&min_stock=20", response)
    
    # Category filtering by name
    response = requests.get(f"{BASE_URL}/products/?category=electronics")
    print_response("/products/?category=electronics", response)
    
    # Date filtering (products created in last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
    response = requests.get(f"{BASE_URL}/products/?created_after={thirty_days_ago}")
    print_response(f"/products/?created_after={thirty_days_ago}", response)


def demo_sorting_and_ordering():
    """Demo sorting and ordering functionality"""
    print_section("📊 SORTING & ORDERING")
    
    # Order by price (ascending)
    response = requests.get(f"{BASE_URL}/products/?ordering=price&page_size=5")
    print_response("/products/?ordering=price&page_size=5", response)
    
    # Order by price (descending)
    response = requests.get(f"{BASE_URL}/products/?ordering=-price&page_size=5")
    print_response("/products/?ordering=-price&page_size=5", response)
    
    # Order by name
    response = requests.get(f"{BASE_URL}/products/?ordering=name&page_size=5")
    print_response("/products/?ordering=name&page_size=5", response)
    
    # Order categories
    response = requests.get(f"{BASE_URL}/categories/?ordering=name")
    print_response("/categories/?ordering=name", response)


def demo_pagination():
    """Demo enhanced pagination"""
    print_section("📄 ENHANCED PAGINATION")
    
    # Custom page size
    response = requests.get(f"{BASE_URL}/products/?page_size=3")
    print_response("/products/?page_size=3", response)
    
    # Second page
    response = requests.get(f"{BASE_URL}/products/?page=2&page_size=3")
    print_response("/products/?page=2&page_size=3", response)
    
    # Category pagination
    response = requests.get(f"{BASE_URL}/categories/?page_size=2")
    print_response("/categories/?page_size=2", response)


def demo_combined_filtering():
    """Demo combining multiple filters"""
    print_section("🎯 COMBINED FILTERING")
    
    # Complex filter combination
    response = requests.get(
        f"{BASE_URL}/products/?category=electronics&min_price=200&in_stock=true&ordering=-price&page_size=5"
    )
    print_response(
        "/products/?category=electronics&min_price=200&in_stock=true&ordering=-price&page_size=5",
        response
    )
    
    # Search with filters
    response = requests.get(
        f"{BASE_URL}/products/?search=laptop&max_price=2000&ordering=price"
    )
    print_response("/products/?search=laptop&max_price=2000&ordering=price", response)


def demo_enhanced_responses():
    """Demo enhanced API responses"""
    print_section("✨ ENHANCED API RESPONSES")
    
    # Enhanced product detail
    response = requests.get(f"{BASE_URL}/products/1/")
    if response.status_code == 200:
        print_response("/products/1/", response)
        data = response.json()
        print(f"\n🔍 Enhanced fields in product detail:")
        print(f"  📦 Stock Status: {data.get('stock_status', 'N/A')}")
        print(f"  💰 Inventory Value: ${data.get('inventory_value', 'N/A')}")
        print(f"  📅 Days Since Created: {data.get('days_since_created', 'N/A')}")
        print(f"  🏷️  Category Details: {data.get('category_details', 'N/A')}")
    
    # Enhanced category detail
    response = requests.get(f"{BASE_URL}/categories/1/")
    if response.status_code == 200:
        print_response("/categories/1/", response)
        data = response.json()
        print(f"\n🔍 Enhanced fields in category detail:")
        print(f"  📊 Total Products: {data.get('products_count', 'N/A')}")
        print(f"  ✅ In Stock Products: {data.get('in_stock_products_count', 'N/A')}")
        print(f"  💵 Average Price: ${data.get('average_price', 'N/A')}")
        print(f"  💰 Total Inventory Value: ${data.get('total_inventory_value', 'N/A')}")


def demo_category_products():
    """Demo enhanced category products endpoint"""
    print_section("🗂️ CATEGORY PRODUCTS WITH FILTERING")
    
    # Basic category products
    response = requests.get(f"{BASE_URL}/categories/1/products/")
    print_response("/categories/1/products/", response)
    
    # Category products with filtering
    response = requests.get(f"{BASE_URL}/categories/1/products/?min_price=500&ordering=price")
    print_response("/categories/1/products/?min_price=500&ordering=price", response)
    
    # Category products with search
    response = requests.get(f"{BASE_URL}/categories/1/products/?search=gaming")
    print_response("/categories/1/products/?search=gaming", response)


def main():
    """Run all demos"""
    print("🚀 E-commerce Product API - Enhanced Features Demo")
    print(f"🌐 Base URL: {BASE_URL}")
    print("⚠️  Make sure your Django server is running on localhost:8000")
    
    try:
        # Test server connection
        response = requests.get(f"{BASE_URL}/products/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding properly. Status: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to run: python manage.py runserver")
        return
    
    # Run all demos
    demo_search_functionality()
    demo_advanced_filtering()
    demo_sorting_and_ordering()
    demo_pagination()
    demo_combined_filtering()
    demo_enhanced_responses()
    demo_category_products()
    
    print_section("🎉 DEMO COMPLETE")
    print("✅ All enhanced features demonstrated successfully!")
    print("📚 Check the README.md for complete API documentation")


if __name__ == "__main__":
    main()