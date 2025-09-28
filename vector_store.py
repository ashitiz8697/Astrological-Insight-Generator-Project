# Tiny in-memory vector store with cosine similarity
import numpy as np
from collections import defaultdict


class VectorStore:
def __init__(self):
self.store = {}


def add(self, doc_id, text, embedding=None):
if embedding is None:
from embeddings_stub import embed_text
embedding = embed_text(text)
self.store[doc_id] = {"text": text, "emb": embedding}


def similarity_search(self, query_emb, k=3):
scores = []
for doc_id, rec in self.store.items():
dot = float(np.dot(query_emb, rec['emb']))
scores.append((dot, rec['text'], doc_id))
scores.sort(reverse=True)
return [{"score": s, "text": t, "id": i} for s,t,i in scores[:k]]
