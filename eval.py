"""Evaluation: hit-rate of retrieval against a 20-question set (eval_questions.json).

Usage:
    python eval.py [--k 3] [--min-hit1 0.8] [--min-hit3 0.95]

Reports hit@1 / hit@k and lists misses. Honest measure — no LLM, just retrieval.
With --min-hit1/--min-hit3, exits non-zero when a threshold is missed (CI gate).
"""
import argparse
import json
import sys
from pathlib import Path

import config
import query


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3, help="top-k for hit@k")
    ap.add_argument("--min-hit1", type=float, default=0.0, help="exit non-zero if hit@1 below this")
    ap.add_argument("--min-hit3", type=float, default=0.0, help="exit non-zero if hit@3 below this")
    args = ap.parse_args()

    qs = json.loads((Path(__file__).resolve().parent / "eval_questions.json").read_text(encoding="utf-8"))
    hits1 = hitsk = 0
    misses = []
    for item in qs:
        q, expect = item["q"], item["expect"]
        top = query.retrieve(q, args.k)
        texts = " ".join(t for t, _, _ in top)
        h1 = expect in top[0][0] if top else False
        hk = expect in texts
        hits1 += h1
        hitsk += hk
        if not hk:
            misses.append((q, expect))
    n = len(qs)
    rate1 = hits1 / n
    ratek = hitsk / n
    print(f"eval set: {n} questions | top-{args.k}")
    print(f"hit@{1}: {hits1}/{n} = {rate1:.0%}")
    print(f"hit@{args.k}: {hitsk}/{n} = {ratek:.0%}")
    if misses:
        print("\nmisses:")
        for q, e in misses:
            print(f"  ✗ {q}  (expected: {e})")

    failed = []
    if args.min_hit1 and rate1 < args.min_hit1:
        failed.append(f"hit@1 {rate1:.0%} < {args.min_hit1:.0%}")
    if args.min_hit3 and ratek < args.min_hit3:
        failed.append(f"hit@{args.k} {ratek:.0%} < {args.min_hit3:.0%}")
    if failed:
        print("\n❌ EVAL GATE FAILED: " + "; ".join(failed))
        sys.exit(1)
    print("\n✅ eval gate passed")


if __name__ == "__main__":
    main()
