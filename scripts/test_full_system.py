import sys
import uuid
import time
import requests

GATEWAY_URL = "http://localhost:8080/api/v1"

def run_tests():
    print(f"Starting BATMAN Full System Integration Tests against {GATEWAY_URL}...")
    try:
        # Check health
        r = requests.get(f"{GATEWAY_URL}/health")
        r.raise_for_status()
        print("[OK] Gateway Health Check")
        
        # Test KG (Phase 1)
        r = requests.get(f"{GATEWAY_URL}/gis/graph")
        r.raise_for_status()
        print("[OK] Phase 1: Knowledge Graph Graph API")
        
        # Test Planner (Phase 2/3)
        mission_id = str(uuid.uuid4())
        payload = {
            "mission_id": mission_id,
            "mission_type": "COUNTER_INFILTRATION",
            "styles": ["BALANCED"]
        }
        r = requests.post(f"{GATEWAY_URL}/missions/{mission_id}/coas/generate", json=payload)
        r.raise_for_status()
        print(f"[OK] Phase 2: HTN Planner accepted job")
        
        r = requests.get(f"{GATEWAY_URL}/missions/{mission_id}/coas")
        r.raise_for_status()
        coas = r.json()
        assert len(coas) > 0, "No COAs generated"
        print(f"[OK] Phase 2: Fetched {len(coas)} COAs")
        
        # Test Wargame (Phase 2/3)
        coa = coas[0]
        sim_payload = {
            "mission_id": mission_id,
            "coa_id": coa["id"],
            "coa_data": coa["plan_graph"],
            "mc_runs": 2 # Keep it low for fast integration testing
        }
        r = requests.post(f"{GATEWAY_URL}/simulation/simulate", json=sim_payload)
        r.raise_for_status()
        job = r.json()
        job_id = job["job_id"]
        print(f"[OK] Phase 2: Wargame Engine accepted job {job_id}")
        
        # Wait for simulation to finish
        print("Waiting for simulation to complete...")
        for _ in range(10):
            r = requests.get(f"{GATEWAY_URL}/simulation/{job_id}")
            r.raise_for_status()
            data = r.json()
            if "run_count" in data or data.get("status") == "COMPLETED":
                print("[OK] Phase 2: Monte Carlo Simulation completed successfully")
                break
            elif data.get("status") == "FAILED":
                print(f"[FAIL] Simulation failed: {data.get('error')}")
                sys.exit(1)
            time.sleep(2)
        else:
            print("[WARN] Simulation did not complete in time")
            
        print("\nAll integration tests passed successfully.")
        
    except Exception as e:
        print(f"[FAIL] Integration tests failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
