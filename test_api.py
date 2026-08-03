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
print("SMOKE TEST PASSED")
