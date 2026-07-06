from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt
from app.auth.security import oauth2_scheme
from app.auth.jwt import decode_token
from app.dependencies.db import get_db
from app.models.user import User

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency injection provider that reads the Bearer token from headers,
    validates its signature and expiration, and retrieves the authenticated User.
    Raises standard HTTP 401 Unauthorized errors on authentication failures.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token payload
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    # Query the corresponding user from DB
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user
