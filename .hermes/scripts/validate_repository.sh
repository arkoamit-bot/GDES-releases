#!/usr/bin/env bash
echo 'Running Quality Gates...'
pytest
ruff check .
