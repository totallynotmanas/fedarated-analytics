import numpy as np
import matplotlib.pyplot as plt
from common.model import create_model


# ===============================
# Configuration
# ===============================

NUM_SILOS = 5
NUM_ROUNDS = 10
LOCAL_EPOCHS = 1


# ===============================
# Generate Synthetic Silo Data
# ===============================

def generate_silo_data(samples=200):
    X = np.random.randn(samples, 10)
    y = (np.sum(X, axis=1) > 0).astype(int)
    return X, y


# ===============================
# Message Schema Builder
# ===============================

def create_update_message(node_id, round_num, weights, num_samples):
    return {
        "node_id": node_id,
        "round": round_num,
        "num_samples": num_samples,
        "weights": [w.tolist() for w in weights],  # JSON serializable
        "mask": None
    }


# ===============================
# Local Training
# ===============================

def local_train(global_weights, data, epochs=1):
    model = create_model()
    model.set_weights(global_weights)

    X, y = data
    model.fit(X, y, epochs=epochs, verbose=0)

    return model.get_weights()


# ===============================
# Weighted Federated Averaging
# ===============================

def federated_average(messages):
    total_samples = sum(msg["num_samples"] for msg in messages)

    avg_weights = []

    for layer_idx in range(len(messages[0]["weights"])):

        weighted_sum = sum(
            np.array(msg["weights"][layer_idx]) *
            (msg["num_samples"] / total_samples)
            for msg in messages
        )

        avg_weights.append(weighted_sum)

    return avg_weights


# ===============================
# Communication Cost (Uplink + Downlink)
# ===============================

def calculate_comm_cost(messages):
    total_bytes = 0
    for msg in messages:
        for layer in msg["weights"]:
            arr = np.array(layer)
            total_bytes += arr.nbytes

    # Multiply by 2 for uplink + downlink
    return total_bytes * 2


# ===============================
# Federated Simulation
# ===============================

def run_federated_simulation():

    silo_data = [generate_silo_data() for _ in range(NUM_SILOS)]
    test_data = generate_silo_data(300)

    accuracy_history = []
    comm_history = []

    global_model = create_model()
    global_weights = global_model.get_weights()

    print("\n========== Federated Training ==========")

    for round_num in range(NUM_ROUNDS):
        print(f"\n--- Round {round_num + 1} ---")

        silo_messages = []

        for i, data in enumerate(silo_data):

            updated_weights = local_train(
                global_weights,
                data,
                epochs=LOCAL_EPOCHS
            )

            message = create_update_message(
                node_id=f"Silo_{i+1}",
                round_num=round_num + 1,
                weights=updated_weights,
                num_samples=len(data[0])
            )

            silo_messages.append(message)

        # Communication Cost
        comm_cost = calculate_comm_cost(silo_messages)
        comm_history.append(comm_cost)

        # Aggregation
        global_weights = federated_average(silo_messages)
        global_model.set_weights(global_weights)

        # Evaluation
        X_test, y_test = test_data
        loss, acc = global_model.evaluate(X_test, y_test, verbose=0)

        accuracy_history.append(acc)

        print(f"Global Accuracy: {acc:.4f}")
        print(f"Communication This Round: {comm_cost / 1024:.2f} KB")

    return accuracy_history, comm_history, silo_data, test_data


# ===============================
# Centralized Baseline
# ===============================

def run_centralized_baseline(silo_data, test_data):

    print("\n========== Centralized Training ==========")

    central_model = create_model()

    X_all = np.vstack([data[0] for data in silo_data])
    y_all = np.hstack([data[1] for data in silo_data])

    central_model.fit(X_all, y_all, epochs=NUM_ROUNDS, verbose=0)

    loss, central_acc = central_model.evaluate(*test_data, verbose=0)

    print(f"Centralized Accuracy: {central_acc:.4f}")

    return central_acc


# ===============================
# Plot Results
# ===============================

def plot_results(accuracy_history, comm_history):

    plt.figure()
    plt.plot(range(1, NUM_ROUNDS + 1), accuracy_history)
    plt.title("Federated Accuracy per Round")
    plt.xlabel("Round")
    plt.ylabel("Accuracy")
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(range(1, NUM_ROUNDS + 1),
             [c / 1024 for c in comm_history])
    plt.title("Communication Cost per Round (KB)")
    plt.xlabel("Round")
    plt.ylabel("Communication (KB)")
    plt.grid()
    plt.show()


# ===============================
# Main Entry
# ===============================

def main():

    accuracy_history, comm_history, silo_data, test_data = \
        run_federated_simulation()

    run_centralized_baseline(silo_data, test_data)

    plot_results(accuracy_history, comm_history)


if __name__ == "__main__":
    main()