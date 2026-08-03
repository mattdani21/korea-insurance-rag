"""Build the index: read data/ docs -> chunk -> embed -> save to index/.

Usage:
    python ingest.py
"""
import json
import re
from pathlib import Path

import numpy as np

import config


def read_docs(data_dir: Path):
    docs = []
    for p in sorted(data_dir.glob("*")):
        if p.suffix.lower() in (".md", ".txt"):
            text = p.read_text(encoding="utf-8")
        elif p.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader
                text = "\n".join((page.extract_text() or "") for page in PdfReader(str(p)).pages)
            except Exception as e:  # noqa: BLE001
                print(f"  ! skip {p.name}: {e}")
                continue
        else:
            continue
        if text.strip():
            docs.append((p.name, text))
    return docs


def chunk(text: str, size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP):
    """Split on paragraph breaks; hard-split long paragraphs with overlap."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for para in paras:
        if len(buf) + len(para) + 1 <= size:
            buf = (buf + "\n" + para).strip()
            continue
        if buf:
            chunks.append(buf)
            buf = ""
        while len(para) > size:
            chunks.append(para[:size])
            para = para[size - overlap:]
        buf = para
    if buf:
        chunks.append(buf)
    return chunks


def main():
    docs = read_docs(config.DATA_DIR)
    print(f"docs found: {len(docs)}")
    if not docs:
        print("No documents in data/ — add .md/.txt/.pdf files first.")
        return

    chunks, meta = [], []
    for name, text in docs:
        for i, c in enumerate(chunk(text)):
            chunks.append(c)
            meta.append({"doc": name, "chunk": i})
    print(f"chunks: {len(chunks)}")

    from fastembed import TextEmbedding  # local, open-weight, no API
    model = TextEmbedding(model_name=config.EMBED_MODEL)
    vectors = np.array(
        list(model.embed(["passage: " + c for c in chunks])), dtype="float32"
    )

    config.INDEX_DIR.mkdir(exist_ok=True)
    np.savez(config.INDEX_DIR / "vectors.npz", vectors=vectors)
    (config.INDEX_DIR / "chunks.json").write_text(
        json.dumps({"chunks": chunks, "meta": meta}, ensure_ascii=False), encoding="utf-8"
    )
    print(f"index saved: {vectors.shape[0]} vectors x {vectors.shape[1]} dims -> {config.INDEX_DIR}")


if __name__ == "__main__":
    main()
