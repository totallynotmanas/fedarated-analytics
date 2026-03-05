import os
import time
import threading
from typing import Dict
from fastapi import FastAPI
import tensorflow as tf
import tensorflow_federated as tff

from common.model import create_tff_model
import silo_node.data_adapter.load_healthcare as hlt
import silo_node.data_adapter.load_finance as fin
import silo_node.data_adapter.load_retail as ret

APP_PORT = int(os.getenv("PORT", "5000"))
EXPECTED_NODES = int(os.getenv("EXPECTED_NODES", "3"))
NUM_ROUNDS = int(os.getenv("NUM_ROUNDS", "5"))

app = FastAPI(title="TFF RemoteExecutor Coordinator")

# In-memory store of registered silos: node_id -> {"grpc_address": ip:port, "domain": domain}
REGISTERED_SILOS: Dict[str, dict] = {}
sim_started = False

@app.get("/health")
def health():
    return {"status": "ok", "expected_nodes": EXPECTED_NODES, "registered": len(REGISTERED_SILOS)}

@app.post("/register")
async def register(req: dict):
    global sim_started
    node_id = req.get("node_id")
    grpc_address = req.get("grpc_address")
    domain = req.get("domain", "Healthcare")
    
    if not node_id or not grpc_address:
        return {"error": "Missing node_id or grpc_address"}

    if node_id not in REGISTERED_SILOS:
        REGISTERED_SILOS[node_id] = {"grpc_address": grpc_address, "domain": domain}
        print(f"[COORDINATOR] Registered {node_id} ({domain}) at {grpc_address}", flush=True)

    if len(REGISTERED_SILOS) >= EXPECTED_NODES and not sim_started:
        sim_started = True
        print("[COORDINATOR] All silos registered. Triggering TFF Training in background...", flush=True)
        threading.Thread(target=run_tff_training).start()

    return {"status": "registered", "node_id": node_id, "total_registered": len(REGISTERED_SILOS)}


def run_tff_training():
    time.sleep(5) # Let workers settle
    
    grpc_channels = [info["grpc_address"] for info in REGISTERED_SILOS.values()]
    print(f"\n[COORDINATOR] Setting up Remote Python Execution Context across {EXPECTED_NODES} workers...")
    
    # Establish connection to the Silos
    tff.backends.native.set_remote_python_execution_context(channels=grpc_channels)

    # 1. Provide the Secure Summation Aggregator
    secure_aggregator = tff.learning.robust_aggregator(
        zeroing=False, clipping=False, debug_measurements_fn=None
    )
    # OR explicit secure sum using SecureSumFactory
    secure_sum_factory = tff.aggregators.SecureSumFactory(
        upper_bound_threshold=100.0,
        lower_bound_threshold=-100.0
    )

    # 2. Build FedAvg
    training_process = tff.learning.algorithms.build_weighted_fed_avg(
        model_fn=create_tff_model,
        client_optimizer_fn=lambda: tf.keras.optimizers.Adam(learning_rate=0.01),
        server_optimizer_fn=lambda: tf.keras.optimizers.Adam(learning_rate=1.0),
        model_aggregator=secure_sum_factory 
    )

    # 3. Construct the Federated Data List
    # TFF will distribute these datasets to the connected execution channels
    federated_data = []
    for node_id, info in REGISTERED_SILOS.items():
        domain = info["domain"]
        if domain == "Healthcare":
            dataset = hlt.generate_healthcare_data()
        elif domain == "Finance":
            dataset = fin.generate_finance_data()
        else:
            dataset = ret.generate_retail_data()
        federated_data.append(dataset)

    # 4. Initialize State
    print("\n[COORDINATOR] Initializing TFF global state...")
    state = training_process.initialize()
    
    print("\n========== Federated TFF Training ==========", flush=True)

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n--- Round {round_num} ---", flush=True)
        
        result = training_process.next(state, federated_data)
        state = result.state
        metrics = result.metrics
        
        # Output criteria requirement: 'Global Loss' and 'Accuracy'
        if 'client_work' in metrics and 'train' in metrics['client_work']:
            # For tf.keras.metrics.BinaryAccuracy & Loss
            train_metrics = metrics['client_work']['train']
            loss = train_metrics.get('loss', 0.0)
            acc = train_metrics.get('accuracy', 0.0)
            print(f"[COORDINATOR] Global Loss: {loss:.4f} | Accuracy: {acc:.4f}", flush=True)
        else:
            print(f"[COORDINATOR] Raw Metrics: {metrics}", flush=True)

    print("\n[COORDINATOR] Training Complete!", flush=True)

