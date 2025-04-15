from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
import requests
import os
from ..config.settings import settings
from ..database.connection import get_db, get_es
from sqlalchemy.orm import Session
from elasticsearch import AsyncElasticsearch

router = APIRouter()

# Get auth service URL from environment
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8000")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_SERVICE_URL}/token")

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

@router.post("/search")
async def search_text(
    query: str,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db),
    es: AsyncElasticsearch = Depends(get_es)
):
    # TODO: Implement actual search logic
    # This is a placeholder for demonstration
    return {
        "results": [
            {"id": 1, "text": f"Result 1 for: {query}"},
            {"id": 2, "text": f"Result 2 for: {query}"}
        ],
        "user": token["user"]
    } 