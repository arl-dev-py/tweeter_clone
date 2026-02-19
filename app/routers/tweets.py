from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models import Tweet, User, Media
from db.engine import get_async_session
from app.routers.medias import MediaOut
from sqlalchemy.orm import selectinload
from app.schemas import TweetCreate, TweetOut, TweetDetailOut, UserOut



router = APIRouter(prefix="/api/v1/tweets", tags=["tweets"])

class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    username: str


TweetOut.model_rebuild()
TweetDetailOut.model_rebuild()

@router.get("/", response_model=list[TweetOut])
async def get_tweets(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(Tweet).options(selectinload(Tweet.user)).order_by(Tweet.created_at.desc())
    )
    return result.scalars().all()

@router.post("/", response_model=TweetOut, status_code=status.HTTP_201_CREATED)
async def create_tweet(tweet_in: TweetCreate, session: AsyncSession = Depends(get_async_session)):
    user = await session.get(User, tweet_in.user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    tweet = Tweet(text=tweet_in.text, user_id=tweet_in.user_id)
    session.add(tweet)
    await session.commit()
    await session.refresh(tweet, ["user"])

    if tweet_in.media_ids:
        for media_id in tweet_in.media_ids:
            media = await session.get(Media, media_id)
            if media:
                media.tweet_id = tweet.id
        await session.commit()
        await session.refresh(tweet, ["medias"])

    return tweet


@router.post("/{tweet_id}/likes", status_code=status.HTTP_200_OK)
async def like_tweet(
    tweet_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    tweet = await session.get(Tweet, tweet_id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tweet not found")
    tweet.likes_count += 1
    await session.commit()
    return {"likes_count": tweet.likes_count}

@router.get("/{tweet_id}", response_model=TweetDetailOut)
async def get_tweet_detail(
    tweet_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Tweet).options(selectinload(Tweet.medias), selectinload(Tweet.user)).where(Tweet.id == tweet_id)
    result = await session.execute(stmt)
    tweet = result.scalar_one_or_none()
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tweet not found")
    return tweet

@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_tweet(
    tweet_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    tweet = await session.get(Tweet, tweet_id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tweet not found")
    await session.delete(tweet)
    await session.commit()
    return {"result": True}

@router.delete("/{tweet_id}/likes", status_code=status.HTTP_200_OK)
async def unlike_tweet(
    tweet_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    tweet = await session.get(Tweet, tweet_id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tweet not found")
    if tweet.likes_count > 0:
        tweet.likes_count -= 1
    await session.commit()
    return {"result": True}
