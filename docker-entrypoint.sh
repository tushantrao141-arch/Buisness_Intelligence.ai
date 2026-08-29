#!/bin/bash
set -e

echo "=== SilentSignal Container Startup ==="

# Check if synthetic raw data exists; generate if missing
if [ ! -f "data/raw/transactions.parquet" ] || [ ! -f "data/raw/source_metadata.json" ]; then
    echo ">> Synthetic demo sources not found. Generating demo data..."
    python scripts/generate_demo.py
else
    echo ">> Demo data found."
fi

# Ensure SQLite audit database is initialized
echo ">> Checking and initializing database..."
python scripts/init_database.py

# If arguments are passed, execute them (e.g., custom commands, test runners)
if [ "$#" -gt 0 ]; then
    echo ">> Executing custom command: $@"
    exec "$@"
fi

# Default command: launch Streamlit
echo ">> Starting Streamlit on port ${STREAMLIT_SERVER_PORT:-8501}..."
exec streamlit run app.py \
    --server.port="${STREAMLIT_SERVER_PORT:-8501}" \
    --server.address="${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}" \
    --server.headless=true
