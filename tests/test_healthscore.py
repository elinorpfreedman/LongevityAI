import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from healthDB import Base, User, PhysicalActivity, SleepActivity, BloodTest
from main import app, get_db
import random
from datetime import datetime, timedelta, timezone
import requests


SQLALCHEMY_TEST_DATABASE_URL = "postgresql+psycopg2://postgres:healthpass@localhost:5432/healthtracker_test"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def seed_users(db):
    users = []
    for i in range(5):
        user = User(username=f"user{i}", email=f"user{i}@test.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        # Add physical activities
        for _ in range(3):
            pa = PhysicalActivity(user_id=user.id, activity_type=random.choice(["running","cycling","swimming"]), duration=random.randint(20, 120))
            db.add(pa)
        # Add sleep activities
        for _ in range(3):
            start = datetime.now(timezone.utc) - timedelta(hours=random.randint(6, 10))
            end = start + timedelta(minutes=random.randint(360, 540))
            sa = SleepActivity(
                user_id=user.id,
                start_time=start,
                end_time=end,
                duration=(end - start).seconds // 60,
        quality=random.choice(["good","fair","poor"])
    )
            db.add(sa)
        # Add blood tests
        for _ in range(2):
            bt = BloodTest(user_id=user.id, test_name=random.choice(["glucose","cholesterol","vitamin D"]),
                           result=random.randint(20, 200), unit="mg/dL")
            db.add(bt)
        db.commit()
        users.append(user)
    yield users
    db.query(BloodTest).delete()
    db.query(SleepActivity).delete()
    db.query(PhysicalActivity).delete()
    db.query(User).delete()
    db.commit()


def test_get_health_score(seed_users):
    for user in seed_users:
        response = client.get(f"/get_health_score?user_id={user.id}")
        assert response.status_code == 200
        data = response.json()
        # Assuming your FHIR-compliant response has resourceType and valueQuantity
        assert "resourceType" in data
        assert data["resourceType"] in ["Observation", "DiagnosticReport"]
        assert "valueQuantity" in data
        assert "value" in data["valueQuantity"]
        assert isinstance(data["valueQuantity"]["value"], (int, float))
        
def test_health_score_no_data(db):
    user = User(username="nodata", email="nodata@test.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.get(f"/get_health_score?user_id={user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["valueQuantity"]["value"] == 0  # No data → score should be 0
    
def fetch_patient(patient_id):
    url = f"https://fhir.example.com/Patient/{patient_id}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return None

