import sys
import os
import httpx

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

BASE_URL = "http://127.0.0.1:8001/api/v1"

def print_result(step: int, description: str, passed: bool, error_msg: str = ""):
    status = "[OK]" if passed else "[ERROR]"
    msg = f" {error_msg}" if error_msg else ""
    print(f"  {step}. {status} {description}{msg}")
    if not passed:
        sys.exit(1)

def run_tests():
    print("=== Verify Security Hardening & Rate Limiter ===")
    client = httpx.Client()
    
    email = "security.lock@finrelief.ai"
    password = "password123"
    
    # 1. Verify Account Lockouts
    print("  1. Testing account lockouts on multiple failed login attempts...")
    db = None
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        u = db.query(User).filter(User.email == email).first()
        if u:
            db.delete(u)
            db.commit()
    except Exception as e:
        print(f"Error cleaning user: {e}")
    finally:
        if db:
            db.close()
            
    try:
        r = client.post(f"{BASE_URL}/auth/register", json={
            "name": "Lockout Test User",
            "email": email,
            "password": password,
            "monthly_income": 4000.0,
            "monthly_expenses": 2000.0
        })
        if r.status_code != 201:
            print_result(1, "Register Lockout User", False, r.text)

        # Fail login 5 times
        for i in range(5):
            r = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "wrong_password_xyz"})
            if i < 4:
                if r.status_code != 401:
                    print_result(1, f"Failed login attempt {i+1}", False, f"Expected 401, got {r.status_code}")
            else:
                if r.status_code != 403:
                    print_result(1, "Lockout attempt 5", False, f"Expected 403 Locked, got {r.status_code}: {r.text}")
        
        # 6th attempt with correct password should still be blocked
        r = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if r.status_code != 403 or "locked" not in r.text.lower():
            print_result(1, "Lockout enforcement on 6th attempt", False, f"Expected HTTP 403, got {r.status_code}: {r.text}")
        else:
            print_result(1, "Successfully locked out user after 5 failed login attempts", True)
            
    except Exception as e:
        print_result(1, "Account lockout verification", False, str(e))

    # 2. Verify Security Headers
    print("  2. Checking HTTP Security Headers on health endpoint...")
    try:
        r = client.get("http://127.0.0.1:8001/health")
        if r.status_code != 200:
            print_result(2, "Access health endpoint", False, f"HTTP {r.status_code}")
            
        headers = r.headers
        expected_headers = {
            "X-XSS-Protection": "1; mode=block",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer-when-downgrade"
        }
        
        for k, v in expected_headers.items():
            if headers.get(k.lower()) != v:
                print_result(2, f"Check security header: {k}", False, f"Expected '{v}', got '{headers.get(k.lower())}'")
        
        print_result(2, "All 4 security headers present with correct values", True)
    except Exception as e:
        print_result(2, "Check security headers", False, str(e))

    # 3. Verify Rate Limiting
    print("  3. Testing rate limiting (sending > 100 requests to trigger 429)...")
    try:
        triggered = False
        for i in range(110):
            r = client.get("http://127.0.0.1:8001/health")
            if r.status_code == 429:
                triggered = True
                break
        
        if triggered:
            print_result(3, "Rate limiter blocked request with HTTP 429 after limit exceeded", True)
        else:
            print_result(3, "Rate limiter trigger", False, "Limit not triggered after 110 rapid requests.")
    except Exception as e:
        print_result(3, "Rate limit validation", False, str(e))

if __name__ == "__main__":
    run_tests()
