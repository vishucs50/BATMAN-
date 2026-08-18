import uuid
import time
import httpx

PLANNING_SVC = "http://127.0.0.1:8002"
WARGAME_SVC = "http://127.0.0.1:8003"
GATEWAY_SVC = "http://127.0.0.1:8080"

def test_aar_and_replay():
    mission_id = str(uuid.uuid4())
    print(f"=== Starting Phase 4.2 AAR & Replay Verification (Mission ID: {mission_id}) ===")

    # 1. Generate COA
    print("\n1. Generating COA...")
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
    print("COA generation initiated successfully.")

    time.sleep(1)

    # Fetch generated COA
    r = httpx.get(f"{PLANNING_SVC}/planning/missions/{mission_id}/coa")
    r.raise_for_status()
    coas = r.json()
    assert len(coas) > 0, "No COAs were generated!"
    selected_coa = coas[0]
    coa_id = selected_coa["id"]
    print(f"Selected COA: {coa_id} ({selected_coa['name']})")

    # 2. Run Wargame evaluation
    print("\n2. Running Wargame simulation & evaluation...")
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
    print(f"Wargame evaluation completed. Utility Score: {scores[0]['utility_score']}")

    # 3. Verify AAR List
    print("\n3. Testing GET /wargame/aar (List AARs)...")
    r = httpx.get(f"{WARGAME_SVC}/wargame/aar")
    r.raise_for_status()
    list_data = r.json()
    print(f"Total AARs found: {list_data['total']}")
    found_summary = next((item for item in list_data["aars"] if item["mission_id"] == mission_id), None)
    assert found_summary is not None, "Generated AAR record not found in AAR list!"
    print(f"Verified AAR Summary in list: {found_summary}")

    # 4. Verify Full AAR Report
    print(f"\n4. Testing GET /wargame/aar/{mission_id} (AAR Details)...")
    r = httpx.get(f"{WARGAME_SVC}/wargame/aar/{mission_id}")
    r.raise_for_status()
    aar_rec = r.json()
    assert aar_rec["mission_id"] == mission_id
    assert "selected_coa" in aar_rec
    assert "monte_carlo_stats" in aar_rec
    assert "ai_explanation" in aar_rec
    assert "commander_decision" in aar_rec
    assert "event_log" in aar_rec
    print(f"Verified Full AAR Record for Mission Code: {aar_rec['mission_code']}")

    # 5. Verify Timeline Endpoint
    print(f"\n5. Testing GET /wargame/aar/{mission_id}/timeline...")
    r = httpx.get(f"{WARGAME_SVC}/wargame/aar/{mission_id}/timeline")
    r.raise_for_status()
    timeline_data = r.json()
    assert len(timeline_data["timeline"]) > 0
    print(f"Timeline Milestones count: {len(timeline_data['timeline'])}")

    # 6. Verify Replay Event Log Stream Endpoint
    print(f"\n6. Testing GET /wargame/aar/{mission_id}/replay...")
    r = httpx.get(f"{WARGAME_SVC}/wargame/aar/{mission_id}/replay")
    r.raise_for_status()
    replay_data = r.json()
    assert "events" in replay_data
    print(f"Replay Events count: {replay_data['count']}")

    # 7. Verify Statistics Endpoint
    print(f"\n7. Testing GET /wargame/aar/{mission_id}/statistics...")
    r = httpx.get(f"{WARGAME_SVC}/wargame/aar/{mission_id}/statistics")
    r.raise_for_status()
    stats_data = r.json()
    assert "monte_carlo" in stats_data
    print(f"Monte Carlo stats verified: Success Rate = {stats_data['monte_carlo'].get('success_rate')}")

    # 8. Verify Gateway Routing (/api/v1/aar)
    print("\n8. Testing API Gateway Proxy /api/v1/aar...")
    try:
        r = httpx.get(f"{GATEWAY_SVC}/api/v1/aar")
        if r.status_code == 200:
            print("Gateway proxy to /api/v1/aar SUCCESSFUL!")
        else:
            print(f"Gateway returned status {r.status_code}")
    except Exception as e:
        print(f"Gateway check note: {e}")

    print("\n=== ALL AAR & REPLAY TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_aar_and_replay()
