# UnivPM AI Assistant

A containerized AI-powered web assistant. This solution leverages a microservices architecture to crawl university data, process it via NLP pipelines, and generate context-aware responses using local Large Language Models (LLMs).

## 🏗 Architecture

The system is composed of the following Docker services:

- **`webapp`**: Node.js/Express/TypeScript frontend (MVC) with Bootstrap 5. Handles user interaction and request concurrency locking.
- **`ai-service`**: Python/FastAPI backend. Orchestrates the NLP pipeline:
  - **Classification**: Scikit-learn Logistic Regression to filter relevant queries.
  - **RAG (Retrieval-Augmented Generation)**: Summarization and QA using Qwen models via Ollama.
- **`crawler`**: Python/FastAPI service using `crawl4ai` (Playwright) to fetch live content from UnivPM.
- **`ollama`**: (Optional) Containerized LLM inference server. Can be replaced by a local instance for better performance on Apple Silicon/GPU.
- **`ngrok`**: Exposes the application to the public internet.

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/) (Recommended for local execution)
- Python 3.10+ (Optional, for local training)

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` to set your configuration. If using **Local Ollama** (recommended for Mac M1/M2/M3), ensure:

```dotenv
OLLAMA_URL=http://host.docker.internal:11434
```

### 2. Ollama Configuration (Local Mode)

To utilize your host's GPU and share models with the project, you must configure your local Ollama instance to listen on all interfaces and store models in the project directory.

**Stop any running Ollama instance** (e.g., from the menu bar), then run:

```bash
# Run this from the project root
export OLLAMA_HOST=0.0.0.0
export OLLAMA_MODELS=$(pwd)/models/models

# Start the server
ollama serve
```

> **Note**: Keep this terminal open. The `OLLAMA_MODELS` path ensures that models pulled by the project are stored within the repo structure.

### 3. Generate Training Data

If you don't have a dataset, you can generate a synthetic one with university-related questions:

```bash
# Generate 2000 samples in data/raw/training_dataset.csv
python scripts/generate_dataset.py
```

### 4. Train the Classifier

Before starting the services, you must train the relevance classifier.

**Option A: Using Docker (Easiest)**
Start the services first, then run the training script inside the container:

```bash
docker-compose up -d
docker-compose exec ai-service python scripts/train_pipeline.py \
  --input-file "data/raw/training_dataset.csv" \
  --text-column "question" \
  --label-column "label" \
  --model logistic_regression
```

**Option B: Local Python**
```bash
pip install -r src/inference/requirements.txt
python scripts/train_pipeline.py \
  --input-file "data/raw/training_dataset.csv" \
  --text-column "question" \
  --label-column "label" \
  --model logistic_regression
```

### 5. Run the Application

Start the entire stack:

```bash
docker-compose up --build
```

- **Web Interface**: [http://localhost:3000](http://localhost:3000)
- **Public URL**: Check the `ngrok` service logs or visit [http://localhost:4040](http://localhost:4040).

## 🛠 Development

- **Hot Reload**: The `webapp` service is configured with `nodemon`. Changes to `src/application` (TS, EJS, CSS) will trigger an automatic rebuild/restart.
- **Logs**: View logs for specific services:
  ```bash
  docker-compose logs -f ai-service
  ```

## 📂 Project Structure

```
├── data/               # Datasets (raw, processed)
├── models/             # Trained .pkl models and Ollama blobs
├── scripts/            # Training and utility scripts
├── src/
│   ├── application/    # Node.js Web App (Frontend/BFF)
│   ├── crawler/        # Python Crawler Service
│   └── inference/      # Python AI/NLP Service
├── utils/              # Shared Python utilities (Preprocessing, Logger)
└── docker-compose.yml  # Orchestration
```

## 🤖 Models Used

- **Classifier**: Logistic Regression (Scikit-learn)
- **Summarization**: `qwen3:0.6b` (via Ollama)
- **QA/Chat**: `qwen3:1.7b` (via Ollama)
