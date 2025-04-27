from backend.core.models.base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    roles = Column(ARRAY(String), default=[])

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    login_audits = relationship("LoginAudit", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(Text, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")

class LoginAudit(BaseModel):
    __tablename__ = "login_audit"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    login_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    success = Column(Boolean, default=True)

    user = relationship("User", back_populates="login_audits")
