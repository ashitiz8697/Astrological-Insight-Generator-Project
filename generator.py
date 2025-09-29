# Pseudo-LLM generator — request/response templating + prompt building
import hashlib
from datetime import datetime
from embeddings_stub import embed_text
from vector_store import VectorStore


# small mock corpus used to personalize output
CORPUS = [
("leadership", "Advice on leading teams gracefully."),
("work", "Handling unexpected work pressure."),
("relationships", "Nurture close relationships today."),
("health", "Small health checks make a big difference."),
]


vector_store = VectorStore()
for doc_id, (k, txt) in enumerate(CORPUS):
vector_store.add(doc_id, txt)




def _name_personalization(name: str) -> int:
  # deterministic small score from name
  h = hashlib.sha256(name.encode()).hexdigest()
  return int(h[:8], 16) % 100




def build_prompt(name, zodiac, dt: datetime, place, profile):
  # A simple prompt template — replace with real LLM call later
  score = profile.get("score", 50)
  now_str = dt.strftime("%b %d")
  prompt = (
  f"User: {name}\n"
  f"Birth Place: {place or 'unknown'}\n"
  f"Zodiac: {zodiac}\n"
  f"Date: {now_str}\n"
  f"ProfileScore: {score}\n"
  "Generate a short, positive daily insight (1-2 sentences) that
  is actionable and style-matched to the zodiac.\n"
  )
  return prompt




def generate_insight(name, zodiac, dt: datetime, place, profile: dict) -> str:
  prompt = build_prompt(name, zodiac, dt, place, profile)


# pseudo-LLM: combine zodiac archetype with top retrieved corpus hit
q_emb = embed_text(prompt)
hits = vector_store.similarity_search(q_emb, k=1)
hint = hits[0]['text'] if hits else ''


# template generation logic
base = f"{name}, your {zodiac} qualities will be highlighted today."
if 'work' in hint.lower():
extra = "Your grounded nature will help you handle unexpected work pressure."
elif 'leadership' in hint.lower():
extra = "Your leadership will open doors — step forward with warmth."
elif 'relationships' in hint.lower():
extra = "Small gestures will deepen an important bond."
else:
extra = "Stay present and take small, steady actions."


# personalization tweak
score = profile.get('score', 50)
if score > 75:
extra += " You may find bold action rewarding today."
elif score < 25:
extra += " Prioritize rest and avoid big decisions."


return f"{base} {extra}"
