from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.models import User, Follower
from db.engine import get_async_session
from datetime import datetime
from typing import List, Any

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class UserCreate(BaseModel):
    username: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    followers_count: int
    following_count: int
    model_config = {"from_attributes": True}


class UserMeOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    followers_count: int
    following_count: int
    tweets: List[Any]
    model_config = {"from_attributes": True}


class UserPublicOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    followers_count: int
    following_count: int
    model_config = {"from_attributes": True}


@router.get("/", response_model=list[UserOut])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    return result.scalars().all()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username exists")
    user = User(username=user_in.username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def follow_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    follower_id = 5

    exists = await session.execute(
        select(Follower).where(
            Follower.follower_id == follower_id,
            Follower.following_id == user_id
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already following")

    follow = Follower(follower_id=follower_id, following_id=user_id)
    session.add(follow)

    await session.execute(
        update(User).where(User.id == follower_id).values(following_count=User.following_count + 1)
    )
    await session.execute(
        update(User).where(User.id == user_id).values(followers_count=User.followers_count + 1)
    )

    await session.commit()
    return {"result": True}


@router.delete("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def unfollow_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    follower_id = 5

    result = await session.execute(
        select(Follower).where(
            Follower.follower_id == follower_id,
            Follower.following_id == user_id
        )
    )
    follow = result.scalar_one_or_none()
    if not follow:
        raise HTTPException(status_code=404, detail="Not following")

    await session.execute(
        update(User).where(User.id == follower_id).values(following_count=User.following_count - 1)
    )
    await session.execute(
        update(User).where(User.id == user_id).values(followers_count=User.followers_count - 1)
    )

    await session.delete(follow)
    await session.commit()
    return {"result": True}


@router.get("/me", response_model=UserMeOut)
async def get_me(session: AsyncSession = Depends(get_async_session)):
    user_id = 4
    stmt = select(User).options(selectinload(User.tweets)).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}", response_model=UserPublicOut)
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(User).options(
        selectinload(User.followers),
        selectinload(User.following)
    ).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
