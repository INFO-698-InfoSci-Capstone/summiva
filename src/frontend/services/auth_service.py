import requests
from typing import Dict, Any, Optional
from config.settings import AUTH_SERVICE_URL, logger

# Global state for auth
token: Optional[str] = None
current_user: Optional[Dict[str, Any]] = None

def login(username: str, password: str) -> bool:
    """Authenticate with backend auth service"""
    global token, current_user
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/token", 
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            current_user = {"username": username}
            logger.info(f"User {username} logged in successfully")
            return True
        logger.warning(f"Login failed: {response.status_code}")
        return False
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False

def logout():
    """Log out current user"""
    global token, current_user
    token = None
    current_user = None
    logger.info("User logged out")

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for API calls"""
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return token is not None

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    return current_user