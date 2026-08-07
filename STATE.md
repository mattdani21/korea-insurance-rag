# State

## Current state

- **Working RAG demo:** `ingest.py` chunks data/*.md (~450 chars, overlap 60) → fastembed `intfloat/multilingual-e5-large` → `index/` (vectors.npz + chunks.json, gitignored); `query.py` does numpy cosine top-k with `--no-llm` retrieval-only mode; `app.py` is a FastAPI web UI + `/ask` endpoint with LLM answers via DeepSeek (any OpenAI-compatible provider).
- **Eval evidence exists:** 20-question set (`eval_questions.json`), retrieval-only — **hit@1 80% (16/20), hit@3 95% (19/20)** on the sample corpus (`eval.py`, `--k` adjustable).
- **CI exists + eval gate:** `.github/workflows/test.yml` runs ingest → retrieval grep check (제6조/제7조) → API smoke test (`test_api.py`) → **`python eval.py --min-hit1 0.8 --min-hit3 0.95`** on push/PR, Python 3.11. `fastembed` pinned to 0.8.x (≥0.8 changed pooling; eval verified on 0.8.x).
- **Public-demo hardening done:** `/ask` rate-limited to 12/min (`app.py`), clause citation chips added to UI (commit cdba94e), partner-guided real-corpus fetch script (`scripts/fetch_real_contracts.sh`).
- **Deploy config ready:** Dockerfile (index built during `docker build` via `python ingest.py`, uvicorn on `$PORT`), .dockerignore — deploy to Railway is one click from GitHub, pending Matt (needs his Railway account).
- **Multi-doc filtering shipped:** `query.py --doc <substring>`, `/ask` body field `doc`, `GET /documents` (distinct corpus docs), UI dropdown populated client-side; empty result when the filter matches nothing (caller falls back).
- **Model default fixed:** `LLM_MODEL` defaults to `deepseek-v4-flash` (was `deepseek-chat`, not valid on Matt's account).
- Repo is public, README is a polished portfolio artifact with architecture diagram and roadmap.

## Broken / incomplete

- **Corpus is synthetic:** `data/` holds `sample_contract_ko.md` + `sample_claims_guide_ko.md` only — NOT official 약관 (README flags this). The real-corpus roadmap item is still open; `fetch_real_contracts.sh` is a guided manual script (Korean insurer sites geo-block overseas IPs), not an automated downloader.
- **Not deployed:** Dockerfile + Railway instructions ready, but no live URL yet — needs Matt to create the Railway service (autopilot has no Railway access).
- **Portfolio case study written:** `docs/CASE_STUDY.md` (architecture decisions, eval numbers, geo-blocking lesson) — ready for applications/interviews.

## Blockers

- Real-corpus acquisition blocked by geo-blocking — needs VPN, Korea-based partner, or verified public PDF URLs (documented in `scripts/fetch_real_contracts.sh`). M1 tasks remain unchecked.
- LLM answers require `DEEPSEEK_API_KEY` (`.env.example`); CI intentionally tests retrieval-only paths.
- Deploy (M3) needs Matt's Railway account — everything else for it is prepared.

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
