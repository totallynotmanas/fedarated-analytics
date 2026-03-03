from __future__ import annotations

import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np

from common.cryptography import from_jsonable, to_jsonable

APP_HOST = os.getenv("HOST", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", "8000"))
EXPECTED_NODES = int(os.getenv("EXPECTED_NODES", "3"))

app = FastAPI(title="Coordinator (Toy Secure Aggregation)")

# In-memory store: round -> node_id -> masked_update
ROUND_STORE: Dict[int, Dict[str, np.ndarray]] = {}


class RegisterReq(BaseModel):
    node_id: str


class SubmitUpdateReq(BaseModel):
    node_id: str = Field(..., examples=["SILO_1"])
    round: int = Field(..., ge=1, examples=[1])
    masked_update: List[float]


@app.get("/health")
def health():
    return {"status": "ok", "expected_nodes": EXPECTED_NODES}


@app.post("/register")
def register(req: RegisterReq):
    # Optional — kept for completeness
    return {"status": "registered", "node_id": req.node_id}


@app.post("/submit_update")
def submit_update(req: SubmitUpdateReq):
    update = from_jsonable(req.masked_update)
    r = req.round
    if r not in ROUND_STORE:
        ROUND_STORE[r] = {}
    ROUND_STORE[r][req.node_id] = update

    got = len(ROUND_STORE[r])
    return {"status": "received", "round": r, "received": got, "expected": EXPECTED_NODES}


@app.get("/aggregate")
def aggregate(round: int = 1):
    if round not in ROUND_STORE or len(ROUND_STORE[round]) == 0:
        raise HTTPException(status_code=404, detail="No updates for this round yet.")

    if len(ROUND_STORE[round]) < EXPECTED_NODES:
        return {
            "status": "waiting",
            "round": round,
            "received": len(ROUND_STORE[round]),
            "expected": EXPECTED_NODES,
        }

    # Sum masked updates; pairwise masks cancel out -> aggregate of (DP-applied) updates
    updates = list(ROUND_STORE[round].values())
    agg = np.sum(np.stack(updates, axis=0), axis=0).astype(np.float32)

    return {
        "status": "ready",
        "round": round,
        "participants": sorted(list(ROUND_STORE[round].keys())),
        "aggregate_update": to_jsonable(agg),
        "l2_norm": float(np.linalg.norm(agg)),
    }

