from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.routers.medias import MediaOut


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    followers_count: int
    following_count: int
    model_config = {"from_attributes": True}

class TweetCreate(BaseModel):
    text: str
    user_id: int
    media_ids: Optional[List[int]] = []

class TweetOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    text: str
    likes_count: int
    created_at: datetime
    user: UserOut

class TweetDetailOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    text: str
    likes_count: int
    medias: List[MediaOut] = []
    created_at: datetime
    user: UserOut


UserOut.model_rebuild()
TweetOut.model_rebuild()
TweetDetailOut.model_rebuild()
MediaOut.model_rebuild()
