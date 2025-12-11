import os
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

class RAGSQLService:
    def __init__(self):
        try:
            self.engine = create_engine(DATABASE_URL)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection initialized.")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.engine = None
        
        # Initialize LLM (Prefer Gemini, fallback to Ollama)
        if GEMINI_API_KEY:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=GEMINI_API_KEY,
                temperature=0.1
            )
            self.llm_creative = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=GEMINI_API_KEY,
                temperature=0.7
            )
            logger.info("Initialized Gemini API")
        else:
            self.llm = ChatOllama(base_url=OLLAMA_URL, model="qwen3:1.7b", temperature=0.1)
            self.llm_creative = ChatOllama(base_url=OLLAMA_URL, model="qwen3:1.7b", temperature=0.7)
            logger.warning("Gemini API Key missing. Fallback to Ollama.")

        # --- Prompts ---
        
        # 1. Router Prompt
        self.router_prompt = ChatPromptTemplate.from_template(
            """Analizza la domanda dell'utente.
            Se la domanda riguarda:
            - Dati strutturati (voti, medie, conteggi studenti, iscritti).
            - Statistiche, trend, andamenti.
            - Richieste esplicite di visualizzazione: "dashboard", "grafico", "plot", "chart".
            - Informazioni su entità specifiche del database: Studenti, Corsi di Laurea, Esami, Appelli.
            ... allora la destinazione è "sql".

            Se la domanda riguarda:
            - Informazioni descrittive generali (chi siamo, contatti, storia).
            - Regolamenti testuali, bandi, news.
            ... allora la destinazione è "text".
            
            Domanda: {question}
            
            Rispondi ESCLUSIVAMENTE con un oggetto JSON: {{"destination": "sql"}} oppure {{"destination": "text"}}
            """
        )
        
        # 2. SQL Generation Prompt
        self.sql_prompt = ChatPromptTemplate.from_template(
            """Sei un esperto SQL PostgreSQL. Genera una query SQL per rispondere alla domanda.
            Usa SOLO le seguenti tabelle: studenti, corsi_laurea, insegnamenti, appelli, esami.
            
            Schema rilevante:
            - studenti(id, matricola, nome, cognome, corso_laurea_id, anno_iscrizione, status)
            - corsi_laurea(id, nome, tipo_laurea)
            - insegnamenti(id, nome, cfu, anno_corso, corso_laurea_id)
            - esami(id, studente_id, appello_id, voto, lode, stato)
            - appelli(id, insegnamento_id, data_appello)

            Regole:
            - Non usare tabelle non elencate.
            - Usa JOIN corrette.
            - Se la domanda chiede medie, usa AVG().
            - Se chiede conteggi, usa COUNT().
            - Restituisci SOLO la stringa SQL valida, senza markdown, senza premesse.

            Domanda: {question}
            SQL:"""
        )

        # 3. Visualization Prompt
        self.viz_prompt = ChatPromptTemplate.from_template(
            """Agisci come Frontend Developer. Hai i seguenti dati JSON derivanti da una query SQL:
            {data}
            
            La domanda originale era: "{question}"
            
            Genera una configurazione Chart.js (type, data, options) in formato JSON valida per visualizzare questi dati.
            Scegli il tipo di grafico migliore (bar, pie, line) in base ai dati.
            Assicurati che il JSON sia valido e parsabile. Non includere commenti o markdown.
            
            JSON Config:"""
        )

    def route_query(self, question: str) -> str:
        chain = self.router_prompt | self.llm | JsonOutputParser()
        try:
            res = chain.invoke({"question": question})
            return res.get("destination", "text")
        except Exception as e:
            logger.error(f"Routing error: {e}")
            return "text"

    def save_dashboard_history(self, question: str, sql: str, data: List[Dict], viz_config: Dict):
        if not self.engine: return
        try:
            with self.engine.connect() as conn:
                # Use simple parameterized query. data and viz_config dumped to json string.
                import json
                conn.execute(
                    text("""
                        INSERT INTO dashboard_history (user_query, generated_sql, context_json, generated_ejs)
                        VALUES (:q, :s, :d, :v)
                    """),
                    {
                        "q": question,
                        "s": sql,
                        "d": json.dumps(data, default=str),
                        "v": json.dumps(viz_config)
                    }
                )
                conn.commit()
                logger.info("Dashboard history saved.")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def execute_sql_chain(self, question: str) -> Dict[str, Any]:
        if not self.engine:
            return {"error": "Database not available"}

        # 1. Generate SQL
        sql_chain = self.sql_prompt | self.llm | StrOutputParser()
        try:
            generated_sql = sql_chain.invoke({"question": question})
            # Clean SQL
            generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
            logger.info(f"Generated SQL: {generated_sql}")
        except Exception as e:
             logger.error(f"SQL Gen error: {e}")
             return {"error": "Failed to generate SQL"}

        # 2. Execute SQL
        result_data = []
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(generated_sql))
                keys = result.keys()
                # Serialize dates/decimals manually if needed, usually simple types are fine
                result_data = []
                for row in result.fetchall():
                    row_dict = {}
                    for k, v in zip(keys, row):
                        row_dict[k] = str(v) # Convert everything to string for safety in JSON
                    result_data.append(row_dict)
        except Exception as e:
            logger.error(f"SQL Execution error: {e}")
            return {"error": str(e), "sql": generated_sql}

        # 3. Generate Viz Config
        if result_data:
            viz_chain = self.viz_prompt | self.llm_creative | JsonOutputParser()
            try:
                # Limit data passed to LLM
                viz_config = viz_chain.invoke({"data": str(result_data[:20]), "question": question})
            except Exception as e:
                logger.error(f"Viz generation error: {e}")
                viz_config = {}
        else:
            viz_config = {}

        # 4. Save History
        self.save_dashboard_history(question, generated_sql, result_data, viz_config)

        return {
            "type": "dashboard",
            "sql": generated_sql,
            "data": result_data,
            "chart_config": viz_config
        }
