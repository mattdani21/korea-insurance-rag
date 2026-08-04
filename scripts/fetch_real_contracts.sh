#!/usr/bin/env bash
# Fetch REAL Korean insurance contract (보험약관) PDFs into data/ for a production-grade corpus.
# NOTE: many Korean insurer sites geo-block overseas IPs — run from Korea, via VPN, or ask your partner in Seoul.
set -e
cd "$(dirname "$0")/.."

mkdir -p data
echo "Candidate sources (verify URLs yourself — insurer sites change them often):"
cat <<'EOF'
  - Samsung Life:     https://www.samsunglife.com → 상품 → 약관 (PDF)
  - Hanwha Life:      https://www.hanwhalife.com  → 약관자료실
  - Kyobo Life:       https://www.kyobolife.co.kr (geo-blocks overseas IPs)
  - FSS (regulator):  https://www.fss.or.kr  → 보험약관 자료
  - KIRI:             https://www.kiri.or.kr (Korea Insurance Research Institute)
  - Carrot (insurtech): https://www.carrotins.com → 약관
EOF

echo
echo "Concrete path (recommended — use your partner in Seoul):"
cat <<'EOF'
  1. Ask your partner (or use a VPN) to open any Korean insurer's product page:
       - Samsung Life:  https://www.samsunglife.com  → 상품 → [종신보험/건강보험] → 약관/상품요약서
       - Hanwha Life:   https://www.hanwhalife.com   → 상품 → 약관자료실
       - Carrot:        https://www.carrotins.com    → 약관
  2. Save the 약관 PDF into this data/ directory (e.g. data/samsung_life_terms.pdf).
  3. Repeat for 2–4 different products/insurers (variety beats volume for a demo corpus).
  4. Re-run: python ingest.py  (pypdf extracts the text; see requirements.txt)
  5. Re-check: python eval.py  (expect hit@1 to shift with real clauses)
EOF

echo
echo "Example direct download (works for some publicly linked PDFs):"
echo '  curl -L -o data/samsung_contract.pdf "<pdf-url>"'
echo
echo "After downloading PDFs into data/, re-run: python ingest.py"
echo "pypdf (in requirements.txt) handles PDF extraction."
