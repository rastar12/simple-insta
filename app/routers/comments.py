import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db import User, Comment, Post, get_async_session
from app.users import current_active_user
from app.schemas import CommentCreate

router = APIRouter(
    tags=["comments"]
)

@router.post("/{post_id}")
async def create_comment(
    post_id: uuid.UUID,
    comment_data: CommentCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Check if post exists
    result = await session.execute(select(Post).where(Post.id == post_id)) 
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        content=comment_data.content,
        user_id=user.id,
        post_id=post_id
    )
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    
    return {
        "id": str(new_comment.id),
        "content": new_comment.content,
        "user_id": str(new_comment.user_id),
        "post_id": str(new_comment.post_id),
        "created_at": new_comment.created_at.isoformat(),
        "email": user.email
    }

@router.get("/{post_id}")
async def get_comments(
    post_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()
    
    return [
        {
            "id": str(c.id),
            "content": c.content,
            "user_id": str(c.user_id),
            "email": c.user.email,
            "created_at": c.created_at.isoformat()
        } for c in comments
    ]
