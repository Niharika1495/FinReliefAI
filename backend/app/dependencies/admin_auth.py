from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt
from app.auth.security import oauth2_scheme
from app.auth.jwt import decode_token
from app.dependencies.db import get_db
from app.models.admin import Admin

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Dependency injection provider that reads the Bearer token from headers,
    validates its signature and expiration, verifies the administrator role claim,
    and retrieves the authenticated Admin from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied. Administrator privileges required.",
    )
    
    try:
        # Decode the token payload
        payload = decode_token(token)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            raise credentials_exception
        if role != "admin":
            raise forbidden_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    # Query the corresponding admin from DB
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin is None:
        raise credentials_exception
        
    return admin
