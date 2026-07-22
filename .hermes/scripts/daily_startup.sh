#!/bin/bash
# GDES AI Factory — Daily Startup Script
# Run this at the beginning of each development session

GDES_REPO="/c/Users/User/Documents/GitHub/GDES"
HERMES_DIR="/e/OneDrive/Project Hermes/.hermes"

echo "=========================================="
echo "  GDES AI Factory — Daily Startup"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 1. Repository Status
echo "--- Repository Status ---"
cd "$GDES_REPO"
echo "Branch: $(git branch --show-current)"
echo "Last commit: $(git log --oneline -1)"
echo "Uncommitted changes:"
git status --short
echo ""

# 2. Quality Gates
echo "--- Quality Gates ---"
echo "Running pytest..."
python -m pytest --tb=short -q 2>&1 | tail -5
echo ""

echo "Running ruff..."
ruff check . 2>&1 | tail -3
echo ""

echo "Running mypy..."
mypy . --ignore-missing-imports 2>&1 | tail -3
echo ""

# 3. Migration Check
echo "--- Migration Status ---"
python manage.py makemigrations --check 2>&1
echo ""

# 4. Disk Space
echo "--- System Info ---"
echo "Python: $(python --version)"
echo "Django: $(python -c 'import django; print(django.VERSION)' 2>/dev/null || echo 'N/A')"
echo ""

echo "=========================================="
echo "  Startup Complete"
echo "=========================================="
