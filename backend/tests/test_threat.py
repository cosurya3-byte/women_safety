from app.routers.safety import ThreatIn, assess
def test_late_night_deviation_scores_risk():
    score,level,factors,_=assess(ThreatIn(latitude=1,longitude=1,hour=23,route_deviation=True,duration_minutes=0))
    assert score == 55 and level == "MODERATE" and "Late night travel" in factors
