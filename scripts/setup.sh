#!/bin/bash

# AI Agent Platform Setup Script
# This script helps you get the platform running quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_deps=()
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        REQUIRED_NODE_VERSION="18.0.0"
        if [ "$(printf '%s\n' "$REQUIRED_NODE_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_NODE_VERSION" ]; then
            print_status "Node.js version $NODE_VERSION is installed ✓"
        else
            print_error "Node.js version $NODE_VERSION is too old. Required: $REQUIRED_NODE_VERSION or higher"
            missing_deps+=("node")
        fi
    else
        print_error "Node.js is not installed"
        missing_deps+=("node")
    fi
    
    # Check npm
    if command_exists npm; then
        print_status "npm is installed ✓"
    else
        print_error "npm is not installed"
        missing_deps+=("npm")
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        REQUIRED_PYTHON_VERSION="3.11.0"
        if [ "$(printf '%s\n' "$REQUIRED_PYTHON_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_PYTHON_VERSION" ]; then
            print_status "Python version $PYTHON_VERSION is installed ✓"
        else
            print_error "Python version $PYTHON_VERSION is too old. Required: $REQUIRED_PYTHON_VERSION or higher"
            missing_deps+=("python3")
        fi
    else
        print_error "Python 3 is not installed"
        missing_deps+=("python3")
    fi
    
    # Check pip
    if command_exists pip3; then
        print_status "pip3 is installed ✓"
    else
        print_error "pip3 is not installed"
        missing_deps+=("pip3")
    fi
    
    # Check Docker
    if command_exists docker; then
        print_status "Docker is installed ✓"
    else
        print_warning "Docker is not installed (optional, but recommended)"
    fi
    
    # Check Docker Compose
    if command_exists docker-compose; then
        print_status "Docker Compose is installed ✓"
    else
        print_warning "Docker Compose is not installed (optional, but recommended)"
    fi
    
    # Check Git
    if command_exists git; then
        print_status "Git is installed ✓"
    else
        print_error "Git is not installed"
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo ""
        echo "Please install the missing dependencies and run this script again."
        echo ""
        echo "Installation guides:"
        echo "- Node.js: https://nodejs.org/"
        echo "- Python: https://www.python.org/"
        echo "- Docker: https://docs.docker.com/get-docker/"
        echo "- Git: https://git-scm.com/"
        exit 1
    fi
}

# Function to setup environment variables
setup_environment() {
    print_header "Setting up Environment Variables"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Created .env file from .env.example"
        else
            print_error ".env.example not found. Creating basic .env file..."
            create_basic_env
        fi
    else
        print_status ".env file already exists"
    fi
    
    # Check if required environment variables are set
    if ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
        print_warning "Environment variables appear to be configured"
    else
        print_warning "Please edit .env file and add your API keys:"
        echo "  - OPENAI_API_KEY (required)"
        echo "  - DATABASE_URL (if not using Docker)"
        echo "  - SECRET_KEY (generate a secure random string)"
        echo "  - NEXTAUTH_SECRET (generate a secure random string)"
        echo ""
        read -p "Press Enter to continue after editing .env file..."
    fi
}

# Function to create basic .env file
create_basic_env() {
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORGANIZATION=your_openai_organization_here

# Database
DATABASE_URL=postgresql://aiagent:password@localhost:5432/aiagent_platform

# Security
SECRET_KEY=$(openssl rand -base64 32)
NEXTAUTH_SECRET=$(openssl rand -base64 32)

# Redis
REDIS_URL=redis://localhost:6379

# Development
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
    print_status "Created basic .env file"
}

# Function to install frontend dependencies
install_frontend_deps() {
    print_header "Installing Frontend Dependencies"
    
    if [ -f "package.json" ]; then
        print_status "Installing npm dependencies..."
        npm install
        print_status "Frontend dependencies installed ✓"
    else
        print_error "package.json not found"
        exit 1
    fi
}

# Function to install backend dependencies
install_backend_deps() {
    print_header "Installing Backend Dependencies"
    
    if [ -d "backend" ]; then
        cd backend
        
        if [ -f "requirements.txt" ]; then
            print_status "Creating Python virtual environment..."
            python3 -m venv venv
            
            print_status "Activating virtual environment..."
            source venv/bin/activate
            
            print_status "Installing Python dependencies..."
            pip install -r requirements.txt
            
            print_status "Backend dependencies installed ✓"
            cd ..
        else
            print_error "backend/requirements.txt not found"
            exit 1
        fi
    else
        print_error "backend directory not found"
        exit 1
    fi
}

# Function to setup database
setup_database() {
    print_header "Setting up Database"
    
    if command_exists docker && command_exists docker-compose; then
        print_status "Using Docker for database setup..."
        docker-compose up -d postgres redis
        print_status "Database services started ✓"
    else
        print_warning "Docker not available. Please ensure PostgreSQL and Redis are running."
        print_warning "Database URL: postgresql://aiagent:password@localhost:5432/aiagent_platform"
        print_warning "Redis URL: redis://localhost:6379"
    fi
}

# Function to run database migrations
run_migrations() {
    print_header "Running Database Migrations"
    
    if [ -d "backend" ]; then
        cd backend
        source venv/bin/activate
        
        if command_exists alembic; then
            print_status "Running database migrations..."
            alembic upgrade head
            print_status "Database migrations completed ✓"
        else
            print_warning "Alembic not found. Skipping migrations."
        fi
        
        cd ..
    fi
}

# Function to start services
start_services() {
    print_header "Starting Services"
    
    if command_exists docker && command_exists docker-compose; then
        print_status "Starting all services with Docker Compose..."
        docker-compose up -d
        print_status "All services started ✓"
        
        echo ""
        echo "Services are starting up. Please wait a few moments..."
        echo ""
        echo "Available services:"
        echo "- Frontend: http://localhost:3000"
        echo "- Backend API: http://localhost:8000"
        echo "- API Documentation: http://localhost:8000/docs"
        echo "- Database Admin: http://localhost:5050"
        echo "- Monitoring: http://localhost:3001"
        echo ""
        
    else
        print_status "Starting services manually..."
        
        # Start backend
        echo "Starting backend in background..."
        cd backend
        source venv/bin/activate
        uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        echo "Starting frontend in background..."
        npm run dev &
        FRONTEND_PID=$!
        
        echo ""
        echo "Services started:"
        echo "- Backend PID: $BACKEND_PID"
        echo "- Frontend PID: $FRONTEND_PID"
        echo ""
        echo "To stop services:"
        echo "kill $BACKEND_PID $FRONTEND_PID"
        echo ""
        echo "Available services:"
        echo "- Frontend: http://localhost:3000"
        echo "- Backend API: http://localhost:8000"
        echo "- API Documentation: http://localhost:8000/docs"
        echo ""
    fi
}

# Function to check service health
check_health() {
    print_header "Checking Service Health"
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check backend health
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "Backend is healthy ✓"
    else
        print_warning "Backend health check failed"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Frontend is accessible ✓"
    else
        print_warning "Frontend is not accessible"
    fi
}

# Function to display next steps
show_next_steps() {
    print_header "Setup Complete!"
    
    echo ""
    echo "🎉 AI Agent Platform is ready to use!"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Create your first AI agent"
    echo "3. Start building amazing AI applications!"
    echo ""
    echo "Useful links:"
    echo "- Frontend: http://localhost:3000"
    echo "- Backend API: http://localhost:8000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo "- Database Admin: http://localhost:5050 (admin@aiagent.com / admin)"
    echo "- Monitoring Dashboard: http://localhost:3001 (admin / admin)"
    echo ""
    echo "Need help? Check out:"
    echo "- Documentation: README.md"
    echo "- Issues: https://github.com/yourusername/ai-agent-platform/issues"
    echo ""
    echo "Happy building! 🚀"
}

# Main setup function
main() {
    print_header "AI Agent Platform Setup"
    echo ""
    echo "This script will help you set up the AI Agent Platform."
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
        print_error "This script must be run from the root directory of the AI Agent Platform"
        exit 1
    fi
    
    # Run setup steps
    check_prerequisites
    setup_environment
    install_frontend_deps
    install_backend_deps
    setup_database
    run_migrations
    start_services
    check_health
    show_next_steps
}

# Handle script arguments
case "${1:-}" in
    "check")
        check_prerequisites
        ;;
    "env")
        setup_environment
        ;;
    "install")
        install_frontend_deps
        install_backend_deps
        ;;
    "start")
        start_services
        ;;
    "health")
        check_health
        ;;
    "help"|"-h"|"--help")
        echo "AI Agent Platform Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  check     - Check prerequisites only"
        echo "  env       - Setup environment variables only"
        echo "  install   - Install dependencies only"
        echo "  start     - Start services only"
        echo "  health    - Check service health only"
        echo "  help      - Show this help message"
        echo ""
        echo "Run without arguments to perform complete setup."
        ;;
    *)
        main
        ;;
esac