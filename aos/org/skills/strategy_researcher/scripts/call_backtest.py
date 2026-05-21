#!/usr/bin/env python3
"""Call /backtests/execution-config with automatic retry on DATA_MISSING_SYNC_REQUIRED.

本脚本受 TKT-2026-005C 资源闸约束。
详见 aos/runtime/tickets/open/TKT-2026-005C-backtest-safety-guard.md

闸值（默认硬上限，超过须 AOS_BOSS_OVERRIDE=1 环境变量）：
- max_symbols=20  — 单次回测最多 20 只标的
- max_years=3     — 回测时间窗口最多 3 年
- timeout=90s     — HTTP 请求超时

Input (stdin, JSON): {"execution_config": {...}, "run_id": "optional"}
Output (stdout, JSON): {"ok": bool, "run_id": "...", "status": "completed", "retried": bool, ...}
Exit codes: 0 success, 1 retryable (network), 2 business error.

Behavior:
- On HTTP 200, extract data.run_id / data.status and return.
- On HTTP 400 with code=DATA_MISSING_SYNC_REQUIRED, remove missing_symbols from
  execution_config.universe.symbols and retry ONCE. If still failing, return error.
- Other 400 codes (INVALID_EXECUTION_CONFIG / UNSUPPORTED_UNIVERSE_TYPE / EMPTY_UNIVERSE)
  are surfaced immediately so the caller LLM can revise the hypothesis.
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.request, urllib.error
from typing import Any

DEFAULT_BASE = os.environ.get("QUANT_BACKEND_URL", "http://192.168.1.136:8000")
ENDPOINT = "/backtests/execution-config"

# TKT-2026-005C 资源闸常量
MAX_SYMBOLS_DEFAULT = 20
MAX_YEARS_DEFAULT = 3
REQUEST_TIMEOUT_SEC = 90
BOSS_OVERRIDE_ENV = "AOS_BOSS_OVERRIDE"


class BacktestGuardrailError(ValueError):
    """Raised when request parameters exceed safety guardrails without BOSS_OVERRIDE.

    Attributes:
        exceeded: list of string descriptions of exceeded limits.
        hint: human-readable hint for the caller.
        boss_override_required: always True when raised.
    """
    def __init__(self, exceeded: list[str]):
        self.exceeded = exceeded
        self.boss_override_required = True
        hints: list[str] = []
        for e in exceeded:
            hints.append(e)
        self.hint = "; ".join(hints)
        super().__init__(self.hint)


def _validate_request(body: dict, boss_override: bool) -> None:
    """Validate request body against TKT-2026-005C resource guardrails.

    Raises BacktestGuardrailError if any limit is exceeded and BOSS_OVERRIDE is not set.
    """
    exceeded: list[str] = []

    # Check universe.symbols count
    try:
        symbols = body["execution_config"]["universe"]["symbols"]
        symbol_count = len(symbols)
        if symbol_count > MAX_SYMBOLS_DEFAULT:
            exceeded.append(
                f"symbols={symbol_count} > MAX_SYMBOLS_DEFAULT={MAX_SYMBOLS_DEFAULT}; "
                f"set {BOSS_OVERRIDE_ENV}=1 to override"
            )
    except (KeyError, TypeError):
        pass

    # Check backtest time span years
    try:
        params = body["execution_config"]["backtest_params"]
        start_str = params.get("start_date") or params.get("start") or ""
        end_str = params.get("end_date") or params.get("end") or ""
        # Parse ISO dates: "2018-01-01" or "20180101"
        import re
        def _parse_year(s: str) -> int | None:
            m = re.match(r"(\d{4})", s)
            return int(m.group(1)) if m else None
        start_year = _parse_year(start_str)
        end_year = _parse_year(end_str)
        if start_year is not None and end_year is not None:
            years = end_year - start_year
            if years > MAX_YEARS_DEFAULT:
                exceeded.append(
                    f"years={years} (from {start_year} to {end_year}) > MAX_YEARS_DEFAULT={MAX_YEARS_DEFAULT}; "
                    f"set {BOSS_OVERRIDE_ENV}=1 to override"
                )
    except (KeyError, TypeError):
        pass

    if exceeded and not boss_override:
        raise BacktestGuardrailError(exceeded)
    elif exceeded and boss_override:
        # Log warning but allow
        import logging
        logging.warning(
            "BOSS_OVERRIDE active for %s", "; ".join(exceeded)
        )
        print(
            json.dumps({
                "ok": True,
                "warning": "BOSS_OVERRIDE active",
                "details": exceeded,
            }),
            file=sys.stderr,
        )


def _post(base_url: str, body: dict, timeout: float) -> tuple[int, dict]:
    url = base_url.rstrip("/") + ENDPOINT
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail_raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(detail_raw)
        except json.JSONDecodeError:
            return e.code, {"raw": detail_raw}


def _prune_universe(body: dict, missing: list[str]) -> dict:
    """Return a deep-enough copy with missing symbols removed from universe.symbols."""
    import copy
    pruned = copy.deepcopy(body)
    try:
        symbols = pruned["execution_config"]["universe"]["symbols"]
        pruned["execution_config"]["universe"]["symbols"] = [s for s in symbols if s not in set(missing)]
    except (KeyError, TypeError):
        pass
    return pruned


def _summarize_success(payload: dict, retried: bool) -> dict:
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    return {
        "ok": True,
        "retried": retried,
        "run_id": data.get("run_id"),
        "task_id": data.get("task_id"),
        "status": data.get("status"),
        "message": payload.get("message"),
        "raw": payload,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Invoke execution-config backtest via HTTP.")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--timeout", type=float, default=REQUEST_TIMEOUT_SEC,
                    help=f"HTTP request timeout in seconds (default {REQUEST_TIMEOUT_SEC}, "
                         f"hard limit per TKT-2026-005C)")
    ap.add_argument("--input-file", help="Read JSON body from file instead of stdin.")
    ap.add_argument("--no-retry-on-missing-data", action="store_true",
                    help="Disable automatic retry after pruning missing_symbols.")
    ap.add_argument("--max-symbols", type=int, default=MAX_SYMBOLS_DEFAULT,
                    help=f"Max universe symbols (default {MAX_SYMBOLS_DEFAULT}, "
                         f"hard limit per TKT-2026-005C). Exceeding requires AOS_BOSS_OVERRIDE=1.")
    ap.add_argument("--max-years", type=int, default=MAX_YEARS_DEFAULT,
                    help=f"Max backtest time span in years (default {MAX_YEARS_DEFAULT}, "
                         f"hard limit per TKT-2026-005C). Exceeding requires AOS_BOSS_OVERRIDE=1.")
    args = ap.parse_args()

    raw = open(args.input_file, "r", encoding="utf-8").read() if args.input_file else sys.stdin.read()
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": "invalid_json_input", "detail": str(e)}))
        return 2

    # --- TKT-2026-005C 资源闸: validate before sending ---
    boss_override = os.environ.get(BOSS_OVERRIDE_ENV) == "1"
    try:
        _validate_request(body, boss_override)
    except BacktestGuardrailError as e:
        print(json.dumps({
            "ok": False,
            "error_type": "guardrail_violation",
            "hint": e.hint,
            "boss_override_required": True,
            "exceeded": e.exceeded,
        }, ensure_ascii=False))
        return 2

    try:
        status, payload = _post(args.base_url, body, args.timeout)
    except (urllib.error.URLError, TimeoutError) as e:
        print(json.dumps({
            "ok": False,
            "error_type": "network_error",
            "hint": f"Backend unreachable or timed out after {args.timeout}s",
            "boss_override_required": False,
            "detail": str(e),
        }))
        return 1

    if status == 200 and isinstance(payload, dict) and payload.get("success"):
        print(json.dumps(_summarize_success(payload, retried=False), ensure_ascii=False))
        return 0

    # HTTP 400 branch: inspect error code
    code = payload.get("code") if isinstance(payload, dict) else None
    if status == 400 and code == "DATA_MISSING_SYNC_REQUIRED" and not args.no_retry_on_missing_data:
        missing = payload.get("missing_symbols") or []
        if missing:
            pruned = _prune_universe(body, missing)
            remaining = pruned.get("execution_config", {}).get("universe", {}).get("symbols", [])
            if not remaining:
                print(json.dumps({
                    "ok": False, "error": "empty_universe_after_prune",
                    "status": 400, "missing_symbols": missing, "detail": payload,
                }, ensure_ascii=False))
                return 2
            try:
                status2, payload2 = _post(args.base_url, pruned, args.timeout)
            except (urllib.error.URLError, TimeoutError) as e:
                print(json.dumps({
                    "ok": False, "error": "network_error_on_retry",
                    "error_type": "network_error",
                    "hint": f"Backend unreachable on retry after {args.timeout}s",
                    "boss_override_required": False,
                    "detail": str(e),
                }))
                return 1
            if status2 == 200 and isinstance(payload2, dict) and payload2.get("success"):
                summary = _summarize_success(payload2, retried=True)
                summary["pruned_symbols"] = missing
                print(json.dumps(summary, ensure_ascii=False))
                return 0
            print(json.dumps({
                "ok": False, "error": "retry_failed", "status": status2,
                "pruned_symbols": missing, "detail": payload2,
            }, ensure_ascii=False))
            return 2

    # Any other non-success
    print(json.dumps({
        "ok": False,
        "error_type": f"http_{status}",
        "hint": f"Backend returned HTTP {status}",
        "boss_override_required": False,
        "code": code,
        "detail": payload,
    }, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())
