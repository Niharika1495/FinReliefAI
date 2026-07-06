import sys
import httpx

BASE_URL = "http://127.0.0.1:8001/api/v1"

def print_result(step: int, description: str, passed: bool, error_msg: str = ""):
    status = "[OK]" if passed else "[ERROR]"
    msg = f" {error_msg}" if error_msg else ""
    print(f"{step}. {status} {description}{msg}")
    if not passed:
        sys.exit(1)

def run_tests():
    print("=== FinRelief AI Financial Health Analysis Engine Verification ===")

    # Step 1: Register and Login users
    print("1. Authenticating test clients...")
    client = httpx.Client()
    
    email_a = "usera.analysis@finrelief.ai"
    email_zero = "userzero.analysis@finrelief.ai"
    email_noloans = "usernoloan.analysis@finrelief.ai"
    password = "password123"

    # Clean up database of pre-existing test users using direct DB access
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        db.query(User).filter(User.email.in_([email_a, email_zero, email_noloans])).delete()
        db.commit()
        db.close()
    except Exception:
        pass

    # Register User A (High Debt, Overdue)
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User A Analysis",
        "email": email_a,
        "password": password,
        "monthly_income": 5000.0,
        "monthly_expenses": 2000.0
    })
    if r.status_code != 201:
        print_result(1, "Register User A", False, f"HTTP {r.status_code}: {r.text}")

    # Register User Zero (Zero Income)
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User Zero Analysis",
        "email": email_zero,
        "password": password,
        "monthly_income": 0.0,
        "monthly_expenses": 1000.0
    })
    if r.status_code != 201:
        print_result(1, "Register User Zero", False, f"HTTP {r.status_code}: {r.text}")

    # Register User No Loans
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User No Loans Analysis",
        "email": email_noloans,
        "password": password,
        "monthly_income": 4000.0,
        "monthly_expenses": 1500.0
    })
    if r.status_code != 201:
        print_result(1, "Register User No Loans", False, f"HTTP {r.status_code}: {r.text}")

    # Logins
    # User A
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_a, "password": password})
    token_a = r.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User Zero
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_zero, "password": password})
    token_zero = r.json()["access_token"]
    headers_zero = {"Authorization": f"Bearer {token_zero}"}

    # User No Loans
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_noloans, "password": password})
    token_noloans = r.json()["access_token"]
    headers_noloans = {"Authorization": f"Bearer {token_noloans}"}

    print_result(1, "User A, User Zero, and User No Loans successfully authenticated", True)

    # Step 2: Create loans for User A and User Zero
    print("2. Populating active loans...")
    # User A Loans
    loans_a = [
        {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 15000.0, "interest_rate": 16.0, "emi": 400.0, "overdue_months": 2},
        {"lender_name": "Citibank", "loan_type": "Personal", "outstanding_amount": 5000.0, "interest_rate": 8.5, "emi": 150.0, "overdue_months": 0}
    ]
    for idx, l_data in enumerate(loans_a):
        r = client.post(f"{BASE_URL}/loans", json=l_data, headers=headers_a)
        if r.status_code != 201:
            print_result(2, f"Create User A loan {idx}", False, r.text)

    # User Zero Loan
    loan_zero = {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 1000.0, "interest_rate": 5.0, "emi": 100.0, "overdue_months": 0}
    r = client.post(f"{BASE_URL}/loans", json=loan_zero, headers=headers_zero)
    if r.status_code != 201:
        print_result(2, "Create User Zero loan", False, r.text)

    print_result(2, "All loans successfully populated for target test users", True)

    # Step 3: Test GET /financial-analysis for User A
    print("3. Testing GET /financial-analysis for User A...")
    r = client.get(f"{BASE_URL}/financial-analysis", headers=headers_a)
    if r.status_code != 200:
        print_result(3, "GET /financial-analysis failed", False, f"HTTP {r.status_code}: {r.text}")
    
    res = r.json()
    if not res["success"] or res["message"] != "Financial analysis generated successfully.":
        print_result(3, "GET success response wrapper mismatch", False, str(res))
    
    data = res["data"]
    # Check User A math details
    # Surplus: 5000 - 2000 - 550 = 2450
    # DTI: 550 / 5000 = 11%
    # Score: Base 100 - (DTI penalty: 11 * 0.5 = 5.5) - (Outstanding penalty: 20000 / 5000 = 4.0) - (Overdue penalty: 2 * 10 = 20.0) - (High interest: 16% > 15% -> 5.0) = 65.5
    # Risk Level: MEDIUM
    # Repayment Capacity: GOOD (surplus > 1500 and dti < 30)
    # Total Outstanding: 20000
    # Total active loans: 2
    if data["monthly_surplus"] != 2450.0:
        print_result(3, "Monthly surplus calculation incorrect", False, f"Got {data['monthly_surplus']}")
    if data["dti_ratio"] != 11.0 or data["emi_ratio"] != 11.0:
        print_result(3, "DTI / EMI Ratio calculation incorrect", False, f"Got DTI {data['dti_ratio']}")
    if data["total_outstanding"] != 20000.0:
        print_result(3, "Total outstanding debt incorrect", False, f"Got {data['total_outstanding']}")
    if data["total_active_loans"] != 2:
        print_result(3, "Total active loans count incorrect", False, f"Got {data['total_active_loans']}")
    if data["financial_health_score"] != 65.5:
        print_result(3, "Financial Health Score calculation incorrect", False, f"Got {data['financial_health_score']}")
    if data["risk_level"] != "MEDIUM":
        print_result(3, "Risk Level mapping incorrect", False, f"Got {data['risk_level']}")
    if data["repayment_capacity"] != "GOOD":
        print_result(3, "Repayment Capacity mapping incorrect", False, f"Got {data['repayment_capacity']}")
    
    # Recommendations check: should include the 3 expected ones
    recs = data["recommendations"]
    if len(recs) < 3 or len(recs) > 5:
        print_result(3, "Recommendations count out of bounds", False, f"Got {len(recs)}: {recs}")
    
    expected_recs = [
        "Prioritize paying off high-interest loans first to save on interest costs.",
        "Prioritize resolving overdue accounts to stop late penalties and protect credit history.",
        "Consider increasing your monthly repayment amount to pay down outstanding balance faster."
    ]
    for expected in expected_recs:
        if expected not in recs:
            print_result(3, f"Recommendation trigger absent: '{expected}'", False, str(recs))
            
    print_result(3, "GET analysis returned perfectly computed rule results for User A", True)

    # Step 4: Test POST /financial-analysis/recalculate for User A
    print("4. Testing POST /financial-analysis/recalculate for User A...")
    r = client.post(f"{BASE_URL}/financial-analysis/recalculate", json={}, headers=headers_a)
    if r.status_code != 200:
        print_result(4, "POST recalculate failed", False, f"HTTP {r.status_code}: {r.text}")
    
    res = r.json()
    data = res["data"]
    if data["financial_health_score"] != 65.5:
        print_result(4, "Health score recalculate mismatch", False, str(data))
    print_result(4, "POST recalculation endpoint functional and matches GET values", True)

    # Step 5: Test database state updates
    print("5. Verifying database state persistence on financial-profile...")
    r = client.get(f"{BASE_URL}/financial-profile", headers=headers_a)
    if r.status_code != 200:
        print_result(5, "GET financial-profile retrieval failed", False, f"HTTP {r.status_code}")
    
    profile = r.json()["data"]
    if profile["dti_ratio"] != 11.0 or profile["monthly_surplus"] != 2450.0 or profile["stress_level"] != "MEDIUM":
        print_result(5, "Database profile update persistence verification failed", False, str(profile))
    print_result(5, "Financial profile model successfully populated and in sync with calculation engine", True)

    # Step 6: Test Zero Income boundary conditions
    print("6. Testing zero income boundary scenario...")
    r = client.get(f"{BASE_URL}/financial-analysis", headers=headers_zero)
    if r.status_code != 200:
        print_result(6, "GET analysis for User Zero failed", False, f"HTTP {r.status_code}")
    
    data = r.json()["data"]
    # Income = 0, EMI = 100 -> DTI = 100%, EMI ratio = 100%
    # Surplus: 0 - 1000 - 100 = -1100
    # Health Score: Base 100 - (DTI penalty: 100 * 0.5 = 50.0) - (Outstanding: 1000 / 5000 = 0.2) = 49.8
    # Risk Level: HIGH
    # Repayment capacity: VERY_WEAK (surplus < 0 or dti >= 70)
    if data["dti_ratio"] != 100.0 or data["emi_ratio"] != 100.0:
        print_result(6, "Zero income DTI ratio capping failed", False, str(data))
    if data["monthly_surplus"] != -1100.0:
        print_result(6, "Zero income monthly surplus incorrect", False, str(data))
    if data["financial_health_score"] != 49.8:
        print_result(6, "Zero income health score computation failed", False, str(data))
    if data["risk_level"] != "HIGH" or data["repayment_capacity"] != "VERY_WEAK":
        print_result(6, "Zero income risk/capacity classification mismatch", False, str(data))
    print_result(6, "Zero income safety boundaries validated successfully", True)

    # Step 7: Test No Loans boundary conditions
    print("7. Testing no active loans boundary scenario...")
    r = client.get(f"{BASE_URL}/financial-analysis", headers=headers_noloans)
    if r.status_code != 200:
        print_result(7, "GET analysis for User No Loans failed", False, f"HTTP {r.status_code}")
        
    data = r.json()["data"]
    # Income = 4000, Expenses = 1500, Loans = 0 -> surplus = 2500, DTI = 0, rates = 0, overdue = 0, score = 100
    if data["total_active_loans"] != 0 or data["total_outstanding"] != 0.0 or data["total_monthly_emi"] != 0.0:
        print_result(7, "No loans aggregates calculation incorrect", False, str(data))
    if data["average_interest_rate"] != 0.0 or data["highest_interest_rate"] != 0.0 or data["maximum_overdue_months"] != 0:
        print_result(7, "No loans metrics defaults incorrect", False, str(data))
    if data["financial_health_score"] != 100.0 or data["risk_level"] != "LOW" or data["repayment_capacity"] != "GOOD":
        print_result(7, "No loans health score classifications incorrect", False, str(data))
    
    recs = data["recommendations"]
    if len(recs) < 3 or len(recs) > 5:
        print_result(7, "No loans recommendations count out of bounds", False, str(recs))
    print_result(7, "No loans defaults and fallback recommendations validated successfully", True)

    # Cleanup test users from DB
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        db.query(User).filter(User.email.in_([email_a, email_zero, email_noloans])).delete()
        db.commit()
        db.close()
    except Exception:
        pass

    print("\n=== All Phase 6 API & Service Rules Verified Successfully (7/7) ===")

if __name__ == "__main__":
    run_tests()
