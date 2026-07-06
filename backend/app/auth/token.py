from typing import Any, Dict, Optional
import jwt
from app.auth.jwt import decode_token

def get_token_subject(token: str) -> Optional[str]:
    """
    Decodes a JWT access token and extracts the subject ('sub') claim,
    which normally represents the user email or ID.
    Returns None if decryption fails or if 'sub' is missing.
    """
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except (jwt.PyJWTError, Exception):
        return None
