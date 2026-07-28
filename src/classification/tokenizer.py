import json
import os
import re
from typing import Dict, List, Tuple
from config.settings import settings
from config.logger import logger

CATEGORIES: List[str] = [
    "Artificial Intelligence",
    "Machine Learning",
    "Cyber Security",
    "Cloud Computing",
    "Computer Vision",
    "Robotics",
    "Natural Language Processing",
    "Blockchain",
    "IoT",
    "Data Science"
]


class TextTokenizer:
    """Vocabulary and Tokenizer Manager for TensorFlow Classifier."""

    def __init__(self, num_words: int = 10000, max_len: int = 200):
        self.num_words = num_words
        self.max_len = max_len
        self.word_index: Dict[str, int] = {"<PAD>": 0, "<UNK>": 1}
        self.category2idx: Dict[str, int] = {cat: idx for idx, cat in enumerate(CATEGORIES)}
        self.idx2category: Dict[int, str] = {idx: cat for idx, cat in enumerate(CATEGORIES)}

    def clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\d+", " ", text)
        return " ".join(text.split())

    def fit_on_texts(self, texts: List[str]) -> None:
        word_counts: Dict[str, int] = {}
        for text in texts:
            cleaned = self.clean_text(text)
            for word in cleaned.split():
                word_counts[word] = word_counts.get(word, 0) + 1

        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        for idx, (word, _) in enumerate(sorted_words[: self.num_words - 2]):
            self.word_index[word] = idx + 2

    def texts_to_sequences(self, texts: List[str]) -> List[List[int]]:
        sequences = []
        for text in texts:
            cleaned = self.clean_text(text)
            seq = [self.word_index.get(w, 1) for w in cleaned.split()]
            sequences.append(seq)
        return sequences

    def pad_sequences(self, sequences: List[List[int]]) -> List[List[int]]:
        padded = []
        for seq in sequences:
            if len(seq) >= self.max_len:
                padded.append(seq[: self.max_len])
            else:
                padded.append(seq + [0] * (self.max_len - len(seq)))
        return padded

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            "word_index": self.word_index,
            "num_words": self.num_words,
            "max_len": self.max_len,
            "category2idx": self.category2idx
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved tokenizer to {filepath}")

    def load(self, filepath: str) -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.word_index = data["word_index"]
            self.num_words = data["num_words"]
            self.max_len = data["max_len"]
            self.category2idx = data["category2idx"]
            self.idx2category = {int(v): k for k, v in self.category2idx.items()}
            return True
        except Exception as e:
            logger.error(f"Failed loading tokenizer from {filepath}: {e}")
            return False


text_tokenizer = TextTokenizer()
