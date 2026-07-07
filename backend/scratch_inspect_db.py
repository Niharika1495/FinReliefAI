from app.database.session import SessionLocal
from app.models.user import User
from app.models.financial_profile import FinancialProfile

db = SessionLocal()
try:
    users = db.query(User).all()
    print("=== Registered Users ===")
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}, Income: {u.monthly_income}, Expenses: {u.monthly_expenses}")
        # Check financial profile
        profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == u.id).first()
        if profile:
            print(f"  Profile found: surplus={profile.monthly_surplus}, stress={profile.stress_level}")
        else:
            print("  [WARNING] No financial profile found!")
finally:
    db.close()
