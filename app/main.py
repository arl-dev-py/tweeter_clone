from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
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

# SUPERUSER БЕЗ АВТОРИЗАЦИИ
app.include_router(users.router, prefix="/api")
# Остальные С АВТОРИЗАЦИЕЙ
app.include_router(tweets.router, prefix="/api", dependencies=[Depends(api_key_auth)])
app.include_router(medias.router, prefix="/api", dependencies=[Depends(api_key_auth)])


@app.get("/")
async def root():
    return {"message": "Microblog API running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
