#!/bin/bash
# GDES AI Factory — Report Generator
# Generates all standard reports

REPORT_DIR="/e/OneDrive/Project Hermes/.hermes/reports"
mkdir -p "$REPORT_DIR"

echo "Generating AI Factory reports..."

# Run repository scan
python "/e/OneDrive/Project Hermes/.hermes/scripts/repository_scan.py"

# Run project memory update
python "/e/OneDrive/Project Hermes/.hermes/scripts/update_project_memory.py"

# Run validation
bash "/e/OneDrive/Project Hermes/.hermes/scripts/validate_repository.sh"

echo "All reports generated in $REPORT_DIR"
ls -la "$REPORT_DIR"
