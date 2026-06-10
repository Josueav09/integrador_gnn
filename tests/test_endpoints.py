import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000"

def login():
    url = f"{BASE_URL}/auth/login"
    payload = json.dumps({
        "email": "admin@pnp.gob.pe",
        "password": "TesisUTP2026*"
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url, 
        data=payload, 
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print("Successfully authenticated as admin!")
            return res_json.get("access_token")
    except Exception as e:
        print(f"Login failed: {e}")
        if hasattr(e, 'read'):
            try:
                print(f"Login error response: {e.read().decode('utf-8')}")
            except:
                pass
        return None

def test_endpoint(path, token):
    url = f"{BASE_URL}{path}"
    print(f"Testing GET {url} ...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            body = response.read().decode('utf-8')
            data = json.loads(body)
            print(f"  -> SUCCESS! Status: {status}")
            print(f"  -> Keys: {list(data.keys())}")
            if "success" in data:
                print(f"  -> data.success: {data['success']}")
            return True
    except Exception as e:
        print(f"  -> FAILED: {e}")
        if hasattr(e, 'read'):
            try:
                print(f"     Error response: {e.read().decode('utf-8')}")
            except:
                pass
        return False

if __name__ == "__main__":
    print("=== ACQUIRING TOKEN VIA LOGIN ===")
    token = login()
    if not token:
        print("Could not obtain token. Exiting.")
        sys.exit(1)
        
    endpoints = [
        "/dashboard/kpis",
        "/dashboard/analisis",
        "/dashboard/stats-distrito/TODOS",
        "/predict/grafo",
        "/predict/metricas",
        "/predict/monitor",
        "/predict/detalles",
        "/predict/distritos",
        "/admin/pipeline",
        "/admin/uploads",
        "/admin/logs"
    ]
    
    print("\n=== STARTING ENDPOINT TESTS ===")
    all_success = True
    for ep in endpoints:
        success = test_endpoint(ep, token)
        if not success:
            all_success = False
        print("-" * 50)
        
    if all_success:
        print("ALL AUTHENTICATED ENDPOINTS RETURNED SUCCESSFUL RESPONSES!")
        sys.exit(0)
    else:
        print("SOME ENDPOINTS FAILED!")
        sys.exit(1)
