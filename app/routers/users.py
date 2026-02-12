from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.models import User
from db.engine import get_async_session
from datetime import datetime

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class UserCreate(BaseModel):
    username: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

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
