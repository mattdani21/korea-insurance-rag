# State

## Current state

- **Working RAG demo:** `ingest.py` chunks data/*.md (~450 chars, overlap 60) → fastembed `intfloat/multilingual-e5-large` → `index/` (vectors.npz + chunks.json, gitignored); `query.py` does numpy cosine top-k with `--no-llm` retrieval-only mode; `app.py` is a FastAPI web UI + `/ask` endpoint with LLM answers via DeepSeek (any OpenAI-compatible provider).
- **Eval evidence exists:** 20-question set (`eval_questions.json`), retrieval-only — **hit@1 80% (16/20), hit@3 95% (19/20)** on the sample corpus (`eval.py`, `--k` adjustable).
- **CI exists:** `.github/workflows/test.yml` runs ingest → retrieval grep check (제6조/제7조) → API smoke test (`test_api.py`, asserts 200s + ≥3 sources) on push/PR, Python 3.11.
- **Public-demo hardening done:** `/ask` rate-limited to 12/min (`app.py`), clause citation chips added to UI (commit cdba94e), partner-guided real-corpus fetch script (`scripts/fetch_real_contracts.sh`).
- Repo is public, README is a polished portfolio artifact with architecture diagram and roadmap.

## Broken / incomplete

- **Corpus is synthetic:** `data/` holds `sample_contract_ko.md` + `sample_claims_guide_ko.md` only — NOT official 약관 (README flags this). The real-corpus roadmap item is still open; `fetch_real_contracts.sh` is a guided manual script (Korean insurer sites geo-block overseas IPs), not an automated downloader.
- **No deploy config:** no Dockerfile, no railway.json/Render blueprint, no hosting — the web demo only runs locally (`uvicorn app:app --reload`).
- **README roadmap is stale:** items "chunk-level citation rendering in the UI" and "Korean UI polish" are partially done (cdba94e) but checkboxes are still unchecked; multi-doc filtering still open.
- **No eval CI gate:** eval.py is not wired into the workflow — numbers can drift silently.

## Blockers

- Real-corpus acquisition blocked by geo-blocking — needs VPN, Korea-based partner, or verified public PDF URLs (documented in `scripts/fetch_real_contracts.sh`).
- LLM answers require `DEEPSEEK_API_KEY` (`.env.example`); CI intentionally tests retrieval-only paths.

## Test command

```bash
python ingest.py && python test_api.py
# Full CI sequence (per .github/workflows/test.yml):
#   python ingest.py
#   python query.py "보험금 지급 사유는 무엇인가요?" --no-llm
#   python test_api.py
# Retrieval quality:
python eval.py
```

## Run command

```bash
# End-to-end demo (index → retrieval check → LLM if key set):
bash demo.sh

# Web UI:
uvicorn app:app --reload   # → http://localhost:8000
```
