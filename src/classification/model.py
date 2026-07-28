from typing import Any
from config.logger import logger
from src.classification.tokenizer import CATEGORIES

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    _TF_AVAILABLE = True
except Exception as _e_tf:
    logger.warning(f"TensorFlow import skipped: {_e_tf}")
    _TF_AVAILABLE = False


def create_tensorflow_model(
    vocab_size: int = 10000,
    embedding_dim: int = 64,
    max_len: int = 200,
    num_classes: int = len(CATEGORIES)
) -> Any:
    """Build a TensorFlow 2.x Embedding + Conv1D + GlobalMaxPooling + Dense neural classifier."""
    if not _TF_AVAILABLE:
        logger.warning("TensorFlow library is not installed.")
        return None

    model = models.Sequential([
        layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_len),
        layers.Dropout(0.2),
        layers.Conv1D(filters=128, kernel_size=5, activation="relu"),
        layers.GlobalMaxPooling1D(),
        layers.Dense(64, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model
