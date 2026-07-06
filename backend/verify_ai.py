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
    print("=== FinRelief AI Gemini AI Negotiation Engine Verification ===")

    # Step 1: Register and Login users
    print("1. Authenticating test clients...")
    client = httpx.Client()
    
    email_a = "usera.ai@finrelief.ai"
    email_b = "userb.ai@finrelief.ai"
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

    # Register User A
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User A AI",
        "email": email_a,
        "password": password,
        "monthly_income": 6000.0,
        "monthly_expenses": 3000.0
    })
    if r.status_code != 201:
        print_result(1, "Register User A", False, f"HTTP {r.status_code}: {r.text}")

    # Register User B
    r = client.post(f"{BASE_URL}/auth/register", json={
        "name": "User B AI",
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
    headers_a = {"Authorization": f"Bearer {token_a}", "x-gemini-api-key": "mock_key_success"}

    r = client.post(f"{BASE_URL}/auth/login", json={"email": email_b, "password": password})
    token_b = r.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}", "x-gemini-api-key": "mock_key_success"}

    print_result(1, "Users successfully authenticated", True)

    # Step 2: Create a loan for User A
    print("2. Populating active loan for User A...")
    loan_data = {"lender_name": "Chase Bank", "loan_type": "Personal", "outstanding_amount": 10000.0, "interest_rate": 18.0, "emi": 500.0, "overdue_months": 3}
    r = client.post(f"{BASE_URL}/loans", json=loan_data, headers=headers_a)
    if r.status_code != 201:
        print_result(2, "Create User A loan", False, r.text)
    loan_id = r.json()["data"]["id"]
    print_result(2, f"Active loan ID {loan_id} successfully created", True)

    # Step 3: Test POST /ai/negotiation-strategy
    print("3. Testing negotiation strategy generation...")
    r = client.post(f"{BASE_URL}/ai/negotiation-strategy", json={"loan_id": loan_id}, headers=headers_a)
    if r.status_code != 200:
        print_result(3, "POST /ai/negotiation-strategy failed", False, f"HTTP {r.status_code}: {r.text}")
    res = r.json()
    if not res["success"] or "strategy" not in res["data"] or not res["data"]["strategy"]:
        print_result(3, "Strategy structure invalid", False, str(res))
    strategy_text = res["data"]["strategy"]
    print_result(3, "Negotiation strategy successfully generated", True)

    # Step 4: Test POST /ai/settlement-letter
    print("4. Testing settlement request letter generation...")
    r = client.post(f"{BASE_URL}/ai/settlement-letter", json={"loan_id": loan_id}, headers=headers_a)
    if r.status_code != 200:
        print_result(4, "POST /ai/settlement-letter failed", False, f"HTTP {r.status_code}")
    res = r.json()
    if not res["success"] or "letter_content" not in res["data"]:
        print_result(4, "Letter content structure invalid", False, str(res))
    print_result(4, "Settlement request letter successfully generated", True)

    # Step 5: Test POST /ai/negotiation-email
    print("5. Testing negotiation email generation...")
    r = client.post(f"{BASE_URL}/ai/negotiation-email", json={"loan_id": loan_id}, headers=headers_a)
    if r.status_code != 200:
        print_result(5, "POST /ai/negotiation-email failed", False, f"HTTP {r.status_code}")
    res = r.json()
    if not res["success"] or "subject" not in res["data"] or "email_body" not in res["data"]:
        print_result(5, "Email response structure invalid", False, str(res))
    print_result(5, "Negotiation email successfully generated", True)

    # Step 6: Test POST /ai/financial-explanation
    print("6. Testing plain-English financial explanation generation...")
    r = client.post(f"{BASE_URL}/ai/financial-explanation", json={}, headers=headers_a)
    if r.status_code != 200:
        print_result(6, "POST /ai/financial-explanation failed", False, f"HTTP {r.status_code}")
    res = r.json()
    if not res["success"] or "explanation" not in res["data"]:
        print_result(6, "Explanation response structure invalid", False, str(res))
    print_result(6, "Financial analysis explanation successfully generated", True)

    # Step 7: Verify AI History Logging
    print("7. Verifying generation logging inside AIHistory...")
    r = client.get(f"{BASE_URL}/ai/history", headers=headers_a)
    if r.status_code != 200:
        print_result(7, "GET /ai/history failed", False, f"HTTP {r.status_code}")
    
    history_items = r.json()["data"]
    # We ran 4 AI actions, so we should have 4 history records
    if len(history_items) != 4:
        print_result(7, f"Expected 4 history logs, got {len(history_items)}", False)
        
    # Check one item details
    log_id = history_items[0]["id"]
    r = client.get(f"{BASE_URL}/ai/history/{log_id}", headers=headers_a)
    if r.status_code != 200:
        print_result(7, "GET /ai/history/{id} failed", False, f"HTTP {r.status_code}")
    
    log_item = r.json()["data"]
    if log_item["user_id"] != history_items[0]["user_id"] or not log_item["prompt"] or not log_item["response"]:
        print_result(7, "History record properties mismatched", False, str(log_item))
    print_result(7, "AI history log records successfully captured and queried", True)

    # Step 8: Multi-tenant Access control validation
    print("8. Testing multi-tenant access control for AI history...")
    # User B tries to read User A's history record -> returns 403 Forbidden or 404 Not Found
    r = client.get(f"{BASE_URL}/ai/history/{log_id}", headers=headers_b)
    if r.status_code not in (403, 404):
        print_result(8, "Security lock bypass allowed read access to foreign history", False, f"HTTP {r.status_code}")
    print_result(8, "Security access control checks block unauthorized history read requests", True)

    # Step 9: Edge Case - Invalid API Key
    print("9. Testing invalid API key error handling...")
    bad_headers = {"Authorization": f"Bearer {token_a}", "x-gemini-api-key": "mock_key_invalid"}
    r = client.post(f"{BASE_URL}/ai/financial-explanation", json={}, headers=bad_headers)
    if r.status_code != 401 or r.json()["error_code"] != "GEMINI_AUTHENTICATION_ERROR":
        print_result(step=9, description="Invalid API Key response validation", passed=False, error_msg=f"HTTP {r.status_code}: {r.text}")
    print_result(9, "Invalid key correctly rejected with 401 GEMINI_AUTHENTICATION_ERROR", True)

    # Step 10: Edge Case - Timeout Handling
    print("10. Testing API request timeout handling...")
    timeout_headers = {"Authorization": f"Bearer {token_a}", "x-gemini-api-key": "mock_key_timeout"}
    r = client.post(f"{BASE_URL}/ai/financial-explanation", json={}, headers=timeout_headers)
    if r.status_code != 504 or r.json()["error_code"] != "GEMINI_TIMEOUT":
         print_result(10, "Timeout response validation", False, f"HTTP {r.status_code}: {r.text}")
    print_result(10, "Timeouts correctly handled and wrapped in 504 GEMINI_TIMEOUT", True)

    # Step 11: Edge Case - Empty Response Handling
    print("11. Testing empty AI response handling...")
    empty_headers = {"Authorization": f"Bearer {token_a}", "x-gemini-api-key": "mock_key_empty"}
    r = client.post(f"{BASE_URL}/ai/financial-explanation", json={}, headers=empty_headers)
    if r.status_code != 500 or r.json()["error_code"] != "GEMINI_EMPTY_RESPONSE":
         print_result(11, "Empty response validation", False, f"HTTP {r.status_code}: {r.text}")
    print_result(11, "Empty responses correctly handled and wrapped in 500 GEMINI_EMPTY_RESPONSE", True)

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

    print("\n=== All Phase 8 API & Service Rules Verified Successfully (11/11) ===")

if __name__ == "__main__":
    run_tests()
