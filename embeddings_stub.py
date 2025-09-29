from typing import List
import hashlib
import struct
import math

EMBED_DIM = 64

def _float_from_bytes(b: bytes) -> float:
    if len(b) < 4:
        b = b.ljust(4, b'\0')
    i = struct.unpack(">I", b[:4])[0]
    return ((i / 0xFFFFFFFF) * 2.0) - 1.0

def embed_texts(texts: List[str]) -> List[List[float]]:
    out = []
    for t in texts:
        h = hashlib.md5(t.encode("utf-8")).digest()
        vec = []
        for i in range(EMBED_DIM):
            start = (i * 3) % len(h)
            f = _float_from_bytes(h[start:start+4])
            vec.append(f)
        norm = math.sqrt(sum(x*x for x in vec))
        if norm == 0:
            norm = 1.0
        vec = [x / norm for x in vec]
        out.append(vec)
    return out

def embed_text(text: str) -> List[float]:
    return embed_texts([text])[0]

if __name__ == "__main__":
    print(len(embed_texts(["hello world"])[0]))
