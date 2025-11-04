#!/bin/bash

# Production deployment script for Janasamparka
set -e

# Configuration
PROJECT_NAME="janasamparka"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy.log"
ENV_FILE=".env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >> $LOG_FILE
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1" >> $LOG_FILE
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if environment file exists
    if [[ ! -f $ENV_FILE ]]; then
        error "Environment file $ENV_FILE not found"
        exit 1
    fi
    
    # Create necessary directories
    mkdir -p $BACKUP_DIR
    mkdir -p logs
    mkdir -p uploads/media
    mkdir -p uploads/profile_photos
    mkdir -p uploads/documents
    
    log "Prerequisites check completed"
}

# Backup current deployment
backup_deployment() {
    log "Creating backup of current deployment..."
    
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    mkdir -p $BACKUP_PATH
    
    # Backup database
    if docker-compose ps db | grep -q "Up"; then
        log "Backing up database..."
        docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > $BACKUP_PATH/database.sql
        log "Database backup completed"
    fi
    
    # Backup uploads
    if [[ -d "uploads" ]]; then
        log "Backing up uploads..."
        cp -r uploads $BACKUP_PATH/
        log "Uploads backup completed"
    fi
    
    # Backup configuration
    cp docker-compose.production.yml $BACKUP_PATH/
    cp nginx/nginx.conf $BACKUP_PATH/
    cp $ENV_FILE $BACKUP_PATH/
    
    log "Backup created at $BACKUP_PATH"
}

# Build and deploy services
deploy_services() {
    log "Building and deploying services..."
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f docker-compose.production.yml pull
    
    # Build custom images
    log "Building application images..."
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose -f docker-compose.production.yml down
    
    # Start new services
    log "Starting new services..."
    docker-compose -f docker-compose.production.yml up -d
    
    log "Services deployed successfully"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check backend health
    log "Checking backend health..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "Backend health check passed"
    else
        error "Backend health check failed"
        return 1
    fi
    
    # Check database connection
    log "Checking database connection..."
    if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U $DB_USER > /dev/null 2>&1; then
        log "Database health check passed"
    else
        error "Database health check failed"
        return 1
    fi
    
    # Check Redis connection
    log "Checking Redis connection..."
    if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log "Redis health check passed"
    else
        error "Redis health check failed"
        return 1
    fi
    
    log "All health checks passed"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait for database to be ready
    sleep 10
    
    # Run migrations
    docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
    
    log "Database migrations completed"
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    log "Cleanup completed"
}

# Send notification
send_notification() {
    local status=$1
    
    if [[ $status == "success" ]]; then
        log "Deployment completed successfully!"
        
        # Send success notification (configure as needed)
        # curl -X POST "webhook-url" -d "Deployment successful"
    else
        error "Deployment failed!"
        
        # Send failure notification (configure as needed)
        # curl -X POST "webhook-url" -d "Deployment failed"
    fi
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f docker-compose.production.yml down
    
    # Restore from backup (implement as needed)
    warning "Rollback functionality needs to be implemented based on your backup strategy"
    
    log "Rollback completed"
}

# Main deployment function
main() {
    log "Starting Janasamparka deployment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    backup_deployment
    
    # Deploy services
    if deploy_services; then
        # Run migrations
        if run_migrations; then
            # Health check
            if health_check; then
                # Cleanup
                cleanup
                
                # Send success notification
                send_notification "success"
                
                log "Deployment completed successfully!"
            else
                error "Health check failed"
                rollback
                send_notification "failed"
                exit 1
            fi
        else
            error "Migration failed"
            rollback
            send_notification "failed"
            exit 1
        fi
    else
        error "Service deployment failed"
        rollback
        send_notification "failed"
        exit 1
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    backup)
        backup_deployment
        ;;
    health)
        health_check
        ;;
    cleanup)
        cleanup
        ;;
    rollback)
        rollback
        ;;
    *)
        echo "Usage: $0 {deploy|backup|health|cleanup|rollback}"
        exit 1
        ;;
esac
