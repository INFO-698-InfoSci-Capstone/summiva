# core/imports.py
"""
Standardized import paths for Summiva.

This module provides a consistent way to import common dependencies
across all Summiva services. Use this instead of directly importing
from various locations to ensure consistent paths.
"""

# Third-party imports
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
import importlib

# Ensure src directory is in path for absolute imports
# Look for project root either from relative path or from common Docker mount points
possible_roots = [
    Path(__file__).parent.parent.parent.parent,  # Local dev: file/backend/core -> project_root
    Path("/app"),  # Common Docker container mount point
    Path("/app").parent,  # In case /app is the src directory
]

project_root = None
for path in possible_roots:
    # More lenient check - just make sure there's a src directory and config directory
    if path.exists():
        # Check if this is the project root (contains src and config)
        if (path / "src").exists() and (path / "config").exists():
            project_root = path
            break
        # Check if this is the src directory itself (happens in some Docker setups)
        elif path.name == "src" and (path.parent / "config").exists():
            project_root = path.parent
            break
        # Check if we're in the app directory and src is a subdirectory
        elif (path / "src" / "backend").exists():
            project_root = path
            break

if not project_root:
    # Print debug info to help diagnose the issue
    cwd = Path.cwd()
    print(f"Current working directory: {cwd}")
    print(f"File location: {Path(__file__)}")
    print("Paths checked:")
    for path in possible_roots:
        print(f"  {path} - exists: {path.exists()}")
        if path.exists():
            print(f"    contains 'src': {(path / 'src').exists()}")
            print(f"    contains 'config': {(path / 'config').exists()}")
            if (path / 'src').exists():
                print(f"    contains 'src/backend': {(path / 'src' / 'backend').exists()}")
    
    raise RuntimeError("Cannot determine project root path. Check directory structure.")

# Define these paths early for use in setup_imports
PROJECT_ROOT = project_root
BACKEND_DIR = PROJECT_ROOT / 'src' / 'backend'
CONFIG_DIR = PROJECT_ROOT / 'config'

# Add critical paths to sys.path immediately
paths_to_add = [
    str(PROJECT_ROOT),
    str(BACKEND_DIR),
    str(CONFIG_DIR)
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Specific fix for Docker environment - modify sys.path to include settings directory properly
settings_dir = CONFIG_DIR / 'settings'
if settings_dir.exists() and str(settings_dir) not in sys.path:
    sys.path.insert(0, str(settings_dir))
    # Also ensure the parent config directory is properly recognized as a package
    if not (CONFIG_DIR / '__init__.py').exists():
        try:
            (CONFIG_DIR / '__init__.py').touch()
        except:
            print(f"Warning: Could not create __init__.py in {CONFIG_DIR}")
    if not (CONFIG_DIR / 'settings' / '__init__.py').exists():
        try:
            (CONFIG_DIR / 'settings' / '__init__.py').touch()
        except:
            print(f"Warning: Could not create __init__.py in {CONFIG_DIR / 'settings'}")
        
# Now we can safely import from config
try:
    # First try checking if module_paths.py exists and can be directly imported
    module_paths_file = CONFIG_DIR / 'settings' / 'module_paths.py'
    if module_paths_file.exists():
        # Create a spec and load the module directly
        print(f"Found module_paths.py at {module_paths_file}")
        spec = importlib.util.spec_from_file_location("module_paths", module_paths_file)
        module_paths = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_paths)
        
        PROJECT_ROOT = module_paths.PROJECT_ROOT
        BACKEND_DIR = module_paths.BACKEND_DIR
        CONFIG_DIR = module_paths.CONFIG_DIR
        get_module_path = module_paths.get_module_path
        get_import_path = module_paths.get_import_path
    else:
        # Fall back to package import approach
        try:
            from config.settings.module_paths import (
                PROJECT_ROOT, BACKEND_DIR, CONFIG_DIR, 
                get_module_path, get_import_path
            )
        except ImportError:
            # Use the values we already defined above
            print(f"Using built-in path definitions as module_paths.py could not be imported")
            # Define fallback functions if they don't exist
            def get_module_path(module_name):
                return BACKEND_DIR / module_name
                
            def get_import_path(module_name):
                return f"src.backend.{module_name}"
