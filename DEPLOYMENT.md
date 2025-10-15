# Deployment Guide

## Environment Variables

Create a `.env` file based on `.env.example` and configure:

```bash
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
SECURE_SSL_REDIRECT=True
```

## Platform-Specific Deployment

### Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
5. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```
6. Deploy: `git push heroku main`
7. Run migrations: `heroku run python manage.py migrate`
8. Create superuser: `heroku run python manage.py createsuperuser`

### Render

1. Connect your GitHub repository
2. Create a new Web Service
3. Use settings from `render.yaml`
4. Add environment variables in dashboard
5. Deploy automatically on git push

### Railway

1. Connect your GitHub repository
2. Create new project
3. Add PostgreSQL database
4. Set environment variables:
   - SECRET_KEY (generate secure key)
   - DEBUG=False
   - ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
5. Railway auto-detects Django and deploys

### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build and run commands:
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Run: `gunicorn ecommerce_api.wsgi:application`
3. Add PostgreSQL database
4. Set environment variables
5. Deploy

## Post-Deployment Steps

1. Run migrations: `python manage.py migrate`
2. Collect static files: `python manage.py collectstatic`
3. Create superuser: `python manage.py createsuperuser`
4. (Optional) Load sample data: `python manage.py load_sample_data`
5. Test all endpoints
6. Configure domain and SSL certificate

## Security Checklist

- [ ] SECRET_KEY is unique and secure
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Database credentials are secure
- [ ] CORS origins are restricted
- [ ] HTTPS/SSL is enabled
- [ ] Security headers are enabled
- [ ] Regular backups configured
