"""
Module paths configuration.

Defines the structure of modules in the Summiva project.
This allows for consistent import resolution across services.
"""

import os
import sys
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
LOGS_DIR = PROJECT_ROOT / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True, parents=True)

# Backend services
SERVICES = [
    "auth",
    "core",
    "grouping",
    "search",
    "summarization", 
    "tagging",
    "clustering"  # Added based on docker-compose.yml
]

# Service directories - handle both nested and top-level services
SERVICE_DIRS = {}
for service in SERVICES:
    # Check if service exists as a top-level directory under src
    if (SRC_DIR / service).exists():
        SERVICE_DIRS[service] = SRC_DIR / service
    # Check if it exists as a nested service in backend
    elif (BACKEND_DIR / service).exists():
        SERVICE_DIRS[service] = BACKEND_DIR / service
    # Default to backend/service for new services
    else:
        SERVICE_DIRS[service] = BACKEND_DIR / service

# Common subdirectories in each service
COMMON_SERVICE_SUBDIRS = [
    "api",
    "models",
    "schemas",
    "utils",
    "core",
    "database"
]

# Add project root to Python path if not already there
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def setup_python_path():
    """
    Configure Python path to ensure imports work properly.
    Call this function at the entry point of each service.
    """
    # Add key directories to Python path if they're not already there
    for path in [str(PROJECT_ROOT), str(SRC_DIR), str(CONFIG_DIR)]:
        if path not in sys.path:
            sys.path.insert(0, path)
    return sys.path

def get_service_path(service_name: str) -> Path:
    """Get the directory path for a service."""
    if service_name not in SERVICE_DIRS:
        raise ValueError(f"Unknown service: {service_name}")
    return SERVICE_DIRS[service_name]

def get_module_path(module_path: str) -> Path:
    """
    Get the full path to a module.
    
    Example: 
        get_module_path("backend.auth.models") -> Path("/path/to/src/backend/auth/models")
    """
    parts = module_path.split(".")
    
    # Handle src modules
    if parts[0] == "src":
        if len(parts) == 1:
            return SRC_DIR
        rest_of_path = os.path.join(*parts[1:])
        return SRC_DIR / rest_of_path
        
    # Handle backend modules
    elif parts[0] == "backend":
        if len(parts) == 1:
            return BACKEND_DIR
        
        service = parts[1]
        if len(parts) == 2:
            if service in SERVICE_DIRS:
                return SERVICE_DIRS[service]
            else:
                return BACKEND_DIR / service
            
        # Handle further subdirectories
        subpath = os.path.join(*parts[2:])
        if service in SERVICE_DIRS:
            return SERVICE_DIRS[service] / subpath
        else:
            return BACKEND_DIR / service / subpath
        
    # Handle direct service access (if it's a top-level service)
    elif parts[0] in SERVICE_DIRS:
        service = parts[0]
        if len(parts) == 1:
            return SERVICE_DIRS[service]
        subpath = os.path.join(*parts[1:])
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
    
    # Remove .py extension if present
    if parts[-1].endswith('.py'):
        parts[-1] = parts[-1][:-3]
    
    # Convert to dot notation
    import_path = '.'.join(parts)
    
    return import_path

def ensure_dir(directory_path: Path) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path: The path to the directory
    """
    directory_path.mkdir(exist_ok=True, parents=True)
    return directory_path