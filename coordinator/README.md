# Federated Learning & Analytics Module

## Role: ML Scientist (Federated Learning & Analytics)

This module implements the intelligence layer of the privacy-preserving distributed analytics system. It simulates a federated learning setup where multiple decentralized data silos train a shared global model without sharing raw data.

---

## Objective

To evaluate:

- Model convergence in a federated setting
- Communication cost per training round
- Performance comparison between federated and centralized training
- Scalability as the number of silos increases

---

## Model Architecture

A simple neural network is defined in `common/model.py`:

- Input: 10 features
- Dense (32) + ReLU
- Dense (16) + ReLU
- Output: 1 (Sigmoid for binary classification)

The model predicts whether the sum of input features is positive or negative.

---

## Federated Learning Design

### 1️⃣ Local Training (Silos)
Each silo:
- Trains the global model locally
- Uses only its private dataset
- Sends model weights (not raw data) to the coordinator

### 2️⃣ Communication Protocol

Each silo sends a structured update message:

```json
{
  "node_id": "Silo_1",
  "round": 3,
  "num_samples": 200,
  "weights": [...],
  "mask": null
}
```

### Fields:

- node_id: Identifier of the silo
- round: Current training round
- num_samples: Used for weighted aggregation
- weights: Model parameters
- mask: Reserved for secure aggregation

### Performance Metrics

The system tracks:

- Global accuracy per round
- Communication cost per round (KB)
- Centralized baseline accuracy
- Communication cost includes:
- Uplink (Silo → Coordinator)
- Downlink (Coordinator → Silos)

### Experimental Results

Observed behavior:

- Federated accuracy increases steadily across rounds
- Communication cost scales linearly with number of silos
- Centralized training provides upper-bound performance
- Federated model approaches centralized accuracy over time

### How to Run

From project root:
```bash
python -m coordinator.app
```

Adjust parameters in `app.py`:
```python
NUM_SILOS = 5
NUM_ROUNDS = 10
```
