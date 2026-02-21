from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from db.engine import get_async_session
from db.models import User, Follower
from app.middleware import api_key_auth
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    api_key: str

    model_config = ConfigDict(from_attributes=True)


async def get_current_user(user: User = Depends(api_key_auth)):
    return user


class UserPublicOut(BaseModel):
    id: int
    username: str
    followers: List[dict]
    following: List[dict]


@router.get("/me", response_model=dict)
async def get_me(user: User = Depends(get_current_user)):
    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.username,
            "followers": [],
            "following": [],
        },
    }


@router.get("/{user_id}")
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(User)
        .options(selectinload(User.followers), selectinload(User.following))
        .where(User.id == user_id)
    )
    result = await session.execute(stmt)
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    followers = [
        {"id": f.follower.id, "name": f.follower.username}
        for f in target_user.followers
    ]
    following = [
        {"id": f.following.id, "name": f.following.username}
        for f in target_user.following
    ]

    return {
        "result": True,
        "user": {
            "id": target_user.id,
            "name": target_user.username,
            "followers": followers,
            "following": following,
        },
    }


@router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    target_user = await session.get(User, user_id)
    if not target_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    exists = await session.execute(
        select(Follower).where(
            Follower.follower_id == current_user.id, Follower.following_id == user_id
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already following")

    follow = Follower(follower_id=current_user.id, following_id=user_id)
    session.add(follow)

    current_user.following_count += 1
    target_user.followers_count += 1

    await session.commit()
    return {"result": True}


@router.delete("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    target_user = await session.get(User, user_id)
    if not target_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    follow_stmt = select(Follower).where(
        Follower.follower_id == current_user.id, Follower.following_id == user_id
    )
    result = await session.execute(follow_stmt)
    follow = result.scalar_one_or_none()

    if not follow:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not following")

    await session.delete(follow)

    current_user.following_count = max(0, current_user.following_count - 1)
    target_user.followers_count = max(0, target_user.followers_count - 1)

    await session.commit()
    return {"result": True}


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str, session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username exists")

    api_key = f"test-api-key-{uuid.uuid4().hex}"[:20]
    user = User(username=username, api_key=api_key)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/superuser", status_code=status.HTTP_201_CREATED)
async def create_superuser(
    username: str, session: AsyncSession = Depends(get_async_session)
):
    api_key = "test-api-key"

    result = await session.execute(select(User).where(User.api_key == api_key))
    if result.scalar_one_or_none():
        return {"result": True, "message": "Superuser already exists with test-api-key"}

    result = await session.execute(select(User).where(User.username == username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        existing_user.api_key = api_key
        await session.commit()
        return {
            "result": True,
            "message": f"Superuser {username} updated",
            "api_key": api_key,
        }
    else:
        user = User(username=username, api_key=api_key)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {"result": True, "user_id": user.id, "api_key": api_key}
