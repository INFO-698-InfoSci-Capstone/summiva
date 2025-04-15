from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
import requests
import os

app = FastAPI(title="Tagging Service")

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

@app.post("/tag")
async def tag_text(text: str, token: str = Depends(verify_token)):
    # TODO: Implement actual tagging logic
    # This is a placeholder for demonstration
    return {
        "tags": ["tag1", "tag2", "tag3"],
        "user": token["user"]
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
