import tensorflow as tf
import tensorflow_federated as tff
import collections

# Feature dimension that matches our data adapters
INPUT_DIM = 10
NUM_CLASSES = 2 # Binary classification across all our domains

def create_keras_model():
    """Returns a compiled standard Keras Dense Neural Network."""
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(INPUT_DIM,), name='dense_1'),
        tf.keras.layers.Dense(16, activation='relu', name='dense_2'),
        tf.keras.layers.Dense(NUM_CLASSES if NUM_CLASSES > 2 else 1, activation='sigmoid', name='output')
    ])
    
    # We don't strictly *need* to compile it with optimizer here in TFF, 
    # but providing loss and metrics is required.
    return model

def create_tff_model():
    """Wraps the Keras model in tff.learning.models.from_keras_model"""
    keras_model = create_keras_model()
    
    # Define the input specification matching the dataset yielded by our data adapters
    input_spec = collections.OrderedDict(
        x=tf.TensorSpec(shape=(None, INPUT_DIM), dtype=tf.float32),
        y=tf.TensorSpec(shape=(None, 1), dtype=tf.int32)
    )
    
    return tff.learning.models.from_keras_model(
        keras_model=keras_model,
        input_spec=input_spec,
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=[tf.keras.metrics.BinaryAccuracy(name='accuracy')]
    )