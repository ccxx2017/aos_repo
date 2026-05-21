#!/usr/bin/env python3
"""Query the knowledge base HTTP API.

Subcommands:
  index                  -> GET /api/v1/knowledge/index
  log                    -> GET /api/v1/knowledge/log
  archives               -> GET /api/v1/knowledge/archives
  archive <strategy_id>  -> GET /api/v1/knowledge/archives/<id>

Output (stdout, JSON):
  index / log / archive -> {"ok": true, "content": "<markdown>"}
  archives              -> {"ok": true, "archives": [{...}, ...]}
  errors                -> {"ok": false, "error": "...", "status": int, "detail": ...}
Exit codes: 0 success, 1 retryable (network), 2 business error (incl. 404).
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

DEFAULT_BASE = os.environ.get("QUANT_BACKEND_URL", "http://192.168.1.136:8000")
PREFIX = "/api/v1/knowledge"


def _get(base_url: str, path: str, timeout: float) -> tuple[int, object]:
    url = base_url.rstrip("/") + path
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail_raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(detail_raw)
        except json.JSONDecodeError:
            return e.code, {"raw": detail_raw}


def main() -> int:
    ap = argparse.ArgumentParser(description="Knowledge-base HTTP client.")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--timeout", type=float, default=30.0)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index")
    sub.add_parser("log")
    sub.add_parser("archives")
    p_arch = sub.add_parser("archive")
    p_arch.add_argument("strategy_id")
    args = ap.parse_args()

    if args.cmd == "index":
        path = f"{PREFIX}/index"
    elif args.cmd == "log":
        path = f"{PREFIX}/log"
    elif args.cmd == "archives":
        path = f"{PREFIX}/archives"
    elif args.cmd == "archive":
        path = f"{PREFIX}/archives/{urllib.parse.quote(args.strategy_id, safe='')}"
    else:
        print(json.dumps({"ok": False, "error": "unknown_subcommand"}))
        return 2

    try:
        status, payload = _get(args.base_url, path, args.timeout)
    except (urllib.error.URLError, TimeoutError) as e:
        print(json.dumps({"ok": False, "error": "network_error", "detail": str(e)}))
        return 1

    if status == 200:
        if args.cmd == "archives":
            print(json.dumps({"ok": True, "archives": payload}, ensure_ascii=False))
        elif args.cmd == "archive":
            # archive endpoint returns a dict {strategy_id, content, file_path}
            content = payload.get("content") if isinstance(payload, dict) else None
            print(json.dumps({
                "ok": True,
                "strategy_id": payload.get("strategy_id") if isinstance(payload, dict) else None,
                "content": content,
                "file_path": payload.get("file_path") if isinstance(payload, dict) else None,
            }, ensure_ascii=False))
        else:
            # index / log endpoints return a raw markdown string
            print(json.dumps({"ok": True, "content": payload}, ensure_ascii=False))
        return 0

    print(json.dumps({"ok": False, "error": f"http_{status}", "status": status, "detail": payload},
                     ensure_ascii=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())