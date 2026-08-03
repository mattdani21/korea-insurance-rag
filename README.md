# 🇰🇷 보험약관 RAG — Korean Insurance Contract Q&A (Portfolio Demo)

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
- **Generation:** DeepSeek API by default (`deepseek-chat`, OpenAI-compatible) — swap in any provider via `LLM_BASE_URL`/`LLM_MODEL`/`*_API_KEY`
- **Citations:** every answer is grounded in retrieved passages with clause references; retrieval-only mode (`--no-llm`) works fully offline
- **No heavy stack:** numpy cosine search — the corpus is small and this keeps the demo dependency-light

## Sample data ⚠️

`data/` contains **synthetic sample documents** (a life-insurance contract structure + claims guide) written for the demo — they mirror the structure of real 보험약관 but are NOT official terms. Replace them with real documents:

```bash
bash scripts/fetch_real_contracts.sh   # sources listed; many Korean sites geo-block overseas IPs (use VPN / partner in Seoul)
```

Then re-run `python ingest.py`. The pipeline treats every file in `data/` as corpus.


## Roadmap

- [ ] Real 보험약관 corpus (3–5 insurers, PDF ingest via pypdf)
- [ ] Chunk-level citation rendering in the UI (clause number chips)
- [ ] Evaluation set (20 Q&A pairs) with retrieval hit-rate reporting
- [ ] Korean UI polish + hosted demo (Railway/Render)
- [ ] Multi-doc filtering (product type, insurer)

## Contact

Matthew Hendricks — mattdani21@gmail.com — linkedin.com/in/matthew-hendricks-779576144
