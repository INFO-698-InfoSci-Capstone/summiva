# Authentication service package
"""
Summiva Authentication Service
============================
Provides user authentication and authorization functionality for the Summiva platform.
"""

import sys
import os
from pathlib import Path

# Add project root and other critical paths to path for proper imports
project_root = Path(__file__).parent.parent.parent.parent
backend_dir = project_root / 'src' / 'backend'
config_dir = project_root / 'config'
settings_dir = config_dir / 'settings'

# Add all necessary paths to sys.path
for path in [str(project_root), str(backend_dir), str(config_dir), str(settings_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Create __init__.py files in config directories if needed to make them proper packages
for dir_path in [config_dir, settings_dir]:
    init_file = dir_path / '__init__.py'
    if not init_file.exists():
        try:
            init_file.touch()
            print(f"Created __init__.py in {dir_path}")
        except Exception as e:
            print(f"Warning: Could not create __init__.py in {dir_path}: {str(e)}")

# Import necessary setup functions
try:
    # Try multiple import approaches to be robust in different environments
    try:
        from src.backend.core.imports import setup_imports
    except ImportError:
        try:
            sys.path.insert(0, str(backend_dir / 'core'))
            from imports import setup_imports
        except ImportError as e:
            print(f"Could not import setup_imports using any method: {str(e)}")
            # Define a minimal setup_imports function as fallback
            def setup_imports():
                print("Using fallback setup_imports function")
                return
    
    # Setup imports to ensure proper module resolution
    setup_imports()
except Exception as e:
    print(f"Error in auth/__init__.py import setup: {str(e)}")
    print(f"Current sys.path: {sys.path}")

# Version and metadata
__version__ = '1.0.0'
__service__ = 'auth'