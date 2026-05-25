from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserProfile


class PostCreate(BaseModel):
    content: str
    image_url: str = ""


class PostUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None


class PostOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    content: str
    image_url: str
    created_at: datetime
    updated_at: datetime
    author: UserProfile
    likes_count: int = 0
    comments_count: int = 0
