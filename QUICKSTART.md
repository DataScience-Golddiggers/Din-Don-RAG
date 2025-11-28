# 🚀 Quick Start Guide

## Setup in 3 Minuti

### 1. Installa e Configura

```bash
# Clona e entra nella directory
cd ALLMond

# Crea ambiente virtuale
python -m venv .venv

# Attiva ambiente (Windows)
.venv\Scripts\activate

# Installa tutto
pip install -r requirements.txt
python scripts/download_nltk_data.py
```

### 2. Inizializza Progetto

```bash
python scripts/init_project.py
```

Questo script:
- ✓ Crea struttura cartelle
- ✓ Copia file .env
- ✓ Verifica dipendenze
- ✓ Scarica risorse NLTK

### 3. Prova il Notebook

```bash
jupyter notebook
```

Apri `notebooks/nlp_pipeline.ipynb` e prova con i dati di esempio in `data/raw/example_data.csv`.

---

## Esempi Veloci

### Esempio 1: Preprocessing Testo

```python
from src.text_preprocessing import TextPreprocessor

preprocessor = TextPreprocessor(language="italian")

text = "Visita https://example.com per maggiori info! #NLP"
cleaned = preprocessor.clean_text(text)
print(cleaned)  # "visita maggiori info"

tokens = preprocessor.tokenize(cleaned)
print(tokens)  # ['visita', 'maggiori', 'info']
```

### Esempio 2: Training Modello da CLI

```bash
python scripts/train_pipeline.py \
    --input-file data/raw/example_data.csv \
    --text-column text \
    --label-column label \
    --model logistic_regression \
    --language italian
```

### Esempio 3: Predizione

```bash
# Predizione su singolo testo
python scripts/predict.py \
    --input-text "Bando per assegnazione borse di studio"

# Predizione su file CSV
python scripts/predict.py \
    --input-file data/raw/new_data.csv \
    --output-file predictions.csv
```

### Esempio 4: Pipeline Completa in Python

```python
from src.data_loader import DataLoader
from src.text_preprocessing import TextPreprocessor
from src.feature_extraction import FeatureExtractor
from src.model_trainer import ModelTrainer
from sklearn.model_selection import train_test_split

# 1. Carica dati
loader = DataLoader()
df = loader.load_csv("data/raw/example_data.csv")

# 2. Preprocessing
preprocessor = TextPreprocessor(language="italian")
df_clean = preprocessor.preprocess_dataframe(df, "text")

# 3. Feature extraction
extractor = FeatureExtractor()
X, vectorizer = extractor.extract_tfidf(
    df_clean['processed_text'].tolist(),
    max_features=100
)

# 4. Split
y = df_clean['label'].values
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. Training
trainer = ModelTrainer("logistic_regression")
trainer.train(X_train, y_train)

# 6. Valutazione
metrics = trainer.evaluate(X_test, y_test)
print(metrics)

# 7. Salva modello
trainer.save_model()
```

---

## Workflow Consigliato per Progetto Nuovo

### Fase 1: Raccolta Dati
- Metti i tuoi file CSV/JSON/Excel in `data/raw/`
- Oppure usa `src/scraper.py` per web scraping

### Fase 2: Esplorazione
- Apri `notebooks/nlp_pipeline.ipynb`
- Carica i dati (sezione 3)
- Esegui analisi esplorativa (sezione 4)

### Fase 3: Preprocessing
- Adatta `clean_text()` alle tue esigenze (sezione 5)
- Scegli lingua per stopwords (sezione 6)
- Esegui preprocessing completo
- Salva dati puliti in `data/cleaned/`

### Fase 4: Modellazione
- Prova diversi modelli (sezioni 11-12)
- Confronta metriche
- Fai hyperparameter tuning se necessario
- Salva il modello migliore

### Fase 5: Valutazione
- Classification report
- Confusion matrix
- Cross-validation
- Test su nuovi dati

### Fase 6: Produzione
- Usa `scripts/predict.py` per predizioni
- Integra in applicazione
- Monitora performance

---

## Comandi Utili

```bash
# Formatta codice
make format

# Esegui test
make test

# Pulisci file temporanei
make clean

# Avvia Jupyter
make run-notebook

# Training con Make
make train ARGS="--input-file data/raw/data.csv"
```

---

## Docker (Opzionale)

```bash
# Build e avvia container
docker-compose up -d

# Accedi a Jupyter
# Apri browser: http://localhost:8888
```

---

## Troubleshooting Rapido

### Errore: "No module named 'src'"
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Windows: set PYTHONPATH=%PYTHONPATH%;%cd%
```

### Errore: NLTK data not found
```bash
python scripts/download_nltk_data.py
```

### Errore: UnicodeDecodeError
```python
# Usa encoding diverso
df = pd.read_csv("file.csv", encoding="latin-1")
```

### Memoria insufficiente
```python
# Riduci max_features
vectorizer = TfidfVectorizer(max_features=100)  # invece di 1000
```

---

## Prossimi Passi

1. **Leggi README.md completo** per dettagli
2. **Esplora notebooks/** per tutorial
3. **Consulta SETUP.md** per configurazione avanzata
4. **Leggi CONTRIBUTING.md** se vuoi contribuire

---

## Supporto

- 📚 [Documentazione completa](README.md)
- 🐛 [Segnala bug](https://github.com/your-username/ALLMond/issues)
- 💬 [Discussioni](https://github.com/your-username/ALLMond/discussions)

Buon lavoro! 🍃
