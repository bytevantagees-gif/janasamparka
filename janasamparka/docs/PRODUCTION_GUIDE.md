# Janasamparka Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying Janasamparka in a production environment with high availability, security, and scalability.

## Architecture

### Components

- **Backend API**: FastAPI application with Gunicorn WSGI server
- **Database**: PostgreSQL 15 with PostGIS extension
- **Cache**: Redis 7 for caching and session storage
- **Reverse Proxy**: Nginx with SSL termination and load balancing
- **Monitoring**: Prometheus + Grafana for metrics
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **File Storage**: AWS S3 or local storage with optimization

### Infrastructure Requirements

#### Minimum Requirements
- **CPU**: 4 cores
- **Memory**: 8GB RAM
- **Storage**: 100GB SSD
- **Network**: 100 Mbps

#### Recommended Requirements
- **CPU**: 8 cores
- **Memory**: 16GB RAM
- **Storage**: 500GB SSD
- **Network**: 1 Gbps

## Prerequisites

### System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### SSL Certificates

```bash
# Create SSL directory
sudo mkdir -p /etc/ssl/janasamparka

# Generate self-signed certificate (for testing)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/janasamparka/key.pem \
  -out /etc/ssl/janasamparka/cert.pem

# OR use Let's Encrypt for production
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d janasamparka.karnataka.gov.in
```

## Configuration

### Environment Variables

Create `.env.production`:

```bash
# Database Configuration
DB_USER=janasamparka
DB_PASSWORD=your_secure_password
DB_NAME=janasamparka_prod
DATABASE_URL=postgresql://janasamparka:your_secure_password@db:5432/janasamparka_prod

# Redis Configuration
REDIS_PASSWORD=your_redis_password
REDIS_URL=redis://:your_redis_password@redis:6379/0

# Application Configuration
SECRET_KEY=your_very_secure_secret_key_here
ENVIRONMENT=production
DEBUG=false
APP_VERSION=1.0.0

# AWS Configuration (for file storage)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=janasamparka-files
AWS_REGION=ap-south-1

# Monitoring
SENTRY_DSN=your_sentry_dsn
GRAFANA_PASSWORD=your_grafana_password

# External APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
FIREBASE_CREDENTIALS_PATH=/etc/firebase/credentials.json
```

### Nginx Configuration

Update `nginx/nginx.conf` with your domain and SSL paths.

### Database Configuration

```bash
# Create database user and password
sudo -u postgres createuser --interactive
sudo -u postgres createdb janasamparka_prod
```

## Deployment Steps

### 1. Clone Repository

```bash
git clone https://github.com/your-org/janasamparka.git
cd janasamparka
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.production.example .env.production

# Edit with your values
nano .env.production
```

### 3. Generate Secrets

```bash
# Generate secure secrets
python scripts/generate_secrets.py --environment production
```

### 4. Deploy Application

```bash
# Run deployment script
./scripts/deploy.sh
```

### 5. Verify Deployment

```bash
# Check service status
docker-compose -f docker-compose.production.yml ps

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Health check
curl https://api.janasamparka.karnataka.gov.in/health
```

## Monitoring and Maintenance

### Health Checks

```bash
# Application health
curl https://api.janasamparka.karnataka.gov.in/health

# Detailed health
curl https://api.janasamparka.karnataka.gov.in/health/detailed

# Database health
docker-compose exec db pg_isready -U janasamparka

# Redis health
docker-compose exec redis redis-cli ping
```

### Log Management

```bash
# View application logs
docker-compose logs -f backend

# View Nginx logs
docker-compose logs -f nginx

# View system logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backup Procedures

#### Database Backup

```bash
# Automated daily backup
0 2 * * * /path/to/scripts/backup_database.sh

# Manual backup
docker-compose exec db pg_dump -U janasamparka janasamparka_prod > backup_$(date +%Y%m%d).sql
```

#### File Backup

```bash
# Backup uploads
rsync -av uploads/ backup_server:/backups/janasamparka/uploads/

# Backup configuration
cp docker-compose.production.yml backups/
cp nginx/nginx.conf backups/
cp .env.production backups/
```

### Updates and Upgrades

```bash
# Update application
git pull origin main
./scripts/deploy.sh

# Update dependencies
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d --build
```

## Security

### SSL/TLS Configuration

- Use TLS 1.2 and 1.3 only
- Implement HSTS headers
- Regular certificate renewal (Let's Encrypt)

### Firewall Rules

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow SSH (restricted)
sudo ufw allow 22/tcp

# Block other ports
sudo ufw default deny incoming
sudo ufw enable
```

### Security Headers

The Nginx configuration includes:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security

### Rate Limiting

- API endpoints: 10 requests/second
- Authentication endpoints: 5 requests/second
- WebSocket connections: 100 connections/IP

## Performance Optimization

### Database Optimization

```sql
-- Create indexes
CREATE INDEX CONCURRENTLY idx_complaints_status_priority ON complaints(status, priority);
CREATE INDEX CONCURRENTLY idx_complaints_constituency_status ON complaints(constituency_id, status);

-- Analyze table statistics
ANALYZE complaints;

-- Vacuum and reindex
VACUUM ANALYZE complaints;
REINDEX TABLE complaints;
```

### Caching Strategy

- Redis for session storage
- Application-level caching for frequently accessed data
- CDN for static assets

### Monitoring Metrics

Key metrics to monitor:
- Response time (P95 < 500ms)
- Error rate (< 1%)
- Database connection pool
- Memory usage (< 80%)
- CPU usage (< 70%)

## Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose -f docker-compose.production.yml up -d --scale backend=5

# Add load balancer instances
# Configure multiple Nginx instances behind HAProxy or AWS ALB
```

### Database Scaling

- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Database sharding for large datasets

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose logs backend

# Check configuration
docker-compose config

# Check port conflicts
netstat -tulpn | grep :8000
```

#### Database Connection Issues

```bash
# Test database connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check database logs
docker-compose logs db
```

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart backend

# Check for memory leaks
docker-compose exec backend python -m memory_profiler app/main.py
```

### Emergency Procedures

#### Service Recovery

```bash
# Restart all services
docker-compose -f docker-compose.production.yml restart

# Restore from backup
./scripts/restore.sh backup_20240101_120000

# Rollback deployment
./scripts/deploy.sh rollback
```

#### Incident Response

1. Identify affected services
2. Check logs and metrics
3. Implement temporary fix
4. Communicate with stakeholders
5. Root cause analysis
6. Permanent fix implementation

## Compliance and Auditing

### Data Protection

- GDPR compliance for user data
- Regular security audits
- Penetration testing
- Data encryption at rest and in transit

### Audit Logging

- All user actions logged
- Administrative actions tracked
- File access monitored
- Security events recorded

## Support and Maintenance

### Contact Information

- **Technical Support**: tech@janasamparka.karnataka.gov.in
- **Security Issues**: security@janasamparka.karnataka.gov.in
- **Emergency Hotline**: +91-80-XXXX-XXXX

### Maintenance Schedule

- **Daily**: Health checks, log rotation
- **Weekly**: Security updates, performance monitoring
- **Monthly**: Backup verification, dependency updates
- **Quarterly**: Security audits, performance tuning
- **Yearly**: Architecture review, capacity planning

## Appendix

### Configuration Templates

See the `config/` directory for detailed configuration templates.

### Monitoring Dashboards

Import provided Grafana dashboards from `monitoring/grafana/dashboards/`.

### API Documentation

Available at `https://api.janasamparka.karnataka.gov.in/docs` (production disabled).

### Changelog

See `CHANGELOG.md` for version history and updates.
