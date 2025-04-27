# src/utils/security.py

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from src.config.config import settings
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
import requests
import os
from ..config.settings import settings
from ..database.connection import get_db, get_es
from sqlalchemy.orm import Session
from elasticsearch import AsyncElasticsearch


security = HTTPBearer()


# Get auth service URL from environment
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8000")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_SERVICE_URL}/token")

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


async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return response.json()
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )