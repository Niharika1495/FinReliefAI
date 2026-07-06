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
    print("=== FinRelief AI AI Settlement Recommendation Engine Verification ===")

    # Step 1: Register and Login users
    print("1. Authenticating test clients...")
    client = httpx.Client()
    
    email_a = "usera.settlement@finrelief.ai"
    email_b = "userb.settlement@finrelief.ai"
    email_zero = "userzero.settlement@finrelief.ai"
    email_noloans = "usernoloan.settlement@finrelief.ai"
    password = "password123"

    # Clean up database of pre-existing test users using direct DB access
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        db.query(User).filter(User.email.in_([email_a, email_b, email_zero, email_noloans])).delete()
        db.commit()
        db.close()
    except Exception:
        pass

    # Register User A
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User A Settlement",
        "email": email_a,
        "password": password,
        "monthly_income": 5000.0,
        "monthly_expenses": 2000.0
    })
    if r.status_code != 201:
        print_result(1, "Register User A", False, f"HTTP {r.status_code}: {r.text}")

    # Register User B
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User B Settlement",
        "email": email_b,
        "password": password,
        "monthly_income": 4000.0,
        "monthly_expenses": 1500.0
    })
    if r.status_code != 201:
        print_result(1, "Register User B", False, f"HTTP {r.status_code}: {r.text}")

    # Register User Zero
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User Zero Settlement",
        "email": email_zero,
        "password": password,
        "monthly_income": 0.0,
        "monthly_expenses": 1000.0
    })
    if r.status_code != 201:
        print_result(1, "Register User Zero", False, f"HTTP {r.status_code}: {r.text}")

    # Register User No Loans
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User No Loans Settlement",
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

    # User B
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_b, "password": password})
    token_b = r.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User Zero
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_zero, "password": password})
    token_zero = r.json()["access_token"]
    headers_zero = {"Authorization": f"Bearer {token_zero}"}

    # User No Loans
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_noloans, "password": password})
    token_noloans = r.json()["access_token"]
    headers_noloans = {"Authorization": f"Bearer {token_noloans}"}

    print_result(1, "Users successfully authenticated", True)

    # Step 2: Create loans for User A, User B, and User Zero
    print("2. Populating active loans...")
    # User A Loans:
    # 1. Personal, Outstanding: 15000, Rate: 16%, EMI: 400, Overdue: 3 months (Chase)
    # 2. Credit Card, Outstanding: 5000, Rate: 8.5%, EMI: 150, Overdue: 0 months (Citibank)
    # 3. Auto, Outstanding: 25000, Rate: 6.2%, EMI: 500, Overdue: 1 month (Wells Fargo) - to be soft deleted later
    loans_a = [
        {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 15000.0, "interest_rate": 16.0, "emi": 400.0, "overdue_months": 3},
        {"lender_name": "Citibank", "loan_type": "Credit Card", "outstanding_amount": 5000.0, "interest_rate": 8.5, "emi": 150.0, "overdue_months": 0},
        {"lender_name": "Wells Fargo", "loan_type": "Auto", "outstanding_amount": 25000.0, "interest_rate": 6.2, "emi": 500.0, "overdue_months": 1}
    ]
    created_loans_a = []
    for idx, l_data in enumerate(loans_a):
        r = client.post(f"{BASE_URL}/loans", json=l_data, headers=headers_a)
        if r.status_code != 201:
            print_result(2, f"Create User A loan {idx}", False, r.text)
        created_loans_a.append(r.json()["data"])

    # User B Loan
    loan_b = {"lender_name": "Bank of America", "loan_type": "Personal", "outstanding_amount": 8000.0, "interest_rate": 12.0, "emi": 200.0, "overdue_months": 0}
    r = client.post(f"{BASE_URL}/loans", json=loan_b, headers=headers_b)
    if r.status_code != 201:
        print_result(2, "Create User B loan", False, r.text)
    created_loan_b = r.json()["data"]

    # User Zero Loan
    loan_zero = {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 1000.0, "interest_rate": 5.0, "emi": 100.0, "overdue_months": 0}
    r = client.post(f"{BASE_URL}/loans", json=loan_zero, headers=headers_zero)
    if r.status_code != 201:
        print_result(2, "Create User Zero loan", False, r.text)

    print_result(2, "All active loans successfully populated in DB", True)

    # Step 3: Test GET /settlement calculations for User A before soft-delete
    print("3. Testing GET /settlement calculations for User A...")
    r = client.get(f"{BASE_URL}/settlement", headers=headers_a)
    if r.status_code != 200:
        print_result(3, "GET /settlement failed", False, f"HTTP {r.status_code}: {r.text}")
    
    recs = r.json()["data"]
    if len(recs) != 3:
        print_result(3, f"Expected 3 recommendations, got {len(recs)}", False, str(recs))

    # Verify fields of Chase Bank (Outstanding: 15000, Overdue: 3)
    chase_rec = next((x for x in recs if x["loan_id"] == created_loans_a[0]["id"]), None)
    if not chase_rec:
        print_result(3, "Chase Bank recommendation absent", False)
    
    # Assert Chase values
    # Eligibility: Overdue >= 3 -> ELIGIBLE
    # Risk calculation:
    #   DTI: Total EMI = 400 + 150 + 500 = 1050. DTI = (1050 / 5000) * 100 = 21%
    #   Health score: 100 - (DTI penalty: 21 * 0.5 = 10.5) - (Outstanding: 45000 / 5000 = 9.0) - (Overdue: 30) - (High interest: 16% > 15% -> 5) = 45.5
    #   Risk level: Score 45.5 is in [40, 60) -> HIGH
    #   High risk -> Settlement percentage: 60.0%
    # Recommended Amount: 15000 * 0.6 = 9000.0
    # Estimated Savings: 15000 - 9000 = 6000.0
    # Payoff Months: surplus = 5000 - 2000 - 1050 = 1950. Chase payoff capacity = 1950 + 400 = 2350. months = ceil(9000 / 2350) = 4 months.
    # Negotiation Difficulty: Overdue = 3, Outstanding = 15000, Rate = 16 -> overdue >= 3 (HIGH)
    if chase_rec["eligibility"] != "ELIGIBLE":
        print_result(3, "Chase eligibility calculation incorrect", False, str(chase_rec))
    if chase_rec["settlement_percentage"] != 60.0:
        print_result(3, "Chase percentage calculation incorrect", False, str(chase_rec))
    if chase_rec["recommended_amount"] != 9000.0:
        print_result(3, "Chase recommended amount incorrect", False, str(chase_rec))
    if chase_rec["estimated_savings"] != 6000.0:
        print_result(3, "Chase savings calculation incorrect", False, str(chase_rec))
    if chase_rec["estimated_payoff_months"] != 4:
        print_result(3, "Chase payoff months forecast incorrect", False, str(chase_rec))
    if chase_rec["negotiation_difficulty"] != "HIGH":
        print_result(3, "Chase difficulty analysis incorrect", False, str(chase_rec))

    print_result(3, "Individual recommendation properties verified successfully", True)

    # Step 4: Test GET /settlement/{loan_id} details & authorization
    print("4. Testing specific loan recommendation retrieve & multi-tenant auth...")
    loan_id_a = created_loans_a[0]["id"]
    r = client.get(f"{BASE_URL}/settlement/{loan_id_a}", headers=headers_a)
    if r.status_code != 200:
        print_result(4, "Fetch target loan recommendation failed", False, f"HTTP {r.status_code}")
    if r.json()["data"]["loan_id"] != loan_id_a:
        print_result(4, "Recommendation loan ID mismatch", False, r.text)

    # User B requests User A's recommendation -> returns 403 Forbidden or 404 Not Found
    r = client.get(f"{BASE_URL}/settlement/{loan_id_a}", headers=headers_b)
    if r.status_code not in (403, 404):
        print_result(4, "Multi-tenant bypass allowed read access", False, f"Allowed with HTTP {r.status_code}")
    print_result(4, "Single resource query and ownership locks successfully verified", True)

    # Step 5: Test Soft Delete Isolation
    print("5. Testing soft deleted loan isolation...")
    # Soft delete Wells Fargo loan (Outstanding: 25000)
    wells_fargo_id = created_loans_a[2]["id"]
    r = client.delete(f"{BASE_URL}/loans/{wells_fargo_id}", headers=headers_a)
    if r.status_code != 200:
        print_result(5, "Soft delete loan call failed", False)

    # Recalculate recommendations
    r = client.post(f"{BASE_URL}/settlement/recalculate", headers=headers_a)
    if r.status_code != 200:
        print_result(5, "POST recalculate failed", False)
    
    recs_new = r.json()["data"]
    if len(recs_new) != 2:
        print_result(5, "Recalculate did not drop soft-deleted loan recommendation", False, f"Got {len(recs_new)} items")
    if any(x["loan_id"] == wells_fargo_id for x in recs_new):
        print_result(5, "Soft-deleted loan still present in recommendations", False)
        
    print_result(5, "Soft-deleted loan successfully filtered out from computations", True)

    # Step 6: Test GET /settlement/summary aggregates for User A (now with 2 active loans)
    print("6. Testing GET /settlement/summary for User A...")
    # Active:
    # 1. Personal, Chase, 15000, rate: 16%, emi: 400, overdue: 3 months. (Eligible)
    # 2. Credit Card, Citibank, 5000, rate: 8.5%, emi: 150, overdue: 0. (Not eligible)
    # New Health calculation:
    #   total emi = 550. DTI = 11.0%. Health score: 100 - (dti: 5.5) - (out: 20000/5000 = 4) - (overdue: 30) - (high interest: 5) = 55.5 (HIGH risk)
    # Recommended %: 60% for both.
    # Recommended amount: Chase = 9000.0, Citibank = 3000.0. Total recommended = 12000.0.
    # Savings: Chase = 6000.0, Citibank = 2000.0. Total savings = 8000.0.
    # Eligible count: Only Chase is eligible (eligibility check is Overdue >= 3 OR DTI > 60 OR Health Score < 50) -> count = 1.
    # Average settlement % for eligible loans: 60.0%
    r = client.get(f"{BASE_URL}/settlement/summary", headers=headers_a)
    if r.status_code != 200:
        print_result(6, "GET /settlement/summary failed", False, f"HTTP {r.status_code}: {r.text}")
    
    summary = r.json()["data"]
    if summary["eligible_loans"] != 1:
        print_result(6, "Eligible loans count incorrect in summary", False, str(summary))
    if summary["average_settlement_percentage"] != 60.0:
        print_result(6, "Average settlement percentage incorrect in summary", False, str(summary))
    if summary["total_savings"] != 8000.0:
        print_result(6, "Total savings incorrect in summary", False, str(summary))
    if summary["total_recommended_settlement"] != 12000.0:
        print_result(6, "Total recommended settlement incorrect in summary", False, str(summary))
    if summary["highest_priority_loan_id"] != created_loans_a[0]["id"] or summary["highest_priority_loan_lender"] != "Chase Bank":
        print_result(6, "Highest priority loan fields incorrect in summary", False, str(summary))
        
    recs_tips = summary["recommendations"]
    if len(recs_tips) < 3 or len(recs_tips) > 5:
        print_result(6, "Recommendations count out of range in summary", False, str(recs_tips))
    print_result(6, "Settlement summary aggregations validated successfully", True)

    # Step 7: Zero Income checks for User Zero
    print("7. Testing zero income calculations boundary...")
    r = client.get(f"{BASE_URL}/settlement/summary", headers=headers_zero)
    if r.status_code != 200:
        print_result(7, "GET summary for User Zero failed", False, f"HTTP {r.status_code}")
    
    summary_zero = r.json()["data"]
    # User Zero: 1 loan, outstanding 1000, rate 5, emi 100, overdue 0. DTI = 100.0% (due to zero income)
    # Overdue = 0, DTI = 100% (>60), Health score = 49.8 (<50) -> ELIGIBLE -> count = 1.
    # Recommended %: High risk -> 60.0%
    # Savings: 1000 - 600 = 400.0
    if summary_zero["eligible_loans"] != 1:
        print_result(7, "Zero income eligible loans mismatch", False, str(summary_zero))
    if summary_zero["total_savings"] != 400.0 or summary_zero["total_recommended_settlement"] != 600.0:
        print_result(7, "Zero income calculations mismatch", False, str(summary_zero))
        
    # Check payoff months directly for User Zero
    r = client.get(f"{BASE_URL}/settlement", headers=headers_zero)
    rec_zero = r.json()["data"][0]
    # Surplus: 0 - 1000 - 100 = -1100. Divisor = surplus + emi = -1100 + 100 = -1000 (not >0) -> payoff months defaults to 60.
    if rec_zero["estimated_payoff_months"] != 60:
        print_result(7, "Zero income payoff months defaulting failed", False, str(rec_zero))
        
    print_result(7, "Zero income bounds handled successfully", True)

    # Step 8: No Loans check
    print("8. Testing no active loans boundary...")
    r = client.get(f"{BASE_URL}/settlement/summary", headers=headers_noloans)
    if r.status_code != 200:
        print_result(8, "GET summary for User No Loans failed", False)
        
    summary_no = r.json()["data"]
    if summary_no["eligible_loans"] != 0 or summary_no["total_savings"] != 0.0 or summary_no["total_recommended_settlement"] != 0.0:
        print_result(8, "No loans summary values incorrect", False, str(summary_no))
    if summary_no["highest_priority_loan_id"] is not None or summary_no["highest_priority_loan_lender"] is not None:
        print_result(8, "No loans priority fields incorrect", False, str(summary_no))
    if len(summary_no["recommendations"]) < 2:
        print_result(8, "No loans default recommendations missing", False, str(summary_no))
    print_result(8, "No active loans bounds verified successfully", True)

    # Cleanup test users from DB
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        db.query(User).filter(User.email.in_([email_a, email_b, email_zero, email_noloans])).delete()
        db.commit()
        db.close()
    except Exception:
        pass

    print("\n=== All Phase 7 API & Service Rules Verified Successfully (8/8) ===")

if __name__ == "__main__":
    run_tests()
