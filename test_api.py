"""Smoke test for the FastAPI app (no server needed)."""
from fastapi.testclient import TestClient

import app

c = TestClient(app.app)
r1 = c.get("/")
print("GET / :", r1.status_code, "HTML" if "보험약관" in r1.text else "???")
r2 = c.post("/ask", json={"question": "보험금 지급 사유는 무엇인가요?"})
j = r2.json()
print("POST /ask :", r2.status_code, "| sources:", len(j["sources"]),
      "| answer:", (j["answer"] or "retrieval-only (no key in this process)")[:80])
assert r1.status_code == 200 and r2.status_code == 200 and len(j["sources"]) >= 3

# Multi-doc filtering: /documents lists the corpus; /ask?doc= restricts sources
r3 = c.get("/documents")
docs = r3.json()["docs"]
print("GET /documents :", r3.status_code, "| docs:", docs)
assert r3.status_code == 200 and len(docs) >= 1

top_doc = j["sources"][0]["doc"]  # filter to the doc the unfiltered top-1 came from
r4 = c.post("/ask", json={"question": "보험금 지급 사유는 무엇인가요?", "doc": top_doc})
j4 = r4.json()
print("POST /ask filtered:", r4.status_code, "| sources:", len(j4["sources"]), "| doc:", j4["doc"])
assert r4.status_code == 200 and j4["doc"] == top_doc and len(j4["sources"]) >= 1
assert all(s["doc"] == top_doc for s in j4["sources"]), "filter leaked sources from other docs"

r5 = c.post("/ask", json={"question": "보험금 지급 사유는 무엇인가요?", "doc": "no-such-doc-xyz"})
assert r5.status_code == 200 and len(r5.json()["sources"]) == 0
print("FILTER TESTS PASSED")

print("SMOKE TEST PASSED")
