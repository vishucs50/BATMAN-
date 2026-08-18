import sys
import uuid
import time
import requests

GATEWAY_URL = "http://localhost:8080/api/v1"
headers = {"Authorization": "Bearer fake_token"}

def simulate_user_flow():
    print("--- Simulating Commander User Flow ---")
    mission_id = str(uuid.uuid4())
    
    # 1. Threat Assessment (Simulate User looking at Threat Dashboard)
    print("1. Requesting Threat Assessment...")
    r = requests.post(f"{GATEWAY_URL}/threats/assess", json={"location": "Alpha Grid", "radius_km": 50})
    if r.status_code == 200:
        print(f" [OK] Threat Assessed: {r.json()}")
    else:
        print(f" [FAIL] Threat Assessment: {r.status_code} - {r.text}")

    # 2. Planning (User creates a mission and generates COAs)
    print("\n2. Generating Courses of Action (COAs)...")
    payload = {
        "mission_id": mission_id,
        "mission_type": "COUNTER_INFILTRATION",
        "styles": ["BOLD", "BALANCED", "CAUTIOUS"]
    }
    r = requests.post(f"{GATEWAY_URL}/missions/{mission_id}/coas/generate", json=payload)
    if r.status_code == 202 or r.status_code == 200:
        print(f" [OK] COA Generation Job started")
    else:
        print(f" [FAIL] COA Generation: {r.status_code} - {r.text}")
        sys.exit(1)

    r = requests.get(f"{GATEWAY_URL}/missions/{mission_id}/coas")
    coas = r.json()
    print(f" [OK] Retrieved {len(coas)} COAs")
    if not coas:
        sys.exit(1)

    # 3. Simulate (User simulates the best COA)
    coa = coas[1] # Choose BALANCED
    print(f"\n3. Simulating COA: {coa['name']} (ID: {coa['id']})...")
    sim_payload = {
        "mission_id": mission_id,
        "coa_id": coa["id"],
        "coa_data": coa["plan_graph"],
        "mc_runs": 10
    }
    r = requests.post(f"{GATEWAY_URL}/simulation/simulate", json=sim_payload)
    if r.status_code != 202 and r.status_code != 200:
        print(f" [FAIL] Simulation: {r.status_code} - {r.text}")
        sys.exit(1)
        
    job_id = r.json()["job_id"]
    print(f" [OK] Simulation Job ID: {job_id}")
    
    print(" Waiting for simulation to complete...")
    max_retries = 15
    for i in range(max_retries):
        r = requests.get(f"{GATEWAY_URL}/simulation/{job_id}")
        data = r.json()
        if data.get("status") == "COMPLETED" or "run_count" in data:
            print(f" [OK] Simulation Completed! Success Rate: {data.get('success_rate')}")
            break
        elif data.get("status") == "FAILED":
            print(f" [FAIL] Simulation Failed: {data.get('error')}")
            break
        time.sleep(1)
    else:
        print(" [WARN] Simulation Timeout")

    # 4. Approve (User Approves the COA)
    print("\n4. Approving COA...")
    r = requests.post(f"{GATEWAY_URL}/missions/{mission_id}/coas/{coa['id']}/approve", json={"actor_id": str(uuid.uuid4()), "actor_role": "COMMANDING_OFFICER", "rationale": "Looks good."})
    if r.status_code == 200:
        print(" [OK] COA Approved")
    else:
        print(f" [FAIL] COA Approval: {r.status_code} - {r.text}")

if __name__ == "__main__":
    simulate_user_flow()
