import urllib.request
import json
import sys
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

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
        return None

def test_prediction(token, distrito, fecha, tipo_delito="TODOS"):
    url = f"{BASE_URL}/predict/predecir"
    payload = json.dumps({
        "fecha_consulta": fecha,
        "distrito": distrito,
        "tipo_delito": tipo_delito
    }).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\nTesting POST {url} with: distrito='{distrito}', fecha='{fecha}', tipo_delito='{tipo_delito}'")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            data = json.loads(body)
            print(f"  -> SUCCESS! status: {data.get('status')}")
            hotspots = data.get("hotspots", [])
            print(f"  -> Returned {len(hotspots)} hotspots")
            if hotspots:
                print(f"  -> Sample Hotspot 1: {hotspots[0]}")
                assert "lat" in hotspots[0], "Missing lat in hotspot!"
                assert "lng" in hotspots[0], "Missing lng in hotspot!"
                assert "distrito" in hotspots[0], "Missing distrito in hotspot!"
                print("     (lat, lng, distrito) verification: PASSED")
                
                if distrito != "TODOS":
                    for h in hotspots:
                        assert distrito.upper() in h["distrito"].upper(), f"District mismatch! Hotspot district '{h['distrito']}' not matching query '{distrito}'"
                    print(f"     District masking validation for '{distrito}': PASSED")
            return True
    except Exception as e:
        print(f"  -> FAILED: {e}")
        if hasattr(e, 'read'):
            print(f"     Error Response: {e.read().decode('utf-8')}")
        return False

if __name__ == "__main__":
    token = login()
    if not token:
        sys.exit(1)
        
    # Test 1: Global prediction on a historical date
    test_prediction(token, "TODOS", "2026-03-25")
    
    # Test 2: District prediction on a historical date
    test_prediction(token, "COMAS", "2026-03-25")
    
    # Test 3: Prediction on a future date (simulated)
    test_prediction(token, "TODOS", "2026-05-20")
    
    # Test 4: Prediction for San Martin De Porres on future date
    test_prediction(token, "SAN MARTIN DE PORRES", "2026-05-20")
