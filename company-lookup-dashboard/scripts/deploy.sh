#!/bin/bash

# Company Lookup Dashboard - Deployment Script
# This script handles deployment to various environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY="your-registry.com"
PROJECT_NAME="company-lookup-dashboard"
BACKEND_IMAGE="${DOCKER_REGISTRY}/${PROJECT_NAME}-backend"
FRONTEND_IMAGE="${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] ENVIRONMENT"
    echo ""
    echo "ENVIRONMENT:"
    echo "  staging     Deploy to staging environment"
    echo "  production  Deploy to production environment"
    echo "  local       Deploy locally with Docker"
    echo ""
    echo "OPTIONS:"
    echo "  -t, --tag TAG        Docker image tag (default: latest)"
    echo "  -b, --build-only     Build images only, don't deploy"
    echo "  -p, --push-only      Push images only, don't deploy"
    echo "  -s, --skip-tests     Skip running tests before deployment"
    echo "  -f, --force          Force deployment without confirmation"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 staging"
    echo "  $0 production --tag v1.2.3"
    echo "  $0 local --skip-tests"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Please install them before proceeding"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to get current git info
get_git_info() {
    if command_exists git && git rev-parse --git-dir >/dev/null 2>&1; then
        GIT_COMMIT=$(git rev-parse --short HEAD)
        GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        GIT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "")
        
        # Check for uncommitted changes
        if ! git diff --quiet || ! git diff --cached --quiet; then
            print_warning "You have uncommitted changes"
            if [[ "$FORCE" != "true" ]]; then
                read -p "Continue anyway? [y/N] " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    exit 1
                fi
            fi
        fi
        
        print_info "Git commit: $GIT_COMMIT"
        print_info "Git branch: $GIT_BRANCH"
        [[ -n "$GIT_TAG" ]] && print_info "Git tag: $GIT_TAG"
    else
        print_warning "Not in a Git repository"
        GIT_COMMIT="unknown"
        GIT_BRANCH="unknown"
    fi
}

# Function to run tests
run_tests() {
    print_header "Running Tests"
    
    # Backend tests
    print_info "Running backend tests..."
    cd backend
    
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        pytest tests/ -v --tb=short || {
            print_error "Backend tests failed"
            exit 1
        }
    else
        print_warning "Virtual environment not found, running tests in Docker..."
        docker run --rm -v "$(pwd):/app" -w /app python:3.11 bash -c "
            pip install -r requirements.txt
            pytest tests/ -v --tb=short
        " || {
            print_error "Backend tests failed"
            exit 1
        }
    fi
    
    cd ..
    
    # Frontend tests
    print_info "Running frontend tests..."
    cd frontend
    
    if [[ -d "node_modules" ]]; then
        npm run test -- --passWithNoTests --watchAll=false || {
            print_error "Frontend tests failed"
            exit 1
        }
    else
        print_warning "Node modules not found, running tests in Docker..."
        docker run --rm -v "$(pwd):/app" -w /app node:18 bash -c "
            npm install
            npm run test -- --passWithNoTests --watchAll=false
        " || {
            print_error "Frontend tests failed"
            exit 1
        }
    fi
    
    cd ..
    
    print_success "All tests passed"
}

# Function to build Docker images
build_images() {
    print_header "Building Docker Images"
    
    # Build backend image
    print_info "Building backend image..."
    docker build -t "${BACKEND_IMAGE}:${IMAGE_TAG}" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg GIT_COMMIT="$GIT_COMMIT" \
        --build-arg GIT_BRANCH="$GIT_BRANCH" \
        backend/
    
    # Build frontend image
    print_info "Building frontend image..."
    docker build -t "${FRONTEND_IMAGE}:${IMAGE_TAG}" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg GIT_COMMIT="$GIT_COMMIT" \
        --build-arg GIT_BRANCH="$GIT_BRANCH" \
        frontend/
    
    print_success "Docker images built successfully"
    
    # Show image sizes
    print_info "Image sizes:"
    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "$PROJECT_NAME"
}

