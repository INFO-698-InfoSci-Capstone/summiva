"""
Authentication Service Main Entry Point
=====================================
"""
# -----------------------
# Standard Library
# -----------------------
import os
import sys
from pathlib import Path

# -----------------------
# Fix Import Paths
# -----------------------
# Add project root to sys.path to enable absolute imports
project_root = Path("/app")
config_dir = project_root / "config"
settings_dir = config_dir / "settings"

# Make sure these directories exist
os.makedirs(config_dir, exist_ok=True)
os.makedirs(settings_dir, exist_ok=True)

# Add all necessary paths to sys.path
for path in [str(project_root), str(config_dir), str(settings_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# -----------------------
# Third-Party Libraries
# -----------------------
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

# -----------------------
# Internal Modules
# -----------------------
# Create a simple settings module if it can't be imported
try:
    from backend.core.service_init import init_service
except ImportError:
    print("Could not import from backend.core.service_init, attempting to resolve imports")
    try:
        # Try relative import
        from ..core.service_init import init_service
    except ImportError:
        # Create a stub if imports fail
        print("Creating fallback service_init function")
        def init_service(app, service_name):
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            return app

from backend.auth.api.auth_api import router as auth_router

def setup_routes(app):
    """Set up all route handlers for the authentication service"""
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

async def startup_handler(app):
    """Additional startup tasks specific to authentication service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("auth")
    logger.info("Initializing authentication services...")
    # Add any auth-specific initialization here
    # e.g., initialize JWT, set up security features, etc.

async def shutdown_handler(app):
    """Additional shutdown tasks specific to authentication service"""
    from config.logs.logging import setup_logging
    logger = setup_logging("auth")
    logger.info("Cleaning up authentication resources...")
    # Add any auth-specific cleanup here

# -----------------------
# App Initialization
# -----------------------
app = FastAPI(
    title="Auth Service",
    description="Summiva Authentication Service",
    version="1.0.0"
)

# Initialize the service
app = init_service(
    service_name="auth",
    routes_setup=setup_routes,
    startup_handlers=[startup_handler],
    shutdown_handlers=[shutdown_handler]
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "auth"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
