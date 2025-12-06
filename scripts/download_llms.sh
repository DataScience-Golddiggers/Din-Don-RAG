#!/bin/bash

# Script to download LLM models to the local Ollama instance (or container).
# Usage: ./scripts/download_llms.sh [OLLAMA_URL]
# Default OLLAMA_URL is http://localhost:11434

OLLAMA_URL=${1:-http://localhost:11434}

echo "Targeting Ollama instance at: $OLLAMA_URL"
echo "Ensure Ollama is running (e.g., 'docker-compose up -d ollama' or local server)."

# Function to pull a model
pull_model() {
    local model_name=$1
    echo "----------------------------------------------------------------"
    echo "Starting pull for model: $model_name"
    echo "----------------------------------------------------------------"
    
    # Use curl to trigger the pull. 
    # stream=true is default, so we will see progress JSONs. 
    # We can pipe to jq if available to format, or just let it flow.
    # For simplicity, we just run it.
    
    curl -X POST "$OLLAMA_URL/api/pull" -d "{\"name\": \"$model_name\"}"
    
    echo -e "\n\nCompleted pull for $model_name"
}

# Pull the requested models
# Note: If 'qwen3' is not available in the registry, this will return an error JSON.
pull_model "qwen3:0.6b"
pull_model "qwen3:1.7b"

echo "----------------------------------------------------------------"
echo "All operations finished."
