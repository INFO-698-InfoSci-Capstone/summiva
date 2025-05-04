"""
Core API Module
==============
Contains base classes and utilities for building consistent APIs across services.
"""

from backend.core.imports import setup_imports
setup_imports()

from backend.core.api.base_api import create_api_router

__all__ = ['create_api_router']