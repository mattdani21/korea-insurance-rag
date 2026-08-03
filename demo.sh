#!/usr/bin/env bash
# End-to-end demo: build index -> retrieval-only check -> LLM answer (if key set)
set -e
cd "$(dirname "$0")"
PY=${PY:-}
if [ -z "$PY" ]; then
  if [ -x ./.venv/bin/python ]; then PY=./.venv/bin/python; else PY=python3; fi
fi

echo "[1/3] Building index..."
"$PY" ingest.py

echo
echo "[2/3] Retrieval-only check (offline)..."
"$PY" query.py "보험금 지급 사유는 무엇인가요?" --no-llm

if [ -n "$DEEPSEEK_API_KEY" ]; then
  echo
  echo "[3/3] LLM answer..."
  "$PY" query.py "청약철회는 언제까지 가능한가요?"
else
  echo
  echo "[3/3] Skipped — DEEPSEEK_API_KEY not set. Export it or copy .env.example to .env."
fi
