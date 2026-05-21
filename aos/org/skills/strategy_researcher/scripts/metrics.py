#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metrics.py — 研究回合指标聚合 & 格式化工具（纯标准库）

用途：
  strategy-researcher 数字员工在完成一个 ticket 的 N 轮研究后，
  用本工具把各轮 round_<N>.json 里的回测指标聚合为 metrics.json，
  并产出跨轮对比 markdown 表格，供 summary.md / 研究报告引用。

边界：
  - 不驱动研究流程、不调 HTTP、不调 LLM。
  - 研究循环决策在智能体（见 prompts/research_workflow.md）。
  - 本工具只做确定性数学与格式化。

输入约定：
  --run-dir 指向 ${RESEARCH_RUNS}/{ticket_id}/
  目录下若干 round_<N>.json，每份支持两种路径：

  路径 A（旧）：builder_response.backtest.metrics
    {
      "hypothesis": "...",
      "builder_response": {
        "backtest": {
          "run_id": "...",
          "metrics":       {"sharpe_ratio": ..., ...},
          "train_metrics": {...},
          "test_metrics":  {...},
          "phase_stats":   {...}
        }
      }
    }

  路径 B（新 v0.2.1）：compile-ir + execution-config 分离
    {
      "hypothesis": "...",
      "builder_response": {"ok": true, "data": {...}},       # compile-ir 响应
      "backtest_response": {                                # execution-config 响应
        "ok": true, "run_id": "...", "status": "completed",
        "raw": {
          "data": {
            "run_id": "...",
            "metrics": {"sharpe_ratio": ..., ...},
            "train_metrics": {...},
            "test_metrics": {...},
            "phase_stats": {...}
          }
        }
      }
    }

  某轮没有回测（builder_failed 等） → 两个字段均缺失/None。

  本工具自动检测两条路径，优先从 backtest_response 提取，
  回退到 builder_response.backtest，不再将新路径误判为 no_backtest。

输出：
  - 写入 <run-dir>/metrics.json
  - stdout 打印 markdown 对比表

退出码：
  0 正常 · 2 不可恢复（run-dir 不存在、未处理异常）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# 报告中主要对比维度（与 data/knowledge/schema.md §2.2 对齐，4 位小数）
SUMMARY_METRICS = [
    "sharpe_ratio",
    "annualized_return",
    "max_drawdown",
    "calmar_ratio",
    "win_rate",
]

ROUND_FILE_RE = re.compile(r"^round_(\d+)\.json$")


def _extract_backtest(data: dict) -> dict | None:
    """Extract backtest metrics from round data, supporting both old and new paths.

    Priority:
    1. backtest_response (new path: compile-ir + execution-config)
    2. builder_response.backtest (old path: single-invoke with auto_backtest)

    Returns a dict with keys: run_id, metrics, train_metrics, test_metrics,
    never_triggered_transitions, or None if no backtest data found.
    """
    # Path B (new): backtest_response from execution-config
    bt_resp = data.get("backtest_response") or {}
    if bt_resp.get("ok"):
        # Direct success format
        raw = bt_resp.get("raw") or bt_resp
        bt_data = raw.get("data") or {}
        metrics = bt_data.get("metrics") or None
        if metrics:
            return {
                "run_id": bt_data.get("run_id") or bt_resp.get("run_id"),
                "metrics": metrics,
                "train_metrics": bt_data.get("train_metrics"),
                "test_metrics": bt_data.get("test_metrics"),
                "never_triggered_transitions":
                    (bt_data.get("phase_stats") or {}).get("never_triggered_transitions"),
            }

    # Path A (old): builder_response.backtest.metrics
    bt = (data.get("builder_response") or {}).get("backtest") or {}
    metrics = bt.get("metrics") or None
    if metrics:
        return {
            "run_id": bt.get("run_id"),
            "metrics": metrics,
            "train_metrics": bt.get("train_metrics"),
            "test_metrics": bt.get("test_metrics"),
            "never_triggered_transitions":
                (bt.get("phase_stats") or {}).get("never_triggered_transitions"),
        }

    return None


