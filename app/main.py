from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import create_db_and_tables
from app.users import auth_backend, Fastapi_users
from app.schemas import UserRead, UserCreate, UserUpdate
from app.routers import posts, comments

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    await create_db_and_tables()
    yield

app = FastAPI(
    title="InstaBackend",
    description="A modular FastAPI image sharing backend",
    version="1.0.0",
    lifespan=lifespan
)

# Authentication Routers
app.include_router(
    Fastapi_users.get_auth_router(auth_backend), 
    prefix="/auth/jwt", 
    tags=["auth"]
)
app.include_router(
    Fastapi_users.get_register_router(UserRead, UserCreate), 
    prefix="/auth", 
    tags=["auth"]
)
app.include_router(
    Fastapi_users.get_verify_router(UserRead), 
    prefix="/auth", 
    tags=["auth"]
)
app.include_router(
    Fastapi_users.get_reset_password_router(), 
    prefix="/auth", 
    tags=["auth"]
)
app.include_router(
    Fastapi_users.get_users_router(UserRead, UserUpdate), 
    prefix="/users", 
    tags=["users"]
)

# Post Routers
app.include_router(posts.router, prefix="/posts", tags=["posts"])
# Comment Routers
app.include_router(comments.router, prefix="/comments", tags=["comments"])

@app.get("/")
async def root():
    return {"message": "Welcome to InstaBackend API. Go to /docs for documentation."}
