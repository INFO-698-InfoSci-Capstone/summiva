from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Union, List

# ------------------------
# 🧑‍💻 User Models
# ------------------------

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    roles: Optional[List[str]] = []  # e.g., ["admin", "editor"]

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserInDB(UserRead):
    hashed_password: str

# ------------------------
# 🔐 Auth Models
# ------------------------

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class TokenPayload(BaseModel):
    sub: Union[int, str]  # user id
    exp: datetime
    roles: Optional[List[str]] = []

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    roles: Optional[List[str]] = []

# ------------------------
# 🔄 Refresh Token Support
# ------------------------

class RefreshToken(BaseModel):
    refresh_token: str

class RefreshTokenCreate(BaseModel):
    user_id: int
    refresh_token: str
    expires_at: datetime

class RefreshTokenInDB(RefreshTokenCreate):
    id: int
    revoked: bool = False
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ------------------------
# 📜 Login History / Audit
# ------------------------

class LoginAuditRecord(BaseModel):
    id: int
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_time: datetime
    success: bool

    class Config:
        orm_mode = True
