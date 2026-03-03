"""common/cryptography.py

Security & Crypto Lead module.

Implements:
1) Toy Secure Aggregation via **pairwise masking**:
   - For each pair (i, j), both silos derive the same pseudo-random mask.
   - One silo adds it, the other subtracts it.
   - When the coordinator sums all masked updates, masks cancel out.

2) Optional Differential Privacy (DP):
   - L2 clipping + Gaussian noise added to update.

This module is intentionally minimal and readable for coursework demos.

⚠️ Not production-secure. For real deployments you need:
- authenticated key exchange (e.g., ECDH),
- dropout-resilient secure aggregation,
- secure enclaves / MPC frameworks,
- audit logging and access control.

"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple, Optional

import numpy as np


def _stable_int_seed(*parts: str) -> int:
    """Derive a stable 32-bit seed from arbitrary strings."""
    h = hashlib.sha256(("|".join(parts)).encode("utf-8")).digest()
    # Take first 4 bytes as uint32
    return int.from_bytes(h[:4], "big", signed=False)


def prg_mask(seed: int, shape: Tuple[int, ...]) -> np.ndarray:
    """Pseudo-random mask generator using NumPy PCG64."""
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=1.0, size=shape).astype(np.float32)


@dataclass(frozen=True)
class DPConfig:
    enabled: bool = False
    l2_clip: float = 1.0
    noise_multiplier: float = 0.5
    seed: int = 12345  # only for reproducibility in demos


def l2_clip(vec: np.ndarray, clip_norm: float) -> np.ndarray:
    """Clip vector to have L2 norm at most clip_norm."""
    norm = float(np.linalg.norm(vec))
    if norm <= clip_norm or norm == 0.0:
        return vec
    return (vec * (clip_norm / norm)).astype(np.float32)


def add_gaussian_noise(vec: np.ndarray, std: float, seed: int) -> np.ndarray:
    """Add Gaussian noise with given std."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, std, size=vec.shape).astype(np.float32)
    return (vec + noise).astype(np.float32)


def apply_dp(vec: np.ndarray, cfg: DPConfig) -> np.ndarray:
    """Apply DP: L2 clip + Gaussian noise."""
    if not cfg.enabled:
        return vec.astype(np.float32)

    clipped = l2_clip(vec.astype(np.float32), cfg.l2_clip)
    # Typical DP std = noise_multiplier * clip_norm
    std = float(cfg.noise_multiplier * cfg.l2_clip)
    return add_gaussian_noise(clipped, std=std, seed=cfg.seed)


def secure_mask_update(
    update: np.ndarray,
    node_id: str,
    peer_ids: Sequence[str],
    shared_secret: str,
) -> np.ndarray:
    """Apply pairwise masks so that masks cancel after summation.

    Convention:
      For each pair (A, B):
        if A < B: A adds mask(A,B), B subtracts mask(A,B)

    Mask derivation:
      seed = SHA256(shared_secret | min_id | max_id) -> PRG -> mask vector
    """
    masked = update.astype(np.float32).copy()
    my = node_id

    for peer in peer_ids:
        if peer == my:
            continue
        a, b = (my, peer) if my < peer else (peer, my)
        seed = _stable_int_seed(shared_secret, a, b)

        mask = prg_mask(seed, shape=masked.shape)

        if my < peer:
            masked += mask
        else:
            masked -= mask

    return masked.astype(np.float32)


def to_jsonable(vec: np.ndarray) -> List[float]:
    """Convert numpy vector to JSON-friendly list."""
    return [float(x) for x in vec.reshape(-1)]


def from_jsonable(lst: Sequence[float]) -> np.ndarray:
    """Convert list back to numpy vector."""
    return np.array(lst, dtype=np.float32)

