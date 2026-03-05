import tensorflow as tf
import numpy as np

def generate_healthcare_data(num_samples=1000, batch_size=32):
    """
    Simulates loading `hospital_records.csv`.
    Predicts patient risk levels based on 10 synthetic vital signs.
    """
    print("Loading Healthcare dataset (hospital_records.csv)...")
    # For predictability, let's make it a somewhat learnable linear separation
    np.random.seed(42)
    
    X = np.random.normal(loc=0.0, scale=1.0, size=(num_samples, 10)).astype(np.float32)
    
    # Simple rule: if sum of vital signs > 0, patient is high risk (1)
    y = (np.sum(X, axis=1) > 0).astype(np.int32).reshape(-1, 1)
    
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    
    # TFF requires dict-like objects {'x': features, 'y': labels}
    dataset = dataset.map(lambda x, y: {'x': x, 'y': y})
    return dataset.batch(batch_size)
