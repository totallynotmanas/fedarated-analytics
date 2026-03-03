# Privacy-Preserving Distributed Analytics (Toy Secure Aggregation + DP)

This repo is a **demo scaffold** for privacy-preserving distributed analytics across decentralized data silos.

## What’s implemented (Security & Crypto Lead scope)
- **Secure Aggregation (pairwise masking, toy):**
  - Each silo generates *pairwise masks* with every other silo (deterministically) and adds/subtracts them so masks cancel **only after summation**.
  - The coordinator only sees **masked** individual updates and can only recover the **aggregate**.
- **Differential Privacy (DP) helper:**
  - Optional L2 clipping + Gaussian noise added to each silo update before secure masking.
- **Communication protocol (REST):**
  - `POST /submit_update` for silo → coordinator
  - `GET /aggregate` to retrieve aggregate once all silos submitted

> Note: This is a **toy** implementation for academics/demos. Production Secure Aggregation requires robust key exchange, dropout handling, and cryptographic hardening.

## Quick start (Docker Compose)
From `deployment/`:

```bash
docker compose up --build
```

You should see:
- Coordinator running at `http://localhost:8000`
- 3 silos submitting masked updates
- Coordinator printing / returning the aggregated update

## Endpoints
- `POST /register` (optional)
- `POST /submit_update`
- `GET /aggregate?round=1`

## Folder structure
- `common/cryptography.py` — secure masking + DP utilities
- `coordinator/app.py` — FastAPI coordinator
- `silo-node/client-logic.py` — silo client that generates local update, adds DP, masks, sends

