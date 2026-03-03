# Report Notes (Security & Crypto Lead)

## Secure Aggregation (Toy Pairwise Masking)
Goal: Coordinator must not learn any *individual* silo update.

For each pair of silos (i, j):
- Both derive the same random mask vector `m_ij` using a shared secret and PRG.
- If i < j: silo i **adds** `m_ij`
- Else: silo i **subtracts** `m_ij`

Masked update sent by silo i:
\[
u'_i = u_i + \sum_{j>i} m_{ij} - \sum_{j<i} m_{ji}
\]

Coordinator aggregates:
\[
\sum_i u'_i = \sum_i u_i + (\text{all masks cancel}) = \sum_i u_i
\]

So coordinator learns only the aggregate.

## Differential Privacy (DP)
Each silo applies:
1. L2 clipping: \(\|u\|_2 \le C\)
2. Adds Gaussian noise: \(\mathcal{N}(0, \sigma^2 C^2)\)

This reduces the risk of reconstructing individual training samples from gradients.

## REST Protocol
- `POST /submit_update` with:
  - `node_id`, `round`, `masked_update: [float]`
- `GET /aggregate?round=1` returns aggregate when all updates are received.

