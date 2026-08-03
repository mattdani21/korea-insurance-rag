"""Ask questions against the index.

Retrieval-only mode works fully offline. Set DEEPSEEK_API_KEY (or any
OpenAI-compatible key via LLM_BASE_URL/LLM_MODEL) for grounded LLM answers.

Usage:
    python query.py "보험금 지급 사유는 무엇인가요?" --no-llm
    python query.py "청약철회는 언제까지 가능한가요?"
"""
import argparse
import json

import numpy as np

import config


def load_index():
    data = np.load(config.INDEX_DIR / "vectors.npz")
    store = json.loads((config.INDEX_DIR / "chunks.json").read_text(encoding="utf-8"))
    return data["vectors"], store["chunks"], store["meta"]


def retrieve(question: str, k: int = config.TOP_K):
    from fastembed import TextEmbedding
    vectors, chunks, meta = load_index()
    model = TextEmbedding(model_name=config.EMBED_MODEL)
    qv = np.array(list(model.embed(["query: " + question])), dtype="float32")[0]
    sims = vectors @ qv / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(qv) + 1e-9)
    top = np.argsort(sims)[::-1][:k]
    return [(chunks[i], meta[i], float(sims[i])) for i in top]


def ask_llm(question: str, hits):
    from openai import OpenAI
    client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
    context = "\n\n---\n\n".join(
        f"[출처 {i + 1}] {text}" for i, (text, _, _) in enumerate(hits)
    )
    sys_msg = (
        "You are an assistant for Korean insurance contract documents (보험약관). "
        "Answer ONLY from the provided context. Cite clause numbers (조) when possible. "
        "Answer in the same language as the question. If the context does not contain "
        "the answer, say so clearly — never invent clauses."
    )
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": f"질문: {question}\n\n문서:\n{context}"},
        ],
    )
    return resp.choices[0].message.content


def main():
    ap = argparse.ArgumentParser(description="Korean insurance contract Q&A (RAG)")
    ap.add_argument("question", nargs="?", help="question in Korean or English")
    ap.add_argument("--no-llm", action="store_true", help="retrieval only (offline)")
    ap.add_argument("--k", type=int, default=config.TOP_K, help="top-k passages")
    args = ap.parse_args()

    q = args.question or input("질문: ").strip()
    if not q:
        return

    hits = retrieve(q, args.k)
    print("\n=== Retrieved passages ===")
    for i, (text, m, s) in enumerate(hits):
        print(f"[{i + 1}] ({m['doc']} #{m['chunk']}, score={s:.3f})\n{text[:220]}...\n")

    if args.no_llm or not config.LLM_API_KEY:
        print("(retrieval-only mode — set DEEPSEEK_API_KEY for grounded LLM answers)")
        return

    print("=== Answer ===")
    print(ask_llm(q, hits))


if __name__ == "__main__":
    main()