except Exception as e:
    print(f"Error importing config modules: {str(e)}")
    print(f"Current sys.path: {sys.path}")
    raise

# Settings imports
try:
    settings_file = CONFIG_DIR / 'settings' / 'settings.py'
    if settings_file.exists():
        # Create a spec and load the module directly
        print(f"Found settings.py at {settings_file}")
        spec = importlib.util.spec_from_file_location("settings", settings_file)
        settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings)
        settings = settings.settings  # Get the settings object from the module
    else:
        # Try standard import approaches
        try:
            from config.settings import settings
        except ImportError:
            sys.path.insert(0, str(CONFIG_DIR / 'settings'))
            try:
                from settings import settings
            except ImportError as e:
                print(f"Warning: Could not import settings: {str(e)}. Using empty settings object.")
                # Create an empty settings object for fallback
                class EmptySettings:
                    def __getattr__(self, name):
                        print(f"Warning: Accessing undefined setting '{name}'")
                        return None
                settings = EmptySettings()
except Exception as e:
    print(f"Error occurred while loading settings: {str(e)}")

# Database imports - now using src.backend prefix for consistency
try:
    from src.backend.core.database.database import (
        get_db, 
        init_db, 
        Base, 
        engine, 
        SessionLocal
    )
except ImportError as e:
    print(f"Error importing database modules: {str(e)}")
    print(f"Current sys.path: {sys.path}")
    raise

# Authentication imports
def get_auth_imports():
    """Return auth-related imports to avoid circular imports"""
    try:
        from src.backend.core.security.auth_backend import JWTAuthBackend
        return {
            'JWTAuthBackend': JWTAuthBackend
        }
    except ImportError as e:
        print(f"Error importing auth backend: {str(e)}")
        print(f"Current sys.path: {sys.path}")
        raise Exception(f"Failed to import JWTAuthBackend: {str(e)}")

def setup_imports():
    """
    Configure Python's import system to properly resolve our module structure.
    Call this at application startup to ensure imports work correctly.
    """
    # Create critical paths if they don't exist
    for path in [PROJECT_ROOT, CONFIG_DIR, CONFIG_DIR / 'settings']:
        path_obj = Path(path)
        if not path_obj.exists():
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f"Created missing directory: {path_obj}")
            except Exception as e:
                print(f"Warning: Could not create directory {path_obj}: {str(e)}")
    
    # Create __init__.py files if they don't exist
    for path in [CONFIG_DIR, CONFIG_DIR / 'settings']:
        init_file = path / '__init__.py'
        if not init_file.exists() and path.exists():
            try:
                init_file.touch()
                print(f"Created __init__.py in {path}")
            except Exception as e:
                print(f"Warning: Could not create __init__.py in {path}: {str(e)}")
    
    print(f"Import paths configured. PROJECT_ROOT: {PROJECT_ROOT}")

def import_service_module(service_name: str, module_name: str):
    """
    Dynamically import a module from a specific service.
    
    Args:
        service_name: Name of the service (e.g., 'auth', 'summarization')
        module_name: Name of the module within the service (e.g., 'models', 'api')
        
    Returns:
        The imported module
    """
    full_module_path = f"src.backend.{service_name}.{module_name}"
    try:
        return importlib.import_module(full_module_path)
    except ImportError as e:
        print(f"Failed to import {full_module_path}: {str(e)}")
        raise

def resolve_circular_imports(import_func):
    """
    Decorator to resolve circular imports by delaying import until function call
    """
    def wrapper(*args, **kwargs):
        return import_func(*args, **kwargs)
    return wrapper