#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo ">> Building and starting SilentSignal via Docker Compose..."
docker compose up --build -d

echo ">> Waiting for SilentSignal to become healthy..."
url="http://localhost:8501"
timeout=30
elapsed=0

while [ $elapsed -lt $timeout ]; do
    if curl -s -f "$url/_stcore/health" > /dev/null 2>&1; then
        echo ">> SilentSignal is live at $url"
        exit 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

echo ">> Container started! Access the app at: $url"
