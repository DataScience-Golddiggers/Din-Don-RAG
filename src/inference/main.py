import os
import sys
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import httpx
# LangChain imports
# from langchain_ollama import ChatOllama # Rimosso l'import di Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Add /app to path to import utils
sys.path.append("/app")
from utils.text_preprocessing import TextPreprocessor

# Import new RAG SQL Service
from rag_sql import RAGSQLService

app = FastAPI()

# Configuration
# OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434") # Rimosso l'URL di Ollama
CRAWLER_URL = os.getenv("CRAWLER_URL", "http://crawler:8001")
MODEL_PATH = "/app/models/logistic_regression.pkl"
VECTORIZER_PATH = "/app/models/vectorizer.pkl"

# Model names (non più usati per il percorso text, Ollama ignorato)
# SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "qwen3:0.6b")
# QA_MODEL = os.getenv("QA_MODEL", "qwen3:1.7b")

# Models DTOs
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    relevant: bool
    context_used: bool
    dashboard_data: Optional[Dict[str, Any]] = None # New field for dashboard

# Global variables
classifier = None
vectorizer = None
preprocessor = None
# llm_summary = None # Non usati in quanto Ollama è ignorato e la logica text è disabilitata
# llm_qa = None      # Non usati in quanto Ollama è ignorato e la logica text è disabilitata
rag_sql_service = None

@app.on_event("startup")
async def startup_event():
    global classifier, vectorizer, preprocessor, rag_sql_service # Rimosse llm_summary, llm_qa
    
    # 1. Load Scikit-Learn Models (Classification)
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            classifier = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
            print("Classifier and Vectorizer loaded successfully.")
        else:
            print(f"Models not found at {MODEL_PATH} or {VECTORIZER_PATH}. Classification will be skipped.")
    except Exception as e:
        print(f"Error loading models: {e}")

    # 2. Initialize Preprocessor
    preprocessor = TextPreprocessor(language="italian")
    
    # 3. Inizializzazione RAG SQL Service (che ora usa gemini-3-pro-preview)
    try:
        rag_sql_service = RAGSQLService()
        print("RAG SQL Service initialized with gemini-3-pro-preview.")
    except Exception as e:
        print(f"Error initializing RAG SQL Service: {e}")


def classify_relevance(question: str) -> bool:
    """Returns True if the question is relevant using the loaded classifier."""
    if not classifier or not vectorizer:
        # If classifier is missing, we assume relevant to allow usage.
        return True
        
    cleaned_question = preprocessor.preprocess(question)
    X = vectorizer.transform([cleaned_question])
    prediction = classifier.predict(X)[0]
    return bool(prediction == 1)

# Funzione crawl_content ora commentata/ignorata per il percorso 'text'
# async def crawl_content() -> str:
#     print("Crawling logic bypassed for text queries as per user request.")
#     return ""

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    # 0. Route Query (SQL vs Text)
    route = "text"
    if rag_sql_service:
        route = rag_sql_service.route_query(request.question)
        print(f"Query routing decision: {route}")
    
    if route == "sql" and rag_sql_service:
        # Esegue la catena SQL (usa gemini-3-pro-preview)
        result = rag_sql_service.execute_sql_chain(request.question)
        if "error" in result:
             return AskResponse(
                answer=f"Ho provato a consultare il database ma ho riscontrato un errore: {result['error']}",
                relevant=True,
                context_used=True
            )
        
        return AskResponse(
            answer="Ho generato una dashboard con i dati richiesti.",
            relevant=True,
            context_used=True,
            dashboard_data=result
        )

    # --- PERCORSO RAG TESTUALE (Summarization e Crawling disabilitati) ---
    # La classificazione della rilevanza rimane, ma il resto della pipeline testuale è ignorato.
    try:
        is_relevant = classify_relevance(request.question)
        if not is_relevant:
            return AskResponse(
                answer="La tua domanda non sembra essere pertinente con l\'argomento trattato (Università Politecnica delle Marche).",
                relevant=False,
                context_used=False
            )
    except Exception as e:
        print(f"Classification error: {e}")
        # Procede anche se la classificazione fallisce

    # raw_content = await crawl_content() # La funzione crawl_content è stata disabilitata o bypassata

    # La logica di LangChain per riassunto e QA è disabilitata.
    # truncated_content = raw_content[:15000] 
    # summary_template = ...
    # summarize_chain = ...
    # summary_text = ...
    # qa_template = ...
    # qa_chain = ...
    # answer_text = ...

    return AskResponse(
        answer="Al momento, la funzionalità di ricerca testuale (web crawling, riassunto e QA con LLM) è disabilitata per concentrarsi sulle query SQL. Posso aiutarti con domande che riguardano statistiche e dati accademici (es. 'media voti ingegneria informatica', 'quanti studenti in ingegneria gestionale?').",
        relevant=True,
        context_used=False
    )

@app.get("/health")
def health():
    return {"status": "ok"} # Rimosso 'ollama_url' in quanto Ollama è ignorato