def load_rounds(run_dir: Path) -> list[dict[str, Any]]:
    rounds: list[dict[str, Any]] = []
    for p in sorted(run_dir.iterdir()):
        m = ROUND_FILE_RE.match(p.name)
        if not m:
            continue
        idx = int(m.group(1))
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            rounds.append({"round": idx, "status": "parse_error", "error": str(e)})
            continue

        bt = _extract_backtest(data)
        if bt is None:
            rounds.append({
                "round": idx,
                "status": "no_backtest",
                "hypothesis": data.get("hypothesis"),
            })
            continue

        rounds.append({
            "round": idx,
            "status": "ok",
            "hypothesis": data.get("hypothesis"),
            "run_id": bt["run_id"],
            "metrics": bt["metrics"],
            "train_metrics": bt["train_metrics"],
            "test_metrics": bt["test_metrics"],
            "never_triggered_transitions": bt["never_triggered_transitions"],
        })
    rounds.sort(key=lambda r: r["round"])
    return rounds


def fmt(value: Any, decimals: int = 4) -> str:
    if value is None:
        return "N/A"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if f != f:  # NaN
        return "N/A"
    return f"{f:.{decimals}f}"


def pick_best(rounds: list[dict], metric: str) -> dict | None:
    best = None
    for r in rounds:
        if r.get("status") != "ok":
            continue
        v = (r.get("metrics") or {}).get(metric)
        try:
            vf = float(v)
        except (TypeError, ValueError):
            continue
        if vf != vf:  # NaN
            continue
        if best is None or vf > best["value"]:
            best = {"round": r["round"], "run_id": r.get("run_id"),
                    "metric": metric, "value": vf}
    return best


def summarize(rounds: list[dict]) -> dict:
    ok_rounds = [r for r in rounds if r.get("status") == "ok"]
    return {
        "num_rounds": len(rounds),
        "num_with_backtest": len(ok_rounds),
        "best_by_sharpe_ratio": pick_best(ok_rounds, "sharpe_ratio"),
        "best_by_calmar_ratio": pick_best(ok_rounds, "calmar_ratio"),
    }


def render_markdown_table(rounds: list[dict]) -> str:
    headers = ["Round", "Status"] + SUMMARY_METRICS + ["Run ID"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for r in rounds:
        if r.get("status") != "ok":
            row = [str(r["round"]), r.get("status", "?")] \
                  + ["—"] * len(SUMMARY_METRICS) + ["—"]
        else:
            row = [str(r["round"]), "ok"]
            m = r.get("metrics") or {}
            for key in SUMMARY_METRICS:
                row.append(fmt(m.get(key)))
            row.append(r.get("run_id") or "—")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def cmd_aggregate(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.is_dir():
        print(json.dumps(
            {"ok": False, "error": "run_dir_not_found", "path": str(run_dir)},
            ensure_ascii=False))
        return 2

    rounds = load_rounds(run_dir)
    payload = {
        "ticket_id": run_dir.name,
        "run_dir": str(run_dir),
        "rounds": rounds,
        "summary": summarize(rounds),
    }
    out_path = run_dir / "metrics.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(render_markdown_table(rounds))
    print()
    print(f"# metrics.json written: {out_path}")
    print(f"# summary: {json.dumps(payload['summary'], ensure_ascii=False)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate research-run round metrics (stdlib only).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_agg = sub.add_parser(
        "aggregate",
        help="Read round_*.json from run-dir, write metrics.json, print markdown table.")
    p_agg.add_argument(
        "--run-dir", required=True,
        help="Path to ${RESEARCH_RUNS}/{ticket_id}/")
    p_agg.set_defaults(func=cmd_aggregate)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as e:  # 最后兜底
        print(json.dumps(
            {"ok": False, "error": "unhandled", "detail": str(e)},
            ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())