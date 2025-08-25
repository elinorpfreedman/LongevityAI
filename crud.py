from sqlalchemy.orm import Session
from healthDB import User, PhysicalActivity, SleepActivity, BloodTest
from schemas import UserCreate, PhysicalActivityCreate, SleepActivityCreate, BloodTestCreate
from datetime import datetime


def create_user(db: Session, user: UserCreate):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, updates: dict):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    for key, value in updates.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

def create_physical_activity(db: Session, user_id: int, activity: PhysicalActivityCreate):
    db_activity = PhysicalActivity(user_id=user_id, activity_type=activity.activity_type, duration=activity.duration)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_physical_activity(db: Session, activity_id: int):
    return db.query(PhysicalActivity).filter(PhysicalActivity.id == activity_id).first()

def get_user_activities(db: Session, user_id: int):
    return db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).all()

def update_physical_activity(db: Session, activity_id: int, updates: dict):
    activity = db.query(PhysicalActivity).filter(PhysicalActivity.id == activity_id).first()
    if not activity:
        return None
    for key, value in updates.items():
        setattr(activity, key, value)
    db.commit()
    db.refresh(activity)
    return activity

def delete_physical_activity(db: Session, activity_id: int):
    activity = db.query(PhysicalActivity).filter(PhysicalActivity.id == activity_id).first()
    if not activity:
        return None
    db.delete(activity)
    db.commit()
    return activity

def create_sleep_activity(db: Session, user_id: int, sleep: SleepActivityCreate):
    duration = int((sleep.end_time - sleep.start_time).total_seconds() / 60)
    db_sleep = SleepActivity(
        user_id=user_id,
        start_time=sleep.start_time,
        end_time=sleep.end_time,
        quality=sleep.quality,
        duration=duration
    )
    db.add(db_sleep)
    db.commit()
    db.refresh(db_sleep)
    return db_sleep

def get_sleep_activity(db: Session, sleep_id: int):
    return db.query(SleepActivity).filter(SleepActivity.id == sleep_id).first()

def get_user_sleep_activities(db: Session, user_id: int):
    return db.query(SleepActivity).filter(SleepActivity.user_id == user_id).all()

def update_sleep_activity(db: Session, sleep_id: int, updates: dict):
    sleep = db.query(SleepActivity).filter(SleepActivity.id == sleep_id).first()
    if not sleep:
        return None

    if "start_time" in updates and isinstance(updates["start_time"], str):
        updates["start_time"] = datetime.fromisoformat(updates["start_time"])
    if "end_time" in updates and isinstance(updates["end_time"], str):
        updates["end_time"] = datetime.fromisoformat(updates["end_time"])

    for key, value in updates.items():
        setattr(sleep, key, value)

    if "start_time" in updates or "end_time" in updates:
        sleep.duration = int((sleep.end_time - sleep.start_time).total_seconds() / 60)

    db.commit()
    db.refresh(sleep)
    return sleep

def delete_sleep_activity(db: Session, sleep_id: int):
    sleep = db.query(SleepActivity).filter(SleepActivity.id == sleep_id).first()
    if not sleep:
        return None
    db.delete(sleep)
    db.commit()
    return sleep


def create_blood_test(db: Session, user_id: int, test: BloodTestCreate):
    db_test = BloodTest(
        user_id=user_id,
        test_name=test.test_name,
        result=test.result,
        unit=test.unit
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

def get_blood_test(db: Session, test_id: int):
    return db.query(BloodTest).filter(BloodTest.id == test_id).first()

def get_user_blood_tests(db: Session, user_id: int):
    return db.query(BloodTest).filter(BloodTest.user_id == user_id).all()

def update_blood_test(db: Session, test_id: int, updates: dict):
    test = db.query(BloodTest).filter(BloodTest.id == test_id).first()
    if not test:
        return None
    for key, value in updates.items():
        setattr(test, key, value)
    db.commit()
    db.refresh(test)
    return test

def delete_blood_test(db: Session, test_id: int):
    test = db.query(BloodTest).filter(BloodTest.id == test_id).first()
    if not test:
        return None
    db.delete(test)
    db.commit()
    return test
