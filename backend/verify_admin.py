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
    print("=== Verify Administrative & Audit Engine ===")
    client = httpx.Client()
    
    admin_user = "admin_tester"
    admin_pass = "admin_password_999"
    
    # 1. Clean up and seed admin directly in database
    print("  1. Seeding admin credentials in database...")
    db = None
    try:
        from app.database.session import SessionLocal
        from app.models.admin import Admin
        from app.auth.password import hash_password
        
        db = SessionLocal()
        existing = db.query(Admin).filter(Admin.username == admin_user).first()
        if existing:
            db.delete(existing)
            db.commit()
            
        hashed_pass = hash_password(admin_pass)
        admin = Admin(
            username=admin_user,
            email="admin.tester@finrelief.ai",
            password_hash=hashed_pass,
            role="admin"
        )
        db.add(admin)
        db.commit()
        print_result(1, "Seed administrator credentials in DB", True)
    except Exception as e:
        print_result(1, "Seed administrator credentials in DB", False, str(e))
    finally:
        if db:
            db.close()

    # 2. Login admin via endpoint
    print("  2. Testing admin login...")
    r = client.post(f"{BASE_URL}/admin/login", json={
        "username": admin_user,
        "password": admin_pass
    })
    if r.status_code != 200:
        print_result(2, "Login Admin", False, f"HTTP {r.status_code}: {r.text}")
    
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result(2, "Admin authenticated and issued access token", True)

    # 3. Retrieve admin dashboard metrics
    print("  3. Checking admin dashboard analytics...")
    r = client.get(f"{BASE_URL}/admin/dashboard", headers=headers)
    if r.status_code != 200:
        print_result(3, "Fetch admin dashboard", False, f"HTTP {r.status_code}")
    
    metrics = r.json()["data"]
    health = metrics["system_health"]
    if "cpu_usage_percent" not in health or "db_latency_ms" not in health:
        print_result(3, "Validate health indicators", False, f"Indicators missing: {health}")
    else:
        print_result(3, "Health indicators (CPU, Memory, Disk, DB Latency) loaded successfully", True)

    # 4. List users
    print("  4. Fetching system users list...")
    r = client.get(f"{BASE_URL}/admin/users", headers=headers)
    if r.status_code != 200:
        print_result(4, "Fetch users list", False, f"HTTP {r.status_code}")
    else:
        print_result(4, "System users list retrieved successfully", True)

    # 5. List loans
    print("  5. Fetching system loans list...")
    r = client.get(f"{BASE_URL}/admin/loans", headers=headers)
    if r.status_code != 200:
        print_result(5, "Fetch loans list", False, f"HTTP {r.status_code}")
    else:
        print_result(5, "System loans list retrieved successfully", True)

    # 6. Read audit logs
    print("  6. Checking mutation audit logs...")
    r = client.get(f"{BASE_URL}/admin/audit-logs", headers=headers)
    if r.status_code != 200:
        print_result(6, "Fetch audit logs", False, f"HTTP {r.status_code}")
    
    logs = r.json()["data"]
    if len(logs) == 0:
        print_result(6, "Validate audit log entries", False, "No audit logs found.")
    else:
        found_login = any("Admin login" in log["action"] for log in logs)
        if not found_login:
            print_result(6, "Verify admin login audit log entry", False, f"Admin login action missing from audit: {logs}")
        else:
            print_result(6, "Audit records loaded successfully and mutations tracked correctly", True)

if __name__ == "__main__":
    run_tests()
