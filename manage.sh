#!/bin/bash

# Tapo Control Management Script - Unified Configuration
# Usage: ./manage.sh [dev|prod] [start|stop|restart|logs|build]
# SSL/HTTPS is handled by Synology Domain Certificate

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"

# Load environment variables
if [[ -f "$ENV_FILE" ]]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Set default port values if not in .env
NGINX_HTTP_PORT=${NGINX_HTTP_PORT:-84}
ADMINER_PORT=${ADMINER_PORT:-8081}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║           🏠 TAPO CONTROL                ║"
    echo "║        Smart Plug Management             ║"
    echo "║     (SSL handled by Synology)            ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_urls() {
    local env=$1
    echo -e "${GREEN}📍 Access URLs:${NC}"
    echo -e "   🌐 Nginx HTTP:   ${YELLOW}http://localhost:${NGINX_HTTP_PORT}${NC}"
    echo -e "   📡 FastAPI:      ${YELLOW}http://localhost:5011${NC}"
    
    if [[ "$env" == "dev" ]]; then
        echo -e "   🗄️  Database:    ${YELLOW}http://localhost:${ADMINER_PORT}${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}ℹ️  Configure Synology Reverse Proxy to point to:${NC}"
    echo -e "   ${CYAN}Source (HTTPS): your-domain.com:443${NC}"
    echo -e "   ${CYAN}Target (HTTP):  localhost:${NGINX_HTTP_PORT}${NC}"
}

start_services() {
    local env=$1
    print_banner
    echo -e "${GREEN}🚀 Starting Tapo Control ($env mode)...${NC}"
    
    if [[ "$env" == "dev" ]]; then
        COMPOSE_PROFILES=dev docker-compose up -d
    else
        docker-compose up -d --scale adminer=0
    fi
    
    echo -e "${GREEN}✅ Services started!${NC}"
    print_urls "$env"
}

stop_services() {
    echo -e "${YELLOW}🛑 Stopping Tapo Control...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Services stopped!${NC}"
}

show_logs() {
    local env=$1
    echo -e "${BLUE}📋 Showing logs for $env environment...${NC}"
    docker-compose logs -f
}

build_services() {
    echo -e "${BLUE}🔨 Building services...${NC}"
    docker-compose build --no-cache
    echo -e "${GREEN}✅ Build complete!${NC}"
}

print_help() {
    echo "Usage: $0 [dev|prod] [start|stop|restart|logs|build]"
    echo ""
    echo "Examples:"
    echo "  $0 dev start    # Start development environment"
    echo "  $0 prod start   # Start production environment"
    echo "  $0 dev logs     # View development logs"
    echo "  $0 prod stop    # Stop production environment"
    echo ""
    echo "Note: SSL/HTTPS is handled by Synology Domain Certificate"
}

# Main script logic
case "${1:-}" in
    dev|prod)
        ENV=$1
        case "${2:-start}" in
            start) start_services "$ENV" ;;
            stop) stop_services ;;
            restart) 
                stop_services
                start_services "$ENV"
                ;;
            logs) show_logs "$ENV" ;;
            build) build_services ;;
            *) 
                print_help
                exit 1
                ;;
        esac
        ;;
    *)
        print_help
        exit 1
        ;;
esac 