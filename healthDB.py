from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, event
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

# ------------------- User -------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    physical_activities = relationship(
        "PhysicalActivity", back_populates="user", cascade="all, delete-orphan"
    )
    sleep_activities = relationship(
        "SleepActivity", back_populates="user", cascade="all, delete-orphan"
    )
    blood_tests = relationship(
        "BloodTest", back_populates="user", cascade="all, delete-orphan"
    )

# ------------------- PhysicalActivity -------------------
class PhysicalActivity(Base):
    __tablename__ = "physical_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String, nullable=False)
    duration = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="physical_activities")

# ------------------- SleepActivity -------------------
class SleepActivity(Base):
    __tablename__ = "sleep_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration = Column(Integer)
    quality = Column(String)

    user = relationship("User", back_populates="sleep_activities")

# Auto-calculate duration before insert
@event.listens_for(SleepActivity, "before_insert")
def calculate_sleep_duration(mapper, connection, target):
    if target.start_time and target.end_time:
        target.duration = int((target.end_time - target.start_time).total_seconds() / 60)

# ------------------- BloodTest -------------------
class BloodTest(Base):
    __tablename__ = "blood_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String, nullable=False)
    result = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="blood_tests")
