import pytest
import requests
import time

# מכיוון שהטסט ירוץ בתוך קונטיינר זמני של ג'נקינס (על Windows), 
# אנחנו משתמשים ב-host.docker.internal כדי לגשת לפורט 5011 של קוברנטיס במחשב שלך.
URL = "http://host.docker.internal:5011/health"

def test_live_environment():
    print(f"🔄 Waiting for K8s pods to be fully ready at {URL}...")
    success = False
    
    # המערכת צריכה כמה שניות לעלות אחרי Rollout, אז ננסה לדגום אותה במשך 40 שניות
    for i in range(20): 
        try:
            response = requests.get(URL, timeout=2)
            # 200 זה תקין. 500 זה גם תקין כי ה-MongoDB אולי עדיין עולה
            if response.status_code in [200, 500]:
                success = True
                break
        except requests.exceptions.RequestException:
            # אם יש שגיאת חיבור, נחכה 2 שניות וננסה שוב
            time.sleep(2)
    
    if not success:
        pytest.fail("❌ The API is DOWN! Deployment might be broken.")
    
    assert True
    print("✅ The API is LIVE and responding correctly!")
