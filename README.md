# 🍃 ALLMond

**Natural Language Processing pipeline as simple and delicious as an almond.**

Un framework completo e professionale per progetti di NLP in italiano (e altre lingue).

---

## 🚀 Caratteristiche

- ✅ **Pipeline completa NLP**: dalla raccolta dati al deployment
- ✅ **Preprocessing avanzato**: pulizia testo, tokenizzazione, lemmatization
- ✅ **Feature extraction**: BoW, TF-IDF, Word2Vec, Topic Modeling
- ✅ **Modelli ML**: Naive Bayes, Logistic Regression, SVM, Random Forest
- ✅ **Web Scraping**: strumenti per raccolta dati da web
- ✅ **Jupyter Notebook**: tutorial interattivo completo
- ✅ **Testing**: suite di test con pytest
- ✅ **Logging**: sistema di logging professionale
- ✅ **CLI Scripts**: script pronti per training e predizione
- ✅ **Configurabile**: gestione configurazione tramite file .env

---

## 📦 Installazione

### Prerequisiti

- Python 3.9+
- pip
- virtualenv (consigliato)

### Setup Rapido

```bash
# Clona il repository
git clone https://github.com/your-username/ALLMond.git
cd ALLMond

# Crea ambiente virtuale
python -m venv .venv

# Attiva ambiente virtuale
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Download risorse NLTK
python scripts/download_nltk_data.py

# (Opzionale) Installa spaCy per italiano
python -m spacy download it_core_news_sm
```

### Setup con Make (consigliato)

```bash
make setup
```

---

## 🎯 Quick Start

### 1. Jupyter Notebook (per principianti)

```bash
make run-notebook
# oppure
jupyter notebook
```

Apri `notebooks/nlp_pipeline.ipynb` e segui le istruzioni passo-passo.

### 2. Training da CLI

```bash
python scripts/train_pipeline.py \
    --input-file data/raw/your_data.csv \
    --text-column "text" \
    --label-column "category" \
    --model logistic_regression \
    --language italian

# Oppure con Make
make train ARGS="--input-file data/raw/your_data.csv --text-column text"
```

### 3. Uso Programmatico

```python
from src.data_loader import DataLoader
from src.text_preprocessing import TextPreprocessor
from src.model_trainer import ModelTrainer

# Carica dati
loader = DataLoader()
df = loader.load_csv("data/raw/your_data.csv")

# Preprocessing
preprocessor = TextPreprocessor(language="italian")
df_clean = preprocessor.preprocess_dataframe(df, text_column="text")

# Training
trainer = ModelTrainer(model_type="logistic_regression")
trainer.train(X_train, y_train)

# Valutazione
metrics = trainer.evaluate(X_test, y_test)
print(metrics)
```

---

## 📁 Struttura Progetto

```
ALLMond/
├── data/
│   ├── raw/              # Dati originali
│   ├── processed/        # Dati intermedi
│   └── cleaned/          # Dati puliti finali
├── notebooks/
│   └── nlp_pipeline.ipynb  # Tutorial completo
├── src/
│   ├── config.py         # Configurazione
│   ├── logger.py         # Sistema logging
│   ├── data_loader.py    # Caricamento dati
│   ├── text_preprocessing.py  # Preprocessing testo
│   ├── feature_extraction.py  # Estrazione features
│   ├── model_trainer.py  # Training modelli
│   ├── scraper.py        # Web scraping
│   └── utils.py          # Utilità varie
├── tests/                # Test suite
├── scripts/              # Script CLI
├── models/               # Modelli salvati
├── logs/                 # File di log
├── docs/                 # Documentazione
├── requirements.txt      # Dipendenze
├── pyproject.toml        # Configurazione progetto
├── Makefile              # Automazione task
└── README.md
```

---

## 🛠️ Comandi Disponibili

```bash
make help          # Mostra tutti i comandi disponibili
make install       # Installa dipendenze
make setup         # Setup completo ambiente
make test          # Esegui test
make lint          # Controlla codice (flake8, mypy)
make format        # Formatta codice (black, isort)
make clean         # Pulisci file generati
make run-notebook  # Avvia Jupyter
make train         # Esegui training pipeline
```

---

## 🧪 Testing

```bash
# Esegui tutti i test
make test

# Esegui test specifici
pytest tests/test_text_preprocessing.py -v

# Con coverage report
pytest --cov=src --cov-report=html
```

---

## 📊 Workflow Tipico

1. **Raccolta Dati**
   ```bash
   # Scraping web o caricamento file
   python scripts/scrape_data.py
   ```

2. **Preprocessing**
   - Apri `notebooks/nlp_pipeline.ipynb`
   - Esegui le celle di preprocessing
   - Salva dati puliti in `data/cleaned/`

3. **Training**
   ```bash
   python scripts/train_pipeline.py --input-file data/cleaned/data.csv
   ```

4. **Valutazione**
   - Metriche automatiche (accuracy, F1, precision, recall)
   - Confusion matrix
   - Classification report

5. **Deployment**
   - Modello salvato in `models/`
   - Pronto per produzione

---

## 🔧 Configurazione

Copia `.env.example` in `.env` e modifica:

```bash
cp .env.example .env
```

```env
# Lingua default
DEFAULT_LANGUAGE=italian

# Preprocessing
USE_LEMMATIZATION=true
REMOVE_STOPWORDS=true

# Modellazione
TEST_SIZE=0.2
RANDOM_STATE=42
MAX_FEATURES=1000
```

---

## 📚 Documentazione

- [Quick Start Guide](QUICKSTART.md) - Guida rapida con esempi
- [Best Practices](docs/BEST_PRACTICES.md) - Best practices NLP

---

## 🤝 Contribuire

I contributi sono benvenuti! Per favore:

1. Fork il progetto
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per dettagli.

---

## 📝 License

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

---

## 👥 Autori

- **Your Name** - *Initial work*

---

## 🙏 Ringraziamenti

- NLTK Team
- spaCy Team
- scikit-learn Team
- Hugging Face

---

## 📞 Contatti

- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

---

⭐ **Se questo progetto ti è stato utile, lascia una stella!**
