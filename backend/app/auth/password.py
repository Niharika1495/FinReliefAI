import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a plaintext password string using the native bcrypt library.
    Generates a secure salt automatically and returns the decoded hash.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a pre-hashed password using the native bcrypt library.
    Returns True if credentials match, otherwise False.
    """
    try:
        plain_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False
