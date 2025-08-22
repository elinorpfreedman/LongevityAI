from sqlalchemy import (
    Table, Column, Integer, String, ForeignKey, DateTime, Float, MetaData
)
from sqlalchemy.orm import registry, relationship
import datetime

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, unique=True, nullable=False),
    Column("email", String, unique=True, nullable=False, index=True),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "physical_activities": relationship(
            "PhysicalActivity", back_populates="user", cascade="all, delete-orphan"
        ),
        "sleep_activities": relationship(
            "SleepActivity", back_populates="user", cascade="all, delete-orphan"
        ),
        "blood_tests": relationship(
            "BloodTest", back_populates="user", cascade="all, delete-orphan"
        ),
    },
)

physical_activity_table = Table(
    "physical_activities",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("activity_type", String, nullable=False),
    Column("duration", Float, nullable=False),
    Column("timestamp", DateTime, default=datetime.datetime.utcnow),
)

class PhysicalActivity:
    def __init__(self, user_id: int, activity_type: str, duration: float):
        self.user_id = user_id
        self.activity_type = activity_type
        self.duration = duration
        self.timestamp = datetime.datetime.utcnow()

mapper_registry.map_imperatively(
    PhysicalActivity,
    physical_activity_table,
    properties={
        "user": relationship("User", back_populates="physical_activities"),
    },
)

sleep_activity_table = Table(
    "sleep_activities",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("start_time", DateTime, nullable=False),
    Column("end_time", DateTime, nullable=False),
    Column("quality", String),  
    Column("timestamp", DateTime, default=datetime.datetime.utcnow),
)

class SleepActivity:
    def __init__(self, user_id: int, start_time: datetime.datetime, end_time: datetime.datetime, quality: str):
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time
        self.quality = quality
        self.timestamp = datetime.datetime.utcnow()

mapper_registry.map_imperatively(
    SleepActivity,
    sleep_activity_table,
    properties={
        "user": relationship("User", back_populates="sleep_activities"),
    },
)

blood_test_table = Table(
    "blood_tests",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("test_name", String, nullable=False), 
    Column("result", Float, nullable=False),
    Column("unit", String, nullable=False), 
    Column("timestamp", DateTime, default=datetime.datetime.utcnow),
)

class BloodTest:
    def __init__(self, user_id: int, test_name: str, result: float, unit: str):
        self.user_id = user_id
        self.test_name = test_name
        self.result = result
        self.unit = unit
        self.timestamp = datetime.datetime.utcnow()

mapper_registry.map_imperatively(
    BloodTest,
    blood_test_table,
    properties={
        "user": relationship("User", back_populates="blood_tests"),
    },
)
