# Module paths configuration for Docker environment
"""
Defines the structure of modules in the Summiva project for Docker environment.
This allows for consistent import resolution across services.
"""

import os
from pathlib import Path

# Root directory of the project in Docker
PROJECT_ROOT = Path('/app')

# Main directories
SRC_DIR = PROJECT_ROOT / "src"
BACKEND_DIR = SRC_DIR / "backend"
FRONTEND_DIR = SRC_DIR / "frontend"
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
TESTS_DIR = PROJECT_ROOT / "tests"

# Backend services
SERVICES = [
    "auth",
    "core",
    "grouping",
    "search",
    "summarization", 
    "tagging"
]

# Service directories
SERVICE_DIRS = {
    service: BACKEND_DIR / service
    for service in SERVICES
}

def get_service_path(service_name: str) -> Path:
    """Get the directory path for a service."""
    if service_name not in SERVICES:
        return BACKEND_DIR / service_name
    return SERVICE_DIRS[service_name]

def get_module_path(module_path: str) -> Path:
    """Get the full path to a module."""
    parts = module_path.split(".")
    
    # Handle backend modules
    if parts[0] == "backend":
        if len(parts) == 1:
            return BACKEND_DIR
        service = parts[1]
        if len(parts) == 2:
            return BACKEND_DIR / service
        subpath = os.path.join(*parts[2:])
        return BACKEND_DIR / service / subpath
        
    # Handle other top-level directories
    elif parts[0] == "config":
        subpath = os.path.join(*parts[1:]) if len(parts) > 1 else ""
        return CONFIG_DIR / subpath
    
    elif parts[0] == "tests":
        subpath = os.path.join(*parts[1:]) if len(parts) > 1 else ""
        return TESTS_DIR / subpath
        
    # Handle absolute paths or unknown modules
    else:
        return PROJECT_ROOT / os.path.join(*parts)

def get_import_path(file_path: str) -> str:
    """Convert a file path to an import path."""
    path = Path(file_path).absolute()
    try:
        rel_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return None
    parts = list(rel_path.parts)
    if parts and parts[0] == "src":
        parts.pop(0)
    if parts and parts[-1].endswith('.py'):
        parts[-1] = parts[-1][:-3]
    return '.'.join(parts)