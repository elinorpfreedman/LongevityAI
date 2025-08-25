from datetime import datetime
from healthDB import PhysicalActivity, SleepActivity, BloodTest


TARGET_WEEKLY_ACTIVITY = 150  
RECOMMENDED_SLEEP_MIN = 420    
RECOMMENDED_SLEEP_MAX = 540    
BLOOD_TEST_NORMAL_RANGES = {
    "glucose": (70, 100),
    "cholesterol": (125, 200),
    "vitamin D": (20, 50),
}

def single_blood_test_score(value: float, min_val: float, max_val: float) -> float:
    if min_val <= value <= max_val:
        return 100.0
    mid = (min_val + max_val) / 2
    score = max(0.0, 100 - abs(value - mid) / ((max_val - min_val)/2) * 100)
    return score

def blood_test_score(db, user) -> float:
    blood_tests = db.query(BloodTest).filter(BloodTest.user_id == user.id).all()
    if not blood_tests:
        return 0.0
    scores = []
    for test in blood_tests:
        if test.test_name in BLOOD_TEST_NORMAL_RANGES:
            min_val, max_val = BLOOD_TEST_NORMAL_RANGES[test.test_name]
            scores.append(single_blood_test_score(test.result, min_val, max_val))
        else:
            scores.append(100.0) 
    return sum(scores) / len(scores)

def sleep_score_calculation(db, user):
    sleeps = db.query(SleepActivity).filter(SleepActivity.user_id == user.id).all()
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
    return sleep_score

def physical_activity_score(db, user):
    activities = db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user.id).all()
    total_activity = sum(a.duration for a in activities)
    physical_score = min(total_activity / TARGET_WEEKLY_ACTIVITY * 100, 100) if activities else 0 
    return physical_score  

def calculate_health_score(user, db) -> float:
    physical_score = physical_activity_score(db, user)

    sleep_score = sleep_score_calculation(db, user)

    blood_score = blood_test_score(db,user)

    overall_score = (physical_score + sleep_score + blood_score) / 3
    return round(overall_score, 2)

def health_score_to_fhir(user_id: int, score: float) -> dict:
    """Return a FHIR-compliant Observation for the health score."""
    return {
        "resourceType": "Observation",
        "id": f"healthscore-{user_id}",
        "status": "final",
        "code": {"text": "Health Score"},
        "subject": {"reference": f"User/{user_id}"},
        "valueQuantity": {
            "value": score,
            "unit": "percent",
            "system": "http://unitsofmeasure.org",
            "code": "%"
        }
    }
