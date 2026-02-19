from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.routers import users, tweets, medias
from app.middleware import api_key_auth

app = FastAPI(title="Microblog Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, dependencies=[Depends(api_key_auth)])
app.include_router(tweets.router, dependencies=[Depends(api_key_auth)])
app.include_router(medias.router, dependencies=[Depends(api_key_auth)])

@app.get("/")
async def root():
    return {"message": "Microblog API running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
