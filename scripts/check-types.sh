#!/usr/bin/env bash
# Run type checker on wetwire-gitlab-python source code
# Uses 'ty check' to verify type annotations

set -e

# Color output helpers
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Running type checker on src/wetwire_gitlab...${NC}"
echo ""

# Run ty check
if ty check src/wetwire_gitlab; then
    echo ""
    echo -e "${GREEN}✓ Type checking passed${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Type checking failed${NC}"
    exit 1
fi
