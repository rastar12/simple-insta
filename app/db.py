from typing import AsyncGenerator
from datetime import datetime
import uuid

from fastapi.params import Depends
from sqlalchemy import Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
import os
import dotenv
dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class User(SQLAlchemyBaseUserTableUUID, Base):
    username= Column(String, unique=True, nullable=True)
    bio=Column(String, nullable=True)
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    comments = relationship("Comment", back_populates="post")

    user = relationship("User", back_populates="posts")


engine = create_async_engine(DATABASE_URL, connect_args={"ssl": True})
async_session_maker=async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    # development helper: create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session()->AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession= Depends(get_async_session)):
 yield SQLAlchemyUserDatabase(session, User)