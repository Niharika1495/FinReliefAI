from fastapi.security import OAuth2PasswordBearer

# OAuth2PasswordBearer configuration for reading Bearer Tokens from Authorization Headers.
# Specifies the login endpoint where clients exchange credentials for tokens.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
