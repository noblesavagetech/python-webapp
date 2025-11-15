# Docker Quick Start

## Run with Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec web flask db init
docker-compose exec web flask db migrate -m "Initial migration"
docker-compose exec web flask db upgrade

# Create sample questionnaire
docker-compose exec web bash scripts/init_questionnaire.sh

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

Access the application at http://localhost:5000

## Run with Docker only

```bash
# Build the image
docker build -t finhealth-app .

# Run the container (with SQLite)
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-key \
  finhealth-app

# Run with PostgreSQL (replace with your DB URL)
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-key \
  finhealth-app
```

## Environment Variables for Docker

Create a `.env.docker` file:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/financial_health_db
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret-key
WAVE_CLIENT_ID=your-wave-client-id
WAVE_CLIENT_SECRET=your-wave-client-secret
WAVE_REDIRECT_URI=https://yourdomain.com/api/wave/callback
```

Then use it:
```bash
docker-compose --env-file .env.docker up -d
```

## Production Deployment

For production, use gunicorn (already included):

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
```

Consider adding:
- Nginx reverse proxy
- SSL certificates
- Redis for caching
- Celery for background jobs
- Proper logging configuration
