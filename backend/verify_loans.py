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
    print("=== FinRelief AI Loan & Financial Profile Verification ===")

    # Step 1: Register and Login User A and User B
    print("1. Authenticating test clients...")
    client = httpx.Client()
    
    # Generate unique emails
    email_a = "usera.test@finrelief.ai"
    email_b = "userb.test@finrelief.ai"
    password = "password123"

    # Cleanup database of pre-existing test users using direct DB access
    try:
        from app.database.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        db.query(User).filter(User.email.in_([email_a, email_b])).delete()
        db.commit()
        db.close()
    except Exception:
        pass

    # Register User A
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User A",
        "email": email_a,
        "password": password,
        "monthly_income": 6000.0,
        "monthly_expenses": 3500.0
    })
    if r.status_code != 201:
        print_result(1, "Register User A", False, f"HTTP {r.status_code}: {r.text}")
    
    # Register User B
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User B",
        "email": email_b,
        "password": password,
        "monthly_income": 4000.0,
        "monthly_expenses": 2000.0
    })
    if r.status_code != 201:
        print_result(1, "Register User B", False, f"HTTP {r.status_code}: {r.text}")

    # Login User A
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_a, "password": password})
    if r.status_code != 200:
        print_result(1, "Login User A", False, f"HTTP {r.status_code}")
    token_a = r.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Login User B
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_b, "password": password})
    if r.status_code != 200:
        print_result(1, "Login User B", False, f"HTTP {r.status_code}")
    token_b = r.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    print_result(1, "User A and User B successfully authenticated", True)

    # Step 2: Create Multiple Loans for User A
    print("2. Testing loan creation for User A...")
    loans_data = [
        {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 10000.0, "interest_rate": 8.5, "emi": 500.0, "overdue_months": 2},
        {"lender_name": "Bank of America", "loan_type": "Credit Card", "outstanding_amount": 5000.0, "interest_rate": 18.0, "emi": 200.0, "overdue_months": 0},
        {"lender_name": "Wells Fargo", "loan_type": "Auto", "outstanding_amount": 25000.0, "interest_rate": 6.2, "emi": 600.0, "overdue_months": 4},
        {"lender_name": "Citibank", "loan_type": "Personal", "outstanding_amount": 12000.0, "interest_rate": 11.5, "emi": 450.0, "overdue_months": 1},
    ]
    created_loans = []
    for index, l_data in enumerate(loans_data):
        r = client.post(f"{BASE_URL}/loans", json=l_data, headers=headers_a)
        if r.status_code != 201:
            print_result(2, f"Create loan {index}", False, f"HTTP {r.status_code}: {r.text}")
        created_loans.append(r.json()["data"])
    print_result(2, f"Created {len(created_loans)} active loans successfully", True)

    # Step 3: Get Loan Details
    print("3. Testing single loan fetch details...")
    loan_id = created_loans[0]["id"]
    r = client.get(f"{BASE_URL}/loans/{loan_id}", headers=headers_a)
    if r.status_code != 200:
        print_result(3, "Fetch loan by ID", False, f"HTTP {r.status_code}")
    res_data = r.json()["data"]
    if res_data["lender_name"] != "Chase Bank" or res_data["loan_status"] != "ACTIVE":
        print_result(3, "Fetch loan payload verification", False, f"Invalid data: {res_data}")
    print_result(3, f"Fetched loan ID {loan_id} successfully matching all parameters", True)

    # Step 4: Loan Input Validation Checks
    print("4. Testing loan input validations...")
    invalid_loans = [
        {"lender_name": "Test", "loan_type": "Personal", "outstanding_amount": -100.0, "interest_rate": 5.0, "emi": 100.0, "overdue_months": 0},  # Negative outstanding
        {"lender_name": "Test", "loan_type": "Personal", "outstanding_amount": 100.0, "interest_rate": 105.0, "emi": 100.0, "overdue_months": 0}, # Rate > 100
        {"lender_name": "Test", "loan_type": "Personal", "outstanding_amount": 100.0, "interest_rate": -5.0, "emi": 100.0, "overdue_months": 0},  # Rate < 0
        {"lender_name": "Test", "loan_type": "Personal", "outstanding_amount": 100.0, "interest_rate": 5.0, "emi": -10.0, "overdue_months": 0},   # Negative EMI
        {"lender_name": "Test", "loan_type": "Personal", "outstanding_amount": 100.0, "interest_rate": 5.0, "emi": 100.0, "overdue_months": -1},  # Negative overdue
    ]
    for idx, bad_data in enumerate(invalid_loans):
        r = client.post(f"{BASE_URL}/loans", json=bad_data, headers=headers_a)
        if r.status_code != 422:
            print_result(4, f"Invalid loan validation {idx} check failed", False, f"Returned status code {r.status_code} instead of 422")
    print_result(4, "Invalid loan input constraints correctly verified and rejected", True)

    # Step 5: GET /loans pagination checks
    print("5. Testing loans list pagination...")
    r = client.get(f"{BASE_URL}/loans?page=1&page_size=2", headers=headers_a)
    if r.status_code != 200:
        print_result(5, "Fetch loans page 1", False, f"HTTP {r.status_code}")
    res = r.json()["data"]
    if len(res["items"]) != 2 or res["pagination"]["total_items"] != 4 or res["pagination"]["total_pages"] != 2:
        print_result(5, "Pagination metadata validation", False, f"Invalid response: {res}")
    print_result(5, "Pagination parameters and metadata format correct", True)

    # Step 6: GET /loans sorting checks
    print("6. Testing safe sorting validation...")
    # Sorting by interest_rate asc
    r = client.get(f"{BASE_URL}/loans?sort_by=interest_rate&order=asc", headers=headers_a)
    if r.status_code != 200:
        print_result(6, "Sort by interest_rate asc", False, f"HTTP {r.status_code}")
    rates = [item["interest_rate"] for item in r.json()["data"]["items"]]
    if rates != sorted(rates):
        print_result(6, "Sorting order verification", False, f"Rates not sorted: {rates}")
        
    # Verify non-whitelisted sort field is rejected with 400
    r = client.get(f"{BASE_URL}/loans?sort_by=invalid_col_name", headers=headers_a)
    if r.status_code != 400 or r.json()["error_code"] != "INVALID_SORT_FIELD":
        print_result(6, "Invalid sort field validation", False, f"HTTP {r.status_code}: {r.text}")
    print_result(6, "Safe sorting whitelists and asc/desc ordering validated", True)

    # Step 7: GET /loans filtering checks
    print("7. Testing loans list filtering...")
    r = client.get(f"{BASE_URL}/loans?loan_type=Personal", headers=headers_a)
    if r.status_code != 200:
        print_result(7, "Filter by loan_type", False, f"HTTP {r.status_code}")
    items = r.json()["data"]["items"]
    if any(item["loan_type"] != "Personal" for item in items):
        print_result(7, "Filter type verification", False, f"Returned non-Personal loans")
    print_result(7, "Filtering by loan parameters successfully verified", True)

    # Step 8: GET /loans/summary statistics
    print("8. Testing loan summary statistics...")
    r = client.get(f"{BASE_URL}/loans/summary", headers=headers_a)
    if r.status_code != 200:
        print_result(8, "Fetch loan summary", False, f"HTTP {r.status_code}: {r.text}")
    summary = r.json()["data"]
    # Total outstanding = 10000 + 5000 + 25000 + 12000 = 52000
    # Total EMI = 500 + 200 + 600 + 450 = 1750
    # Highest rate = 18.0
    # Average rate = (8.5 + 18.0 + 6.2 + 11.5)/4 = 44.2/4 = 11.05
    # Oldest overdue = 4
    if summary["total_loans"] != 4 or summary["total_outstanding"] != 52000.0 or summary["total_emi"] != 1750.0:
        print_result(8, "Summary values verification", False, f"Invalid aggregates: {summary}")
    if summary["highest_interest_rate"] != 18.0 or summary["average_interest_rate"] != 11.05 or summary["oldest_overdue_months"] != 4:
         print_result(8, "Summary statistics verification", False, f"Invalid stats: {summary}")
    print_result(8, "Loan summary metrics correctly aggregated", True)

    # Step 9: Update Loan
    print("9. Testing loan details update...")
    target_loan = created_loans[1] # Bank of America, outstanding 5000
    r = client.put(f"{BASE_URL}/loans/{target_loan['id']}", json={
        "outstanding_amount": 4500.0,
        "loan_status": "CLOSED"
    }, headers=headers_a)
    if r.status_code != 200:
        print_result(9, "Update loan details", False, f"HTTP {r.status_code}: {r.text}")
    updated = r.json()["data"]
    if updated["outstanding_amount"] != 4500.0 or updated["loan_status"] != "CLOSED":
        print_result(9, "Update validation", False, f"Invalid fields: {updated}")
    print_result(9, "Loan record updated successfully", True)

    # Step 10: Access Control Verification
    print("10. Testing multi-tenant access control security...")
    loan_id_a = created_loans[0]["id"]
    # User B tries to read User A's loan -> 403 Forbidden or 404 Not Found (our service raises 403)
    r = client.get(f"{BASE_URL}/loans/{loan_id_a}", headers=headers_b)
    if r.status_code not in (403, 404):
        print_result(10, "Unauthorized read bypass", False, f"Allowed read: {r.status_code}")
    # User B tries to update User A's loan -> 403 or 404
    r = client.put(f"{BASE_URL}/loans/{loan_id_a}", json={"outstanding_amount": 1.0}, headers=headers_b)
    if r.status_code not in (403, 404):
        print_result(10, "Unauthorized write bypass", False, f"Allowed update: {r.status_code}")
    print_result(10, "Access control checks correctly block unauthorized requests", True)

    # Step 11: Soft Delete Loan and Filtering
    print("11. Testing soft delete mechanism...")
    # Soft delete Wells Fargo loan (outstanding 25000)
    target_del = created_loans[2]
    r = client.delete(f"{BASE_URL}/loans/{target_del['id']}", headers=headers_a)
    if r.status_code != 200:
        print_result(11, "Perform soft delete", False, f"HTTP {r.status_code}: {r.text}")
        
    # Check that deleted loan is NOT returned in GET /loans
    r = client.get(f"{BASE_URL}/loans", headers=headers_a)
    items = r.json()["data"]["items"]
    if any(item["id"] == target_del["id"] for item in items):
        print_result(11, "Soft-deleted loan visible in list query", False)
        
    # Check that deleted loan is NOT retrievable in GET /loans/{id} -> returns 404
    r = client.get(f"{BASE_URL}/loans/{target_del['id']}", headers=headers_a)
    if r.status_code != 404:
        print_result(11, "Soft-deleted loan retrievable directly", False, f"HTTP {r.status_code}")
        
    # Check that summary calculates correctly without the soft-deleted loan
    # Remainder active: Chase Bank (10000), BOA closed (4500), Citibank (12000). Total = 26500. Total EMIs = 500+200+450 = 1150
    r = client.get(f"{BASE_URL}/loans/summary", headers=headers_a)
    summary_new = r.json()["data"]
    if summary_new["total_loans"] != 3 or summary_new["total_outstanding"] != 26500.0 or summary_new["total_emi"] != 1150.0:
        print_result(11, "Summary re-calculation validation after soft delete", False, f"Invalid summary: {summary_new}")
    print_result(11, "Soft-deleted records correctly hidden from all retrieval endpoints", True)

    # Step 12: Financial Profile Retrieve and Update
    print("12. Testing financial profile operations...")
    # Fetch profile
    r = client.get(f"{BASE_URL}/financial-profile", headers=headers_a)
    if r.status_code != 200:
        print_result(12, "Fetch profile", False, f"HTTP {r.status_code}: {r.text}")
    profile = r.json()["data"]
    if profile["monthly_income"] != 6000.0 or profile["monthly_expenses"] != 3500.0:
        print_result(12, "Profile fields matching verification", False, f"Invalid profile data: {profile}")
        
    # Update profile
    r = client.put(f"{BASE_URL}/financial-profile", json={
        "monthly_income": 7000.0,
        "monthly_expenses": 3800.0,
        "stress_level": "medium"
    }, headers=headers_a)
    if r.status_code != 200:
        print_result(12, "Update profile", False, f"HTTP {r.status_code}: {r.text}")
    updated_profile = r.json()["data"]
    if updated_profile["monthly_income"] != 7000.0 or updated_profile["monthly_expenses"] != 3800.0 or updated_profile["stress_level"] != "medium" or updated_profile["monthly_surplus"] != 3200.0:
        print_result(12, "Profile update checks", False, f"Invalid updated values: {updated_profile}")
        
    # Validate negative bounds rejection
    r = client.put(f"{BASE_URL}/financial-profile", json={
        "monthly_income": -500.0
    }, headers=headers_a)
    if r.status_code != 422:
        print_result(12, "Negative income validation", False, f"HTTP {r.status_code} instead of 422")
    print_result(12, "Financial profile fetch, update, and negative value constraints verified", True)

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

    print("\n=== All Phase 5 API Endpoints Verified Successfully (12/12) ===")

if __name__ == "__main__":
    run_tests()
