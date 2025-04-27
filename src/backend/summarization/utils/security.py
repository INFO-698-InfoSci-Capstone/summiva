# src/utils/security.py

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from backend.summarization_service.src.config.settings import settings

security = HTTPBearer()

def fetch_user_from_auth(bearer_token: str):
    """Verify token and get user info from Auth Service."""
    url = f"{settings.AUTH_SERVICE_URL}/api/v1/auth/users/me"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Auth failed")
        return response.json()
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Auth service unavailable")


def get_authenticated_user_id(
    creds: HTTPAuthorizationCredentials = Security(security)
) -> str:
    user_data = fetch_user_from_auth(creds.credentials)
    user_id = str(user_data.get("id", ""))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user_id