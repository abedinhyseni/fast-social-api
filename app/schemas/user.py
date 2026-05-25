from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    email: EmailStr
    bio: str
    avatar_url: str
    created_at: datetime


class UserProfile(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    bio: str
    avatar_url: str
    created_at: datetime
    followers_count: int = 0
    following_count: int = 0
