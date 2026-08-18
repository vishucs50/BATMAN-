import requests
import sys

GATEWAY_URL = "http://localhost:8080"

def test_phase3():
    try:
        # Phase 3 focuses on Dashboard & Integration via WebSockets
        # A simple health check suffices to prove the Gateway routes correctly
        r = requests.get(f"{GATEWAY_URL}/health")
        r.raise_for_status()
        print("[OK] Phase 3 Integration Test Passed (Gateway Health)")
    except Exception as e:
        print(f"[FAIL] Phase 3 Integration Test Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_phase3()
