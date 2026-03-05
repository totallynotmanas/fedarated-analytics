import os
import time
import requests
import socket
import grpc
from concurrent import futures
import tensorflow as tf
import tensorflow_federated as tff

NODE_ID = os.getenv("NODE_ID", "Silo_X")
DOMAIN = os.getenv("DOMAIN", "Healthcare")
COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://coordinator:5000")
GRPC_PORT = int(os.getenv("GRPC_PORT", "8000"))

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def register_with_coordinator(grpc_address):
    health_url = f"{COORDINATOR_URL}/health"
    print(f"[{NODE_ID}] Attempting initial handshake with Coordinator at {health_url}", flush=True)
    
    connected = False
    for attempt in range(1, 13): 
        try:
            r = requests.get(health_url, timeout=5)
            if r.status_code == 200:
                print(f"[{NODE_ID}] Handshake successful! Coordinator is ready.", flush=True)
                connected = True
                break
            else:
                print(f"[{NODE_ID}] Coordinator returned status {r.status_code}. Retrying in 5 seconds...", flush=True)
        except requests.exceptions.RequestException as e:
            print(f"[{NODE_ID}] Handshake attempt {attempt} failed. Retrying in 5 seconds...", flush=True)
        time.sleep(5.0)

    # Send registration
    url = f"{COORDINATOR_URL}/register"
    payload = {
        "node_id": NODE_ID,
        "domain": DOMAIN,
        "grpc_address": grpc_address
    }
    
    for attempt in range(1, 6):
        try:
            r = requests.post(url, json=payload, timeout=5)
            print(f"[{NODE_ID}] Registration -> {r.status_code} {r.text}", flush=True)
            break
        except Exception as e:
            print(f"[{NODE_ID}] Registration failed: {e}", flush=True)
            time.sleep(2.0)

def main():
    print(f"[{NODE_ID}] Starting TFF gRPC Worker on domain '{DOMAIN}'...", flush=True)
    
    local_ip = get_local_ip()
    grpc_address = f"{local_ip}:{GRPC_PORT}"
    
    # Register in the background while gRPC spins up
    import threading
    threading.Thread(target=register_with_coordinator, args=(grpc_address,), daemon=True).start()

    print(f"[{NODE_ID}] Binding TFF worker to port {GRPC_PORT}...", flush=True)
    
    # 1. Provide an Execution Context
    # TFF provides an ExecutorService to wrap an executor factory over gRPC.
    # To keep it robust across TFF versions, we use the `run_server` helper from tff.simulation
    try:
        # Standard API for recent TFF versions
        executor_factory = tff.framework.local_executor_factory()
        
        # We need the service class. Wait, in modern TFF `run_server` handles this:
        server = tff.simulation.run_server(executor_factory, 10, GRPC_PORT, None, None)
        print(f"[{NODE_ID}] TFF ExecutorService running on port {GRPC_PORT}. Waiting for Coordinator tasks...", flush=True)
        server.wait_for_termination()
    except Exception as e1:
        print(f"[{NODE_ID}] run_server failed, attempting native executor service: {e1}", flush=True)
        try:
            from tensorflow_federated.python.core.impl.executors import executor_service
            from tensorflow_federated.python.core.impl.executors import sequence_executor
            from tensorflow_federated.python.core.impl.executors import reference_resolving_executor
            from tensorflow_federated.python.core.impl.executors import eager_tf_executor

            leaf = eager_tf_executor.EagerTFExecutor()
            seq = sequence_executor.SequenceExecutor(leaf)
            ref = reference_resolving_executor.ReferenceResolvingExecutor(seq)
            
            ex_service = executor_service.ExecutorService(ref)
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            from tensorflow_federated.proto.v0 import executor_pb2_grpc
            executor_pb2_grpc.add_ExecutorGroupServicer_to_server(ex_service, server)
            
            server.add_insecure_port(f'[::]:{GRPC_PORT}')
            server.start()
            print(f"[{NODE_ID}] Native TFF ExecutorService running on port {GRPC_PORT}. Waiting for Coordinator tasks...", flush=True)
            server.wait_for_termination()
        except Exception as e2:
            print(f"[{NODE_ID}] Native approach also failed: {e2}. Cannot start TFF Worker.", flush=True)


if __name__ == "__main__":
    main()
