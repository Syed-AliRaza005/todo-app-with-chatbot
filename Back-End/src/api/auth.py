from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
from typing import Annotated
import os

from ..database import get_db
from ..models import User, RevokedToken
from ..schemas import UserCreate, UserLogin, AuthResponse, UserResponse
from ..auth import hash_password, verify_password, create_access_token, get_user_id_from_token, decode_access_token
from ..dependencies import get_current_user_id


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return JWT token"""

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(new_user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""

    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id
    )


@router.post("/logout")
async def logout(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db)
):
    """Invalidate the current JWT token (server-side logout)"""

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token = authorization.replace("Bearer ", "")

    # Decode token to get expiration and user_id
    try:
        user_id = get_user_id_from_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Get token expiration from payload
    try:
        payload = decode_access_token(token)
        expires_at = datetime.fromtimestamp(payload["exp"])
    except Exception:
        # If we can't decode, use a default expiration of 24 hours from now
        expires_at = datetime.utcnow() + timedelta(hours=24)

    # Create revoked token record
    revoked_token = RevokedToken(
        token_jti=str(hash(token)),
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(revoked_token)
    db.commit()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get the current authenticated user's information"""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
