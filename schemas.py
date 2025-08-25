# schemas.py
from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class PhysicalActivityBase(BaseModel):
    activity_type: str
    duration: float

class PhysicalActivityCreate(PhysicalActivityBase):
    pass

class PhysicalActivityResponse(PhysicalActivityBase):
    id: int
    user_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class SleepActivityBase(BaseModel):
    start_time: datetime
    end_time: datetime
    quality: Optional[str] = None

class SleepActivityCreate(SleepActivityBase):
    pass

class SleepActivityResponse(SleepActivityBase):
    id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    quality: str
    duration: int | None = None
    
    model_config = {"from_attributes": True}

class BloodTestBase(BaseModel):
    test_name: str
    result: float
    unit: str

class BloodTestCreate(BloodTestBase):
    pass

class BloodTestResponse(BloodTestBase):
    id: int
    user_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class UserWithActivities(UserRead):
    physical_activities: List[PhysicalActivityResponse] = Field(default_factory=list)
    sleep_activities: List[SleepActivityResponse] = Field(default_factory=list)
    blood_tests: List[BloodTestResponse] = Field(default_factory=list)

