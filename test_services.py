import os
import pytest
import requests
import time

# הגדרת הפורטים הזמניים שעליהם ירוצו הקונטיינרים שלנו בג'נקינס
API_URL = os.getenv("API_URL", "http://host.docker.internal:5091/health")
FRONT_URL = os.getenv("FRONT_URL", "http://host.docker.internal:5092/")
DASH_URL = os.getenv("DASH_URL", "http://host.docker.internal:5090/")

# פונקציית עזר שממתינה שהקונטיינר יעלה
def wait_for_service(url, name):
    print(f"🔄 Waiting for {name} to be ready at {url}...")
    for _ in range(10):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code in [200, 500]: # 500 תקין ב-API כי אין DB
                return True
        except requests.exceptions.RequestException:
            time.sleep(2)
    return False

# טסט 1: בודק את קונטיינר ה-API
def test_api_container():
    assert wait_for_service(API_URL, "API"), "❌ API container failed to start!"
    response = requests.get(API_URL)
    assert response.status_code in [200, 500]

# טסט 2: בודק את קונטיינר ה-Frontend (היומן)
def test_front_container():
    assert wait_for_service(FRONT_URL, "Frontend"), "❌ Frontend container failed to start!"
    response = requests.get(FRONT_URL)
    assert response.status_code == 200
    # מוודא שה-HTML של היומן באמת נטען
    assert b"<html" in response.content.lower()

# טסט 3: בודק את קונטיינר ה-Dashboard
def test_dashboard_container():
    assert wait_for_service(DASH_URL, "Dashboard"), "❌ Dashboard container failed to start!"
    response = requests.get(DASH_URL)
    assert response.status_code == 200
    # מוודא שהכותרת של הדשבורד קיימת כדי לדעת שהאפליקציה באמת למעלה
    assert b"Live System Architecture" in response.content
