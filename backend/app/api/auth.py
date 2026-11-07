from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.connection import get_db
from app.database.repositories.user_repo import UserRepository
from app.security.authentication import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from app.database.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    if await repo.get_by_username(req.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await repo.get_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    pwd_hash = get_password_hash(req.password)
    user = await repo.create_user(username=req.username, email=req.email, password_hash=pwd_hash)
    return UserResponse(id=user.id, username=user.username, email=user.email, is_active=user.is_active)


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
        except Exception:
            pass

    if not username or not password:
        try:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required",
        )

    repo = UserRepository(db)
    user = await repo.get_by_username(username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        user_id=user.id
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active
    )
