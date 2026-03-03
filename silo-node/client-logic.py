from __future__ import annotations

import os
import time
import json
from typing import List
import numpy as np
import requests

from common.cryptography import DPConfig, apply_dp, secure_mask_update, to_jsonable

NODE_ID = os.getenv("NODE_ID", "SILO_1")
COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://coordinator:8000")
ROUND = int(os.getenv("ROUND", "1"))

# Comma-separated peer node IDs (must match compose)
PEERS = [x.strip() for x in os.getenv("PEERS", "SILO_1,SILO_2,SILO_3").split(",") if x.strip()]

SHARED_SECRET = os.getenv("SHARED_SECRET", "class-demo-secret")

UPDATE_DIM = int(os.getenv("UPDATE_DIM", "20"))

DP_ENABLED = os.getenv("DP_ENABLED", "true").lower() in ("1", "true", "yes")
DP_L2_CLIP = float(os.getenv("DP_L2_CLIP", "1.0"))
DP_NOISE_MULT = float(os.getenv("DP_NOISE_MULT", "0.3"))
DP_SEED = int(os.getenv("DP_SEED", "12345")) + (abs(hash(NODE_ID)) % 10000)  # node-specific seed


def simulate_local_update(node_id: str, dim: int) -> np.ndarray:
    """Create a deterministic 'local update' vector.
    Replace this with real TFF client updates later.
    """
    # Use a node-specific seed so each silo generates different local update
    seed = (abs(hash(node_id)) % (2**32 - 1))
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, 1.0, size=(dim,)).astype(np.float32)


def main():
    print(f"[{NODE_ID}] Starting silo client. Coordinator={COORDINATOR_URL} Round={ROUND}")
    cfg = DPConfig(
        enabled=DP_ENABLED,
        l2_clip=DP_L2_CLIP,
        noise_multiplier=DP_NOISE_MULT,
        seed=DP_SEED,
    )

    # 1) Local compute (toy)
    local_update = simulate_local_update(NODE_ID, UPDATE_DIM)
    dp_update = apply_dp(local_update, cfg)

    # 2) Secure aggregation masking
    peer_ids = [p for p in PEERS if p != NODE_ID]
    masked = secure_mask_update(dp_update, NODE_ID, peer_ids, SHARED_SECRET)

    # 3) Send to coordinator
    payload = {
        "node_id": NODE_ID,
        "round": ROUND,
        "masked_update": to_jsonable(masked),
    }

    url = f"{COORDINATOR_URL}/submit_update"
    for attempt in range(1, 21):
        try:
            r = requests.post(url, json=payload, timeout=5)
            print(f"[{NODE_ID}] submit_update -> {r.status_code} {r.text}")
            break
        except Exception as e:
            print(f"[{NODE_ID}] submit_update attempt {attempt} failed: {e}")
            time.sleep(1.0)

    # Optional: poll aggregate
    agg_url = f"{COORDINATOR_URL}/aggregate?round={ROUND}"
    for _ in range(20):
        try:
            g = requests.get(agg_url, timeout=5)
            print(f"[{NODE_ID}] aggregate -> {g.status_code} {g.text[:200]}...")
            if g.status_code == 200:
                data = g.json()
                if data.get("status") == "ready":
                    break
        except Exception as e:
            print(f"[{NODE_ID}] aggregate poll error: {e}")
        time.sleep(1.0)


if __name__ == "__main__":
    main()

