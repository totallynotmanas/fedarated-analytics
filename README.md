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
