#!/usr/bin/env python3
"""
GDES AI Factory — Repository Scanner
Performs comprehensive analysis of the repository structure.
"""

import json
from pathlib import Path
from collections import defaultdict

GDES_REPO = Path("/c/Users/User/Documents/GitHub/GDES")
REPORT_DIR = Path("/e/OneDrive/Project Hermes/.hermes/reports")

def scan_django_apps():
    """Scan all Django applications and inventory their components."""
    apps = {}
    skip_dirs = {'.git', '__pycache__', '.opencode', '.claude', 'node_modules', 'static', 'templates'}
    
    for item in sorted(GDES_DIR.iterdir()):
        if item.is_dir() and item.name not in skip_dirs and not item.name.startswith('.'):
            if (item / 'models.py').exists() or (item / 'admin.py').exists():
                app_info = {
                    'name': item.name,
                    'path': str(item),
                    'has_models': (item / 'models.py').exists(),
                    'has_views': (item / 'views.py').exists(),
                    'has_serializers': (item / 'serializers.py').exists(),
                    'has_forms': (item / 'forms.py').exists(),
                    'has_admin': (item / 'admin.py').exists(),
                    'has_urls': (item / 'urls.py').exists(),
                    'has_tasks': (item / 'tasks.py').exists(),
                    'has_signals': (item / 'signals.py').exists(),
                    'has_tests': (item / 'tests.py').exists() or (item / 'tests').exists(),
                    'has_migrations': (item / 'migrations').exists(),
                    'py_files': len(list(item.glob('*.py'))),
                    'template_files': len(list(item.rglob('*.html'))),
                }
                apps[item.name] = app_info
    return apps

def scan_root_files():
    """Scan root-level files for documentation and configuration."""
    files = defaultdict(list)
    for item in sorted(GDES_DIR.iterdir()):
        if item.is_file():
            suffix = item.suffix.lower()
            files[suffix].append({
                'name': item.name,
                'size': item.stat().st_size,
            })
    return dict(files)

def generate_report():
    """Generate comprehensive repository scan report."""
    apps = scan_django_apps()
    root_files = scan_root_files()
    
    report = {
        'scan_date': str(Path.cwd()),
        'total_apps': len(apps),
        'apps': apps,
        'root_files_summary': {k: len(v) for k, v in root_files.items()},
    }
    
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    # JSON report
    with open(REPORT_DIR / 'REPOSITORY_SCAN.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Markdown report
    md = "# Repository Scan Report\n\n"
    md += f"**Scan Date:** {report['scan_date']}\n\n"
    md += f"**Total Django Apps:** {report['total_apps']}\n\n"
    md += "## Django Applications\n\n"
    md += "| App | Models | Views | Serializers | Admin | Tests | Migrations |\n"
    md += "|-----|--------|-------|-------------|-------|-------|------------|\n"
    
    for name, info in sorted(apps.items()):
        md += f"| {name} | {'✓' if info['has_models'] else '✗'} | "
        md += f"{'✓' if info['has_views'] else '✗'} | "
        md += f"{'✓' if info['has_serializers'] else '✗'} | "
        md += f"{'✓' if info['has_admin'] else '✗'} | "
        md += f"{'✓' if info['has_tests'] else '✗'} | "
        md += f"{'✓' if info['has_migrations'] else '✗'} |\n"
    
    md += "\n## Root Files\n\n"
    for suffix, count in sorted(root_files_summary.items()):
        md += f"- **{suffix}**: {count} files\n"
    
    with open(REPORT_DIR / 'REPOSITORY_SCAN.md', 'w') as f:
        f.write(md)
    
    print(f"Repository scan complete. Reports saved to {REPORT_DIR}")
    print(f"Found {len(apps)} Django applications.")

if __name__ == '__main__':
    generate_report()
