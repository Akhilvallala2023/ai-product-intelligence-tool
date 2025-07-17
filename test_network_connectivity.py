import requests

BACKEND_URL = "http://localhost:8000"  # Change to your deployed backend URL for production test
NETLIFY_URL = "https://idyllic-sorbet-caaa3d.netlify.app"

def test_backend_health():
    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        print("[Backend Health] Status:", r.status_code)
        print("[Backend Health] Response:", r.text)
        return r.status_code == 200
    except Exception as e:
        print("[Backend Health] ERROR:", e)
        return False

def test_cors():
    try:
        r = requests.options(
            f"{BACKEND_URL}/api/analyze-form",
            headers={
                "Origin": NETLIFY_URL,
                "Access-Control-Request-Method": "POST"
            },
            timeout=10
        )
        cors = r.headers.get("Access-Control-Allow-Origin")
        print("[CORS] Access-Control-Allow-Origin:", cors)
        return cors == NETLIFY_URL or cors == "*"
    except Exception as e:
        print("[CORS] ERROR:", e)
        return False

if __name__ == "__main__":
    print("--- Testing Backend Health ---")
    health_ok = test_backend_health()
    print("--- Testing CORS Headers ---")
    cors_ok = test_cors()
    if health_ok and cors_ok:
        print("\n✅ Network connectivity and CORS are OK!")
    else:
        print("\n❌ Network or CORS issue detected. See above for details.") 