from fastapi import Header, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.engine import get_async_session
from db.models import User

api_key_scheme = APIKeyHeader(name="api-key", auto_error=False)


async def api_key_auth(
    api_key: str = Depends(api_key_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "Invalid API key")
    return user
