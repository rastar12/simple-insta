import uuid 
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin,models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_async_session, get_user_db
import os
import dotenv

dotenv.load_dotenv()
SECRET_KEY= os.getenv("SECRET_KEY")

class userManager(UUIDIDMixin, BaseUserManager[User,uuid.UUID]):
    reset_password_token_audience= SECRET_KEY
    verification_token_audience= SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user, token, request = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")
    async def on_after_request_verify(self, user, token, request = None):
            print(f"User {user.id} has requested verification. Verification token: {token}")

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield userManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

Fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)
current_active_user = Fastapi_users.current_user(active=True)