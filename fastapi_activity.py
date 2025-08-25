# fastapi_activity.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/activities",
    tags=["physical_activities"]
)

@router.post("/", response_model=schemas.PhysicalActivityResponse)
def create_activity(user_id: int, activity: schemas.PhysicalActivityCreate, db: Session = Depends(get_db)):
    return crud.create_physical_activity(db, user_id, activity)

@router.get("/{activity_id}", response_model=schemas.PhysicalActivityResponse)
def read_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = crud.get_physical_activity(db, activity_id)
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return db_activity

@router.get("/user/{user_id}", response_model=list[schemas.PhysicalActivityResponse])
def read_user_activities(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_activities(db, user_id)

@router.put("/{activity_id}", response_model=schemas.PhysicalActivityResponse)
def update_activity(activity_id: int, updates: dict, db: Session = Depends(get_db)):
    updated = crud.update_physical_activity(db, activity_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Activity not found")
    return updated

@router.delete("/{activity_id}", response_model=schemas.PhysicalActivityResponse)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_physical_activity(db, activity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Activity not found")
    return deleted
