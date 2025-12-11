import os
import sys
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import httpx
# LangChain imports
from langchain_ollama import ChatOllama 
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
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434") # Default to host for Mac/Windows
CRAWLER_URL = os.getenv("CRAWLER_URL", "http://crawler:8001")
MODEL_PATH = "/app/models/logistic_regression.pkl"
VECTORIZER_PATH = "/app/models/vectorizer.pkl"

# Model names
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "qwen3:0.6b")
QA_MODEL = os.getenv("QA_MODEL", "qwen3:1.7b")

# Models DTOs
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    relevant: bool
    context_used: bool
    dashboard_data: Optional[Dict[str, Any]] = None

# Global variables
classifier = None
vectorizer = None
preprocessor = None
llm_summary = None 
llm_qa = None      
rag_sql_service = None

@app.on_event("startup")
async def startup_event():
    global classifier, vectorizer, preprocessor, llm_summary, llm_qa, rag_sql_service
    
    # 1. Load Scikit-Learn Models (Classification)
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            classifier = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
            print("Classifier and Vectorizer loaded successfully.")
        else:
            print(f"Models not found. Classification will be skipped.")
    except Exception as e:
        print(f"Error loading models: {e}")

    # 2. Initialize Preprocessor
    preprocessor = TextPreprocessor(language="italian")
    
    # 3. Initialize LangChain Ollama Chat Models (For Legacy RAG)
    try:
        print(f"Initializing Ollama with URL: {OLLAMA_URL}")
        llm_summary = ChatOllama(
            base_url=OLLAMA_URL,
            model=SUMMARY_MODEL,
            temperature=0.2
        )
        llm_qa = ChatOllama(
            base_url=OLLAMA_URL,
            model=QA_MODEL,
            temperature=0.7
        )
        print("LangChain Ollama instances initialized for Legacy RAG.")
    except Exception as e:
        print(f"Error initializing LangChain Ollama: {e}")

    # 4. Initialize RAG SQL Service (Gemini)
    try:
        rag_sql_service = RAGSQLService()
        print("RAG SQL Service initialized with gemini-2.5-flash.")
    except Exception as e:
        print(f"Error initializing RAG SQL Service: {e}")


def classify_relevance(question: str) -> bool:
    if not classifier or not vectorizer:
        return True
    cleaned_question = preprocessor.preprocess(question)
    X = vectorizer.transform([cleaned_question])
    prediction = classifier.predict(X)[0]
    return bool(prediction == 1)

async def crawl_content() -> str:
    """Fetches content from the crawler service asynchronously."""
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            print(f"Richiesta al crawler inviata a {CRAWLER_URL}/crawl...")
            response = await client.post(f"{CRAWLER_URL}/crawl", json={"urls": []})
            
            if response.status_code != 200:
                print(f"Crawler error: {response.status_code}")
                return ""
                
            crawl_data = response.json()
            results = crawl_data.get("results") or []
            
            full_text = ""
            for res in results:
                if res.get("success"):
                    full_text += str(res.get("content", "")) + "\n\n"
            
            return full_text
        except Exception as e:
            print(f"Crawler request failed: {e}")
            return ""

# --- NEW LEGACY ENDPOINT (Ollama + Crawler) ---
@app.post("/ask_legacy", response_model=AskResponse)
async def ask_legacy(request: AskRequest):
    # 1. Classification (Non-blocking mode due to strict classifier)
    try:
        is_relevant = classify_relevance(request.question)
        if not is_relevant:
            print(f"WARN: Legacy classifier marked irrelevant: '{request.question}'. Proceeding anyway.")
    except Exception as e:
        print(f"WARN: Classification error: {e}")

    # 2. Retrieval
    raw_content = await crawl_content()
    if not raw_content:
        return AskResponse(answer="Impossibile recuperare info dal crawler.", relevant=True, context_used=False)

    # 3. LangChain Processing (Ollama)
    if not llm_summary or not llm_qa:
        return AskResponse(answer="Servizio Ollama non disponibile.", relevant=True, context_used=False)

    truncated_content = raw_content[:15000]
    
    # Summarize
    summary_chain = PromptTemplate.from_template(
        "Riassumi il seguente testo accademico:\n{text}\nRiassunto:"
    ) | llm_summary | StrOutputParser()
    
    try:
        summary_text = await summary_chain.ainvoke({"text": truncated_content})
    except Exception as e:
        print(f"Legacy Summary Error: {e}")
        summary_text = truncated_content[:3000]

    # QA
    qa_chain = PromptTemplate.from_template(
        "Contesto:\n{context}\n\nDomanda: {question}\n\nRisposta:"
    ) | llm_qa | StrOutputParser()

    try:
        answer_text = await qa_chain.ainvoke({"context": summary_text, "question": request.question})
    except Exception as e:
        answer_text = f"Errore generazione risposta legacy: {e}"

    return AskResponse(answer=answer_text, relevant=True, context_used=True)


# --- CURRENT GEMINI/SQL ENDPOINT ---
@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    # 0. Route Query (SQL vs Text)
    route = "text"
    if rag_sql_service:
        route = rag_sql_service.route_query(request.question)
        print(f"Query routing decision: {route}")
    
    if route == "sql" and rag_sql_service:
        # Esegue la catena SQL (usa gemini-2.5-flash)
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

    # Fallback Text per Main Page (disabilitato come richiesto)
    return AskResponse(
        answer="La ricerca testuale su questa pagina è disabilitata. Usa la pagina 'Legacy Chat' per usare il Crawler e Ollama.",
        relevant=True,
        context_used=False
    )

@app.get("/health")
def health():
    return {"status": "ok"}
