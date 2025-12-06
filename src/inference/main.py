from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import joblib
import requests
import json
from typing import Optional
import sys

# Add /app to path to import utils
sys.path.append("/app")

from utils.text_preprocessing import TextPreprocessor

app = FastAPI()

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
CRAWLER_URL = os.getenv("CRAWLER_URL", "http://crawler:8001")
MODEL_PATH = "/app/models/logistic_regression.pkl"
VECTORIZER_PATH = "/app/models/vectorizer.pkl"

# Models
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    relevant: bool
    context_used: bool

# Global variables for loaded models
classifier = None
vectorizer = None
preprocessor = None

@app.on_event("startup")
async def startup_event():
    global classifier, vectorizer, preprocessor
    
    # Load NLP models
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            classifier = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
            print("Classifier and Vectorizer loaded successfully.")
        else:
            print(f"Models not found at {MODEL_PATH} or {VECTORIZER_PATH}. Inference will fail.")
    except Exception as e:
        print(f"Error loading models: {e}")

    # Initialize preprocessor
    preprocessor = TextPreprocessor(language="italian")
    
    # Pull Ollama models (fire and forget or wait?)
    # We'll try to pull them. This might take time.
    # Ideally this should be done in the Ollama container entrypoint or manually.
    # We will assume they are present or will be pulled on first use (Ollama does this).

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    global classifier, vectorizer
    
    if not classifier or not vectorizer:
        # Fallback if models are missing: assume relevant for testing? 
        # Or return error. User wants classifier.
        # Let's return error to force training.
        raise HTTPException(status_code=503, detail="Classifier models not loaded. Please train the model first.")

    # 1. Preprocess Question
    # We need to preprocess just like training.
    # TextPreprocessor.preprocess returns a string.
    cleaned_question = preprocessor.preprocess(request.question)
    
    # 2. Vectorize
    # vectorizer.transform expects an iterable
    X = vectorizer.transform([cleaned_question])
    
    # 3. Classify
    prediction = classifier.predict(X)[0] # 0 or 1
    
    if prediction == 0:
        return AskResponse(
            answer="La tua domanda non sembra essere pertinente con l'argomento trattato (Università Politecnica delle Marche).",
            relevant=False,
            context_used=False
        )
    
    # 4. Crawl
    try:
        crawl_response = requests.post(f"{CRAWLER_URL}/crawl", json={"urls": []}) # Empty list uses hardcoded defaults
        crawl_data = crawl_response.json()
        results = crawl_data.get("results", [])
    except Exception as e:
        print(f"Crawler error: {e}")
        return AskResponse(answer="Si è verificato un errore nel recupero delle informazioni.", relevant=True, context_used=False)

    # 5. Aggregate Content
    full_text = ""
    for res in results:
        if res.get("success"):
            full_text += res.get("content", "") + "\n\n"
            
    if not full_text:
        return AskResponse(answer="Non sono riuscito a trovare informazioni aggiornate.", relevant=True, context_used=False)

    # 6. Summarize (using qwen3:0.6b)
    # Truncate full_text to avoid context limit issues if too large
    truncated_text = full_text[:10000] 
    
    summary_prompt = f"Riassumi il seguente testo rimuovendo le parti inutili e mantenendo le informazioni chiave sull'Università:\n\n{truncated_text}"
    
    try:
        summary_res = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": "qwen3:0.6b",
            "prompt": summary_prompt,
            "stream": False
        })
        summary = summary_res.json().get("response", "")
    except Exception as e:
        print(f"Summarization error: {e}")
        summary = truncated_text[:2000] # Fallback to raw text

    # 7. Answer (using qwen3:1.7b)
    qa_prompt = f"Contesto:\n{summary}\n\nDomanda: {request.question}\n\nRispondi alla domanda basandoti solo sul contesto fornito. Se non trovi la risposta nel contesto, dillo."
    
    try:
        answer_res = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": "qwen3:1.7b",
            "prompt": qa_prompt,
            "stream": False
        })
        answer = answer_res.json().get("response", "")
    except Exception as e:
        print(f"QA error: {e}")
        answer = "Si è verificato un errore nella generazione della risposta."

    return AskResponse(
        answer=answer,
        relevant=True,
        context_used=True
    )

@app.get("/health")
def health():
    return {"status": "ok"}
