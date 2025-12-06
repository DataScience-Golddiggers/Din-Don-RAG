FROM python:3.10-slim

WORKDIR /app

# Install build dependencies for wordcloud and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/inference/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (stopwords, punkt, wordnet, punkt_tab)
RUN python -m nltk.downloader stopwords punkt punkt_tab wordnet omw-1.4

COPY src/inference/ .
COPY utils/ ./utils/
# Models will be mounted, but we need the directory to exist
RUN mkdir -p models

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
