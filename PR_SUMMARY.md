# PR_SUMMARY — M2 eval gate + M3 deploy prep (autopilot)

## What
Autopilot pass on the roadmap: M2's unblocked items + M3's deploy preparation.

## Why
- Retrieval quality could drift silently (no eval in CI).
- The README roadmap lied about completed work (citation chips landed in cdba94e but boxes were unchecked).
- The demo has no deploy path — a hosted URL is the whole point of the portfolio repo.
- `LLM_MODEL` defaulted to `deepseek-chat`, which is NOT a valid model on Matt's DeepSeek account (only deepseek-v4-flash / deepseek-v4-pro exist) — same landmine found in kloudy_whale.

## What changed
1. **Eval CI gate** — `eval.py` gains `--min-hit1` / `--min-hit3` (exit non-zero below threshold); `.github/workflows/test.yml` runs `python eval.py --min-hit1 0.8 --min-hit3 0.95` after the API smoke test.
2. **Reproducibility** — `fastembed` pinned to `>=0.8,<0.9` (≥0.8 switched to mean pooling; eval verified on 0.8.x so CI can't silently shift numbers with a future release).
3. **Deploy config** — `Dockerfile` (index built during build via `python ingest.py`, uvicorn on `$PORT`) + `.dockerignore`; README gains a Railway deploy section (one-click from GitHub).
4. **Model fix** — `config.py` `LLM_MODEL` default → `deepseek-v4-flash`; README updated.
5. **Docs** — README evaluation section (gate command + pinning rationale), roadmap checkboxes now truthful (citation chips / Korean UI polish marked done; real-corpus item marked **blocked** with reason), GOAL.md / STATE.md updated to match.

## How tested
On `autopilot/m2-m3`, Python 3.11 venv:
- `python ingest.py` — 7 chunks indexed (sample corpus)
- `python query.py "보험금 지급 사유는 무엇인가요?" --no-llm` → contains 제6조/제7조 ✓
- `python test_api.py` → GET / 200, POST /ask 200, ≥4 sources ✓
- `python eval.py --min-hit1 0.8 --min-hit3 0.95` → hit@1 80%, hit@3 95%, exit 0 ✓

## Not done (blocked / needs owner)
- **M1 (real corpus):** geo-blocked insurer sites; needs VPN or Seoul partner (per GOAL.md). M1 checkboxes untouched.
- **M3 deploy:** everything prepared, but creating the Railway service + setting `DEEPSEEK_API_KEY` needs Matt's Railway account (autopilot has no access). Steps are in the README.
