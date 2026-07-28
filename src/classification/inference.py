import os
import time
from typing import Dict, List, Tuple
import numpy as np
from config.settings import settings
from config.logger import logger
from src.classification.tokenizer import CATEGORIES, text_tokenizer
from src.schemas.classification import CategoryScore, ClassifyResponse

try:
    import tensorflow as tf
    _TF_AVAILABLE = True
except Exception as _e_tf:
    logger.warning(f"TensorFlow import skipped: {_e_tf}")
    _TF_AVAILABLE = False


class DocumentClassifierInference:
    """Production Inference engine for TensorFlow document category classification."""

    def __init__(self):
        self.model_dir = settings.TF_MODEL_PATH
        self.model = None
        self.tokenizer = text_tokenizer
        self.is_loaded = False

    def initialize(self) -> None:
        tokenizer_file = os.path.join(self.model_dir, "tokenizer.json")
        model_file = os.path.join(self.model_dir, "model.h5")

        tok_loaded = self.tokenizer.load(tokenizer_file)

        if _TF_AVAILABLE and os.path.exists(model_file):
            try:
                self.model = tf.keras.models.load_model(model_file)
                self.is_loaded = True
                logger.info(f"Loaded TensorFlow classification model from {model_file}")
            except Exception as e:
                logger.warning(f"Could not load TF model ({e}). Using rule-heuristic classifier.")
        else:
            logger.info("TensorFlow classification model weights not found. Using heuristic classifier.")

    def classify_text(self, text: str) -> ClassifyResponse:
        start_time = time.time()
        if not text or not text.strip():
            return ClassifyResponse(
                predicted_category="General",
                confidence=1.0,
                all_scores=[CategoryScore(category=c, confidence=0.1) for c in CATEGORIES],
                latency_ms=0.0
            )

        if self.is_loaded and self.model:
            try:
                seqs = self.tokenizer.texts_to_sequences([text])
                padded = self.tokenizer.pad_sequences(seqs)
                arr = np.array(padded)
                preds = self.model.predict(arr, verbose=0)[0]
                
                scores = []
                for idx, prob in enumerate(preds):
                    cat_name = self.tokenizer.idx2category.get(idx, CATEGORIES[idx])
                    scores.append(CategoryScore(category=cat_name, confidence=round(float(prob), 4)))

                scores.sort(key=lambda x: x.confidence, reverse=True)
                top = scores[0]
                latency = round((time.time() - start_time) * 1000, 2)
                return ClassifyResponse(
                    predicted_category=top.category,
                    confidence=top.confidence,
                    all_scores=scores,
                    latency_ms=latency
                )
            except Exception as e:
                logger.error(f"TF Inference error: {e}. Executing heuristic fallback.")

        # Keyword Heuristic Fallback Engine
        return self._heuristic_classify(text, start_time)

    def _heuristic_classify(self, text: str, start_time: float) -> ClassifyResponse:
        lower_text = text.lower()
        keyword_map = {
            "Artificial Intelligence": ["artificial intelligence", "ai", "agent", "deepmind", "reasoning", "agi"],
            "Machine Learning": ["machine learning", "neural network", "transformer", "gradient", "hyperparameter", "overfitting"],
            "Cyber Security": ["cybersecurity", "security", "vulnerability", "encryption", "firewall", "auth", "threat"],
            "Cloud Computing": ["cloud", "aws", "azure", "kubernetes", "docker", "serverless", "microservices"],
            "Computer Vision": ["computer vision", "image", "yolo", "cnn", "segmentation", "detection", "opencv"],
            "Robotics": ["robotics", "robot", "kinematics", "actuator", "ros", "autonomous"],
            "Natural Language Processing": ["nlp", "language model", "bert", "gpt", "token", "parsing", "translation"],
            "Blockchain": ["blockchain", "smart contract", "ethereum", "crypto", "decentralized", "consensus"],
            "IoT": ["iot", "internet of things", "sensor", "embedded", "mqtt", "edge computing"],
            "Data Science": ["data science", "pandas", "analytics", "dataframe", "statistics", "visualization"]
        }

        counts = {cat: 0 for cat in CATEGORIES}
        for cat, kw_list in keyword_map.items():
            for kw in kw_list:
                counts[cat] += lower_text.count(kw)

        total_matches = sum(counts.values())
        if total_matches == 0:
            # Default to AI if generic technical paper
            predicted = "Artificial Intelligence"
            confidence = 0.50
            scores = [CategoryScore(category=c, confidence=0.10) for c in CATEGORIES]
        else:
            sorted_cats = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            predicted = sorted_cats[0][0]
            confidence = round(sorted_cats[0][1] / total_matches, 4)
            scores = [
                CategoryScore(category=c, confidence=round((counts[c] / total_matches) if total_matches > 0 else 0.1, 4))
                for c in CATEGORIES
            ]

        latency = round((time.time() - start_time) * 1000, 2)
        return ClassifyResponse(
            predicted_category=predicted,
            confidence=max(confidence, 0.45),
            all_scores=scores,
            latency_ms=latency
        )


classifier_inference = DocumentClassifierInference()
