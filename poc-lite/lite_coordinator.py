import os
import time
import uvicorn
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

# ----------------- Configuration -----------------
APP_PORT = int(os.getenv("PORT", "5000"))
EXPECTED_NODES = int(os.getenv("EXPECTED_NODES", "7"))
NUM_ROUNDS = int(os.getenv("NUM_ROUNDS", "5"))

# The weights will be shapes (10, 32), (32,), (32, 16), (16,), (16, 1), (1,)
# For PoC, we let the first node to submit define the weight shapes.
GLOBAL_WEIGHTS = None
REGISTERED_SILOS = set()

# State for current round
current_round = 0
silo_submissions = []

app = FastAPI(title="Lightweight FedAvg Coordinator")

class RegistrationReq(BaseModel):
    node_id: str
    domain: str

class WeightsSubmission(BaseModel):
    node_id: str
    round_num: int
    weights: List[Any] # A flattened or serialized list of arrays
    metrics: Dict[str, float]

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "expected_nodes": EXPECTED_NODES,
        "registered": len(REGISTERED_SILOS)
    }

@app.post("/register")
def register(req: RegistrationReq):
    if req.node_id not in REGISTERED_SILOS:
        REGISTERED_SILOS.add(req.node_id)
        print(f"[COORDINATOR] Registered {req.node_id} ({req.domain})")
    
    # If everyone is here, open the gates!
    return {
        "status": "registered", 
        "total_registered": len(REGISTERED_SILOS),
        "start_training": len(REGISTERED_SILOS) >= EXPECTED_NODES
    }

@app.get("/weights")
def get_weights():
    # Provide the current global weights to a silo
    if GLOBAL_WEIGHTS is None:
        return {"round": current_round, "weights": None}
    
    # Convert numpy arrays to lists for JSON
    serializable_weights = [w.tolist() for w in GLOBAL_WEIGHTS]
    return {"round": current_round, "weights": serializable_weights}

@app.post("/submit")
def submit_weights(submission: WeightsSubmission):
    global current_round, silo_submissions, GLOBAL_WEIGHTS
    
    print(f"\n[COORDINATOR] Received round {submission.round_num} weights from {submission.node_id}")
    print(f"[COORDINATOR] Metrics: {submission.metrics}")
    
    # Convert back to numpy
    numpy_weights = [np.array(w) for w in submission.weights]
    silo_submissions.append(numpy_weights)
    
    # If we have received from all expected nodes, average them!
    if len(silo_submissions) >= EXPECTED_NODES:
        print(f"\n======== [COORDINATOR] ALL NODES SUBMITTED ROUND {current_round} ========")
        
        # Simple FedAvg (equal weighting for PoC)
        averaged_weights = []
        for layer_idx in range(len(numpy_weights)):
            # Stack the layer across all silos and take the mean
            layer_stack = np.stack([s_weights[layer_idx] for s_weights in silo_submissions])
            averaged_weights.append(np.mean(layer_stack, axis=0))
            
        GLOBAL_WEIGHTS = averaged_weights
        print(f"[COORDINATOR] Successfully aggregated global model for round {current_round}!")
        
        # Reset for next round
        silo_submissions = []
        current_round += 1
        
        if current_round >= NUM_ROUNDS:
            print("\n========== FEDERATED TRAINING COMPLETE ==========")
            
    return {"status": "accepted"}

if __name__ == "__main__":
    print(f"[COORDINATOR] Starting Lightweight Coordinator on port {APP_PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
