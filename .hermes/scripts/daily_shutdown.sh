#!/bin/bash
# GDES AI Factory — Daily Shutdown Script
# Run this at the end of each development session

GDES_REPO="/c/Users/User/Documents/GitHub/GDES"
HERMES_DIR="/e/OneDrive/Project Hermes/.hermes"

echo "=========================================="
echo "  GDES AI Factory — Daily Shutdown"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

cd "$GDES_REPO"

# 1. Final test run
echo "--- Final Test Suite ---"
python -m pytest --tb=short -q 2>&1 | tail -5

# 2. Git status
echo "--- Git Status ---"
git status --short

# 3. Stash WIP if needed
if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes detected. Stashing..."
    git stash push -m "WIP: Daily shutdown $(date +%Y-%m-%d)"
fi

# 4. Update project memory
echo "--- Updating Project Memory ---"
python "$HERMES_DIR/scripts/update_project_memory.py"

echo "=========================================="
echo "  Shutdown Complete"
echo "=========================================="
