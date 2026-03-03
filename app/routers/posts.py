from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
import shutil
import os
import uuid
import tempfile

from app.db import Post, User, get_async_session
from app.images import imagekit
from imagekitio import ImageKitError
from app.users import current_active_user

router = APIRouter(
    tags=["posts"]
)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        file_ext = os.path.splitext(file.filename or "")[1]
        random_filename = f"{uuid.uuid4()}{file_ext}"

        try:
            with open(tmp_path, "rb") as f:
                upload_response = imagekit.files.upload(
                    file=f,
                    file_name=random_filename,
                    use_unique_file_name=True,
                )
        except ImageKitError as e:
            raise HTTPException(status_code=500, detail=f"ImageKit upload failed: {str(e)}")
        
        try:
            db_file_type = upload_response.file_type or "image"
            if db_file_type == "non-image" and upload_response.video_codec:
                db_file_type = "video"

            post = Post(
                user_id=user.id,
                caption=caption,
                url=upload_response.url or "unknown",
                file_type=db_file_type,
                file_name=upload_response.name or "unnamed"
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Post).options(selectinload(Post.user)).order_by(Post.created_at.desc())
    )
    posts = result.scalars().all()

    post_data = []
    for post in posts:
        post_data.append({
            "id": str(post.id),
            "user_id": str(post.user_id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "email": post.user.email if post.user else "Deleted User",
        })
    return {"posts": post_data}

@router.delete("/delete/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        post_uuid = uuid.UUID(post_id)
        results = await session.execute(select(Post).where(Post.id == post_uuid))
        post = results.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")

        await session.delete(post)
        await session.commit()

        return {"detail": "Post deleted successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))
