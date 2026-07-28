import os
import sys
import numpy as np

# Ensure root import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.getcwd())

from config.settings import settings
from config.logger import logger
from src.classification.tokenizer import CATEGORIES, text_tokenizer
from src.classification.model import create_tensorflow_model


def generate_synthetic_dataset():
    """Generate synthetic dataset across 10 categories for initial baseline model training."""
    data = []
    labels = []

    samples_per_category = {
        0: ["Artificial Intelligence reasoning systems and autonomous cognitive architectures evaluated in deep learning research."],
        1: ["Machine learning models trained with gradient descent optimization, loss functions, and cross-validation."],
        2: ["Cyber Security vulnerability exploitation, firewall mitigation, zero-day threat analysis, and cryptographic authentication."],
        3: ["Cloud computing microservices orchestrated with Kubernetes containers and serverless functions."],
        4: ["Computer vision convolutional neural networks performing real-time object detection and instance segmentation."],
        5: ["Robotics kinematics and motion planning for autonomous manipulators using ROS framework."],
        6: ["Natural language processing transformers evaluating attention mechanisms and token sequence classification."],
        7: ["Blockchain smart contract validation using decentralized proof-of-stake consensus protocols."],
        8: ["IoT sensor networks transmitting edge computing telemetry over low-latency MQTT message brokers."],
        9: ["Data science exploratory data analysis, statistical modeling, feature engineering, and predictive analytics."]
    }

    for cat_idx, templates in samples_per_category.items():
        for _ in range(20): # Replicate for baseline training
            text = templates[0] + f" Sample variation {_}."
            data.append(text)
            labels.append(cat_idx)

    return data, labels


def train():
    logger.info("Starting TensorFlow Document Classifier Training Pipeline...")

    data, labels = generate_synthetic_dataset()

    text_tokenizer.fit_on_texts(data)
    seqs = text_tokenizer.texts_to_sequences(data)
    padded = text_tokenizer.pad_sequences(seqs)

    X = np.array(padded)
    y = np.array(labels)

    model = create_tensorflow_model(
        vocab_size=10000,
        embedding_dim=64,
        max_len=200,
        num_classes=len(CATEGORIES)
    )

    if model is None:
        logger.error("TensorFlow is not available. Aborting training.")
        return

    logger.info("Training Keras model...")
    model.fit(X, y, epochs=5, batch_size=8, verbose=1)

    model_dir = settings.TF_MODEL_PATH
    os.makedirs(model_dir, exist_ok=True)

    tokenizer_path = os.path.join(model_dir, "tokenizer.json")
    text_tokenizer.save(tokenizer_path)

    model_path = os.path.join(model_dir, "model.h5")
    model.save(model_path)

    logger.info(f"Model successfully saved to {model_path}")
    logger.info("TensorFlow Document Classifier Training Complete!")


if __name__ == "__main__":
    train()
