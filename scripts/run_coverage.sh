#!/bin/bash

# Script to run tests with coverage and open the HTML report
# Usage: ./scripts/run_coverage.sh

set -e  # Exit on error

echo "🧪 Running tests with coverage..."
poetry run pytest \
    --cov=ticketer \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    -v

echo ""
echo "📊 Coverage report generated!"
echo ""
echo "View in browser:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open htmlcov/index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open htmlcov/index.html 2>/dev/null || echo "Open htmlcov/index.html in your browser"
else
    # Windows or other
    echo "Open htmlcov/index.html in your browser"
fi

echo ""
echo "Summary:"
poetry run coverage report --skip-covered

