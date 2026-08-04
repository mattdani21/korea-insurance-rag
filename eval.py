"""Evaluation: hit-rate of retrieval against a 20-question set (eval_questions.json).

Usage:
    python eval.py [--k 3]

Reports hit@1 / hit@k and lists misses. Honest measure — no LLM, just retrieval.
"""
import argparse
import json
from pathlib import Path

import config
import query


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3, help="top-k for hit@k")
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
    print(f"eval set: {n} questions | top-{args.k}")
    print(f"hit@{1}: {hits1}/{n} = {hits1/n:.0%}")
    print(f"hit@{args.k}: {hitsk}/{n} = {hitsk/n:.0%}")
    if misses:
        print("\nmisses:")
        for q, e in misses:
            print(f"  ✗ {q}  (expected: {e})")


if __name__ == "__main__":
    main()
