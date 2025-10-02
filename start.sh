#!/bin/bash

# E-commerce API Start Script
echo "🚀 Starting E-commerce Product API..."

# Activate virtual environment
source venv/bin/activate

# Check if migrations exist, if not create them
if [ ! -f "api/migrations/0001_initial.py" ]; then
    echo "📝 Creating migrations..."
    python manage.py makemigrations api
fi

# Apply migrations
echo "🔄 Applying migrations..."
python manage.py migrate

# Load sample data if database is empty
PRODUCT_COUNT=$(python manage.py shell -c "from api.models import Product; print(Product.objects.count())")
if [ "$PRODUCT_COUNT" -eq "0" ]; then
    echo "📦 Loading sample data..."
    python manage.py load_sample_data
fi

# Start the server
echo "🌐 Starting Django development server..."
echo "📍 API will be available at: http://127.0.0.1:8000/api/"
echo "🔧 Admin interface at: http://127.0.0.1:8000/admin/"
echo "📚 API documentation: http://127.0.0.1:8000/api/products/ (browsable API)"
echo ""
echo "Press Ctrl+C to stop the server"
python manage.py runserver