from database import SessionLocal, init_db
from healthDB import User, PhysicalActivity, SleepActivity, BloodTest
from datetime import datetime

def main():
    # Create tables if not present (dev only)
    init_db()

    db = SessionLocal()
    try:
        # 1) Create a user
        u = User(username="alice", email="alice@example.com")
        db.add(u)
        db.commit()
        db.refresh(u)
        print("Created user:", u.id, u.username, u.email)

        # 2) Read the user back
        got = db.query(User).filter_by(email="alice@example.com").first()
        print("Fetched user:", got.id, got.username)

        # 3) Create a physical activity for that user
        pa = PhysicalActivity(user_id=got.id, activity_type="running", duration=30.0)
        db.add(pa)
        db.commit()
        db.refresh(pa)
        print("Created activity:", pa.id, pa.activity_type, pa.duration)

        # 4) Create a sleep activity
        start = datetime(datetime.timezone.utc) - datetime.timedelta(hours=8)
        end = datetime(datetime.timezone.utc)
        sa = SleepActivity(user_id=got.id, start_time=start, end_time=end, quality="good")
        db.add(sa)
        db.commit()
        db.refresh(sa)
        print("Created sleep:", sa.id, sa.quality)

        # 5) Create a blood test
        bt = BloodTest(user_id=got.id, test_name="glucose", result=92.0, unit="mg/dL")
        db.add(bt)
        db.commit()
        db.refresh(bt)
        print("Created blood test:", bt.id, bt.test_name, bt.result, bt.unit)

        got_again = db.query(User).filter_by(id=got.id).first()
        print(
            "Counts -> activities:",
            len(got_again.physical_activities),
            "sleep:",
            len(got_again.sleep_activities),
            "blood:",
            len(got_again.blood_tests),
        )
    finally:
        db.close()

if __name__ == "__main__":
    main()
