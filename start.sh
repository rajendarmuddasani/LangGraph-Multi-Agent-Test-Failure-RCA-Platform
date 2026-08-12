#!/bin/sh
set -eu

if [ -z "${RCA_EVIDENCE_API_KEY:-}" ]; then
    echo "RCA_EVIDENCE_API_KEY must be set before startup." >&2
    exit 1
fi

python -m uvicorn evidence_app:app \
    --app-dir backend \
    --host "${RCA_HOST:-127.0.0.1}" \
    --port "${RCA_PORT:-8088}"
