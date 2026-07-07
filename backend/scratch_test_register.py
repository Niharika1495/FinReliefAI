import requests

payload = {
    "name": "IDAMAKANTI NIHARIKA",
    "email": "harika@gmail.com",
    "password": "Password123",
    "monthly_income": 2345,
    "monthly_expenses": 34
}

try:
    res = requests.post("http://localhost:8000/api/v1/auth/register", json=payload)
    print("Status code:", res.status_code)
    try:
        print("Response JSON:", res.json())
    except:
        print("Response Text:", res.text)
except Exception as e:
    print("Error:", e)
