"""FastAPI server: local web UI + /ask endpoint.

Usage:
    uvicorn app:app --reload     # -> http://localhost:8000
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

import config
import query as q

app = FastAPI(title="보험약관 RAG demo — Korean Insurance Contract Q&A")


class Ask(BaseModel):
    question: str
    k: int = config.TOP_K
    doc: Optional[str] = None  # restrict retrieval to one source doc (substring)


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(UI)


@app.get("/documents")
def documents():
    """Distinct corpus documents, for the filter dropdown. (Not /docs — FastAPI
    reserves that path for Swagger UI.)"""
    try:
        return JSONResponse({"docs": q.doc_names()})
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"docs": [], "error": str(e)}, status_code=500)


# tiny in-memory rate limit for the public demo (protects the LLM budget)
import time
_ask_times = []
MAX_ASKS_PER_MIN = 12


@app.post("/ask")
def ask(body: Ask, request: Request):
    now = time.time()
    _ask_times[:] = [t for t in _ask_times if now - t < 60]
    if len(_ask_times) >= MAX_ASKS_PER_MIN:
        return JSONResponse({"detail": "rate limited — try again in a minute"}, status_code=429)
    _ask_times.append(now)
    hits = q.retrieve(body.question, body.k, doc_filter=body.doc)
    answer = None
    if config.LLM_API_KEY:
        try:
            answer = q.ask_llm(body.question, hits)
        except Exception as e:  # noqa: BLE001
            answer = f"(LLM error: {e})"
    return JSONResponse({
        "question": body.question,
        "doc": body.doc,
        "answer": answer,
        "sources": [
            {"text": text[:300], "doc": m["doc"], "score": round(s, 3)}
            for text, m, s in hits
        ],
    })


UI = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>보험약관 RAG demo</title>
<style>
  body { font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
         max-width: 760px; margin: 40px auto; padding: 0 20px; color: #222; }
  h1 { font-size: 22px; } h1 small { color: #888; font-weight: normal; font-size: 13px; }
  textarea { width: 100%; height: 64px; font-size: 15px; padding: 10px; box-sizing: border-box; }
  button { margin-top: 10px; padding: 10px 22px; font-size: 15px; cursor: pointer;
           background: #1a4f8b; color: #fff; border: 0; border-radius: 6px; }
  .card { border: 1px solid #ddd; border-radius: 8px; padding: 14px; margin-top: 14px; }
  .q { font-weight: bold; } .src { color: #555; font-size: 13px; margin-top: 6px; }
  .err { color: #b00; }
</style>
</head>
<body>
<h1>보험약관 RAG <small>Korean Insurance Contract Q&A — portfolio demo</small></h1>
<p>질문을 입력하세요 (e.g. "보험금 지급 사유는 무엇인가요?" / "청약철회는 언제까지 가능한가요?")</p>
<textarea id="q" placeholder="질문…"></textarea><br>
<select id="doc"><option value="">전체 문서 (all documents)</option></select>
<button onclick="ask()">질문하기</button>
<div id="out"></div>
<script>
fetch('/documents').then(r => r.json()).then(d => {
  const sel = document.getElementById('doc');
  (d.docs || []).forEach(name => {
    const o = document.createElement('option');
    o.value = name; o.textContent = name;
    sel.appendChild(o);
  });
}).catch(() => {});
async function ask() {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  const out = document.getElementById('out');
  out.innerHTML = '<div class="card">… 검색 중</div>';
  try {
    const body = {question: q};
    const doc = document.getElementById('doc').value;
    if (doc) body.doc = doc;
    const r = await fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body)});
    const d = await r.json();
    const srcs = (d.sources || []).map((s, i) => {
      const clauses = (s.text.match(/제\s?\d+조/g) || []).filter((v, j, a) => a.indexOf(v) === j);
      const chips = clauses.map(c => `<span style="background:#1a4f8b;color:#fff;border-radius:4px;padding:1px 7px;font-size:11px;margin-right:4px">${c}</span>`).join("");
      return '<div style="margin-top:8px">[' + (i + 1) + '] ' + s.doc + ' · score ' + s.score
        + '<div>' + chips + '</div>'
        + '<div style="color:#777;font-size:12px">' + s.text + '</div></div>';
    }).join('');
    let html = '<div class="card"><div class="q">' + d.question + '</div>'
      + (d.doc ? '<div style="color:#888;font-size:12px;margin-top:2px">filtered to: ' + d.doc + '</div>' : '')
      + '<div style="margin-top:8px">'
      + (d.answer ? d.answer.replace(/\\n/g, '<br>') : '<span class="err">retrieval-only mode — no LLM key set</span>')
      + '</div><div class="src">' + srcs + '</div></div>';
    out.innerHTML = html;
  } catch (e) { out.innerHTML = '<div class="card err">' + e + '</div>'; }
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
