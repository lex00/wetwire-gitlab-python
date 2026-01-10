#!/usr/bin/env bash
# Development environment setup script for wetwire-gitlab-python
# Creates virtual environment and installs dependencies

set -e

# Color output helpers
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up wetwire-gitlab-python development environment...${NC}"

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies using uv
echo -e "${BLUE}Installing dependencies with uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

uv pip install -e ".[dev]"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "Available development scripts:"
echo "  ./scripts/ci.sh          - Run full CI workflow locally"
echo "  ./scripts/check-types.sh - Run type checker"
echo ""
