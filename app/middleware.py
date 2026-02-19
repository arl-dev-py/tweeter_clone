from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def api_key_auth(request: Request, token: str = Depends(security)):
    if token.credentials != "test-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    request.state.api_key = token.credentials
