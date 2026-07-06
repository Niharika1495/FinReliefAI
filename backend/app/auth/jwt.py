from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from fastapi import HTTPException, status
from app.core.settings import settings

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a signed JSON Web Token (JWT) encoding the provided dictionary payload.
    Uses expiration duration defined in central settings.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Sign and encode the token using the secret key and designated algorithm
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes the claims of a JWT without explicit error wrapping.
    Raises jwt.ExpiredSignatureError or jwt.PyJWTError on failure.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a token's integrity and signature.
    Raises HTTP 401 Unauthorized exceptions for expired or malformed payloads.
    """
    try:
        payload = decode_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
