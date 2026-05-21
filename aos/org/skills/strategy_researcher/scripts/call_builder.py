#!/usr/bin/env python3
"""Call /strategy-builder/compile-ir on the quant backend.

This is the PRIMARY endpoint for investigation research rounds.

== Endpoint policy ==
- Investigation rounds MUST use /strategy-builder/compile-ir
- /strategy-builder/invoke is PROHIBITED for investigation flow
  (it is reserved for quant_assistant's interactive conversation mode)

Input (stdin, JSON): the request body expected by the builder endpoint.
Output (stdout, JSON): {"ok": bool, "data"|"error": ..., "status": int}
Exit codes: 0 success, 1 retryable (network), 2 business error.
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.request, urllib.error

DEFAULT_BASE = os.environ.get("QUANT_BACKEND_URL", "http://192.168.1.136:8000")
ENDPOINT = "/strategy-builder/compile-ir"


_DEFAULT_ENDPOINT = ENDPOINT


def main() -> int:
    ap = argparse.ArgumentParser(description="Invoke strategy-builder via HTTP.")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--endpoint", default=_DEFAULT_ENDPOINT, help="API endpoint path, default: %(default)s")
    ap.add_argument("--input-file", help="Read JSON body from file instead of stdin.")
    args = ap.parse_args()

    raw = open(args.input_file, "r", encoding="utf-8").read() if args.input_file else sys.stdin.read()
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": "invalid_json_input", "detail": str(e)}))
        return 2

    url = args.base_url.rstrip("/") + args.endpoint
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            print(json.dumps({"ok": True, "status": resp.status, "data": payload}, ensure_ascii=False))
            return 0
    except urllib.error.HTTPError as e:
        detail_raw = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(detail_raw)
        except json.JSONDecodeError:
            detail = {"raw": detail_raw}
        print(json.dumps({"ok": False, "error": f"http_{e.code}", "status": e.code, "detail": detail}, ensure_ascii=False))
        return 2
    except (urllib.error.URLError, TimeoutError) as e:
        print(json.dumps({"ok": False, "error": "network_error", "detail": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())