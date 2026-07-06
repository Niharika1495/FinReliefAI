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
    print("=== FinRelief AI Dashboard & Analytics APIs Verification ===")

    # Step 1: Register and Login users
    print("1. Authenticating test clients...")
    client = httpx.Client()
    
    email_a = "usera.dash@finrelief.ai"
    email_b = "userb.dash@finrelief.ai"
    password = "password123"

    # Clean up database of pre-existing test users using direct DB access
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        db.query(User).filter(User.email.in_([email_a, email_b])).delete()
        db.commit()
        db.close()
    except Exception:
        pass

    # Register User A (Populated dashboard)
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User A Dashboard",
        "email": email_a,
        "password": password,
        "monthly_income": 6000.0,
        "monthly_expenses": 2500.0
    })
    if r.status_code != 201:
        print_result(1, "Register User A", False, f"HTTP {r.status_code}: {r.text}")

    # Register User B (No Loans, No AI)
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User B Dashboard",
        "email": email_b,
        "password": password,
        "monthly_income": 4000.0,
        "monthly_expenses": 1500.0
    })
    if r.status_code != 201:
        print_result(1, "Register User B", False, f"HTTP {r.status_code}: {r.text}")

    # Logins
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_a, "password": password})
    token_a = r.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_b, "password": password})
    token_b = r.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print_result(1, "Users successfully authenticated", True)

    # Step 2: Populate loans and AI histories for User A
    print("2. Populating liabilities and AI activities for User A...")
    loans_data = [
        {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 10000.0, "interest_rate": 15.5, "emi": 400.0, "overdue_months": 3},
        {"lender_name": "Citibank", "loan_type": "Credit Card", "outstanding_amount": 5000.0, "interest_rate": 9.5, "emi": 150.0, "overdue_months": 0}
    ]
    for idx, l_data in enumerate(loans_data):
        r = client.post(f"{BASE_URL}/loans", json=l_data, headers=headers_a)
        if r.status_code != 201:
            print_result(2, f"Create User A loan {idx}", False, r.text)

    # Generate some mock AI activity records directly in DB
    try:
        from app.database.session import SessionLocal
        from app.models.user import User as UserDB
        from app.models.ai_history import AIHistory
        db = SessionLocal()
        user_db_a = db.query(UserDB).filter(UserDB.email == email_a).first()
        
        # Add 3 AI history logs
        for i in range(3):
            hist = AIHistory(
                user_id=user_db_a.id,
                prompt_type="negotiation_strategy" if i == 0 else "settlement_letter",
                prompt=f"Prompt {i}",
                response=f"Response text {i}"
            )
            db.add(hist)
        db.commit()
        db.close()
    except Exception as db_err:
        print_result(2, "Failed direct DB insert for AI History", False, str(db_err))

    print_result(2, " Liabilities and AI activities populated successfully", True)

    # Step 3: Verify GET /dashboard/overview
    print("3. Testing GET /dashboard/overview for User A...")
    r = client.get(f"{BASE_URL}/dashboard/overview", headers=headers_a)
    if r.status_code != 200:
        print_result(3, "Overview endpoint failed", False, f"HTTP {r.status_code}: {r.text}")
    
    overview = r.json()["data"]
    if overview["user_name"] != "User A Dashboard" or overview["total_active_loans"] != 2:
        print_result(3, "Overview stats mismatch", False, str(overview))
    if overview["total_outstanding_amount"] != 15000.0 or overview["total_monthly_emi"] != 550.0:
        print_result(3, "Overview liability aggregates mismatch", False, str(overview))
    if overview["recent_ai_activity_count"] != 3:
        print_result(3, "Overview recent AI activity count mismatch", False, str(overview))
    print_result(3, "Overview aggregate metrics successfully verified", True)

    # Step 4: Verify GET /dashboard/financial-summary
    print("4. Testing GET /dashboard/financial-summary...")
    r = client.get(f"{BASE_URL}/dashboard/financial-summary", headers=headers_a)
    if r.status_code != 200:
        print_result(4, "Financial summary endpoint failed", False)
    
    fin = r.json()["data"]
    # income=6000, expenses=2500, emi=550 -> surplus = 2950
    if fin["income"] != 6000.0 or fin["expenses"] != 2500.0 or fin["emi"] != 550.0 or fin["surplus"] != 2950.0:
        print_result(4, "Financial stats mismatch", False, str(fin))
    print_result(4, "Financial surplus and income summary successfully verified", True)

    # Step 5: Verify GET /dashboard/loan-analytics
    print("5. Testing GET /dashboard/loan-analytics...")
    r = client.get(f"{BASE_URL}/dashboard/loan-analytics", headers=headers_a)
    if r.status_code != 200:
        print_result(5, "Loan analytics endpoint failed", False)
    
    lan = r.json()["data"]
    if lan["loan_count"] != 2 or lan["outstanding_amount"] != 15000.0:
        print_result(5, "Loan metrics mismatch", False, str(lan))
    if "Personal" not in lan["loan_type_distribution"] or lan["loan_type_distribution"]["Personal"] != 1:
        print_result(5, "Loan type distribution mismatch", False, str(lan))
    if lan["outstanding_amount_by_lender"]["Chase Bank"] != 10000.0:
        print_result(5, "Outstanding by lender split incorrect", False, str(lan))
    print_result(5, "Loan type/status distributions and lender splits successfully verified", True)

    # Step 6: Verify GET /dashboard/settlement-analytics
    print("6. Testing GET /dashboard/settlement-analytics...")
    r = client.get(f"{BASE_URL}/dashboard/settlement-analytics", headers=headers_a)
    if r.status_code != 200:
        print_result(6, "Settlement analytics endpoint failed", False)
        
    san = r.json()["data"]
    # Chase (overdue=3) is ELIGIBLE. Citibank (overdue=0, dti=9.1%, score=69.0) is NOT_ELIGIBLE.
    if san["eligible_loans"] != 1 or san["not_eligible_loans"] != 1 or san["partially_eligible_loans"] != 0:
         print_result(6, "Settlement eligibility categories counts mismatch", False, str(san))
    if san["negotiation_difficulty_distribution"]["HIGH"] != 1 or san["negotiation_difficulty_distribution"]["LOW"] != 1:
         print_result(6, "Negotiation difficulty splits mismatch", False, str(san))
    print_result(6, "Settlement eligibility segments and difficulties successfully verified", True)

    # Step 7: Verify GET /dashboard/ai-analytics
    print("7. Testing GET /dashboard/ai-analytics...")
    r = client.get(f"{BASE_URL}/dashboard/ai-analytics", headers=headers_a)
    if r.status_code != 200:
        print_result(7, "AI analytics endpoint failed", False)
        
    aian = r.json()["data"]
    if aian["total_ai_requests"] != 3:
        print_result(7, "Total AI requests count mismatch", False, str(aian))
    if aian["negotiation_strategies_generated"] != 1 or aian["settlement_letters_generated"] != 2:
        print_result(7, "Prompt type distribution count mismatch", False, str(aian))
    if len(aian["recent_ai_activities"]) != 3:
        print_result(7, "Recent activity list length mismatch", False, str(aian))
    print_result(7, "AI activity metrics and recent logs successfully verified", True)

    # Step 8: Verify GET /dashboard/charts
    print("8. Testing GET /dashboard/charts visualization formats...")
    r = client.get(f"{BASE_URL}/dashboard/charts", headers=headers_a)
    if r.status_code != 200:
        print_result(8, "Charts endpoint failed", False)
        
    charts = r.json()["data"]
    # type pie chart should have items
    if not charts["loan_type_pie_chart"] or charts["loan_type_pie_chart"][0]["name"] not in ("Personal", "Credit Card"):
        print_result(8, "Loan type pie chart format incorrect", False, str(charts))
    if not charts["outstanding_amount_by_lender"] or charts["outstanding_amount_by_lender"][0]["lender_name"] not in ("Chase Bank", "Citibank"):
        print_result(8, "Lender outstanding bar chart format incorrect", False, str(charts))
    print_result(8, "Chart data formats mapped correctly for visualization bindings", True)

    # Step 9: Verify No Loans scenario for User B
    print("9. Testing no active loans boundary checks for User B...")
    r = client.get(f"{BASE_URL}/dashboard/loan-analytics", headers=headers_b)
    if r.status_code != 200:
        print_result(9, "Loan analytics for User B failed", False)
    
    lan_b = r.json()["data"]
    if lan_b["loan_count"] != 0 or lan_b["outstanding_amount"] != 0.0 or len(lan_b["loan_type_distribution"]) != 0:
        print_result(9, "No loans scenario default stats incorrect", False, str(lan_b))
        
    r = client.get(f"{BASE_URL}/dashboard/charts", headers=headers_b)
    charts_b = r.json()["data"]
    if len(charts_b["loan_type_pie_chart"]) != 0 or len(charts_b["outstanding_amount_by_lender"]) != 0:
        print_result(9, "No loans chart data items should be empty", False, str(charts_b))
    print_result(9, "Zero active liabilities boundaries validated successfully", True)

    # Step 10: Verify No AI history scenario for User B
    print("10. Testing no AI history boundary checks for User B...")
    r = client.get(f"{BASE_URL}/dashboard/ai-analytics", headers=headers_b)
    if r.status_code != 200:
        print_result(10, "AI analytics for User B failed", False)
    
    aian_b = r.json()["data"]
    if aian_b["total_ai_requests"] != 0 or len(aian_b["recent_ai_activities"]) != 0:
        print_result(10, "No AI history default stats incorrect", False, str(aian_b))
    print_result(10, "Zero AI requests boundaries validated successfully", True)

    # Cleanup test users from DB
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        db.query(User).filter(User.email.in_([email_a, email_b])).delete()
        db.commit()
        db.close()
    except Exception:
        pass

    print("\n=== All Phase 9 Dashboard APIs Verified Successfully (10/10) ===")

if __name__ == "__main__":
    run_tests()
