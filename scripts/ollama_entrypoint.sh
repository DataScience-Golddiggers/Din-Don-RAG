#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &

# Record Process ID.
pid=$!

# Wait for Ollama to start.
sleep 5

echo "🔴 Checking for Qwen models..."

# Pull qwen3:0.6b if not exists (checking via list is safer, but pull is idempotent)
# We'll just try to pull. If it exists, it checks for updates.
echo "Pulling qwen3:0.6b..."
ollama pull qwen3:0.6b

echo "Pulling qwen3:1.7b..."
ollama pull qwen3:1.7b

echo "🟢 Models ready!"

# Wait for Ollama process to finish.
wait $pid
