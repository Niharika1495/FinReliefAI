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
    print("=== Verify Document Upload & OCR Engine ===")
    client = httpx.Client()
    
    email = "documents.test@finrelief.ai"
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
        "name": "Document Test User",
        "email": email,
        "password": password,
        "monthly_income": 4500.0,
        "monthly_expenses": 2200.0
    })
    if r.status_code != 201:
        print_result(1, "Register Test User", False, f"HTTP {r.status_code}: {r.text}")
    
    r = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if r.status_code != 200:
        print_result(2, "Login Test User", False, f"HTTP {r.status_code}: {r.text}")
    
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result(2, "Authenticated user", True)

    # 3. Upload a mock PDF matching Chase Bank template
    print("  3. Uploading mock PDF...")
    pdf_content = b"%PDF-1.4 mock pdf structure bytes"
    files = {"file": ("mock_chase.pdf", pdf_content, "application/pdf")}
    r = client.post(f"{BASE_URL}/documents/upload", files=files, headers=headers)
    if r.status_code != 201:
        print_result(3, "Upload mock_chase.pdf", False, f"HTTP {r.status_code}: {r.text}")
    
    data = r.json()["data"]
    if data["extracted_lender"] != "Chase Bank" or data["extracted_amount"] != 10000.0 or data["extracted_emi"] != 500.0:
        print_result(3, "Validate OCR Extracted Data", False, f"Extracted details do not match: {data}")
    else:
        print_result(3, "Successfully uploaded PDF and verified high-fidelity OCR extraction", True)

    # 4. Upload file with invalid MIME type (text/plain)
    print("  4. Testing MIME validation restrictions...")
    txt_content = b"simple plain text data"
    files_invalid = {"file": ("mock_data.txt", txt_content, "text/plain")}
    r = client.post(f"{BASE_URL}/documents/upload", files=files_invalid, headers=headers)
    if r.status_code != 400:
        print_result(4, "Reject text/plain upload", False, f"Expected HTTP 400, got {r.status_code}: {r.text}")
    else:
        print_result(4, "Correctly rejected invalid MIME type (text/plain)", True)

    # 5. Fetch documents list
    print("  5. Checking documents list endpoint...")
    r = client.get(f"{BASE_URL}/documents", headers=headers)
    if r.status_code != 200:
        print_result(5, "List user documents", False, f"HTTP {r.status_code}")
    
    docs = r.json()["data"]
    if len(docs) != 1 or docs[0]["filename"] != "mock_chase.pdf":
        print_result(5, "Verify uploaded documents in list", False, f"List incorrect: {docs}")
    else:
        print_result(5, "Documents list endpoint returned correct entries", True)

if __name__ == "__main__":
    run_tests()
