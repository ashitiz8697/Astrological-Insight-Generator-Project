# Astrological-Insight-Generator-Project
# Astrological Insight Generator

A minimal, modular service that takes birth details and returns a personalized daily astrological insight. Built with FastAPI and simple, replaceable stubs for LLMs, embeddings, translation, and vector store so real services (OpenAI / HF / Panchang / FAISS) can be plugged in later.

## Features
- Infer zodiac sign from birth date (simple date ranges)
- Pseudo-LLM / prompt builder that returns human-friendly daily insight
- Simple personalization via deterministic per-user profile cache
- In-memory vector-store & embedding stubs for retrieval-augmented personalization
- Translation stub to enable Hindi/multilingual output
- REST API (POST /predict) returns JSON
- Tests for zodiac logic
- Extensible: easy to swap stubs with real LLMs or Panchang API

## Repo structure
astrological_insight_generator/
├── README.md
├── requirements.txt
├── app.py
├── zodiac.py
├── generator.py
├── embeddings_stub.py
├── vector_store.py
├── cache.py
├── translate_stub.py
├── utils.py
├── sample_input.json
├── Dockerfile
├── .github/
│ └── workflows/ci.yml
├── LICENSE
└── tests/
└── test_zodiac.py


## Quick start (local)
1. Create virtual env and install:
```bash
python -m venv .venv
source .venv/bin/activate       # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
2. Run Server 
uvicorn app:app --reload --port 8000

3. Test with Curl 
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_input.json

Expected Response
{
  "zodiac": "Leo",
  "insight": "Ritika, your Leo qualities will be highlighted today. Your innate leadership and warmth will shine — step forward with warmth.",
  "language": "en"
}

4. Run Tests 
pytest -q

Docker
Build and Run 
docker build -t astro-insight:latest .
docker run -p 8000:8000 astro-insight:latest
