#!/usr/bin/env python3
import subprocess
import time
import sys

# Define the services to start
services = [
    {"name": "Mission Service", "command": ["uvicorn", "services.mission-svc.main:app", "--port", "8001"]},
    {"name": "Planning Service", "command": ["uvicorn", "services.planning-svc.main:app", "--port", "8002"]},
    {"name": "Wargame Service", "command": ["uvicorn", "services.wargame-svc.main:app", "--port", "8003"]},
    {"name": "Threat Service", "command": ["uvicorn", "services.threat-svc.main:app", "--port", "8004"]},
    {"name": "KG Service", "command": ["uvicorn", "services.kg-svc.main:app", "--port", "8006"]},
    {"name": "API Gateway", "command": ["uvicorn", "services.gateway.main:app", "--port", "8080"]},
]

processes = []

try:
    print("Starting BATMAN Backend Services...")
    for svc in services:
        print(f"Starting {svc['name']} on port {svc['command'][3]}...")
        p = subprocess.Popen(svc["command"])
        processes.append((svc["name"], p))
    
    print("\nAll services started! Press Ctrl+C to stop them all.\n")
    
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down services...")
    for name, p in processes:
        print(f"Stopping {name}...")
        p.terminate()
    
    for name, p in processes:
        p.wait()
        
    print("All services stopped.")
    sys.exit(0)
