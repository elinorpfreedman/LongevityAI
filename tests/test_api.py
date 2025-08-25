import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from healthDB import Base, User, PhysicalActivity, SleepActivity, BloodTest
from main import app, get_db
import uuid

# -------------------------
# Test DB Setup
# -------------------------
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

def random_username(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def make_api_user(username=None, email=None):
    if username is None:
        username = random_username("api")
    if email is None:
        email = f"{username}@test.com"
    response = client.post("/users/", json={"username": username, "email": email})
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="module")
def db():
    # Reset database at start
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    username = random_username("fixture")
    user = User(username=username, email=f"{username}@test.com")
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(User).delete()
    db.commit()

def test_create_user():
    username = random_username("create")
    response = client.post("/users/", json={"username": username, "email": f"{username}@test.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username

def test_get_user():
    user = make_api_user()
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]

def test_update_user():
    user = make_api_user()
    new_username = random_username("updated")
    response = client.put(f"/users/{user['id']}", json={"username": new_username, "email": user["email"]})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == new_username

def test_delete_user():
    user = make_api_user()
    response = client.delete(f"/users/{user['id']}")
    assert response.status_code == 200
    # Verify deleted
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 404

@pytest.fixture
def physical_activity_fixture(test_user, db):
    activity = PhysicalActivity(user_id=test_user.id, activity_type="running", duration=60)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    yield activity
    db.query(PhysicalActivity).delete()
    db.commit()

def test_create_physical_activity(test_user):
    payload = {"activity_type": "cycling", "duration": 45}
    response = client.post(f"/activities/?user_id={test_user.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["activity_type"] == "cycling"
    assert data["duration"] == 45
    assert data["user_id"] == test_user.id

def test_update_physical_activity(physical_activity_fixture):
    payload = {"activity_type": "swimming", "duration": 30}
    response = client.put(f"/activities/{physical_activity_fixture.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["activity_type"] == "swimming"
    assert data["duration"] == 30

def test_delete_physical_activity(physical_activity_fixture, db):
    response = client.delete(f"/activities/{physical_activity_fixture.id}")
    assert response.status_code == 200
    assert db.query(PhysicalActivity).filter(PhysicalActivity.id == physical_activity_fixture.id).first() is None


@pytest.fixture
def sleep_activity_fixture(test_user, db):
    start = datetime(2025, 8, 24, 22, 0)
    end = datetime(2025, 8, 25, 6, 0)
    sleep = SleepActivity(user_id=test_user.id, start_time=start, end_time=end, quality="ok")
    db.add(sleep)
    db.commit()
    db.refresh(sleep)
    yield sleep
    db.query(SleepActivity).delete()
    db.commit()

def test_create_sleep_activity(test_user):
    start = datetime(2025, 8, 24, 22, 0)
    end = datetime(2025, 8, 25, 6, 0)
    payload = {"start_time": start.isoformat(), "end_time": end.isoformat(), "quality": "good"}
    response = client.post(f"/sleep/?user_id={test_user.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    expected_duration = int((end - start).total_seconds() / 60)
    assert data["duration"] == expected_duration
    assert data["quality"] == "good"

def test_update_sleep_activity(sleep_activity_fixture):
    new_end = sleep_activity_fixture.end_time + timedelta(hours=1)
    payload = {"end_time": new_end.isoformat(), "quality": "excellent"}
    response = client.put(f"/sleep/{sleep_activity_fixture.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    expected_duration = int((new_end - sleep_activity_fixture.start_time).total_seconds() / 60)
    assert data["duration"] == expected_duration
    assert data["quality"] == "excellent"

def test_delete_sleep_activity(sleep_activity_fixture, db):
    response = client.delete(f"/sleep/{sleep_activity_fixture.id}")
    assert response.status_code == 200
    assert db.query(SleepActivity).filter(SleepActivity.id == sleep_activity_fixture.id).first() is None


@pytest.fixture
def blood_test_fixture(test_user, db):
    test = BloodTest(user_id=test_user.id, test_name="glucose", result=90, unit="mg/dL")
    db.add(test)
    db.commit()
    db.refresh(test)
    yield test
    db.query(BloodTest).delete()
    db.commit()

def test_create_blood_test(test_user):
    payload = {"test_name": "cholesterol", "result": 180, "unit": "mg/dL"}
    response = client.post(f"/blood/?user_id={test_user.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["test_name"] == "cholesterol"
    assert data["result"] == 180

def test_update_blood_test(blood_test_fixture):
    payload = {"result": 190}
    response = client.put(f"/blood/{blood_test_fixture.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 190

def test_delete_blood_test(blood_test_fixture, db):
    response = client.delete(f"/blood/{blood_test_fixture.id}")
    assert response.status_code == 200
    assert db.query(BloodTest).filter(BloodTest.id == blood_test_fixture.id).first() is None
