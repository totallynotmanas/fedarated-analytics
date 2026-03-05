import tensorflow as tf
import numpy as np

def generate_finance_data(num_samples=1000, batch_size=32):
    """
    Simulates loading `transaction_logs.csv`.
    Predicts fraud based on 10 synthetic transaction metrics.
    """
    print("Loading Finance dataset (transaction_logs.csv)...")
    np.random.seed(1337) # different seed to represent domain variance
    
    X = np.random.normal(loc=0.5, scale=2.0, size=(num_samples, 10)).astype(np.float32)
    
    # Simple rule: if sum of metrics > 5, transaction is fraudulent (1)
    y = (np.sum(X, axis=1) > 5).astype(np.int32).reshape(-1, 1)
    
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    dataset = dataset.map(lambda x, y: {'x': x, 'y': y})
    return dataset.batch(batch_size)
