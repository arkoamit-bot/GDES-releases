#!/bin/bash
# GDES AI Factory — Release Preparation
# Prepares a new release

GDES_REPO="/c/Users/User/Documents/GitHub/GDES"

echo "=========================================="
echo "  GDES Release Preparation"
echo "=========================================="

cd "$GDES_REPO"

# 1. Verify clean working directory
echo "--- Checking Working Directory ---"
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working directory is not clean. Commit or stash changes first."
    exit 1
fi

# 2. Run quality gates
echo "--- Running Quality Gates ---"
python -m pytest --tb=short -q || { echo "Tests failed. Cannot proceed."; exit 1; }
ruff check . || { echo "Linting failed. Cannot proceed."; exit 1; }
mypy . --ignore-missing-imports || { echo "Type checking failed. Cannot proceed."; exit 1; }

# 3. Check migrations
echo "--- Checking Migrations ---"
python manage.py makemigrations --check || { echo "Missing migrations. Cannot proceed."; exit 1; }

echo "=========================================="
echo "  All quality gates passed."
echo "  Ready for release."
echo "=========================================="
