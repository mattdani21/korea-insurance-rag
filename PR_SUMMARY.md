# PR_SUMMARY — M4: multi-doc filtering (autopilot)

## What
Roadmap M4 first item: the demo can now restrict retrieval to a single source document, so a mixed corpus (several insurers' contracts) stays navigable.

## Why
Once the real corpus lands (M1), users/interviewers will ask questions that should be answered from one insurer's contract only. Filtering also makes the demo's citations cleaner ("filtered to: samsung_life_terms.pdf").

## What changed
1. **`query.py`** — `retrieve(question, k, doc_filter=None)`: case-insensitive substring match on the source filename, scanning the similarity ranking in order (no re-sort). `doc_names()` returns distinct corpus docs for the dropdown. CLI gains `--doc <substring>` (with a helpful "no chunks match" hint).
2. **`app.py`** — `/ask` accepts an optional `doc` body field (echoed in the response); new `GET /documents` endpoint (named NOT `/docs` — FastAPI reserves `/docs` for Swagger UI, found via a failing test); UI gains a document `<select>` populated from `/documents`, and the answer card shows "filtered to: …".
3. **`test_api.py`** — extended: `/documents` lists the corpus; filtered `/ask` returns sources from the chosen doc only (no leaks); a no-match filter returns 0 sources.
4. **Docs** — README quickstart (2b), features list, roadmap checkbox; GOAL.md / STATE.md updated.

## How tested (local, Python 3.11)
- `python test_api.py` → GET / 200 · /ask 200 (4 sources) · /documents 200 · filtered ask 200 (all sources from the filter doc) · no-match → 0 sources — **PASS**
- `python query.py "보험금 지급 사유는 무엇인가요?" --no-llm --doc claims` → top hit `sample_claims_guide_ko.md` (score 0.851) ✓
- `python eval.py --min-hit1 0.8 --min-hit3 0.95` → hit@1 80% / hit@3 95%, exit 0 (no regression) ✓

## Not done
- M4 citation-chips polish and the portfolio case study remain (next).
- M1 (real corpus) and M3 (Railway deploy) still need Matt (geo-blocked sources / Railway account).
