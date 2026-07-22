#!/usr/bin/env python3
"""
GDES AI Factory — Project Memory Updater
Refreshes the project memory from current repository state.
"""

import os
from pathlib import Path
from datetime import datetime

GDES_REPO = Path("/c/Users/User/Documents/GitHub/GDES")
HERMES_DIR = Path("/e/OneDrive/Project Hermes/.hermes")

def get_git_info():
    """Get current git information."""
    import subprocess
    os.chdir(GDES_REPO)
    
    branch = subprocess.check_output(['git', 'branch', '--show-current']).decode().strip()
    last_commit = subprocess.check_output(['git', 'log', '--oneline', '-1']).decode().strip()
    commit_count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD']).decode().strip()
    
    return {
        'branch': branch,
        'last_commit': last_commit,
        'total_commits': commit_count,
    }

def update_memory():
    """Update project memory file."""
    git_info = get_git_info()
    
    memory = f"""# GDES Project Memory
## Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Git Status
- Current Branch: {git_info['branch']}
- Last Commit: {git_info['last_commit']}
- Total Commits: {git_info['total_commits']}

## Repository Location
- Path: {GDES_REPO}
- AI Factory: {HERMES_DIR}

## Quick Reference
- Django apps in: analytics, api, audit, baseline, bgddr, biobank, biomarkers, clinic, clinical, clinical_reasoning, decision, desktop, encounters, events, feedback, fhir, followup, knowledge, labs, pathology, patients, prescriptions, reminders, safety, scheduling, studies, timeline, treatments, users
- Tests: tests/ directory + per-app test files
- Templates: templates/ directory + per-app templates
- Static: static/ and static_src/ directories
"""
    
    memory_dir = HERMES_DIR / 'memory'
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    with open(memory_dir / 'PROJECT_MEMORY.md', 'w') as f:
        f.write(memory)
    
    print(f"Project memory updated at {memory_dir / 'PROJECT_MEMORY.md'}")

if __name__ == '__main__':
    update_memory()
