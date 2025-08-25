# tests/test_integration.py
import pytest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from healthDB import Base, User, PhysicalActivity, SleepActivity, BloodTest
import crud
from schemas import UserCreate, PhysicalActivityCreate, SleepActivityCreate, BloodTestCreate

# ------------------- Test DB setup -------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # in-memory for tests
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for a test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# ------------------- User Tests -------------------
def test_create_user(db_session):
    user_in = UserCreate(username="testuser", email="testuser@test.com")
    user = crud.create_user(db_session, user_in)
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "testuser@test.com"

def test_get_user(db_session):
    user_in = UserCreate(username="getuser", email="getuser@test.com")
    created = crud.create_user(db_session, user_in)
    retrieved = crud.get_user(db_session, created.id)
    assert retrieved.id == created.id
    assert retrieved.username == "getuser"

def test_update_user(db_session):
    user_in = UserCreate(username="updateuser", email="update@test.com")
    user = crud.create_user(db_session, user_in)
    updated = crud.update_user(db_session, user.id, {"username": "updated"})
    assert updated.username == "updated"

def test_delete_user(db_session):
    user_in = UserCreate(username="deleteuser", email="delete@test.com")
    user = crud.create_user(db_session, user_in)
    deleted = crud.delete_user(db_session, user.id)
    assert deleted.id == user.id
    assert crud.get_user(db_session, user.id) is None

# ------------------- PhysicalActivity Tests -------------------
def test_create_physical_activity(db_session):
    user = crud.create_user(db_session, UserCreate(username="pauser", email="pa@test.com"))
    activity_in = PhysicalActivityCreate(activity_type="running", duration=30)
    activity = crud.create_physical_activity(db_session, user.id, activity_in)
    assert activity.id is not None
    assert activity.user_id == user.id
    assert activity.activity_type == "running"

def test_update_physical_activity(db_session):
    user = crud.create_user(db_session, UserCreate(username="pau", email="pau@test.com"))
    activity = crud.create_physical_activity(db_session, user.id, PhysicalActivityCreate(activity_type="cycling", duration=60))
    updated = crud.update_physical_activity(db_session, activity.id, {"duration": 75})
    assert updated.duration == 75

def test_delete_physical_activity(db_session):
    user = crud.create_user(db_session, UserCreate(username="padel", email="padel@test.com"))
    activity = crud.create_physical_activity(db_session, user.id, PhysicalActivityCreate(activity_type="swimming", duration=45))
    deleted = crud.delete_physical_activity(db_session, activity.id)
    assert deleted.id == activity.id
    assert crud.get_physical_activity(db_session, activity.id) is None

# ------------------- SleepActivity Tests -------------------
# ------------------- SleepActivity Tests -------------------
def test_create_sleep_activity(db_session):
    user = crud.create_user(db_session, UserCreate(username="sleepuser", email="sleep@test.com"))
    sleep_in = SleepActivityCreate(
        start_time=datetime(2025, 8, 24, 22, 0),
        end_time=datetime(2025, 8, 25, 6, 0),
        quality="good"
    )
    sleep = crud.create_sleep_activity(db_session, user.id, sleep_in)
    assert sleep.id is not None
    assert sleep.user_id == user.id
    assert sleep.quality == "good"
    # Duration in minutes
    assert sleep.duration == 480  # 8 hours * 60 minutes

def test_update_sleep_activity(db_session):
    user = crud.create_user(db_session, UserCreate(username="sleepupd", email="sleepupd@test.com"))
    sleep_in = SleepActivityCreate(
        start_time=datetime(2025, 8, 24, 23, 0),
        end_time=datetime(2025, 8, 25, 7, 0),
        quality="ok"
    )
    sleep = crud.create_sleep_activity(db_session, user.id, sleep_in)
    updated = crud.update_sleep_activity(db_session, sleep.id, {"quality": "excellent"})
    assert updated.quality == "excellent"
    # Make sure duration is still correct
    expected_duration = int((sleep_in.end_time - sleep_in.start_time).total_seconds() / 60)
    assert updated.duration == expected_duration

def test_delete_sleep_activity(db_session):
    user = crud.create_user(db_session, UserCreate(username="sleepdel", email="sleepdel@test.com"))
    sleep_in = SleepActivityCreate(
        start_time=datetime(2025, 8, 24, 21, 0),
        end_time=datetime(2025, 8, 25, 5, 0),
        quality="poor"
    )
    sleep = crud.create_sleep_activity(db_session, user.id, sleep_in)
    deleted = crud.delete_sleep_activity(db_session, sleep.id)
    assert deleted.id == sleep.id
    assert crud.get_sleep_activity(db_session, sleep.id) is None

# ------------------- BloodTest Tests -------------------
def test_create_blood_test(db_session):
    user = crud.create_user(db_session, UserCreate(username="blooduser", email="blood@test.com"))
    test_in = BloodTestCreate(test_name="cholesterol", result=190.5, unit="mg/dL")
    test = crud.create_blood_test(db_session, user.id, test_in)
    assert test.id is not None
    assert test.user_id == user.id
    assert test.test_name == "cholesterol"

def test_update_blood_test(db_session):
    user = crud.create_user(db_session, UserCreate(username="bloodupd", email="bloodupd@test.com"))
    test = crud.create_blood_test(db_session, user.id, BloodTestCreate(test_name="glucose", result=110, unit="mg/dL"))
    updated = crud.update_blood_test(db_session, test.id, {"result": 105})
    assert updated.result == 105

def test_delete_blood_test(db_session):
    user = crud.create_user(db_session, UserCreate(username="blooddel", email="blooddel@test.com"))
    test = crud.create_blood_test(db_session, user.id, BloodTestCreate(test_name="vitamin D", result=30, unit="ng/mL"))
    deleted = crud.delete_blood_test(db_session, test.id)
    assert deleted.id == test.id
    assert crud.get_blood_test(db_session, test.id) is None
