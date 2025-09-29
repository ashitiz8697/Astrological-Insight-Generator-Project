"""
embeddings_stub.py

A simple deterministic "embedding" generator using hashing.
This is a stub to simulate embedding vectors without calling a real model.

- Deterministic: the same text always maps to the same vector.
- Normalized: vectors have unit norm, so cosine similarity is valid.
- Dimension: fixed to DIM (default = 64).

Replace this with real embeddings (e.g., OpenAI, HuggingFace sentence-transformers)
when integrating into production.
"""

import hashlib
import numpy as np

DIM = 64  # embedding dimension


def embed_text(text: str) -> np.ndarray:
    """
    Generate a deterministic pseudo-embedding for the given text.

    Parameters
    ----------
    text : str
        Input text string.

    Returns
    -------
    np.ndarray
        Normalized vector of shape (DIM,) with dtype float32.
    """
    if not isinstance(text, str):
        raise ValueError("embed_text requires a string input")

    # Hash the text into bytes
    h = hashlib.sha256(text.encode("utf-8")).digest()

    # Convert bytes -> numeric array
    arr = np.frombuffer(h, dtype=np.uint8).astype(np.float32)

    # Resize to fixed dimension
    vec = np.resize(arr, DIM)

    # Normalize to unit length
    norm = np.linalg.norm(vec) + 1e-9
    vec = vec / norm

    return vec
