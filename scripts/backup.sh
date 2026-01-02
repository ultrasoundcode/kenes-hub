#!/bin/bash

# Kenes Hub Backup Script
# This script creates backups of the application

set -e

# Configuration
BACKUP_DIR="/opt/backups/kenes-hub"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="kenes-hub-backup-$DATE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
print_step() {
    echo -e "${YELLOW}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
backup_database() {
    print_step "Backing up database..."
    
    docker-compose exec -T db pg_dump -U postgres kenes_hub > "$BACKUP_DIR/$BACKUP_NAME.sql"
    
    if [ $? -eq 0 ]; then
        print_success "Database backup created: $BACKUP_NAME.sql"
    else
        print_error "Database backup failed"
        exit 1
    fi
}

# Backup media files
backup_media() {
    print_step "Backing up media files..."
    
    tar -czf "$BACKUP_DIR/$BACKUP_NAME-media.tar.gz" -C ./backend/media .
    
    if [ $? -eq 0 ]; then
        print_success "Media files backup created: $BACKUP_NAME-media.tar.gz"
    else
        print_error "Media files backup failed"
        exit 1
    fi
}

# Backup environment file
backup_env() {
    print_step "Backing up environment file..."
    
    cp .env "$BACKUP_DIR/$BACKUP_NAME.env"
    
    if [ $? -eq 0 ]; then
        print_success "Environment file backup created: $BACKUP_NAME.env"
    else
        print_error "Environment file backup failed"
        exit 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    print_step "Cleaning up old backups..."
    
    # Keep only last 7 days of backups
    find "$BACKUP_DIR" -name "kenes-hub-backup-*" -mtime +7 -delete
    
    print_success "Old backups cleaned up"
}

# Main backup function
main() {
    echo "========================================"
    echo "     Kenes Hub Backup Script          "
    echo "========================================"
    echo ""
    
    backup_database
    backup_media
    backup_env
    cleanup_old_backups
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    Backup completed successfully!    ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Backup location: ${YELLOW}$BACKUP_DIR${NC}"
}

# Run main function
main "$@"