#!/bin/bash

# Advanced RAG System Deployment Script
# This script helps you deploy the Advanced RAG Agent Chat System

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

check_requirements() {
    print_header "Checking Requirements"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
        docker --version
    else
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed"
        docker-compose --version
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

setup_environment() {
    print_header "Setting Up Environment"
    
    if [ ! -f .env ]; then
        print_info "Creating .env file from template..."
        cp .env.template .env
        print_success ".env file created"
        print_info "Please edit .env file and add your OpenAI API key:"
        echo "  nano .env"
        echo ""
        read -p "Press Enter when you've configured .env file..."
    else
        print_success ".env file already exists"
    fi
    
    # Check if OPENAI_API_KEY is set
    source .env
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
        print_error "OPENAI_API_KEY is not set in .env file"
        print_info "Please edit .env and add your OpenAI API key"
        exit 1
    else
        print_success "OPENAI_API_KEY is configured"
    fi
}

create_directories() {
    print_header "Creating Directories"
    
    mkdir -p uploads logs faiss_index
    print_success "Created necessary directories"
}

build_containers() {
    print_header "Building Docker Containers"
    
    print_info "This may take a few minutes..."
    docker-compose build
    print_success "Containers built successfully"
}

start_services() {
    print_header "Starting Services"
    
    print_info "Starting all services..."
    docker-compose up -d
    
    print_info "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Services started successfully"
        echo ""
        docker-compose ps
    else
        print_error "Some services failed to start"
        echo ""
        docker-compose logs --tail=50
        exit 1
    fi
}

test_api() {
    print_header "Testing API"
    
    print_info "Testing health endpoint..."
    
    # Wait for API to be ready
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            print_success "API is responding"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "API did not respond after 30 seconds"
            print_info "Check logs with: docker-compose logs backend"
            exit 1
        fi
        sleep 1
    done
    
    # Show health check response
    echo ""
    echo "Health check response:"
    curl -s http://localhost:8080/health | python3 -m json.tool || echo "{}"
    echo ""
}

show_info() {
    print_header "Deployment Complete! 🎉"
    
    echo "Your Advanced RAG Agent Chat System is now running!"
    echo ""
    echo "📍 API Endpoints:"
    echo "   • Main API:       http://localhost:8080"
    echo "   • Health Check:   http://localhost:8080/health"
    echo "   • API Docs:       http://localhost:8080/docs"
    echo "   • ChromaDB:       http://localhost:8000"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   • View logs:      docker-compose logs -f"
    echo "   • Stop services:  docker-compose down"
    echo "   • Restart:        docker-compose restart"
    echo "   • Shell access:   docker-compose exec backend bash"
    echo ""
    echo "🧪 Test the system:"
    echo "   • REST API:       python test_client.py test"
    echo "   • WebSocket Chat: python test_client.py"
    echo ""
    echo "📚 Next Steps:"
    echo "   1. Register a user:   POST /api/auth/register"
    echo "   2. Get auth token:    POST /api/auth/token"
    echo "   3. Upload documents:  POST /api/documents/upload"
    echo "   4. Start chatting:    POST /api/chat/query"
    echo ""
    print_info "Check README.md for detailed documentation"
}

stop_services() {
    print_header "Stopping Services"
    
    docker-compose down
    print_success "Services stopped"
}

cleanup() {
    print_header "Cleaning Up"
    
    print_info "This will remove containers and volumes"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        print_success "Cleanup complete"
    else
        print_info "Cleanup cancelled"
    fi
}

# Main script
main() {
    case "${1:-deploy}" in
        deploy)
            check_requirements
            setup_environment
            create_directories
            build_containers
            start_services
            test_api
            show_info
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            test_api
            show_info
            ;;
        cleanup)
            cleanup
            ;;
        logs)
            docker-compose logs -f ${2:-backend}
            ;;
        *)
            echo "Usage: $0 {deploy|stop|restart|cleanup|logs [service]}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment (build and start)"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  cleanup  - Remove containers and volumes"
            echo "  logs     - View logs (optional: specify service name)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"