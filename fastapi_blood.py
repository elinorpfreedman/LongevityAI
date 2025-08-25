from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/blood",
    tags=["blood_tests"]
)

@router.post("/", response_model=schemas.BloodTestResponse)
def create_blood(user_id: int, test: schemas.BloodTestCreate, db: Session = Depends(get_db)):
    return crud.create_blood_test(db, user_id, test)

@router.get("/{test_id}", response_model=schemas.BloodTestResponse)
def read_blood(test_id: int, db: Session = Depends(get_db)):
    db_test = crud.get_blood_test(db, test_id)
    if not db_test:
        raise HTTPException(status_code=404, detail="Blood test not found")
    return db_test

@router.get("/user/{user_id}", response_model=list[schemas.BloodTestResponse])
def read_user_blood(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_blood_tests(db, user_id)

@router.put("/{test_id}", response_model=schemas.BloodTestResponse)
def update_blood(test_id: int, updates: dict, db: Session = Depends(get_db)):
    updated = crud.update_blood_test(db, test_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Blood test not found")
    return updated

@router.delete("/{test_id}", response_model=schemas.BloodTestResponse)
def delete_blood(test_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_blood_test(db, test_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blood test not found")
    return deleted
