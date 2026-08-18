import uuid
import httpx
import time

PLANNING_SVC = "http://127.0.0.1:8002"
WARGAME_SVC = "http://127.0.0.1:8003"

def run_test():
    mission_id = str(uuid.uuid4())
    print(f"Starting Mission Memory test with Mission ID: {mission_id}")

    # 1. Generate COA
    print("1. Generating COA...")
    gen_req = {
        "mission_id": mission_id,
        "mission_type": "COUNTER_INFILTRATION",
        "world_state": {
            "terrain": "FORESTED",
            "weather": "CLEAR",
            "threat_level": "HIGH"
        }
    }
    r = httpx.post(f"{PLANNING_SVC}/planning/coa/generate", json=gen_req, timeout=60.0)
    r.raise_for_status()
    
    # Wait a bit for COA generation
    time.sleep(1)
    
    # List generated COAs
    r = httpx.get(f"{PLANNING_SVC}/planning/missions/{mission_id}/coa")
    r.raise_for_status()
    coas = r.json()
    if not coas:
        print("Error: No COAs generated")
        return
        
    selected_coa = coas[0]
    coa_id = selected_coa["id"]
    print(f"Selected COA: {coa_id} ({selected_coa['name']})")

    # 2. Evaluate in Wargame
    print("2. Running Wargame evaluation...")
    eval_req = {
        "mission_id": mission_id,
        "mission_type": "COUNTER_INFILTRATION",
        "coas": [{
            "coa_id": coa_id,
            "task_hierarchy": selected_coa["plan_graph"],
            "estimated_duration_min": selected_coa["timeline"]["estimated_duration_min"],
            "required_resources": selected_coa["resource_plan"]
        }],
        "world_state": {
            "terrain": "PLAINS",
            "initial_weather": "CLEAR",
            "threat_probability": 0.3
        },
        "mc_runs": 20
    }
    
    r = httpx.post(f"{WARGAME_SVC}/wargame/evaluate", json=eval_req, timeout=120.0)
    r.raise_for_status()
    scores = r.json()
    
    if not scores:
        print("Error: No scores returned from wargame")
        return
        
    score = scores[0]
    print(f"Wargame Result - Success Rate/Utility: {score['utility_score']}")

    # 3. Retain in Mission Memory
    print("3. Retaining outcome in Mission Memory...")
    retain_req = {
        "mission_id": mission_id,
        "coa_id": coa_id,
        "mission_type": "COUNTER_INFILTRATION",
        "terrain": "FORESTED",
        "threat": "HIGH",
        "resources": 0.8,
        "urgency": 0.9,
        "success_rate": score["utility_score"] / 100.0, # Normalizing assuming it's out of 100
        "plan_skeleton": selected_coa["plan_graph"],
        "failure_modes": [{"mode": "Ambush", "probability": 0.1}]
    }
    
    r = httpx.post(f"{PLANNING_SVC}/planning/cbr/retain", json=retain_req)
    r.raise_for_status()
    print(f"Retain response: {r.json()}")

    # 4. Verify Retrieval
    print("4. Verifying Case in Database...")
    r = httpx.get(f"{PLANNING_SVC}/planning/cbr/cases")
    r.raise_for_status()
    cases = r.json()
    print(f"Total Retained Cases: {cases['retained_count']}")
    
    found = False
    for c in cases["cases"]:
        if c["id"] == f"SIM-{mission_id}-{coa_id}":
            found = True
            print("Successfully found newly retained case in CBR!")
            break
            
    if not found:
        print("Error: Case not found in database")

if __name__ == "__main__":
    run_test()
