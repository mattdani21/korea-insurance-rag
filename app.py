"""FastAPI server: local web UI + /ask endpoint.

Usage:
    uvicorn app:app --reload     # -> http://localhost:8000
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

import config
import query as q

app = FastAPI(title="보험약관 RAG demo — Korean Insurance Contract Q&A")


class Ask(BaseModel):
    question: str
    k: int = config.TOP_K


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(UI)


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
    hits = q.retrieve(body.question, body.k)
    answer = None
    if config.LLM_API_KEY:
        try:
            answer = q.ask_llm(body.question, hits)
        except Exception as e:  # noqa: BLE001
            answer = f"(LLM error: {e})"
    return JSONResponse({
        "question": body.question,
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
<button onclick="ask()">질문하기</button>
<div id="out"></div>
<script>
async function ask() {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  const out = document.getElementById('out');
  out.innerHTML = '<div class="card">… 검색 중</div>';
  try {
    const r = await fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({question: q})});
    const d = await r.json();
    let html = '<div class="card"><div class="q">' + d.question + '</div><div style="margin-top:8px">'
      + (d.answer ? d.answer.replace(/\\n/g, '<br>') : '<span class="err">retrieval-only mode — no LLM key set</span>')
      + '</div>';
    html += '<div class="src">' + d.sources.map((s,i) =>
      '<div style="margin-top:8px">[' + (i+1) + '] ' + s.doc + ' · score ' + s.score
      + '<div style="color:#777;font-size:12px">' + s.text + '</div></div>').join('') + '</div></div>';
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
