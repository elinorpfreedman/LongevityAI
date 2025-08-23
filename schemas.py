from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class PhysicalActivityBase(BaseModel):
    activity_type: str
    duration: float

class PhysicalActivityCreate(PhysicalActivityBase):
    pass

class PhysicalActivityResponse(PhysicalActivityBase):
    id: int
    user_id: int
    timestamp: datetime.datetime

    class Config:
        orm_mode = True


class SleepActivityBase(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    quality: Optional[str] = None

class SleepActivityCreate(SleepActivityBase):
    pass

class SleepActivityResponse(SleepActivityBase):
    id: int
    user_id: int
    timestamp: datetime.datetime

    class Config:
        orm_mode = True


class BloodTestBase(BaseModel):
    test_name: str
    result: float
    unit: str

class BloodTestCreate(BloodTestBase):
    pass

class BloodTestResponse(BloodTestBase):
    id: int
    user_id: int
    timestamp: datetime.datetime

    class Config:
        orm_mode = True


class UserWithActivities(UserResponse):
    physical_activities: List[PhysicalActivityResponse] = []
    sleep_activities: List[SleepActivityResponse] = []
    blood_tests: List[BloodTestResponse] = []