# Function to push Docker images
push_images() {
    print_header "Pushing Docker Images"
    
    # Login to registry if needed
    if [[ "$DOCKER_REGISTRY" != *"localhost"* ]] && [[ "$DOCKER_REGISTRY" != *"127.0.0.1"* ]]; then
        print_info "Logging into Docker registry..."
        docker login "$DOCKER_REGISTRY" || {
            print_error "Failed to login to Docker registry"
            exit 1
        }
    fi
    
    # Push backend image
    print_info "Pushing backend image..."
    docker push "${BACKEND_IMAGE}:${IMAGE_TAG}"
    
    # Push frontend image
    print_info "Pushing frontend image..."
    docker push "${FRONTEND_IMAGE}:${IMAGE_TAG}"
    
    # Tag and push as latest if this is a production deployment
    if [[ "$ENVIRONMENT" == "production" ]] && [[ "$IMAGE_TAG" != "latest" ]]; then
        print_info "Tagging as latest..."
        docker tag "${BACKEND_IMAGE}:${IMAGE_TAG}" "${BACKEND_IMAGE}:latest"
        docker tag "${FRONTEND_IMAGE}:${IMAGE_TAG}" "${FRONTEND_IMAGE}:latest"
        docker push "${BACKEND_IMAGE}:latest"
        docker push "${FRONTEND_IMAGE}:latest"
    fi
    
    print_success "Docker images pushed successfully"
}

# Function to deploy locally
deploy_local() {
    print_header "Deploying Locally"
    
    # Stop existing containers
    print_info "Stopping existing containers..."
    docker-compose down || true
    
    # Update docker-compose with new image tags
    export BACKEND_IMAGE_TAG="${BACKEND_IMAGE}:${IMAGE_TAG}"
    export FRONTEND_IMAGE_TAG="${FRONTEND_IMAGE}:${IMAGE_TAG}"
    
    # Start services
    print_info "Starting services..."
    docker-compose up -d --build
    
    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    check_deployment_health "http://localhost:8000"
    
    print_success "Local deployment completed"
    print_info "Backend: http://localhost:8000"
    print_info "Frontend: http://localhost:3000"
    print_info "API Docs: http://localhost:8000/docs"
}

# Function to deploy to staging
deploy_staging() {
    print_header "Deploying to Staging"
    
    # This is a placeholder for your staging deployment logic
    # You would customize this based on your infrastructure
    
    print_info "Updating staging environment..."
    
    # Example: SSH deployment
    if command_exists ssh; then
        ssh staging-server << EOF
            cd /opt/company-lookup-dashboard
            docker-compose pull
            docker-compose up -d
            docker system prune -f
EOF
    fi
    
    # Example: Kubernetes deployment
    if command_exists kubectl; then
        kubectl set image deployment/backend backend="${BACKEND_IMAGE}:${IMAGE_TAG}"
        kubectl set image deployment/frontend frontend="${FRONTEND_IMAGE}:${IMAGE_TAG}"
        kubectl rollout status deployment/backend
        kubectl rollout status deployment/frontend
    fi
    
    # Check health
    check_deployment_health "https://staging.yourdomain.com"
    
    print_success "Staging deployment completed"
}

# Function to deploy to production
deploy_production() {
    print_header "Deploying to Production"
    
    # Extra confirmation for production
    if [[ "$FORCE" != "true" ]]; then
        print_warning "You are about to deploy to PRODUCTION!"
        print_info "Environment: $ENVIRONMENT"
        print_info "Image tag: $IMAGE_TAG"
        print_info "Git commit: $GIT_COMMIT"
        print_info "Git branch: $GIT_BRANCH"
        echo ""
        read -p "Are you sure you want to continue? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Production deployment cancelled"
            exit 0
        fi
    fi
    
    print_info "Deploying to production..."
    
    # This is a placeholder for your production deployment logic
    # You would customize this based on your infrastructure
    
    # Example: Blue-green deployment
    # deploy_blue_green
    
    # Example: Rolling deployment
    # deploy_rolling
    
    # Example: Docker Swarm
    if command_exists docker; then
        docker service update --image "${BACKEND_IMAGE}:${IMAGE_TAG}" company-dashboard-backend
        docker service update --image "${FRONTEND_IMAGE}:${IMAGE_TAG}" company-dashboard-frontend
    fi
    
    # Check health
    check_deployment_health "https://yourdomain.com"
    
    print_success "Production deployment completed"
    
    # Send notification (optional)
    send_deployment_notification
}

