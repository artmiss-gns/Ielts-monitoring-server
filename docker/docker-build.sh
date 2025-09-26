#!/bin/bash
# Docker build script for IELTS monitoring system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BUILD_TYPE="production"
PUSH_IMAGE=false
TAG_LATEST=false
REGISTRY=""

# Function to print colored output
print_status() {
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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE        Build type: development, production (default: production)"
    echo "  -p, --push            Push image to registry after build"
    echo "  -l, --latest          Tag as latest"
    echo "  -r, --registry REG    Registry URL (e.g., docker.io/username)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --type production --push --latest"
    echo "  $0 -t development"
    echo "  $0 --registry myregistry.com/myuser --push"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        -p|--push)
            PUSH_IMAGE=true
            shift
            ;;
        -l|--latest)
            TAG_LATEST=true
            shift
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate build type
if [[ "$BUILD_TYPE" != "development" && "$BUILD_TYPE" != "production" ]]; then
    print_error "Invalid build type: $BUILD_TYPE. Must be 'development' or 'production'"
    exit 1
fi

# Set image name
IMAGE_NAME="ielts-monitor"
if [[ -n "$REGISTRY" ]]; then
    IMAGE_NAME="$REGISTRY/$IMAGE_NAME"
fi

# Get version from git or use timestamp
if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
    VERSION=$(git describe --tags --always --dirty 2>/dev/null || git rev-parse --short HEAD)
else
    VERSION=$(date +%Y%m%d-%H%M%S)
fi

print_status "Building IELTS Monitor Docker image..."
print_status "Build type: $BUILD_TYPE"
print_status "Version: $VERSION"
print_status "Image name: $IMAGE_NAME"

# Build the image
print_status "Starting Docker build..."

if [[ "$BUILD_TYPE" == "development" ]]; then
    docker build \
        --target production \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VERSION="$VERSION" \
        --tag "$IMAGE_NAME:$VERSION-dev" \
        --tag "$IMAGE_NAME:dev" \
        .
    
    BUILT_TAG="$IMAGE_NAME:dev"
else
    docker build \
        --target production \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VERSION="$VERSION" \
        --tag "$IMAGE_NAME:$VERSION" \
        .
    
    BUILT_TAG="$IMAGE_NAME:$VERSION"
    
    # Tag as latest if requested
    if [[ "$TAG_LATEST" == true ]]; then
        docker tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:latest"
        print_status "Tagged as latest"
    fi
fi

print_success "Docker build completed successfully!"
print_status "Built image: $BUILT_TAG"

# Push to registry if requested
if [[ "$PUSH_IMAGE" == true ]]; then
    if [[ -z "$REGISTRY" ]]; then
        print_warning "No registry specified, skipping push"
    else
        print_status "Pushing image to registry..."
        docker push "$IMAGE_NAME:$VERSION"
        
        if [[ "$TAG_LATEST" == true && "$BUILD_TYPE" == "production" ]]; then
            docker push "$IMAGE_NAME:latest"
        fi
        
        if [[ "$BUILD_TYPE" == "development" ]]; then
            docker push "$IMAGE_NAME:dev"
        fi
        
        print_success "Image pushed successfully!"
    fi
fi

# Show image info
print_status "Image information:"
docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

print_success "Build process completed!"
print_status "To run the container:"
echo "  docker run -d --name ielts-monitor $BUILT_TAG"
print_status "To run with docker-compose:"
echo "  docker-compose up -d"
