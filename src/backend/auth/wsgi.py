"""
WSGI entry point for the Auth service
====================================
This file sets up the proper Python path before importing the app
"""
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path so Python can find the auth module
current_dir = Path(__file__).parent
backend_dir = current_dir.parent  # src/backend directory
sys.path.insert(0, str(backend_dir))

# Now the auth module will be importable
from auth.main import app

# This is what Gunicorn will import
application = app