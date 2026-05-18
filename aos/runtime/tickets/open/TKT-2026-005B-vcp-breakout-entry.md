---
ticket_id: TKT-2026-00X
title: VCP 形态突破点入场策略研究
intent_type: investigation
assigned_to: agent-strategy-researcher
status: open
priority: normal
created_by: Boss
created_at: 2026-05-08
tags: [breakout, trend_continuation, volume, consolidation, vcp]
---

## 研究目标

验证并落地如下形态的交易策略：

> 标的此前处于明确上升趋势 → 经历一轮时间和幅度有限的回调 →
> 回调末期价格结构趋于紧凑（波动收敛、换手萎缩）→
> 在某一日出现明显放量拉升并突破前期整理区间高点 →
> 以突破日或次日开盘作为买入点。

回答以下问题：
1. 该形态在 A 股市场是否存在可观测、可量化的统计优势？
2. "趋势""调整""紧凑""放量""突破"五要素中，哪一条对收益贡献最大？
   哪一条可以放宽甚至去掉而不伤害 sharpe？
3. 该策略的失效模式是什么（指数级熊市？题材股泡沫破裂？小市值流动性枯竭？）
4. 相对 KB 中现有 `breakout` / `trend_following` 档案的最佳 sharpe，能否提升？

## 约束

- **Universe**：沪深 A 股，剔除 ST / *ST / 上市不足 250 交易日的新股；
  日均成交额中位数 > 5000 万（过滤流动性太差的标的）
- **时间窗**：2018-01-01 ~ 2024-12-31，train/test 按 70/30 时间切分
  （不要随机切分，形态策略对时序敏感）
- **持仓约束**：多头 only；单笔仓位 ≤ 10%；同时持仓 ≤ 10 只
- **成本假设**：双边 0.0012（含佣金+印花税+滑点），按你们 backtest 默认即可
- **禁用**：未来函数、日内高频、杠杆、衍生品
- **主指标**：sharpe_ratio（样本外）；辅助关注 calmar、最大回撤、胜率、盈亏比

## 研究员的裁量空间（明确授权）

以下你自己决定，不需要问我：
- "前期趋势"的定义（多少日？MA 斜率？涨幅阈值？）
- "调整"的刻画（时间窗口？最大回撤百分比？）
- "紧凑"如何量化（ATR 收敛？布林带宽？真实波幅比？）
- "放量"的倍数（vs MA5 / MA20？几倍？）
- "突破"参照哪条线（整理区间 high？前高？某条 MA？）
- 出场规则（固定止盈？追踪止损？时间止损？MA 破位？）

建议第 1 轮用**最简定义**先跑出基线，后续轮次逐一放宽 / 收紧单个要素，
符合 `hypothesis_heuristics.md` 的"单一变量"原则。

## 成功标准

触发以下任一即视为工单完成：
- 找到一个样本外 sharpe > 1.2、最大回撤 < 25% 的参数组合，且机制解释清晰
- 或，证明该形态在 A 股**不成立**（样本外 sharpe ≤ 0.5 且跨多轮假设无法改善），
  附失效原因分析——**负向结论同样有价值，不要凑数**

## 交付要求

按 `prompts/report_template.md` 标准交付，报告命名：
`TKT-2026-00X-vcp-breakout-entry.md`

## Worklog

### 2026-05-18 — agent-strategy-researcher
- **Phase 0**: git pull --rebase ✅
- **Phase 1**: intent=investigation, assigned=agent-strategy-researcher ✅
- **Phase 2**: KB reachable; archives listed 9 strategies (trend_following/breakout intent, none VCP-specific); log read; index read. Best existing test Sharpe ~1.52 (stg_20260414_1effbf).
- **Phase 3 Round 1**:
  - Hypothesis: 4-phase VCP IR (watch→pullback→breakout→holding) with 5 conditions
  - Builder: stg_20260518_2ee7d5 created (4 phases)
  - Backtest: run-1547739a-20180101-20241231-34868704 via call_backtest.py
  - Result: **0 trades** — all conditions too restrictive, never triggered. total_return=-1.0, sharpe=N/A
  - Analysis: IR watch→pullback transition required volume>MA20*1.5 AND ATR contraction <0.8 AND drawdown<0.6 simultaneously — conflicting conditions prevented entry
- **Phase 3 Round 2**: Attempted simplified 2-phase IR. Builder session corrupted after conversational loop. Backend at 192.168.1.136:8000 became unresponsive after hanging backtest requests.
- **Status**: `paused_for_boss_review` — backend unreachable, only 1/5 planned rounds completed with 0 trades
- **Tags**: `git_sync_ok`, `builder_failed_round2`, `backend_unreachable`, `paused_for_boss_review`