from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from app.models import Tweet, User
from db.engine import get_async_session

router = APIRouter(prefix="/api/v1/tweets", tags=["tweets"])

class TweetCreate(BaseModel):
    text: str
    user_id: int

class TweetOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    text: str
    user_id: int
    created_at: datetime

@router.get("/", response_model=list[TweetOut])
async def get_tweets(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Tweet))
    return result.scalars().all()

@router.post("/", response_model=TweetOut, status_code=status.HTTP_201_CREATED)
async def create_tweet(tweet_in: TweetCreate, session: AsyncSession = Depends(get_async_session)):
    user = await session.get(User, tweet_in.user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    tweet = Tweet(text=tweet_in.text, user_id=tweet_in.user_id)
    session.add(tweet)
    await session.commit()
    await session.refresh(tweet)
    return tweet
