#!/usr/bin/env bash
# Happy-path smoke test for the 3 HTTP client scripts.
# Requires backend reachable at $QUANT_BACKEND_URL (default 192.168.1.136:8000).
set -euo pipefail 2>/dev/null || set -euo
cd "$(dirname "$0")/.."
BASE="${QUANT_BACKEND_URL:-http://192.168.1.136:8000}"
echo "== Backend: $BASE =="

echo "-- kb_query index --"
python3 scripts/kb_query.py --base-url "$BASE" index | head -c 400 ; echo

echo "-- kb_query archives --"
python3 scripts/kb_query.py --base-url "$BASE" archives | head -c 400 ; echo

echo "-- kb_query archive (expect 404 for fake id) --"
set +e
python3 scripts/kb_query.py --base-url "$BASE" archive nonexistent-xxx
rc=$?
set -e
[ "$rc" = "2" ] && echo "404 surfaced correctly (exit 2)" || { echo "unexpected rc=$rc"; exit 1; }

echo "-- kb_query log --"
python3 scripts/kb_query.py --base-url "$BASE" log | head -c 400 ; echo

echo "All smoke checks passed."