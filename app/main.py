import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
DIR = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/static", StaticFiles(directory=DIR), name='static')
# /css/... → static/css/...
app.mount(
    "/css",
    StaticFiles(directory=os.path.join(DIR, "css")),
    name="css",
)

# /js/... → static/js/...
app.mount(
    "/js",
    StaticFiles(directory=os.path.join(DIR, "js")),
    name="js",
)
# SUPERUSER БЕЗ АВТОРИЗАЦИИ
app.include_router(users.router, prefix="/api")
# Остальные С АВТОРИЗАЦИЕЙ
app.include_router(tweets.router, prefix="/api", dependencies=[Depends(api_key_auth)])
app.include_router(medias.router, prefix="/api", dependencies=[Depends(api_key_auth)])


@app.get("/")
async def root():
    return FileResponse(os.path.join(DIR, "index.html"))

@app.get("/health")
async def health():
    return {"status": "healthy"}
