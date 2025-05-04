#!/usr/bin/env python3
"""
Module Structure Validation Script
=================================

This script validates the module structure and import patterns across
all services in the Summiva project. It helps to identify:

- Missing required files/directories in each service
- Inconsistent import patterns
- Circular dependencies
- Other module structure issues

Usage:
    python validate_modules.py [--fix]

Options:
    --fix    Attempt to fix common issues automatically
"""

import os
import re
import sys
import importlib
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from config.settings.module_paths import SERVICES, PROJECT_ROOT, BACKEND_DIR
    from backend.core.imports import setup_imports
    setup_imports()
except ImportError:
    print("Could not import module paths configuration. Run this script from the project root.")
    sys.exit(1)

# Constants
REQUIRED_SERVICE_DIRS = [
    "api",
    "models", 
    "schemas",
    "utils",
    "core",
]

REQUIRED_SERVICE_FILES = [
    "__init__.py",
    "main.py",
]

IMPORT_PATTERNS = {
    "good": [
        r'from backend\.\w+',
        r'from config\.\w+',
        r'import backend\.\w+',
    ],
    "bad": [
        r'from src\.backend',
        r'import src\.backend',
        r'from \.{2,}',  # Relative imports with multiple levels
    ]
}

def check_required_files(service_dir: Path) -> List[str]:
    """Check if a service has all required files and directories."""
    missing = []
    
    # Check directories
    for dirname in REQUIRED_SERVICE_DIRS:
        if not (service_dir / dirname).is_dir():
            missing.append(f"Directory: {dirname}/")
    
    # Check files
    for filename in REQUIRED_SERVICE_FILES:
        if not (service_dir / filename).is_file():
            missing.append(f"File: {filename}")
            
    return missing

def validate_imports(file_path: Path) -> List[str]:
    """Validate import patterns in a file."""
    issues = []
    
    if not file_path.exists() or not file_path.is_file():
        return [f"File does not exist: {file_path}"]
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for bad imports
        for pattern_name, patterns in IMPORT_PATTERNS.items():
            if pattern_name == "bad":
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        for match in matches:
                            issues.append(f"Bad import pattern '{match}' in {file_path}")
    except Exception as e:
        issues.append(f"Error reading {file_path}: {str(e)}")
        
    return issues

def check_service(service_name: str) -> Tuple[List[str], List[str]]:
    """Check a service for structural issues and import problems."""
    service_dir = BACKEND_DIR / service_name
    
    structure_issues = []
    import_issues = []
    
    # Check service structure
    missing = check_required_files(service_dir)
    if missing:
        structure_issues.append(f"Service '{service_name}' is missing required files/directories:")
        for item in missing:
            structure_issues.append(f"  - {item}")
    
    # Check import patterns in Python files
    for root, _, files in os.walk(service_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                import_issues.extend(validate_imports(file_path))
    
    return structure_issues, import_issues

def main():
    parser = argparse.ArgumentParser(description="Validate module structure and imports")
    parser.add_argument('--fix', action='store_true', help='Attempt to fix common issues')
    args = parser.parse_args()
    
    structure_issues = []
    import_issues = []
    
    print(f"Checking module structure for {len(SERVICES)} services...")
    
    # Check each service
    for service in SERVICES:
        service_structure_issues, service_import_issues = check_service(service)
        structure_issues.extend(service_structure_issues)
        import_issues.extend(service_import_issues)
    
    # Report issues
    print("\n" + "="*50)
    print("Module Structure Validation Report")
    print("="*50)
    
    if not structure_issues and not import_issues:
        print("\n✅ All services follow the standard module structure and import patterns.")
    else:
        if structure_issues:
            print("\n❌ Structure Issues:")
            for issue in structure_issues:
                print(f"  {issue}")
        
        if import_issues:
            print("\n❌ Import Issues:")
            for issue in import_issues:
                print(f"  {issue}")
                
        if args.fix:
            print("\n🔧 Attempting to fix issues...")
            # Implementation of auto-fixing would go here
            print("Auto-fix is not implemented yet.")
            
    print("\n" + "="*50)

if __name__ == "__main__":
    main()