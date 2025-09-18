# TheraSwitchRx Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Python 3.11+
- 2GB+ RAM
- 10GB+ disk space

### Quick Deploy (Docker)
```bash
# Clone the repository
git clone <your-repo-url>
cd med-recommender

# Copy environment file
cp .env.example .env

# Edit .env with your production values
nano .env

# Build and run with Docker
docker-compose up -d

# Check status
docker-compose ps
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production
export BASE_URL=https://your-domain.com

# Run the application
python web_app.py
```

### Environment Variables
- `BASE_URL`: Your production domain
- `SECRET_KEY`: Change to a secure random key
- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Set to 'production'

### Production Checklist
- [ ] Update BASE_URL in .env
- [ ] Change SECRET_KEY
- [ ] Set up SSL certificate
- [ ] Configure reverse proxy (nginx)
- [ ] Set up monitoring
- [ ] Configure backups for api_keys.db
- [ ] Test API endpoints

### API Endpoints
- Web App: `https://your-domain.com`
- API Docs: `https://your-domain.com/api/docs`
- Get API Key: `https://your-domain.com/get-api-key`
- Health Check: `https://your-domain.com/api/v1/health`

### Monitoring
Check application health:
```bash
curl https://your-domain.com/api/v1/health
```

### Troubleshooting
- Check logs: `docker-compose logs theraswitchrx`
- Restart: `docker-compose restart`
- Update: `docker-compose pull && docker-compose up -d`