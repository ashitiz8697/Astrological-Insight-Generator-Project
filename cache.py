# Simple profile cache for personalization. Uses LRU-like eviction.
from collections import OrderedDict
import hashlib


class ProfileCache:
def __init__(self, max_size=1000):
self.max_size = max_size
self._store = OrderedDict()


def _make_profile(self, name):
# deterministic pseudo-profile
h = hashlib.md5(name.encode()).hexdigest()
score = int(h[:4], 16) % 100
return {"name": name, "score": score}


def get_or_create_profile(self, name: str):
if name in self._store:
val = self._store.pop(name)
self._store[name] = val
return val
profile = self._make_profile(name)
if len(self._store) >= self.max_size:
self._store.popitem(last=False)
self._store[name] = profile
return profile
