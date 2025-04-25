from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import settings

# Database and Models
from src.backend.auth.database.database import get_db
from src.backend.auth.models.user import User

# Core Logic
from src.backend.auth.core.auth_logic import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_access_token,
)

# Schemas
from src.backend.auth.schemas.user_schemas import (
    UserCreate,
    UserRead,
    Token,
    RefreshToken,
)

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # Placeholder logic (replace with real DB auth in production)
    if form_data.username != "test" or form_data.password != "test":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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


# ----- Register User -----
@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, hashed_password=hashed_password, full_name=user.full_name
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

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# ----- Refresh Access Token -----
@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshToken) -> Token:
    token_data = decode_access_token(data.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    access_token = create_access_token(data={"sub": token_data["sub"]})
    return {
        "access_token": access_token,
        "refresh_token": data.refresh_token,
        "token_type": "bearer",
    }


# ----- Get Current User Info -----
@router.get("/users/me", response_model=UserRead)
def read_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
) -> UserRead:
    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    user = db.query(User).filter(User.email == token_data["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email, hashed_password=hashed_password, full_name=user.full_name
        )
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
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshToken) -> Token:
    try:
        token_data = decode_access_token(data.refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
            )

        access_token = create_access_token(data={"sub": token_data.email})
        return {
            "access_token": access_token,
            "refresh_token": data.refresh_token,
            "token_type": "bearer",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users/me", response_model=UserRead)
def read_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
) -> UserRead:
    try:
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
            )

        try:
            user = db.query(User).filter(User.email == token_data.email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            return user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal Server Error"
        ) @ router.post("/register", response_model=UserRead)


def register(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email, hashed_password=hashed_password, full_name=user.full_name
        )
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
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshToken) -> Token:
    try:
        token_data = decode_access_token(data.refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
            )

        access_token = create_access_token(data={"sub": token_data.email})
        return {
            "access_token": access_token,
            "refresh_token": data.refresh_token,
            "token_type": "bearer",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users/me", response_model=UserRead)
def read_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
) -> UserRead:
    try:
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
            )

        try:
            user = db.query(User).filter(User.email == token_data.email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            return user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
