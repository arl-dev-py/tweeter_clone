from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.engine import get_async_session
from db.models import Media, User
from app.middleware import api_key_auth
import os
import uuid
from datetime import datetime
from fastapi.responses import FileResponse

router = APIRouter(prefix="/medias", tags=["medias"])


async def get_current_user(user: User = Depends(api_key_auth)):
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_media(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    os.makedirs("media", exist_ok=True)
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"media/{filename}"

    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    media = Media(url=f"/medias/{filename}")
    session.add(media)
    await session.flush()
    return {"result": True, "media_id": media.id}


@router.get("/", status_code=status.HTTP_200_OK)
async def get_medias(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Media).where(Media.tweet_id.is_(None)))
    medias = result.scalars().all()
    return {"result": True, "medias": [{"id": m.id, "url": m.url} for m in medias]}


@router.get("/{filename:path}")
async def get_media_file(filename: str):
    file_path = f"media/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Media not found")
