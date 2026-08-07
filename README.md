# 🇰🇷 보험약관 RAG — Korean Insurance Contract Q&A (Portfolio Demo)

[![test](https://github.com/mattdani21/korea-insurance-rag/actions/workflows/test.yml/badge.svg)](https://github.com/mattdani21/korea-insurance-rag/actions)

> 한국어 보험약관 문서를 검색하고 질문에 답하는 RAG(Retrieval-Augmented Generation) 시스템 데모.
> Built by Matthew Hendricks — senior data/ML engineer (actuarial validation, LLM/RAG, regulated fintech).
> Part of a relocation portfolio targeting Korean insurers, fintech (Toss/Coupang), and actuarial-tech vendors.

**Why this exists:** Korean insurance contracts (보험약관) are famously dense. A system that can answer "보험금은 언제 지급되나요?" with cited clause numbers — in Korean — is the kind of thing Korean insurance AI teams actually build. This repo shows: Korean-language NLP, RAG architecture, open-weight embeddings, LLM integration with source citations, and domain care (no hallucinated clauses).

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate   # or use your existing env
pip install -r requirements.txt

# 1. Build the index (embeds data/*.md into index/)
python ingest.py

# 2. Ask (retrieval-only — no API key needed)
python query.py "보험금 지급 사유는 무엇인가요?" --no-llm

# 3. Ask with LLM answers (set DEEPSEEK_API_KEY or any OpenAI-compatible key)
cp .env.example .env   # add your key
python query.py "청약철회는 언제까지 가능한가요?"

# 4. Web UI
uvicorn app:app --reload   # → http://localhost:8000
```

## Architecture

```
data/*.md,*.txt,*.pdf ──► ingest.py (chunk ~450 chars, overlap) ──► fastembed
        (multilingual-e5-small, open-weight, local)             ──► index/vectors.npz
                                                                  └► index/chunks.json
query.py / app.py: question ──► embed (query: prefix) ──► cosine top-k ──► DeepSeek API
        (OpenAI-compatible, any provider) ──► answer + cited sources
```

- **Embeddings:** `intfloat/multilingual-e5-large` via [fastembed](https://github.com/qdrant/fastembed) — local, open-weight, no API cost, handles Korean well
- **Generation:** DeepSeek API by default (`deepseek-v4-flash`, OpenAI-compatible) — swap in any provider via `LLM_BASE_URL`/`LLM_MODEL`/`*_API_KEY`
- **Citations:** every answer is grounded in retrieved passages with clause references; retrieval-only mode (`--no-llm`) works fully offline
- **No heavy stack:** numpy cosine search — the corpus is small and this keeps the demo dependency-light

## Sample data ⚠️

`data/` contains **synthetic sample documents** (a life-insurance contract structure + claims guide) written for the demo — they mirror the structure of real 보험약관 but are NOT official terms. Replace them with real documents:

```bash
bash scripts/fetch_real_contracts.sh   # sources listed; many Korean sites geo-block overseas IPs (use VPN / partner in Seoul)
```

Then re-run `python ingest.py`. The pipeline treats every file in `data/` as corpus.


## Evaluation

20-question Korean Q&A set (`eval_questions.json`) against the sample corpus — retrieval only, no LLM:

- **hit@1: 80%** (16/20) · **hit@3: 95%** (19/20)

Run it yourself: `python eval.py`. The one miss (보험증권 교부 시점) reflects clause-overlap in the sample chunking — a real 약관 corpus with finer chunking should push hit@1 higher.

**CI gate:** the eval runs on every push/PR with thresholds enforced (`python eval.py --min-hit1 0.8 --min-hit3 0.95`) — retrieval quality can't drift silently. `fastembed` is pinned to the 0.8.x family because ≥0.8 changed pooling (mean vs CLS); eval numbers are verified on 0.8.x.

## Deployment (Railway)

One-click from GitHub (Dockerfile included — builds the index during deploy):

1. Railway dashboard → **New Project → Deploy from GitHub repo** → `mattdani21/korea-insurance-rag`
2. Add variable: `DEEPSEEK_API_KEY` (LLM answers; retrieval-only works without it)
3. Deploy — the build runs `python ingest.py` (embeds the corpus), the container serves uvicorn on `$PORT`
4. Healthcheck: GET `/` returns the UI (200); Railway's default check works

Or locally: `uvicorn app:app --reload` → http://localhost:8000

## Roadmap

- [x] Evaluation set (20 Q&A pairs, hit@1 80% / hit@3 95%)
- [x] CI: GitHub Actions test workflow (ingest + retrieval check + API smoke test + **eval gate**)
- [x] Chunk-level citation rendering in the UI (clause number chips — commit cdba94e)
- [x] Korean UI polish (commit cdba94e)
- [x] Deploy config (Dockerfile, $PORT binding, index built at deploy — commit pending)
- [ ] Real 보험약관 corpus (3–5 insurers, PDF ingest via pypdf) — **blocked**: geo-blocked sources, needs VPN / Seoul partner (see `scripts/fetch_real_contracts.sh`)
- [ ] Hosted demo deployed to Railway + public URL in README
- [ ] Multi-doc filtering (product type, insurer)

## Contact

Matthew Hendricks — mattdani21@gmail.com — linkedin.com/in/matthew-hendricks-779576144
