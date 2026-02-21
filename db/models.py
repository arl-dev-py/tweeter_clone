from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from db.engine import Base
from datetime import datetime

Base.__allow_unmapped__ = True


class User(Base, AsyncAttrs):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    api_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), nullable=False
    )
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)

    tweets: Mapped[list["Tweet"]] = relationship(back_populates="author")
    followers: Mapped[list["Follower"]] = relationship(
        "Follower", foreign_keys="Follower.following_id", back_populates="follower"
    )
    following: Mapped[list["Follower"]] = relationship(
        "Follower", foreign_keys="Follower.follower_id", back_populates="following"
    )
    likes: Mapped[list["Like"]] = relationship(back_populates="user")


class Tweet(Base, AsyncAttrs):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(String(250))
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), nullable=False
    )

    author: Mapped["User"] = relationship(back_populates="tweets")
    medias: Mapped[list["Media"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )


class Media(Base, AsyncAttrs):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tweet_id: Mapped[int] | None = mapped_column(ForeignKey("tweets.id"), index=True)
    url: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), nullable=False
    )

    tweet: Mapped["Tweet"] | None = relationship(back_populates="medias")


class Follower(Base, AsyncAttrs):
    __tablename__ = "followers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), nullable=False
    )

    follower: Mapped["User"] = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )
    following: Mapped["User"] = relationship(
        "User", foreign_keys=[following_id], back_populates="followers"
    )


class Like(Base, AsyncAttrs):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(), nullable=False
    )

    tweet: Mapped["Tweet"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship(back_populates="likes")
