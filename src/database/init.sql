-- Attivazione estensione pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- =========================================================
-- 1. SCHEMA ACCADEMICO (Dati strutturati)
-- =========================================================

CREATE TABLE corsi_laurea (
    id SERIAL PRIMARY KEY,
    codice VARCHAR(10) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo_laurea VARCHAR(20) CHECK (tipo_laurea IN ('Triennale', 'Magistrale', 'Ciclo Unico')),
    descrizione TEXT
);

CREATE TABLE studenti (
    id SERIAL PRIMARY KEY,
    matricola VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    data_nascita DATE,
    corso_laurea_id INTEGER REFERENCES corsi_laurea(id),
    anno_iscrizione INTEGER,
    status VARCHAR(20) DEFAULT 'ATTIVO' -- ATTIVO, LAUREATO, RINUNCIATARIO
);

CREATE TABLE insegnamenti (
    id SERIAL PRIMARY KEY,
    codice VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    cfu INTEGER NOT NULL,
    anno_corso INTEGER CHECK (anno_corso BETWEEN 1 AND 6),
    semestre INTEGER CHECK (semestre IN (1, 2)),
    corso_laurea_id INTEGER REFERENCES corsi_laurea(id)
);

CREATE TABLE appelli (
    id SERIAL PRIMARY KEY,
    insegnamento_id INTEGER REFERENCES insegnamenti(id),
    data_appello DATE NOT NULL,
    aula VARCHAR(50),
    note TEXT
);

CREATE TABLE esami (
    id SERIAL PRIMARY KEY,
    studente_id INTEGER REFERENCES studenti(id),
    appello_id INTEGER REFERENCES appelli(id),
    voto INTEGER CHECK (voto >= 0 AND voto <= 30),
    lode BOOLEAN DEFAULT FALSE,
    stato VARCHAR(20) DEFAULT 'SUPERATO', -- SUPERATO, RESPINTO, ASSENTE
    data_registrazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_esame_appello UNIQUE (studente_id, appello_id)
);

-- =========================================================
-- 2. SUPPORTO RAG & AI (Dati vettoriali e Metadata)
-- =========================================================

-- Tabella per i documenti testuali (PDF bandi, pagine web, ecc.)
CREATE TABLE rag_documents (
    id SERIAL PRIMARY KEY,
    source_url VARCHAR(255),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(768), -- Dimensione standard per modelli come nomic-embed-text o simili
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per descrivere lo schema database all'AI (Semantic Router)
CREATE TABLE db_schema_info (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL, -- Descrizione semantica (es. "Contiene i voti degli studenti")
    ddl_snippet TEXT,          -- La definizione SQL della tabella
    embedding vector(768)      -- Embedding della descrizione
);

-- Storico delle dashboard generate per il context-aware refinement
CREATE TABLE dashboard_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_query TEXT NOT NULL,
    generated_sql TEXT,
    generated_ejs TEXT,
    context_json JSONB, -- I dati grezzi ritornati dalla query SQL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Utente readonly per l'AI (da usare nel servizio Python per sicurezza)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'ai_readonly') THEN

      CREATE ROLE ai_readonly WITH LOGIN PASSWORD 'ai_readonly_password';
      GRANT CONNECT ON DATABASE postgres TO ai_readonly;
      GRANT USAGE ON SCHEMA public TO ai_readonly;
      GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_readonly;
      ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ai_readonly;
   END IF;
END
$do$;
