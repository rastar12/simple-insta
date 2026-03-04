from typing import Optional
from pydantic import BaseModel
from fastapi_users import schemas
from datetime import datetime
import uuid

class PostCreate(BaseModel):
    title: str
    content: str
    

class PostResponse(BaseModel):
    title:str
    content:str

class UserRead(schemas.BaseUser[uuid.UUID]):
    username: Optional[str] = None
    bio: Optional[str] =None

class UserCreate(schemas.BaseUserCreate):
    username: Optional[str] = None
    bio: Optional[str] = None

class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None
    bio: Optional[str] = None


class CommentCreate(BaseModel):
    content: str

class CommentRead(BaseModel):
    id: uuid.UUID
    content: str
    user_id: uuid.UUID
    post_id: uuid.UUID
    created_at: datetime
    email: str

    class Config:
        from_attributes = True

