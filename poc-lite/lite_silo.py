import os
import sys
import time
import requests
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--node_id", default=os.getenv("NODE_ID", "Silo_X"))
parser.add_argument("--domain", default=os.getenv("DOMAIN", "Healthcare"))
parser.add_argument("--coordinator_url", default=os.getenv("COORDINATOR_URL", "http://localhost:5000"))
args = parser.parse_args()

NODE_ID = args.node_id
DOMAIN = args.domain
COORDINATOR_URL = args.coordinator_url

# Dummy model weights shape (matches our model.py)
# 10 input features -> 32 dense -> 16 dense -> 1 output
WEIGHT_SHAPES = [
    (10, 32), (32,), 
    (32, 16), (16,), 
    (16, 1),  (1,)
]

def generate_random_weights():
    # Initialize random weights for the first round if no global weights exist
    return [np.random.normal(0, 0.1, size=shape) for shape in WEIGHT_SHAPES]

def local_training(global_weights):
    print(f"[{NODE_ID}] Simulating local training on {DOMAIN} data...")
    # Simulate training time
    time.sleep(np.random.uniform(1.0, 3.0))
    
    # Simulate weight updates (add small random noise to global weights)
    updated_weights = []
    for w in global_weights:
        noise = np.random.normal(0, 0.01, size=w.shape)
        updated_weights.append(w - noise) # Simulated gradient descent step
    
    # Simulate a decreasing loss and increasing accuracy
    simulated_loss = np.random.uniform(0.3, 0.6)
    simulated_acc = np.random.uniform(0.7, 0.9)
    
    return updated_weights, {"loss": simulated_loss, "accuracy": simulated_acc}

def main():
    print(f"[{NODE_ID}] Starting Lightweight FedAvg Worker...")
    
    # 1. Register with coordinator
    registered = False
    while not registered:
        try:
            r = requests.post(f"{COORDINATOR_URL}/register", json={"node_id": NODE_ID, "domain": DOMAIN})
            if r.status_code == 200:
                print(f"[{NODE_ID}] Successfully registered with coordinator.")
                registered = True
        except requests.exceptions.ConnectionError:
            print(f"[{NODE_ID}] Coordinator not ready. Retrying in 2s...")
            time.sleep(2)
            
    # Wait for coordinator to say "start_training"
    training_started = False
    while not training_started:
        try:
            # Re-register to poll status
            r = requests.post(f"{COORDINATOR_URL}/register", json={"node_id": NODE_ID, "domain": DOMAIN})
            data = r.json()
            if data.get("start_training"):
                training_started = True
            else:
                time.sleep(2)
        except:
            time.sleep(2)

    # 2. Federated Training Loop
    current_round = 0
    while True:
        try:
            # Poll for new weights
            r = requests.get(f"{COORDINATOR_URL}/weights")
            if r.status_code != 200:
                time.sleep(2)
                continue
                
            data = r.json()
            global_round = data.get("round", 0)
            
            # If the coordinator has moved to a new round, we should too
            if global_round == current_round:
                global_weights = data.get("weights")
                
                # Convert list back to numpy, or init fresh if None
                if global_weights is None:
                    np_weights = generate_random_weights()
                else:
                    np_weights = [np.array(w) for w in global_weights]
                
                # Perform local training
                updated_weights, metrics = local_training(np_weights)
                
                # Submit back to coordinator
                serializable_weights = [w.tolist() for w in updated_weights]
                submit_payload = {
                    "node_id": NODE_ID,
                    "round_num": current_round,
                    "weights": serializable_weights,
                    "metrics": metrics
                }
                requests.post(f"{COORDINATOR_URL}/submit", json=submit_payload)
                print(f"[{NODE_ID}] Submitted round {current_round} updates.")
                
                # Move to the next round locally so we don't double-submit
                current_round += 1
                time.sleep(2) # Give coordinator time to aggregate
            else:
                # Coordinator is still waiting for others on an older round, or it has finished
                time.sleep(2)
                
        except Exception as e:
            print(f"[{NODE_ID}] Error in training loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
