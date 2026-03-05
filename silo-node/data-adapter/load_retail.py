import tensorflow as tf
import numpy as np

def generate_retail_data(num_samples=1000, batch_size=32):
    """
    Simulates loading `inventory_sales.csv`.
    Predicts supply chain shortfall based on 10 synthetic sales metrics.
    """
    print("Loading Retail dataset (inventory_sales.csv)...")
    np.random.seed(9999) # different seed
    
    X = np.random.normal(loc=-0.5, scale=0.8, size=(num_samples, 10)).astype(np.float32)
    
    # Simple rule: if sum > -2, stock shortfall is likely (1)
    y = (np.sum(X, axis=1) > -2).astype(np.int32).reshape(-1, 1)
    
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    dataset = dataset.map(lambda x, y: {'x': x, 'y': y})
    return dataset.batch(batch_size)
