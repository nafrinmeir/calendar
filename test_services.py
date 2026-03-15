import os
import pytest
import requests
import time

API_URL = os.getenv("API_URL", "http://host.docker.internal:5091/health")
FRONT_URL = os.getenv("FRONT_URL", "http://host.docker.internal:5092/")
DASH_URL = os.getenv("DASH_URL", "http://host.docker.internal:5090/")

def wait_for_service(url, name):
    print(f"🔄 Waiting for {name} to be ready at {url}...")
    # מחכה יותר פעמים (15) ונותן לקונטיינר 10 שניות לענות בכל פעם
    for _ in range(15):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 500]:
                return True
        except requests.exceptions.RequestException:
            time.sleep(2)
    return False

def test_api_container():
    assert wait_for_service(API_URL, "API"), "❌ API container failed to start!"
    response = requests.get(API_URL, timeout=10)
    assert response.status_code in [200, 500]

def test_front_container():
    assert wait_for_service(FRONT_URL, "Frontend"), "❌ Frontend container failed to start!"
    response = requests.get(FRONT_URL, timeout=10)
    assert response.status_code == 200
    assert b"<html" in response.content.lower()

def test_dashboard_container():
    assert wait_for_service(DASH_URL, "Dashboard"), "❌ Dashboard container failed to start!"
    response = requests.get(DASH_URL, timeout=10)
    assert response.status_code == 200
    assert b"Live System Architecture" in response.content
