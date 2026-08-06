# Goal

Land Korean work — the demo project proving capability to Korean employers and clients

## Roadmap

### M1 — Build a real 보험약관 corpus

- [ ] Download 3–5 real Korean insurance contracts (life + health + insurtech variety) via `scripts/fetch_real_contracts.sh` — using a Seoul partner/VPN for geo-blocked sources (Samsung Life, Hanwha, Kyobo, Carrot)
- [ ] Verify pypdf extraction works on the real PDFs (the current `data/` corpus is synthetic sample docs only)
- [ ] Re-run `python ingest.py` on the real corpus and re-check `python eval.py` (hit@1 will shift with real clause structure)

*Definition of done:* index built from ≥3 real insurer contracts, replacing the synthetic sample corpus; eval results recorded against the real corpus.

### M2 — Hard evidence: eval + CI on the real corpus

- [ ] Keep hit@1 ≥ 80% / hit@3 ≥ 95% on the real corpus, or tune chunking (CHUNK_SIZE/CHUNK_OVERLAP in `config.py`) and document the change
- [ ] Update the README evaluation section with real-corpus numbers and the known miss (보험증권 교부 시점 clause overlap)
- [ ] Extend `.github/workflows/test.yml` to run `python eval.py` as a CI gate (ingest + retrieval check + API smoke already covered)
- [ ] Update the stale README roadmap checkboxes (clause citation chips landed in commit cdba94e but the roadmap is not updated)

*Definition of done:* CI runs the full pipeline including eval on the real corpus, and README reflects current numbers.

### M3 — Ship the hosted web demo

- [ ] Add deploy config (Railway/Render): uvicorn `app:app`, `$PORT` binding, healthcheck on `/`, build step running `python ingest.py`
- [ ] Wire `DEEPSEEK_API_KEY` via platform secrets (`.env.example` already documents it; `config.py` reads env)
- [ ] Confirm the /ask rate limit (12/min in `app.py`) holds under public traffic and the UI renders Korean correctly
- [ ] Deploy and publish the public URL in the README

*Definition of done:* a public URL answers Korean questions with clause-cited sources and survives the rate limit without key exposure.

### M4 — Prove it in the interview loop

- [ ] Multi-doc filtering (product type, insurer) from the README roadmap so the demo handles a mixed corpus
- [ ] Add chunk-level citation chips polish in the UI (base landed in cdba94e)
- [ ] Write the portfolio case study: architecture (fastembed e5-large → numpy cosine → DeepSeek), eval numbers, geo-blocking lesson
- [ ] Share the demo link + case study on LinkedIn and in applications to Korean insurers/fintech/actuarial vendors

*Definition of done:* the hosted demo link and eval evidence are referenced in Matt's Korea job-search materials and interviews.

## Notes

- Issues are disabled on this repo; track work via these checklists and commits.
- Current corpus is synthetic (README warns: NOT official terms) — M1 is the single most credibility-critical milestone.
