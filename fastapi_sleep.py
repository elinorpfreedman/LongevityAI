from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/sleep",
    tags=["sleep_activities"]
)

@router.post("/", response_model=schemas.SleepActivityResponse)
def create_sleep(user_id: int, sleep: schemas.SleepActivityCreate, db: Session = Depends(get_db)):
    return crud.create_sleep_activity(db, user_id, sleep)

@router.get("/{sleep_id}", response_model=schemas.SleepActivityResponse)
def read_sleep(sleep_id: int, db: Session = Depends(get_db)):
    db_sleep = crud.get_sleep_activity(db, sleep_id)
    if not db_sleep:
        raise HTTPException(status_code=404, detail="Sleep activity not found")
    return db_sleep

@router.get("/user/{user_id}", response_model=list[schemas.SleepActivityResponse])
def read_user_sleep(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_sleep_activities(db, user_id)

@router.put("/{sleep_id}", response_model=schemas.SleepActivityResponse)
def update_sleep(sleep_id: int, updates: dict, db: Session = Depends(get_db)):
    updated = crud.update_sleep_activity(db, sleep_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Sleep activity not found")
    return updated

@router.delete("/{sleep_id}", response_model=schemas.SleepActivityResponse)
def delete_sleep(sleep_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_sleep_activity(db, sleep_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sleep activity not found")
    return deleted
