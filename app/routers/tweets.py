from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from db.engine import get_async_session
from db.models import Tweet, User, Follower, Media, Like
from app.middleware import api_key_auth
from sqlalchemy.orm import selectinload
from pydantic import BaseModel


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []


class TweetResponse(BaseModel):
    result: bool
    tweet_id: int


router = APIRouter(prefix="/tweets", tags=["tweets"])


async def get_current_user(user: User = Depends(api_key_auth)):
    return user


@router.post("/", response_model=TweetResponse, status_code=status.HTTP_201_CREATED)
async def create_tweet(
    tweet: TweetCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    tweet_obj = Tweet(content=tweet.tweet_data, author_id=user.id)
    session.add(tweet_obj)
    await session.flush()
    await session.refresh(tweet_obj)

    if tweet.tweet_media_ids:
        for media_id in tweet.tweet_media_ids:
            media = await session.get(Media, media_id)
            if media:
                media.tweet_id = tweet_obj.id
        await session.flush()

    return {"result": True, "tweet_id": tweet_obj.id}


@router.get("/")
async def get_tweets_feed(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    following_stmt = select(Follower.following_id).where(
        Follower.follower_id == user.id
    )
    following_result = await session.execute(following_stmt)
    following_ids = [row[0] for row in following_result.fetchall()]

    stmt = (
        select(Tweet)
        .options(
            selectinload(Tweet.medias),
            selectinload(Tweet.author),
            selectinload(Tweet.likes).selectinload(Like.user),
        )
        .where(Tweet.author_id.in_(following_ids + [user.id]))
        .order_by(desc(Tweet.likes_count), desc(Tweet.created_at))
    )

    result = await session.execute(stmt)
    tweets = result.scalars().all()

    tweets_data = []
    for tweet in tweets:
        tweets_data.append(
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachments": [media.url for media in tweet.medias],
                "author": {"id": tweet.author.id, "name": tweet.author.username},
                "likes": [
                    {"user_id": l.user.id, "name": l.user.username} for l in tweet.likes
                ],
            }
        )

    return {"result": True, "tweets": tweets_data}


@router.delete("/{tweet_id}")
async def delete_tweet(
    tweet_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    tweet = await session.get(Tweet, tweet_id)
    if not tweet or tweet.author_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tweet not found")

    await session.delete(tweet)
    await session.flush()
    return {"result": True}


@router.post("/{tweet_id}/likes")
async def like_tweet(
    tweet_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    tweet = await session.get(Tweet, tweet_id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tweet not found")

    exists_result = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
    )
    if exists_result.scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already liked")

    like = Like(tweet_id=tweet_id, user_id=user.id)
    session.add(like)
    tweet.likes_count += 1
    await session.flush()

    return {"result": True}


@router.delete("/{tweet_id}/likes")
async def unlike_tweet(
    tweet_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    tweet = await session.get(Tweet, tweet_id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tweet not found")

    like_result = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
    )
    like_obj = like_result.scalar_one_or_none()
    if like_obj:
        await session.delete(like_obj)
        tweet.likes_count = max(0, tweet.likes_count - 1)
        await session.flush()

    return {"result": True}
