from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import os

# Configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY or SECRET_KEY == "your-secret-key-change-in-production":
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set or is using default value. Please set a strong secret key.")

ALGORITHM = "HS256"
# Default expiration: 24 hours (consider reducing for sensitive applications)
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Validate expiration time is reasonable
if JWT_EXPIRATION_HOURS > 168:  # More than a week
    raise ValueError("JWT_EXPIRATION_HOURS should not exceed 168 hours (1 week) for security reasons.")
elif JWT_EXPIRATION_HOURS < 1:  # Less than 1 hour
    raise ValueError("JWT_EXPIRATION_HOURS should be at least 1 hour.")


def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for a user"""
    if expires_delta is None:
        expires_delta = timedelta(hours=JWT_EXPIRATION_HOURS)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(user_id),  # Subject = user_id
        "exp": expire,
        "iat": datetime.now(timezone.utc),  # Issued at
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def extract_token_jti(token: str) -> str:
    """Extract the JTI (JWT ID) from a token payload"""
    try:
        # Decode token without validation to get the claims
        from jose import jwt
        decoded_payload = jwt.get_unverified_claims(token)
        jti = decoded_payload.get("jti")
        if not jti:
            # Generate a unique JTI if none exists in token
            import hashlib
            import time
            jti = hashlib.sha256(f"{token}_{time.time()}".encode()).hexdigest()
        return jti
    except Exception:
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()


def get_user_id_from_token(token: str) -> UUID:
    """Extract user_id from a JWT token"""
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise JWTError("Token missing 'sub' claim")
    return UUID(user_id_str)
