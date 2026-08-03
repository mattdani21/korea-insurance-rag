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
echo "Example (Samsung Life product terms are often linked from the product page):"
echo '  curl -L -o data/samsung_contract.pdf "<pdf-url>"'
echo
echo "After downloading PDFs into data/, re-run: python ingest.py"
echo "pypdf (in requirements.txt) handles PDF extraction."
