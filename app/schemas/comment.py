from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserProfile


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    content: str
    created_at: datetime
    author: UserProfile
