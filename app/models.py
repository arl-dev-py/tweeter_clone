from sqlalchemy import String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from db.engine import Base
from datetime import datetime


class User(Base, AsyncAttrs):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        nullable=False
    )
    tweets: Mapped[list["Tweet"]] = relationship(back_populates="user")

class Tweet(Base, AsyncAttrs):
    __tablename__ = "tweets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    text: Mapped[str] = mapped_column(String(250))
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="tweets")
    medias: Mapped[list["Media"]] = relationship(back_populates="tweet")

class Media(Base, AsyncAttrs):
    __tablename__ = "medias"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), index=True)
    url: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        nullable=False
    )
    tweet: Mapped["Tweet"] = relationship(back_populates="medias")
