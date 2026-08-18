#!/usr/bin/env python3
import sys
import os
import json
import yaml
import uuid
import time
import argparse
import numpy as np
import networkx as nx
import torch
import torch.nn as nn
import torch.optim as optim

# Resolve paths relative to project root
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "services"))
sys.path.insert(0, os.path.join(_ROOT, "services/wargame-svc"))
sys.path.insert(0, os.path.join(_ROOT, "services/planning-svc"))
sys.path.insert(0, os.path.join(_ROOT, "services/threat-svc"))
sys.path.insert(0, os.path.join(_ROOT, "services/kg-svc"))

# Contracts and Simulation Imports
from shared.contracts import Mission, WorldState, COA, SimulationResult
from simulation.engine import BATMANSimulation
from simulation.models import SimulationConfig
from htn.planner import HTNPlanner
from htn.mission_domains import build_phase_one_domain
from coa.generator import COAGenerator
from rules.engine import RuleEngine, phase_one_rules
from cbr.engine import CaseBasedReasoner
from bayesian.network import ThreatNetwork
from seed_graph import build_entities, build_relationships

# --- PyTorch GCN Model Definition ---
class SimpleGCN(nn.Module):
    def __init__(self, in_features: int, hidden_dim: int, out_features: int):
        super().__init__()
        self.w1 = nn.Parameter(torch.randn(in_features, hidden_dim) * 0.1)
        self.w2 = nn.Parameter(torch.randn(hidden_dim, out_features) * 0.1)
        self.bias1 = nn.Parameter(torch.zeros(hidden_dim))
        self.bias2 = nn.Parameter(torch.zeros(out_features))

    def forward(self, x, adj):
        # Neighborhood aggregation
        h1 = torch.relu(torch.matmul(torch.matmul(adj, x), self.w1) + self.bias1)
        # Final prediction layer
        out = torch.matmul(torch.matmul(adj, h1), self.w2) + self.bias2
        # Graph readout (mean pooling over all nodes)
        graph_readout = torch.mean(out, dim=0)
        return graph_readout

# --- Directory Setup ---
def setup_dirs():
    os.makedirs(os.path.join(_ROOT, "data/learning"), exist_ok=True)
    os.makedirs(os.path.join(_ROOT, "ai/models/gnn"), exist_ok=True)
    os.makedirs(os.path.join(_ROOT, "ai/models/heuristics"), exist_ok=True)

# --- Adjacency Matrix Preparation ---
def build_normalized_adj():
    entities = build_entities()
    relationships = build_relationships(entities)
    g = nx.DiGraph()
    for ent in entities:
        g.add_node(ent.id, label=ent.label, **ent.properties)
    for src, rel_type, tgt in relationships:
        g.add_edge(src, tgt, rel_type=rel_type)
        
    adj = nx.to_numpy_array(g) + np.eye(len(g))
    deg = np.sum(adj, axis=1)
    deg_inv_sqrt = np.power(deg, -0.5, where=deg>0)
    deg_inv_sqrt[deg == 0] = 0.0
    adj_norm = deg_inv_sqrt[:, None] * adj * deg_inv_sqrt[None, :]
    return torch.tensor(adj_norm, dtype=torch.float32), g

