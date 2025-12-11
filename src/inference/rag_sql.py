import os
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
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
        
        # Initialize LLM (Prefer Gemini, fallback to Ollama if needed but strictly using gemini-2.5-flash as requested)
        if GEMINI_API_KEY:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=GEMINI_API_KEY,
                temperature=0.1
            )
            self.llm_creative = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=GEMINI_API_KEY,
                temperature=0.7
            )
            logger.info("Initialized Gemini API (gemini-2.5-flash)")
        else:
             # Fallback logic removed/simplified as we focus on Gemini
             logger.warning("Gemini API Key missing.")
             self.llm = None
             self.llm_creative = None

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

        # 1.5 Planner Prompt (New)
        self.planner_prompt = ChatPromptTemplate.from_template(
            """Sei un Data Analyst senior. L'utente vuole una dashboard o delle statistiche.
            Analizza la richiesta: "{question}"
            
            Scomponila in una lista di massimo 3 domande specifiche e distinte che possono essere risposte con query SQL separate.
            Se la richiesta è semplice o specifica, genera una sola domanda.
            Se chiede una "dashboard" o "panoramica", genera 2 o 3 aspetti diversi (es. trend temporale, distribuzione per categoria, ecc).
            
            Esempio Input: "Mostrami l'andamento degli studenti"
            Esempio Output: ["Quanti studenti si sono iscritti per anno?", "Qual è la distribuzione degli studenti per corso di laurea?", "Qual è la media voti complessiva?"]
            
            Rispondi ESCLUSIVAMENTE con un JSON Array di stringhe.
            """
        )
        
        # 2. SQL Generation Prompt
        self.sql_prompt = ChatPromptTemplate.from_template(
            """Sei un esperto SQL PostgreSQL. Genera una query SQL per rispondere alla domanda.
            Usa SOLO le seguenti tabelle: studenti, corsi_laurea, insegnamenti, appelli, esami.
            
            Schema rilevante con Tipi di Dato:
            - studenti(id INT, matricola TEXT, nome TEXT, cognome TEXT, corso_laurea_id INT, anno_iscrizione INT, status TEXT)
              * NOTA: 'anno_iscrizione' è un INTERO (es. 2023). NON usare EXTRACT() su di esso. Usalo direttamente (es. anno_iscrizione = 2024).
            - corsi_laurea(id INT, nome TEXT, tipo_laurea TEXT)
            - insegnamenti(id INT, nome TEXT, cfu INT, anno_corso INT, corso_laurea_id INT)
            - esami(id INT, studente_id INT, appello_id INT, voto INT, lode BOOLEAN, stato TEXT)
              * NOTA: 'voto' è intero. 'stato' può essere 'SUPERATO', 'RESPINTO'.
            - appelli(id INT, insegnamento_id INT, data_appello DATE)
              * NOTA: 'data_appello' è DATE. Qui PUOI usare EXTRACT(YEAR FROM data_appello).

            Regole:
            - Non usare tabelle non elencate.
            - Usa JOIN corrette.
            - Se la domanda chiede medie, usa AVG().
            - Se chiede conteggi, usa COUNT().
            - IMPORTANTE: Non usare EXTRACT(YEAR...) su 'anno_iscrizione' o 'anno_corso', sono già interi!
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
            IMPORTANTE: Restituisci SOLO il JSON grezzo. NON usare blocchi markdown (```json). NON aggiungere commenti.
            
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

    def execute_single_sql_query(self, question: str) -> Optional[Dict]:
        """Helper to execute a single question flow"""
        # 1. Generate SQL
        sql_chain = self.sql_prompt | self.llm | StrOutputParser()
        try:
            generated_sql = sql_chain.invoke({"question": question})
            generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
            logger.info(f"Generated SQL for '{question}': {generated_sql}")
        except Exception as e:
             logger.error(f"SQL Gen error: {e}")
             return None

        # 2. Execute SQL
        result_data = []
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(generated_sql))
                keys = result.keys()
                for row in result.fetchall():
                    row_dict = {}
                    for k, v in zip(keys, row):
                        row_dict[k] = str(v)
                    result_data.append(row_dict)
        except Exception as e:
            logger.error(f"SQL Execution error: {e}")
            return {"error": str(e), "sql": generated_sql}

        # 3. Generate Viz Config (Robust Parsing)
        viz_config = {}
        if result_data:
            # Use StrOutputParser instead of JsonOutputParser to handle markdown manually
            viz_chain = self.viz_prompt | self.llm_creative | StrOutputParser()
            try:
                raw_viz = viz_chain.invoke({"data": str(result_data[:20]), "question": question})
                # Clean Markdown
                cleaned_viz = raw_viz.replace("```json", "").replace("```", "").strip()
                viz_config = json.loads(cleaned_viz)
            except Exception as e:
                logger.error(f"Viz generation error: {e}. Raw output was: {raw_viz if 'raw_viz' in locals() else 'N/A'}")
                # Fallback: empty config, frontend should handle this or show data table
                viz_config = {}

        # 4. Save History
        self.save_dashboard_history(question, generated_sql, result_data, viz_config)

        return {
            "sql": generated_sql,
            "data": result_data,
            "chart_config": viz_config,
            "title": question
        }

    def execute_sql_chain(self, main_question: str) -> Dict[str, Any]:
        if not self.engine:
            return {"error": "Database not available"}

        # 1. Plan: Decompose question
        planner_chain = self.planner_prompt | self.llm | JsonOutputParser()
        try:
            questions_list = planner_chain.invoke({"question": main_question})
            if not isinstance(questions_list, list):
                questions_list = [main_question]
            logger.info(f"Dashboard Plan: {questions_list}")
        except Exception as e:
            logger.error(f"Planning error: {e}. Fallback to single query.")
            questions_list = [main_question]

        # Limit to 3 charts to avoid timeout/quota
        questions_list = questions_list[:3]

        dashboard_items = []
        for q in questions_list:
            item = self.execute_single_sql_query(q)
            # Check if item is valid and not an error response
            if item and not item.get("error"):
                dashboard_items.append(item)
            elif item and item.get("error"):
                 logger.warning(f"Error in sub-query '{q}': {item['error']}")
        
        if not dashboard_items:
             return {"error": "Failed to generate any charts."}

        return {
            "type": "multi-dashboard",
            "charts": dashboard_items
        }