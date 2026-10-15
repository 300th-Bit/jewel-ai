# Jewel-AI: AI design and sales assistant for independent jewellers

Free stack: Gemini API (free key) for chat and trends, Pollinations for renders, SQLite for storage, FastAPI + one HTML page.

## Run locally (or in Cloud Shell)
    pip install -r requirements.txt
    export GEMINI_API_KEY=your-free-key      # Windows PowerShell: $env:GEMINI_API_KEY="..."
    uvicorn app.main:app --port 8080
    pytest

- Customer app:   http://localhost:8080
- Store dashboard: http://localhost:8080/dashboard.html
- API docs:       http://localhost:8080/docs

## Deploy to Cloud Run (needs a billing-enabled project; light usage fits the free tier)
    gcloud run deploy jewel-ai --source . --region asia-south1 --allow-unauthenticated \
      --max-instances 1 --set-env-vars GEMINI_API_KEY=your-key

`--max-instances 1` keeps one instance so saved requests are consistent. Cloud Run storage is
temporary: SQLite data resets on restart (demo data is re-seeded). For a real store, swap
app/store.py for Firestore.

## Placeholders to replace before the demo
Gold rate, stone prices, making % and GST in app/pricing.py.
