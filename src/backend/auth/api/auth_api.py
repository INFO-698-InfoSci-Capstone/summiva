from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

# Update the settings import to use try/except for better reliability
try:
    from config.settings import settings
except ImportError:
    try:
        import sys
        import os
        # Try to add project root to path if running in Docker
        sys.path.insert(0, os.environ.get("PROJECT_ROOT", "/app"))
        from config.settings.settings import settings
    except ImportError:
        # Fallback to local import if in development
        from src.backend.auth.config.settings import settings

from src.backend.auth.database.database import get_db
from src.backend.auth.models.user import User
from src.backend.auth.models.token import RefreshToken as RefreshTokenDB  # DB model for refresh tokens
from src.backend.auth.core.auth_logic import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_access_token,
)
from src.backend.auth.schemas.user_schemas import (
    UserCreate,
    UserRead,
    Token,
    RefreshToken,
)

from datetime import datetime

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ----- Register User -----
@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=getattr(user, "full_name", None),
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

# ----- Login User -----
@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)) -> Token:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Authentication failed")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    # Store refresh token in DB
    db_refresh = RefreshTokenDB(
        user_id=db_user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

# ----- Login with OAuth2 Form -----
@router.post("/token", response_model=Token)
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Store refresh token in DB
    db_refresh = RefreshTokenDB(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

# ----- Verify Token -----
@router.get("/verify")
async def verify_token(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"valid": True, "user": payload["sub"]}

# ----- Refresh Access Token -----
@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshToken, db: Session = Depends(get_db)) -> Token:
    token_data = decode_access_token(data.refresh_token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db_refresh = db.query(RefreshTokenDB).filter(
        RefreshTokenDB.refresh_token == data.refresh_token,
        RefreshTokenDB.revoked == False,
        RefreshTokenDB.expires_at > datetime.utcnow()
    ).first()

    if not db_refresh:
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    new_access_token = create_access_token(data={"sub": token_data["sub"]})
    db_refresh.last_used_at = datetime.utcnow()
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": data.refresh_token,
        "token_type": "bearer",
    }

# ----- Logout (Revoke Token) -----
@router.post("/logout")
def logout(data: RefreshToken, db: Session = Depends(get_db)):
    db_refresh = db.query(RefreshTokenDB).filter(
        RefreshTokenDB.refresh_token == data.refresh_token,
        RefreshTokenDB.revoked == False
    ).first()

    if not db_refresh:
        raise HTTPException(status_code=404, detail="Refresh token not found")

    db_refresh.revoked = True
    db.commit()
    return {"msg": "Token revoked successfully"}

# ----- Get Current User Info -----
@router.get("/users/me", response_model=UserRead)
def read_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserRead:
    try:
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
            )
        user = db.query(User).filter(User.id == int(token_data["sub"])).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")