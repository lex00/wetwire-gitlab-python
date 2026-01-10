#!/usr/bin/env bash
# Run full CI workflow locally for wetwire-gitlab-python
# Executes linting and testing with coverage

set -e

# Color output helpers
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running CI workflow for wetwire-gitlab${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Track overall success
FAILED=0

# Run ruff linting
echo -e "${BLUE}[1/2] Running ruff linting...${NC}"
if ruff check .; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting failed${NC}"
    FAILED=1
fi
echo ""

# Run pytest with coverage
echo -e "${BLUE}[2/2] Running pytest with coverage...${NC}"
if pytest --cov=wetwire_gitlab --cov-report=term-missing --cov-report=html; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    FAILED=1
fi
echo ""

# Print summary
echo -e "${BLUE}========================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}CI workflow completed successfully!${NC}"
    echo -e "${GREEN}All checks passed.${NC}"
else
    echo -e "${RED}CI workflow failed!${NC}"
    echo -e "${YELLOW}Please fix the issues above.${NC}"
fi
echo -e "${BLUE}========================================${NC}"

# Coverage report location
if [ $FAILED -eq 0 ]; then
    echo ""
    echo "Coverage report generated at: htmlcov/index.html"
fi

exit $FAILED
