from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.auth.database.database import get_db
from backend.auth.core.auth_logic import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    decode_access_token
)
from backend.auth.schemas.user_schemas import UserCreate, UserRead, Token, RefreshToken

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

from backend.auth.models.user import User
@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)) -> Token:
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        access_token = create_access_token(data={"sub": db_user.email})
        refresh_token = create_refresh_token(data={"sub": db_user.email})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshToken) -> Token:
    try:
        token_data = decode_access_token(data.refresh_token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
        
        access_token = create_access_token(data={"sub": token_data.email})
        return {"access_token": access_token, "refresh_token": data.refresh_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users/me", response_model=UserRead)
def read_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)) -> UserRead:
    try:
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
        
        try:
            user = db.query(User).filter(User.email == token_data.email).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            return user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")