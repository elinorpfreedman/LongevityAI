from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi_user import router as users_router
from fastapi_activity import router as physical_router
from fastapi_blood import router as blood_router
from fastapi_sleep import router as sleep_router
from database import get_db
from healthDB import Base, User, PhysicalActivity, SleepActivity, BloodTest

app = FastAPI(title="Health Tracker API")

# Include the routers
app.include_router(users_router)
app.include_router(physical_router)
app.include_router(blood_router)
app.include_router(sleep_router)

# --- Recommended values ---
TARGET_WEEKLY_ACTIVITY = 150  # minutes
RECOMMENDED_SLEEP_MIN = 420    # minutes (7 hours)
RECOMMENDED_SLEEP_MAX = 540    # minutes (9 hours)
BLOOD_TEST_NORMAL_RANGES = {
    "glucose": (70, 100),
    "cholesterol": (125, 200),
    "vitamin D": (20, 50),
}

# --- Helper ---
def blood_test_score(value: float, min_val: float, max_val: float) -> float:
    if min_val <= value <= max_val:
        return 100.0
    mid = (min_val + max_val) / 2
    score = max(0.0, 100 - abs(value - mid) / ((max_val - min_val)/2) * 100)
    return score

@app.get("/get_health_score")
def get_health_score(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # --- Physical Activity Score ---
    activities = db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).all()
    total_activity = sum(a.duration for a in activities)
    physical_score = min(total_activity / TARGET_WEEKLY_ACTIVITY * 100, 100) if activities else 0

    # --- Sleep Score ---
    sleeps = db.query(SleepActivity).filter(SleepActivity.user_id == user_id).all()
    if sleeps:
        avg_sleep = sum(s.duration for s in sleeps) / len(sleeps)
        if avg_sleep < RECOMMENDED_SLEEP_MIN:
            sleep_score = avg_sleep / RECOMMENDED_SLEEP_MIN * 50
        elif avg_sleep > RECOMMENDED_SLEEP_MAX:
            sleep_score = 50 + ((RECOMMENDED_SLEEP_MAX - (avg_sleep - RECOMMENDED_SLEEP_MAX)) / RECOMMENDED_SLEEP_MAX) * 50
            sleep_score = max(0, min(sleep_score, 100))
        else:
            sleep_score = 100
    else:
        sleep_score = 0

    # --- Blood Test Score ---
    blood_tests = db.query(BloodTest).filter(BloodTest.user_id == user_id).all()
    if blood_tests:
        scores = []
        for test in blood_tests:
            if test.test_name in BLOOD_TEST_NORMAL_RANGES:
                min_val, max_val = BLOOD_TEST_NORMAL_RANGES[test.test_name]
                scores.append(blood_test_score(test.result, min_val, max_val))
            else:
                scores.append(100)  # assume optimal
        blood_score = sum(scores) / len(scores)
    else:
        blood_score = 0

    # --- Aggregate Health Score ---
    health_score = (physical_score + sleep_score + blood_score) / 3

    # --- FHIR-Compliant Observation ---
    fhir_observation = {
        "resourceType": "Observation",
        "id": f"healthscore-{user_id}",
        "status": "final",
        "code": {"text": "Health Score"},
        "subject": {"reference": f"User/{user_id}"},
        "valueQuantity": {
            "value": round(health_score, 2),
            "unit": "percent",
            "system": "http://unitsofmeasure.org",
            "code": "%"
        }
    }

    return fhir_observation
