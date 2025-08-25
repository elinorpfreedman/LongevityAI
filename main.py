from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi_user import router as users_router
from fastapi_activity import router as physical_router
from fastapi_blood import router as blood_router
from fastapi_sleep import router as sleep_router
from database import get_db
from healthDB import Base, User, PhysicalActivity, SleepActivity, BloodTest
from healthscore import calculate_health_score
from healthscore import health_score_to_fhir

app = FastAPI(title="Health Tracker API")

# Include the routers
app.include_router(users_router)
app.include_router(physical_router)
app.include_router(blood_router)
app.include_router(sleep_router)


@app.get("/get_health_score")
def get_health_score_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    score = calculate_health_score(user, db)
    return health_score_to_fhir(user.id, score)