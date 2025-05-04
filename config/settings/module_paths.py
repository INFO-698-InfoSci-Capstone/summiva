# Module paths configuration
"""
Defines the structure of modules in the Summiva project.
This allows for consistent import resolution across services.
"""

import os
from pathlib import Path

# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent.parent

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

# Common subdirectories in each service
COMMON_SERVICE_SUBDIRS = [
    "api",
    "models",
    "schemas",
    "utils",
    "core",
    "database"
]

def get_service_path(service_name: str) -> Path:
    """Get the directory path for a service."""
    if service_name not in SERVICES:
        raise ValueError(f"Unknown service: {service_name}")
    return SERVICE_DIRS[service_name]

def get_module_path(module_path: str) -> Path:
    """
    Get the full path to a module.
    
    Example: 
        get_module_path("backend.auth.models") -> Path("/path/to/src/backend/auth/models")
    """
    parts = module_path.split(".")
    
    # Handle backend modules
    if parts[0] == "backend":
        if len(parts) == 1:
            return BACKEND_DIR
        
        service = parts[1]
        if service not in SERVICES:
            raise ValueError(f"Unknown service: {service}")
            
        if len(parts) == 2:
            return SERVICE_DIRS[service]
            
        # Handle further subdirectories
        subpath = os.path.join(*parts[2:])
        return SERVICE_DIRS[service] / subpath
        
    # Handle other top-level directories
    elif parts[0] == "config":
        subpath = os.path.join(*parts[1:]) if len(parts) > 1 else ""
        return CONFIG_DIR / subpath
    
    elif parts[0] == "tests":
        subpath = os.path.join(*parts[1:]) if len(parts) > 1 else ""
        return TESTS_DIR / subpath
        
    # Handle absolute paths or unknown modules
    else:
        # Try to locate module relative to project root
        potential_path = PROJECT_ROOT
        for part in parts:
            potential_path = potential_path / part
            if not potential_path.exists():
                break
        
        if potential_path.exists():
            return potential_path
        
        raise ValueError(f"Unknown module path: {module_path}")

def get_import_path(file_path: str) -> str:
    """
    Convert a file path to an import path.
    
    Example:
        get_import_path("/path/to/src/backend/auth/models/user.py") -> "backend.auth.models.user"
    """
    # Normalize the path
    path = Path(file_path).absolute()
    
    # Get relative path from project root
    try:
        rel_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        # Not under project root
        return None
    
    # Convert path to import notation
    parts = list(rel_path.parts)
    
    # Remove 'src' from the path if present
    if 'src' in parts:
        parts.remove('src')
    
    # Remove .py extension if present
    if parts[-1].endswith('.py'):
        parts[-1] = parts[-1][:-3]
    
    # Convert to dot notation
    import_path = '.'.join(parts)
    
    return import_path