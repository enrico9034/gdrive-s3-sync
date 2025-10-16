#!/bin/bash
# Test runner script for GDrive S3 Sync

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GDrive S3 Sync - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print usage
usage() {
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  unit          - Run unit tests (pytest)"
    echo "  coverage      - Run unit tests with coverage report"
    echo "  oauth2-auth   - Test OAuth2 authentication"
    echo "  oauth2-int    - Run OAuth2 integration tests"
    echo "  integration   - Run Service Account integration tests"
    echo "  all           - Run all tests (unit + OAuth2 integration)"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh unit"
    echo "  ./run_tests.sh coverage"
    echo "  ./run_tests.sh oauth2-int"
    exit 1
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    usage
fi

# Parse command
case "$1" in
    unit)
        echo -e "${YELLOW}Running unit tests...${NC}"
        echo ""
        pytest
        ;;
    
    coverage)
        echo -e "${YELLOW}Running unit tests with coverage...${NC}"
        echo ""
        pytest --cov=src --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}✓ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    oauth2-auth)
        echo -e "${YELLOW}Testing OAuth2 authentication...${NC}"
        echo ""
        echo -e "${BLUE}This will open your browser for authentication if needed${NC}"
        echo ""
        python tests/test_oauth2.py
        ;;
    
    oauth2-int)
        echo -e "${YELLOW}Running OAuth2 integration tests...${NC}"
        echo ""
        echo -e "${BLUE}Prerequisites:${NC}"
        echo "  - OAuth2 credentials configured"
        echo "  - token.pickle exists (run: ./run_tests.sh oauth2-auth)"
        echo "  - S3 bucket configured"
        echo ""
        read -p "Continue? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python tests/integration_test_oauth2.py
        else
            echo -e "${RED}Aborted${NC}"
            exit 1
        fi
        ;;
    
    integration)
        echo -e "${YELLOW}Running Service Account integration tests...${NC}"
        echo ""
        echo -e "${BLUE}Prerequisites:${NC}"
        echo "  - Service Account credentials configured"
        echo "  - S3 bucket configured"
        echo "  - Google Drive folder shared with Service Account"
        echo ""
        read -p "Continue? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python tests/integration_test.py
        else
            echo -e "${RED}Aborted${NC}"
            exit 1
        fi
        ;;
    
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        echo ""
        
        # Unit tests
        echo -e "${BLUE}Step 1: Unit tests${NC}"
        pytest --cov=src --cov-report=term-missing
        
        echo ""
        echo -e "${GREEN}✓ Unit tests passed${NC}"
        echo ""
        
        # OAuth2 integration tests
        echo -e "${BLUE}Step 2: OAuth2 integration tests${NC}"
        echo ""
        read -p "Run OAuth2 integration tests? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python tests/integration_test_oauth2.py
            echo ""
            echo -e "${GREEN}✓ OAuth2 integration tests passed${NC}"
        else
            echo -e "${YELLOW}⊘ Skipped OAuth2 integration tests${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ✓ All requested tests completed${NC}"
        echo -e "${GREEN}========================================${NC}"
        ;;
    
    help)
        usage
        ;;
    
    *)
        echo -e "${RED}Error: Unknown option '$1'${NC}"
        echo ""
        usage
        ;;
esac

echo ""
