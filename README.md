# Astrological-Insight-Generator-Project
Create virtualenv and install deps:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Run server:
uvicorn app:app --reload --port 8000

Test with curl:
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" \
-d @sample_input.json
