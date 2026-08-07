# Case Study — Korean Insurance Contract Q&A (보험약관 RAG)

*Portfolio demo built for the Korea job search — Korean-language NLP, RAG, open-weight
embeddings, LLM generation with source citations, CI-gated evaluation.*

---

## The problem

Korean insurance contracts (보험약관) are dense, clause-heavy documents written in a
formal register that trips up both laypeople and generic search. A customer asking
"보험금은 언제 지급되나요?" (when is the claim paid?) wants an answer with the **clause
number** behind it — not a keyword match and not a hallucinated citation.

The demo's job: prove I can build the kind of system Korean insurance AI teams actually
ship — Korean-language retrieval, grounded generation, and honest evaluation — end to end.

## The approach

A deliberately minimal RAG stack — no vector database, no orchestration framework.
Small corpus, sharp decisions:

```
data/*.md / *.pdf ──► ingest.py (chunk ~450 chars, overlap 60)
                        ──► fastembed (intfloat/multilingual-e5-large, local, open-weight)
                        ──► index/ (vectors.npz + chunks.json)

question ──► embed ("query: " prefix) ──► numpy cosine top-k ──► DeepSeek v4-flash
                ──► answer with clause-number citations
```

### Why these choices

| Decision | Rationale |
|---|---|
| **fastembed + e5-large** | Multilingual embeddings with strong Korean performance; runs locally, no per-query API cost, no data leaves the box. |
| **numpy cosine, no vector DB** | At demo scale (< 100 chunks) a vector database is ceremony. NumPy keeps the stack honest and dependency-light. |
| **Chunk 450 chars / overlap 60** | Sentence-ish granularity preserves clause structure (제6조 etc.) across chunk boundaries. |
| **Retrieval-only eval, no LLM** | The honest measure. hit@1 / hit@3 says nothing about the LLM and everything about the retrieval — which is the part that's actually hard. |
| **DeepSeek v4-flash, temperature 0.2** | Cost-effective Korean-capable generation; low temperature keeps answers close to the cited context. |
| **Clause chips in the UI** | Retrieved passages are regex-scanned for 조 numbers; chips render the citation at a glance — the "trust" affordance. |

## Results

- **hit@1 80% (16/20), hit@3 95% (19/20)** on a 20-question Korean Q&A set
  (`eval_questions.json`), retrieval-only.
- The single miss (보험증권 교부 시점) is a **known, documented** clause-overlap case —
  expected to improve with a real corpus and finer chunking.
- **Eval is a CI gate**: `python eval.py --min-hit1 0.8 --min-hit3 0.95` runs on every
  push/PR. Retrieval quality cannot drift silently.
- `fastembed` pinned to the 0.8.x family after the library switched pooling (mean vs
  CLS) — reproducibility is part of the engineering, not an afterthought.

## Engineering notes

- **Multi-doc filtering** (`--doc`, `/ask` `doc`, `GET /documents`): substring filter
  over source filenames, scanned down the similarity ranking — a mixed corpus of
  several insurers' contracts stays navigable, and citations say *which* contract.
- **Public-demo hardening**: `/ask` rate-limited (12/min), citation chips, healthcheck
  on `/`, Dockerfile with the index built at deploy time.
- **Geo-blocking lesson**: the credibility-critical next step is a *real* 약관 corpus
  (3–5 insurers). Korean insurer sites geo-block overseas IPs — the fetch script
  documents sources and the partner/VPN path rather than pretending automation can
  solve jurisdiction. Being explicit about the blocker is the professional move.

## What's next

1. **Real corpus** (M1) — partner in Seoul or VPN → pypdf extraction → re-run eval.
2. **Hosted demo** (M3) — Railway deploy is one click from GitHub; Dockerfile + docs ready.
3. **Multi-doc polish** — filtering shipped; chunk-level citation chips refinement.

## How to verify everything yourself

```bash
pip install -r requirements.txt
python ingest.py
python eval.py --min-hit1 0.8 --min-hit3 0.95   # 80% / 95%, exit 0
python query.py "보험금 지급 사유는 무엇인가요?" --no-llm --doc claims
uvicorn app:app --reload                        # → http://localhost:8000
```
