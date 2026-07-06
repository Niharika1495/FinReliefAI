import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.auth.jwt import decode_token
from app.database.session import SessionLocal
from app.models.user import User
from app.models.admin import Admin
from app.services.audit_service import AuditService

class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware executing after handlers to log database mutations, 
    identifying client IP, user IDs, and endpoints accessed.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method
        path = request.url.path
        
        response = await call_next(request)
        
        # Audit mutation requests (POST, PUT, DELETE) and authentication actions if successful
        is_mutation = method in {"POST", "PUT", "DELETE"}
        is_auth = "/auth/" in path or "/admin/login" in path
        
        if (is_mutation or is_auth) and response.status_code < 400:
            client_ip = request.client.host if request.client else "unknown"
            request_id = getattr(request.state, "request_id", None)
            
            user_id = None
            auth_header = request.headers.get("Authorization")
            db = SessionLocal()
            try:
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    try:
                        payload = decode_token(token)
                        role = payload.get("role")
                        subject = payload.get("sub")
                        
                        if role == "admin":
                            admin = db.query(Admin).filter(Admin.username == subject).first()
                            if admin:
                                user_id = admin.id
                        else:
                            user = db.query(User).filter(User.email == subject).first()
                            if user:
                                user_id = user.id
                    except Exception:
                        pass
                
                action = f"{method} {path} - Status: {response.status_code}"
                AuditService.create_log(
                    db=db,
                    user_id=user_id,
                    action=action,
                    ip_address=client_ip,
                    endpoint=path,
                    request_id=request_id
                )
            except Exception:
                pass
            finally:
                db.close()
                
        return response
