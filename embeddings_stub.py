# Simple deterministic "embedding" using hashing -> numeric vector
import hashlib
import numpy as np


DIM = 64


def embed_text(text: str):
# deterministic pseudo-embedding
h = hashlib.sha256(text.encode()).digest()
arr = np.frombuffer(h, dtype=np.uint8).astype(np.float32)
# expand or tile to DIM
vec = np.resize(arr, DIM)
# normalize
vec = vec / (np.linalg.norm(vec) + 1e-9)
return vec
