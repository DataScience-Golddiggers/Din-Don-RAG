# 📘 Documentazione del Progetto ALLMond

Benvenuto nella documentazione ufficiale di **ALLMond**, un assistente web intelligente progettato per rispondere a domande relative all'Università Politecnica delle Marche (UnivPM).

## 🌟 Panoramica

ALLMond è una soluzione "RAG" (Retrieval-Augmented Generation) containerizzata che combina:
1.  **Machine Learning Classico**: Per filtrare le domande non pertinenti.
2.  **Web Crawling**: Per recuperare informazioni aggiornate dal sito dell'università.
3.  **Small Language Models (SLM)**: Per sintetizzare le informazioni e generare risposte precise, girando interamente in locale (o su server privati) per garantire privacy ed efficienza.

---

## ✨ Funzionalità Chiave

*   **💬 Chat Intelligente**: Interfaccia conversazionale per porre domande sull'università.
*   **🔍 Ricerca in Tempo Reale**: Il sistema naviga sul sito UnivPM per trovare le informazioni più recenti.
*   **🛡️ Filtro di Pertinenza**: Un classificatore intelligente blocca le domande fuori tema (es. "Qual è la capitale della Francia?") per risparmiare risorse.
*   **🚀 Esecuzione Locale**: Utilizza Ollama per far girare i modelli di intelligenza artificiale senza dipendere da API costose (come OpenAI).
*   **🐳 Architettura a Microservizi**: Facile da installare e scalare grazie a Docker.

---

## 🛠️ Guida all'Installazione

### Prerequisiti

Assicurati di avere installato:
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   [Ollama](https://ollama.com/) (Consigliato per performance ottimali su Mac/Linux)
*   [Python 3.10+](https://www.python.org/) (Opzionale, solo per sviluppo locale)

### 1. Configurazione Iniziale

Clona il repository e configura le variabili d'ambiente:

```bash
# Copia il file di esempio
cp .env.example .env
```

Modifica il file `.env`. Se usi Ollama installato sul tuo computer (host), imposta:
```dotenv
OLLAMA_URL=http://host.docker.internal:11434
```

### 2. Configurazione Ollama (Solo per esecuzione locale)

Per permettere ai container Docker di comunicare con il tuo Ollama locale:

1.  Ferma l'applicazione Ollama se è in esecuzione.
2.  Esegui questo comando nel terminale (dalla radice del progetto):

```bash
export OLLAMA_HOST=0.0.0.0
export OLLAMA_MODELS=$(pwd)/models/models
ollama serve
```
> **Nota**: Questo comando fa sì che Ollama ascolti su tutte le interfacce di rete e salvi i modelli nella cartella del progetto.

### 3. Avvio dell'Applicazione

Avvia tutti i servizi con Docker Compose:

```bash
docker-compose up --build
```

L'applicazione sarà disponibile su: **[http://localhost:3000](http://localhost:3000)**

---

## 📖 Guida all'Uso

1.  Apri il browser e vai su `http://localhost:3000`.
2.  Clicca su **"Inizia a chattare"** o vai alla pagina di Chat.
3.  Scrivi una domanda relativa all'UnivPM (es. *"Quali sono i corsi di ingegneria informatica?"*).
4.  Il sistema:
    *   Verificherà se la domanda è pertinente.
    *   Cercherà informazioni sul sito UnivPM.
    *   Ti fornirà una risposta generata dall'IA basata sui dati trovati.

---

## 👨‍💻 Guida per lo Sviluppatore

### Struttura del Progetto

*   `src/application`: Frontend e Backend Web (Node.js/Express).
*   `src/inference`: Servizio Python che gestisce la logica IA (Classificazione + RAG).
*   `src/crawler`: Servizio Python per scaricare pagine web.
*   `data/`: Contiene i dataset per l'addestramento.
*   `scripts/`: Script utili per la gestione del progetto.

### Generazione Dati e Addestramento

Se vuoi migliorare il classificatore di pertinenza:

1.  **Genera nuovi dati sintetici**:
    ```bash
    python scripts/generate_dataset.py
    ```
    Questo creerà un file CSV in `data/raw/training_dataset.csv`.

2.  **Addestra il modello**:
    Puoi farlo direttamente tramite Docker (senza installare Python localmente):
    ```bash
    docker-compose exec ai-service python scripts/train_pipeline.py \
      --input-file "data/raw/training_dataset.csv" \
      --text-column "question" \
      --label-column "label" \
      --model logistic_regression
    ```

### Modifica dei Prompt

I prompt utilizzati dall'IA si trovano in `src/inference/main.py` (o nei file di configurazione se estratti). Puoi modificarli per cambiare la "personalità" dell'assistente o il modo in cui riassume i testi.

---

## ❓ Risoluzione Problemi

**Problema: "Ollama connection refused"**
*   Assicurati che Ollama sia in esecuzione (`ollama serve`).
*   Verifica che `OLLAMA_HOST` sia impostato su `0.0.0.0`.
*   Controlla che nel file `.env` `OLLAMA_URL` sia corretto (`http://host.docker.internal:11434` per Docker su Mac/Windows).

**Problema: Risposte lente**
*   L'inferenza IA richiede risorse. Se usi Docker su Mac, assicurati di aver allocato abbastanza RAM e CPU a Docker Desktop, oppure usa Ollama nativo (fuori da Docker) come consigliato.

**Problema: Il crawler non trova informazioni**
*   Il sito dell'università potrebbe essere cambiato o irraggiungibile. Controlla i log del servizio crawler: `docker-compose logs crawler`.

---

Per dettagli tecnici approfonditi sull'architettura, consulta il [Report Tecnico](technical_report.md).
