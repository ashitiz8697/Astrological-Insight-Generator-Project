from typing import List, Tuple
from embeddings_stub import embed_texts, EMBED_DIM
import math
import logging

logger = logging.getLogger("vector_store")
logging.basicConfig(level=logging.INFO)

CORPUS = [
    "Focus on clear priorities today; small steady steps win the day.",
    "A social connection may bring an unexpected opportunity - be open.",
    "Avoid multitasking; dedicate a block of time to your most important work.",
    "Self-care will improve productivity: take short breaks and hydrate.",
    "If decisions feel unclear, sleep on them and revisit with fresh eyes.",
    "Creative energy is strong this week — capture ideas even if small.",
]

_CORPUS_EMBEDDS = embed_texts(CORPUS)

def _dot(a: List[float], b: List[float]) -> float:
    return sum(x*y for x, y in zip(a, b))

def _norm(a: List[float]) -> float:
    s = sum(x*x for x in a)
    return math.sqrt(s) if s > 0 else 1.0

def _cosine(a: List[float], b: List[float]) -> float:
    return _dot(a, b) / (_norm(a) * _norm(b))

def retrieve_similar(query_embedding: List[float], k: int = 3) -> List[str]:
    scores: List[Tuple[int, float]] = []
    for idx, emb in enumerate(_CORPUS_EMBEDDS):
        scores.append((idx, _cosine(query_embedding, emb)))
    scores.sort(key=lambda x: x[1], reverse=True)
    topk = [CORPUS[idx] for idx, _score in scores[:k]]
    logger.debug("Retrieve top-k: %s", topk)
    return topk

if __name__ == "__main__":
    from embeddings_stub import embed_text
    q = "leadership and priorities"
    emb = embed_text(q)
    print(retrieve_similar(emb, k=3))
