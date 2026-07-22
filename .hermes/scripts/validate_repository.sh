#!/bin/bash
# GDES AI Factory — Repository Validation
# Runs all quality gates and generates a report

GDES_REPO="/c/Users/User/Documents/GitHub/GDES"
REPORT_DIR="/e/OneDrive/Project Hermes/.hermes/reports"
REPORT_FILE="$REPORT_DIR/VALIDATION_REPORT_$(date +%Y%m%d_%H%M%S).md"

mkdir -p "$REPORT_DIR"

echo "# Repository Validation Report" > "$REPORT_FILE"
echo "**Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

cd "$GDES_REPO"

# Gate 1: pytest
echo "## Gate 1: Testing" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
python -m pytest --tb=short -q 2>&1 >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Gate 2: ruff
echo "## Gate 2: Linting" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
ruff check . 2>&1 >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Gate 3: mypy
echo "## Gate 3: Type Checking" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
mypy . --ignore-missing-imports 2>&1 >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Gate 4: Migrations
echo "## Gate 4: Migration Status" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
python manage.py makemigrations --check 2>&1 >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "**Validation Complete**" >> "$REPORT_FILE"
echo "Report saved to: $REPORT_FILE"
