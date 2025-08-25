from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import get_user, get_users, create_user, update_user, delete_user
from schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

# Get all users
@router.get("/", response_model=list[UserResponse])
def get_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)

# Get user by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Update user
@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    db_user = update_user(db, user_id, updates.dict(exclude_unset=True))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Delete user
@router.delete("/{user_id}", response_model=UserResponse)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
