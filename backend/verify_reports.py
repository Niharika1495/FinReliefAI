import sys
import os
import httpx
import time

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

BASE_URL = "http://127.0.0.1:8001/api/v1"

def print_result(step: int, description: str, passed: bool, error_msg: str = ""):
    status = "[OK]" if passed else "[ERROR]"
    msg = f" {error_msg}" if error_msg else ""
    print(f"  {step}. {status} {description}{msg}")
    if not passed:
        sys.exit(1)

def run_tests():
    print("=== Verify Reports & Export Engine ===")
    client = httpx.Client()
    
    email = "reports.test@finrelief.ai"
    password = "password123"
    
    # 1. Clean up user
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

    # 2. Register & Login
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "Report Test User",
        "email": email,
        "password": password,
        "monthly_income": 5000.0,
        "monthly_expenses": 3000.0
    })
    if r.status_code != 201:
        print_result(1, "Register Test User", False, f"HTTP {r.status_code}: {r.text}")
    
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if r.status_code != 200:
        print_result(2, "Login Test User", False, f"HTTP {r.status_code}: {r.text}")
    
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result(2, "Authenticated user", True)

    # 3. Create dummy loans to have report data
    loans_data = [
        {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 10000.0, "interest_rate": 8.5, "emi": 500.0, "overdue_months": 2},
        {"lender_name": "Citibank", "loan_type": "Credit Card", "outstanding_amount": 5000.0, "interest_rate": 18.0, "emi": 200.0, "overdue_months": 0}
    ]
    for i, ld in enumerate(loans_data):
        r = client.post(f"{BASE_URL}/loans", json=ld, headers=headers)
        if r.status_code != 201:
            print_result(3, f"Create loan {i}", False, f"HTTP {r.status_code}: {r.text}")
    print_result(3, "Added liabilities to user account", True)

    # 4. Request PDF reports
    for rtype in ["financial", "dashboard", "settlement", "loans"]:
        r = client.get(f"{BASE_URL}/reports/{rtype}/pdf", headers=headers)
        if r.status_code != 200:
            print_result(4, f"Download PDF for {rtype}", False, f"HTTP {r.status_code}")
        if "application/pdf" not in r.headers.get("content-type", ""):
            print_result(4, f"Validate PDF Content-Type for {rtype}", False, f"Headers: {r.headers}")
        print_result(4, f"Successfully exported PDF for {rtype}", True)

    # 5. Request CSV reports
    for rtype in ["financial", "dashboard", "settlement", "loans"]:
        r = client.get(f"{BASE_URL}/reports/{rtype}/csv", headers=headers)
        if r.status_code != 200:
            print_result(5, f"Download CSV for {rtype}", False, f"HTTP {r.status_code}")
        if "text/csv" not in r.headers.get("content-type", ""):
            print_result(5, f"Validate CSV Content-Type for {rtype}", False, f"Headers: {r.headers}")
        print_result(5, f"Successfully exported CSV for {rtype}", True)

    # 6. Test Reports Purging / Cleanup
    print("  6. Verifying cache cleanup behavior...")
    try:
        from app.services.report_service import ReportService, REPORTS_DIR
        os.makedirs(REPORTS_DIR, exist_ok=True)
        dummy_file = os.path.join(REPORTS_DIR, "dummy_old_report.pdf")
        with open(dummy_file, "w") as f:
            f.write("mock report content")
        
        two_hours_ago = time.time() - 7200
        os.utime(dummy_file, (two_hours_ago, two_hours_ago))
        
        ReportService.cleanup_old_reports()
        
        if os.path.exists(dummy_file):
            print_result(6, "Cleanup old reports", False, "Dummy old report was not deleted.")
        else:
            print_result(6, "Cleanup old reports deleted file older than 1 hour", True)
    except Exception as e:
        print_result(6, "Cleanup logic validation", False, str(e))

if __name__ == "__main__":
    run_tests()