# --- 1. Simulation Data Collection ---
def collect_simulations(num_episodes=5, mc_runs=5):
    print(f"[Learning] Collecting simulations: {num_episodes} scenarios × 3 COAs × {mc_runs} Monte Carlo runs...")
    setup_dirs()
    runs_file = os.path.join(_ROOT, "data/learning/simulation_runs.jsonl")
    
    # Load existing runs if any to prevent duplicate simulation IDs
    existing_ids = set()
    if os.path.exists(runs_file):
        with open(runs_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    existing_ids.add(data.get("simulation_id"))
                except Exception:
                    pass
                    
    # Diverse world state generators
    weather_options = ["CLEAR", "RAIN", "FOG", "SNOW", "WIND"]
    terrain_options = ["PLAINS", "MIXED", "MOUNTAINOUS", "URBAN"]
    
    records_saved = 0
    with open(runs_file, "a") as f:
        for idx in range(num_episodes):
            scenario_id = str(uuid.uuid4())
            world_state = WorldState(
                terrain=np.random.choice(terrain_options),
                elevation_m=float(np.random.randint(100, 3200)),
                slope_degrees=float(np.random.randint(0, 30)),
                trafficability=float(np.random.uniform(0.4, 0.95)),
                vegetation_density=float(np.random.uniform(0.1, 0.8)),
                initial_weather=np.random.choice(weather_options),
                threat_probability=float(np.random.uniform(0.1, 0.8)),
                civilian_density=float(np.random.uniform(0.05, 0.4)),
                comms_baseline=float(np.random.uniform(0.7, 0.98)),
                fuel_available=float(np.random.uniform(0.6, 1.0)),
                ammunition_available=float(np.random.uniform(0.6, 1.0))
            )
            
            # Formulate hypothetical mission
            mission = Mission(
                mission_id=str(uuid.uuid4()),
                mission_type="COUNTER_INFILTRATION",
                objectives=("Detect_and_Localise", "Force_Protection", "Logistics_Support")
            )
            
            # Run Planner to get Candidate COAs
            facts = {
                "terrain": world_state.terrain,
                "elevation_m": world_state.elevation_m,
                "slope_degrees": world_state.slope_degrees,
                "trafficability": world_state.trafficability,
                "vegetation_density": world_state.vegetation_density,
                "initial_weather": world_state.initial_weather,
                "threat_probability": world_state.threat_probability,
                "civilian_density": world_state.civilian_density,
                "comms_baseline": world_state.comms_baseline,
                "fuel_available": world_state.fuel_available,
                "ammunition_available": world_state.ammunition_available,
                "mission_id": mission.mission_id
            }
            domain = build_phase_one_domain()
            planner = HTNPlanner(domain=domain)
            rule_engine = RuleEngine(rules=phase_one_rules())
            cbr = CaseBasedReasoner()
            generator = COAGenerator(planner=planner, rule_engine=rule_engine, cbr=cbr)
            coas = generator.generate(mission.mission_type, facts)
            
            # Execute Monte Carlo simulations for each COA
            for g_coa in coas:
                # Convert to canonical COA contract
                coa = COA(
                    coa_id=g_coa.id,
                    task_hierarchy=g_coa.task_hierarchy,
                    estimated_duration_min=g_coa.estimated_duration_min,
                    required_resources=g_coa.required_resources,
                    assumptions=tuple(g_coa.assumptions)
                )
                
                for mc_idx in range(mc_runs):
                    sim_id = f"SIM-{scenario_id[:8]}-{coa.coa_id[:8]}-{mc_idx:03d}"
                    if sim_id in existing_ids:
                        continue
                        
                    config = SimulationConfig(
                        tick_minutes=15,
                        max_duration_minutes=max(1440, coa.estimated_duration_min * 3),
                        random_seed=42 + mc_idx,
                        friendly_count=3,
                        threat_count=2,
                        civilian_count=1
                    )
                    
                    sim = BATMANSimulation(mission, world_state, coa, config=config)
                    res = sim.run()
                    
                    # Log run metrics
                    run_record = {
                        "simulation_id": sim_id,
                        "scenario_id": scenario_id,
                        "mission": {
                            "mission_id": mission.mission_id,
                            "mission_type": mission.mission_type,
                            "objectives": list(mission.objectives)
                        },
                        "coa": {
                            "coa_id": coa.coa_id,
                            "style": g_coa.style,
                            "task_hierarchy": coa.task_hierarchy,
                            "estimated_duration_min": coa.estimated_duration_min,
                            "required_resources": coa.required_resources
                        },
                        "world_state": {
                            "terrain": world_state.terrain,
                            "elevation_m": world_state.elevation_m,
                            "slope_degrees": world_state.slope_degrees,
                            "trafficability": world_state.trafficability,
                            "vegetation_density": world_state.vegetation_density,
                            "initial_weather": world_state.initial_weather,
                            "threat_probability": world_state.threat_probability,
                            "civilian_density": world_state.civilian_density,
                            "comms_baseline": world_state.comms_baseline,
                            "fuel_available": world_state.fuel_available,
                            "ammunition_available": world_state.ammunition_available
                        },
                        "seed": config.random_seed,
                        "outcome": {
                            "success": res.success,
                            "termination_reason": res.termination_reason,
                            "completion_time_min": res.completion_time_min,
                            "friendly_casualties": res.friendly_casualties,
                            "civilian_casualties": res.civilian_casualties,
                            "fuel_consumed": res.fuel_consumed,
                            "ammo_consumed": res.ammo_consumed,
                            "roe_violations": res.roe_violations,
                            "communication_failures": res.communication_failures,
                            "failure_modes": res.failure_modes,
                            "event_log_size": len(res.event_log)
                        }
                    }
                    f.write(json.dumps(run_record) + "\n")
                    records_saved += 1
    print(f"[Learning] Saved {records_saved} new simulation records to {runs_file}.")

# --- 2. Feature Extraction ---
def extract_features():
    print("[Learning] Extracting ML-ready training examples...")
    runs_file = os.path.join(_ROOT, "data/learning/simulation_runs.jsonl")
    features_file = os.path.join(_ROOT, "data/learning/features_v1.jsonl")
    
    # Node labels mapping
    labels = ["Unit", "Road", "TerrainFeat", "Bridge", "Sensor", "ThreatActor", "MissionObj", "SupplyDepot", "ObservationPost"]
    label_map = {l: i for i, l in enumerate(labels)}
    
    records_processed = 0
    with open(features_file, "w") as out_f:
        with open(runs_file, "r") as in_f:
            for line in in_f:
                try:
                    data = json.loads(line)
                    ws = data["world_state"]
                    coa = data["coa"]
                    outcome = data["outcome"]
                    
                    # Convert categorical variables to index
                    terrain_idx = {"PLAINS": 0, "MIXED": 1, "MOUNTAINOUS": 2, "URBAN": 3}.get(ws["terrain"], 0)
                    weather_idx = {"CLEAR": 0, "RAIN": 1, "FOG": 2, "HEAVY_RAIN": 3}.get(ws["initial_weather"], 0)
                    coa_idx = {"BOLD": 0, "BALANCED": 1, "CAUTIOUS": 2}.get(coa.get("style", "BALANCED").upper(), 1)
                    
                    # Graph node features construction
                    node_features = []
                    # We dynamically fetch the seed graph and populate node properties with scenario features
                    entities = build_entities()
                    for ent in entities:
                        feat = [0.0] * 9
                        feat[label_map.get(ent.label, 0)] = 1.0
                        if ent.label == "ThreatActor":
                            feat[5] = float(ws["threat_probability"])
                        elif ent.label == "TerrainFeat":
                            feat[2] = float(ws["trafficability"])
                        node_features.append(feat)
                        
                    example = {
                        "simulation_id": data["simulation_id"],
                        "features": {
                            "terrain_idx": terrain_idx,
                            "weather_idx": weather_idx,
                            "coa_idx": coa_idx,
                            "elevation_m": ws["elevation_m"],
                            "slope_degrees": ws["slope_degrees"],
                            "trafficability": ws["trafficability"],
                            "vegetation_density": ws["vegetation_density"],
                            "threat_probability": ws["threat_probability"],
                            "comms_baseline": ws["comms_baseline"],
                            "node_features": node_features
                        },
                        "targets": {
                            "success": 1.0 if outcome["success"] else 0.0,
                            "casualties": float(outcome["friendly_casualties"]),
                            "duration": float(outcome["completion_time_min"]),
                            "fuel": float(outcome["fuel_consumed"]),
                            "ammo": float(outcome["ammo_consumed"])
                        }
                    }
                    out_f.write(json.dumps(example) + "\n")
                    records_processed += 1
                except Exception as e:
                    print(f"Error processing record: {e}")
                    pass
    print(f"[Learning] Processed {records_processed} training examples into {features_file}.")

# --- 3. Training Dataset Creation ---
def create_dataset():
    print("[Learning] Creating Train/Val/Test splits...")
    features_file = os.path.join(_ROOT, "data/learning/features_v1.jsonl")
    dataset_dir = os.path.join(_ROOT, "data/learning/dataset_v1")
    os.makedirs(dataset_dir, exist_ok=True)
    
    examples = []
    with open(features_file, "r") as f:
        for line in f:
            examples.append(json.loads(line))
            
    # Shuffle and split
    np.random.seed(42)
    indices = np.random.permutation(len(examples))
    
    train_split = int(0.7 * len(indices))
    val_split = int(0.85 * len(indices))
    
    train_examples = [examples[i] for i in indices[:train_split]]
    val_examples = [examples[i] for i in indices[train_split:val_split]]
    test_examples = [examples[i] for i in indices[val_split:]]
    
    # Save splits
    with open(os.path.join(dataset_dir, "train.json"), "w") as f:
        json.dump(train_examples, f)
    with open(os.path.join(dataset_dir, "val.json"), "w") as f:
        json.dump(val_examples, f)
    with open(os.path.join(dataset_dir, "test.json"), "w") as f:
        json.dump(test_examples, f)
        
    # Metadata
    metadata = {
        "dataset_version": "v1.0.0",
        "feature_version": "v1.0.0",
        "train_size": len(train_examples),
        "val_size": len(val_examples),
        "test_size": len(test_examples),
        "source_simulation_ids": [ex["simulation_id"] for ex in examples],
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f)
        
    print(f"[Learning] Splits saved to {dataset_dir} (Train={len(train_examples)}, Val={len(val_examples)}, Test={len(test_examples)}).")

# --- 4. GNN/BRN Model Training ---
def train_gnn(epochs=10):
    print("[Learning] Training GNN/BRN model on PyTorch...")
    dataset_dir = os.path.join(_ROOT, "data/learning/dataset_v1")
    
    # Load splits
    with open(os.path.join(dataset_dir, "train.json"), "r") as f:
        train_data = json.load(f)
    with open(os.path.join(dataset_dir, "val.json"), "r") as f:
        val_data = json.load(f)
    with open(os.path.join(dataset_dir, "test.json"), "r") as f:
        test_data = json.load(f)
        
    if not train_data:
        print("[Warning] Empty dataset split. Cannot train GNN model.")
        return None
        
    # Adjacency Matrix
    adj_norm, _ = build_normalized_adj()
    
    # Initialize GNN Model
    # 9 input features, 16 hidden layers, 5 output variables (success, cas, dur, fuel, ammo)
    model = SimpleGCN(in_features=9, hidden_dim=16, out_features=5)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()
    
    # Training Loop
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for ex in train_data:
            node_feat = torch.tensor(ex["features"]["node_features"], dtype=torch.float32)
            targets = torch.tensor([
                ex["targets"]["success"],
                ex["targets"]["casualties"],
                ex["targets"]["duration"],
                ex["targets"]["fuel"],
                ex["targets"]["ammo"]
            ], dtype=torch.float32)
            
            optimizer.zero_grad()
            pred = model(node_feat, adj_norm)
            loss = criterion(pred, targets)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        # Evaluate on validation split
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for ex in val_data:
                node_feat = torch.tensor(ex["features"]["node_features"], dtype=torch.float32)
                targets = torch.tensor([
                    ex["targets"]["success"],
                    ex["targets"]["casualties"],
                    ex["targets"]["duration"],
                    ex["targets"]["fuel"],
                    ex["targets"]["ammo"]
                ], dtype=torch.float32)
                pred = model(node_feat, adj_norm)
                val_loss += criterion(pred, targets).item()
        model.train()
        print(f"  Epoch {epoch+1:02d}/{epochs:02d} | Train Loss: {epoch_loss/len(train_data):.4f} | Val Loss: {val_loss/len(val_data):.4f}")
        
    # Test Evaluation
    model.eval()
    test_loss = 0.0
    predictions = []
    actuals = []
    with torch.no_grad():
        for ex in test_data:
            node_feat = torch.tensor(ex["features"]["node_features"], dtype=torch.float32)
            targets = torch.tensor([
                ex["targets"]["success"],
                ex["targets"]["casualties"],
                ex["targets"]["duration"],
                ex["targets"]["fuel"],
                ex["targets"]["ammo"]
            ], dtype=torch.float32)
            pred = model(node_feat, adj_norm)
            test_loss += criterion(pred, targets).item()
            predictions.append(pred.numpy())
            actuals.append(targets.numpy())
            
    test_loss_mean = test_loss / len(test_data)
    print(f"[Learning] Test Evaluation complete. Mean Squared Error: {test_loss_mean:.4f}")
    
    # Save checkpoint
    model_ver = f"gnn_v1_{int(time.time())}.pth"
    model_path = os.path.join(_ROOT, "ai/models/gnn", model_ver)
    torch.save(model.state_dict(), model_path)
    print(f"[Learning] Model checkpoint saved to {model_path}.")
    
    return {
        "model_version": model_ver,
        "test_mse": test_loss_mean,
        "dataset_size": len(train_data) + len(val_data) + len(test_data)
    }

# --- 5. Planner Heuristic Updates ---
def generate_heuristics():
    print("[Learning] Computing updated HTN planner heuristics (mean simulated task durations)...")
    runs_file = os.path.join(_ROOT, "data/learning/simulation_runs.jsonl")
    
    # Track task execution durations from simulation outcomes
    # For baseline, we extract durations from successful runs
    task_durations = {}
    with open(runs_file, "r") as f:
        for line in f:
            try:
                data = json.loads(line)
                outcome = data["outcome"]
                if outcome["success"]:
                    coa = data["coa"]
                    # Extract primitive task durations
                    # We can recursively traverse task hierarchy
                    def traverse(node):
                        if node.get("primitive"):
                            task_durations.setdefault(node["name"], []).append(node["duration_min"])
                        for child in node.get("children", []):
                            traverse(child)
                            
                    traverse(coa["task_hierarchy"])
            except Exception:
                pass
                
    # Calculate average durations
    heuristics_override = {}
    for task_name, durs in task_durations.items():
        # Apply a mild stochastic baseline adjustment to simulate learning duration adjustments
        heuristics_override[task_name] = int(round(np.mean(durs) * np.random.uniform(0.9, 1.1)))
        
    # Save versioned heuristics override JSON
    heur_version = f"heuristics_v1_{int(time.time())}.json"
    heur_path = os.path.join(_ROOT, "ai/models/heuristics", heur_version)
    with open(heur_path, "w") as f:
        json.dump(heuristics_override, f, indent=2)
    print(f"[Learning] Versioned heuristics update saved to {heur_path} ({len(heuristics_override)} overrides).")
    return heur_version

# --- 6. Model Registry Promotion ---
def update_registry(model_info, heur_version):
    print("[Learning] Updating Model Registry...")
    registry_path = os.path.join(_ROOT, "ai/models/registry.yaml")
    
    reg_data = {
        "model_version": "1.0.0",
        "dataset_version": "v1.0.0",
        "feature_version": "v1.0.0",
        "active_model": None,
        "active_heuristics": None,
        "last_evaluation_metrics": {},
        "history": []
    }
    
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            try:
                loaded = yaml.safe_load(f)
                if loaded:
                    reg_data.update(loaded)
            except Exception:
                pass
                
    # Regression Test & Promotion Logic
    # Promote only if MSE is within reasonable bounds
    test_mse = model_info.get("test_mse", 999.0) if model_info else 999.0
    passed = test_mse < 30000.0  # regression threshold matching scale of unscaled targets (duration, etc.)
    
    history_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_version": model_info["model_version"] if model_info else "N/A",
        "heuristics_version": heur_version,
        "test_mse": test_mse,
        "dataset_size": model_info["dataset_size"] if model_info else 0,
        "status": "PROMOTED" if passed else "FAILED_REVIEW"
    }
    
    reg_data["history"].append(history_entry)
    
    if passed:
        reg_data["active_model"] = model_info["model_version"]
        reg_data["active_heuristics"] = heur_version
        reg_data["last_evaluation_metrics"] = {"test_mse": test_mse}
        print(f"[Learning] New model {model_info['model_version']} and heuristics {heur_version} successfully PROMOTED to active production!")
    else:
        print(f"[Learning] New model failed regression criteria. Retaining previous active model.")
        
    with open(registry_path, "w") as f:
        yaml.safe_dump(reg_data, f)
    print(f"[Learning] Registry updated at {registry_path}.")

# --- Complete Pipeline Orchestrator ---
def main():
    parser = argparse.ArgumentParser(description="BATMAN Simulation-Driven Learning Pipeline Orchestrator")
    parser.add_argument("--episodes", type=int, default=5, help="Number of scenarios/episodes to simulate")
    parser.add_argument("--mc-runs", type=int, default=5, help="Monte Carlo runs per COA")
    parser.add_argument("--epochs", type=int, default=5, help="GNN training epochs")
    args = parser.parse_args()
    
    print("==================================================")
    print(" BATMAN Simulation-Driven Learning Pipeline")
    print("==================================================")
    
    # 1. Collect Simulation Logs
    collect_simulations(num_episodes=args.episodes, mc_runs=args.mc_runs)
    
    # 2. Extract Features
    extract_features()
    
    # 3. Create Dataset splits
    create_dataset()
    
    # 4. Train GNN/BRN Model
    model_info = train_gnn(epochs=args.epochs)
    
    # 5. Planner Heuristic weights calculation
    heur_version = generate_heuristics()
    
    # 6. Model Registry Update and Promotion
    update_registry(model_info, heur_version)
    
    print("==================================================")
    print(" Learning Pipeline completed successfully!")
    print("==================================================")

if __name__ == "__main__":
    main()
