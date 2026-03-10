import requests

BASE = "http://localhost:5000"

def test_health_ok():
    r = requests.get(f"{BASE}/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"