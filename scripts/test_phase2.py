import requests
import sys
import uuid

GATEWAY_URL = "http://localhost:8080"

def test_phase2():
    try:
        payload = {
            "mission_id": str(uuid.uuid4()),
            "parameters": {"threat_level": "HIGH", "objective": "SECURE_BRIDGE"}
        }
        r = requests.post(f"{GATEWAY_URL}/coa/generate", json=payload)
        r.raise_for_status()
        print("[OK] Phase 2 Integration Test Passed")
    except Exception as e:
        print(f"[FAIL] Phase 2 Integration Test Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_phase2()
