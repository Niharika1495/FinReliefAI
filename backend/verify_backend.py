import subprocess
import time
import sys
import os
import httpx

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_backend_verification():
    print("====================================================")
    print("      FinRelief AI - Backend Engine Verification    ")
    print("====================================================\n")

    python_bin = os.path.join("venv", "Scripts", "python.exe")
    if not os.path.exists(python_bin):
        python_bin = "python"

    # Delete existing SQLite database to ensure the schema is cleanly created from scratch
    db_path = "finrelief.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Deleted old finrelief.db to ensure clean database schema setup.")
        except Exception as delete_err:
            print(f"Warning: Could not delete database file: {delete_err}")

    print("Starting FastAPI Uvicorn server on port 8001...")
    server_process = subprocess.Popen(
        [python_bin, "-m", "uvicorn", "app.main:app", "--port", "8001", "--host", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    server_ready = False
    for attempt in range(15):
        time.sleep(1)
        try:
            r = httpx.get("http://127.0.0.1:8001/health", timeout=1.0)
            if r.status_code == 200:
                server_ready = True
                print("FastAPI server is healthy and listening on port 8001.\n")
                break
        except Exception:
            pass

    if not server_ready:
        print("[ERROR] Could not start backend FastAPI server or it timed out.")
        server_process.terminate()
        sys.exit(1)

    test_modules = [
        ("verify_reports", "Reports & Export Engine"),
        ("verify_notifications", "Notification & Reminder Engine"),
        ("verify_documents", "Document Upload & OCR"),
        ("verify_admin", "Admin Dashboard & Audit Logging"),
        ("verify_security", "Security Hardening & Rate Limiting")
    ]

    failed = False
    error_info = ""

    try:
        for module_name, desc in test_modules:
            print(f"\n--- Testing: {desc} ---")
            module = __import__(module_name)
            module.run_tests()
            print(f"--- Completed: {desc} ---\n")
    except Exception as e:
        failed = True
        error_info = str(e)
        import traceback
        traceback.print_exc()
    finally:
        print("\nShutting down backend server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("Backend server shutdown complete.")

    if failed:
        print(f"\n====================================================")
        print(f"[ERROR] Verification suite failed: {error_info}")
        print(f"====================================================")
        sys.exit(1)
    else:
        print(f"\n====================================================")
        print(f"[SUCCESS] All FinRelief AI Backend verification steps passed!")
        print(f"====================================================")
        sys.exit(0)

if __name__ == "__main__":
    run_backend_verification()
