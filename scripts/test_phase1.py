import requests
import sys

GATEWAY_URL = "http://localhost:8080"

def test_phase1():
    try:
        r = requests.get(f"{GATEWAY_URL}/gis/graph")
        r.raise_for_status()
        print("[OK] Phase 1 Integration Test Passed")
    except Exception as e:
        print(f"[FAIL] Phase 1 Integration Test Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_phase1()