# Function to check deployment health
check_deployment_health() {
    local base_url="$1"
    local max_attempts=30
    local attempt=1
    
    print_info "Checking deployment health at $base_url..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$base_url/api/v1/health/simple" >/dev/null; then
            print_success "Health check passed"
            return 0
        fi
        
        print_info "Attempt $attempt/$max_attempts failed, retrying in 5 seconds..."
        sleep 5
        ((attempt++))
    done
    
    print_error "Health check failed after $max_attempts attempts"
    return 1
}

# Function to send deployment notification
send_deployment_notification() {
    print_info "Sending deployment notification..."
    
    # Example: Slack notification
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 $PROJECT_NAME deployed to $ENVIRONMENT\nTag: $IMAGE_TAG\nCommit: $GIT_COMMIT\"}" \
            "$SLACK_WEBHOOK_URL" || print_warning "Failed to send Slack notification"
    fi
    
    # Example: Discord notification
    if [[ -n "$DISCORD_WEBHOOK_URL" ]]; then
        curl -H "Content-Type: application/json" \
            -d "{\"content\":\"🚀 **$PROJECT_NAME** deployed to **$ENVIRONMENT**\n**Tag:** $IMAGE_TAG\n**Commit:** $GIT_COMMIT\"}" \
            "$DISCORD_WEBHOOK_URL" || print_warning "Failed to send Discord notification"
    fi
}

# Function to rollback deployment
rollback_deployment() {
    print_header "Rolling Back Deployment"
    
    print_warning "Rollback functionality not implemented"
    print_info "To rollback manually:"
    print_info "1. Find previous image tag: docker images"
    print_info "2. Re-run deployment with previous tag: $0 $ENVIRONMENT --tag PREVIOUS_TAG"
}

# Function to cleanup old images
cleanup_images() {
    print_header "Cleaning Up Old Images"
    
    print_info "Removing dangling images..."
    docker image prune -f
    
    print_info "Removing old images (keeping last 5)..."
    docker images "${BACKEND_IMAGE}" --format "table {{.Tag}}" | tail -n +2 | tail -n +6 | xargs -I {} docker rmi "${BACKEND_IMAGE}:{}" 2>/dev/null || true
    docker images "${FRONTEND_IMAGE}" --format "table {{.Tag}}" | tail -n +2 | tail -n +6 | xargs -I {} docker rmi "${FRONTEND_IMAGE}:{}" 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Parse command line arguments
IMAGE_TAG="latest"
BUILD_ONLY="false"
PUSH_ONLY="false"
SKIP_TESTS="false"
FORCE="false"
ENVIRONMENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -b|--build-only)
            BUILD_ONLY="true"
            shift
            ;;
        -p|--push-only)
            PUSH_ONLY="true"
            shift
            ;;
        -s|--skip-tests)
            SKIP_TESTS="true"
            shift
            ;;
        -f|--force)
            FORCE="true"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        staging|production|local)
            ENVIRONMENT="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ -z "$ENVIRONMENT" ]]; then
    print_error "Environment is required"
    show_usage
    exit 1
fi

# Main execution
main() {
    print_header "Company Lookup Dashboard - Deployment"
    
    print_info "Environment: $ENVIRONMENT"
    print_info "Image tag: $IMAGE_TAG"
    
    # Check prerequisites
    check_prerequisites
    
    # Get git info
    get_git_info
    
    # Run tests unless skipped
    if [[ "$SKIP_TESTS" != "true" ]] && [[ "$PUSH_ONLY" != "true" ]]; then
        run_tests
    fi
    
    # Build images unless push-only
    if [[ "$PUSH_ONLY" != "true" ]]; then
        build_images
    fi
    
    # Push images unless build-only or local deployment
    if [[ "$BUILD_ONLY" != "true" ]] && [[ "$ENVIRONMENT" != "local" ]]; then
        push_images
    fi
    
    # Deploy unless build-only or push-only
    if [[ "$BUILD_ONLY" != "true" ]] && [[ "$PUSH_ONLY" != "true" ]]; then
        case $ENVIRONMENT in
            local)
                deploy_local
                ;;
            staging)
                deploy_staging
                ;;
            production)
                deploy_production
                ;;
            *)
                print_error "Unknown environment: $ENVIRONMENT"
                exit 1
                ;;
        esac
    fi
    
    # Cleanup old images
    if [[ "$ENVIRONMENT" == "local" ]] || [[ "$BUILD_ONLY" == "true" ]]; then
        cleanup_images
    fi
    
    print_success "Deployment script completed successfully!"
}

# Run main function
main "$@"