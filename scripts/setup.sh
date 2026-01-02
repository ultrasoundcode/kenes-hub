#!/bin/bash

# Kenes Hub Setup Script
# This script helps to set up the Kenes Hub application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${GREEN}"
    echo "=================================="
    echo "     Kenes Hub Setup Script      "
    echo "=================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Setup environment file
setup_env_file() {
    print_step "Setting up environment file..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_success ".env file already exists"
    fi
}

# Build and start Docker containers
build_and_start() {
    print_step "Building and starting Docker containers..."
    
    # Build images
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    print_success "Docker containers started"
}

# Setup database
setup_database() {
    print_step "Setting up database..."
    
    # Wait for database to be ready
    echo "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    docker-compose exec backend python manage.py migrate
    
    # Create superuser
    echo -e "${YELLOW}Creating superuser...${NC}"
    docker-compose exec backend python manage.py createsuperuser
    
    print_success "Database setup completed"
}

# Collect static files
collect_static() {
    print_step "Collecting static files..."
    
    docker-compose exec backend python manage.py collectstatic --noinput
    
    print_success "Static files collected"
}

# Show status
show_status() {
    print_step "Checking services status..."
    
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    Kenes Hub is now running!         ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Frontend: ${YELLOW}http://localhost:3000${NC}"
    echo -e "Backend API: ${YELLOW}http://localhost:8000${NC}"
    echo -e "Admin Panel: ${YELLOW}http://localhost:8000/admin${NC}"
    echo ""
    echo -e "To stop the application, run: ${YELLOW}docker-compose down${NC}"
    echo -e "To view logs, run: ${YELLOW}docker-compose logs -f${NC}"
}

# Main function
main() {
    print_header
    
    check_prerequisites
    setup_env_file
    
    echo ""
    echo -e "${YELLOW}Please review and update the .env file before continuing.${NC}"
    echo -e "${YELLOW}Press Enter when ready...${NC}"
    read
    
    build_and_start
    setup_database
    collect_static
    show_status
}

# Run main function
main "$@"