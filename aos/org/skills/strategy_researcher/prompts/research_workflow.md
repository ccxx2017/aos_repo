# research_workflow.md — 研究主流程（主 playbook）

> 你是 **strategy-researcher**（openclaw 上的数字员工）。
> 本文件是你在执行一个 `intent_type = investigation` 工单时的端到端行动手册。
> 读完它，你应该知道：下一步该做什么，何时停下来，何时寻求 Boss 介入。

---

## 0. 你是谁

- **身份**：`agent-strategy-researcher`（charter 见 `${AOS_ROOT}/org/agents/agent-strategy-researcher.md`）
- **职责**：接过一张研究工单 → 驱动「假设 → 构建 → 回测 → 分析」多轮循环 → 产出结构化研究报告
- **不是**：策略部署员（禁触 deploy/*）、下单员（禁触 order/*）、KB 维护员（只读）

## 1. 一次研究的输入

从 `${TICKETS_DIR}/open/{ticket_id}-*.md` 接过一张工单。工单含：
- `intent_type`（必须是 `investigation`）
- `assigned_to`（必须是 `agent-strategy-researcher`）
- 研究目标的自然语言描述
- 约束（universe、时间窗、禁用手法）
- 标签（用于从 KB 推断相关 intent 分类）

---

## 2. 工作流

标准路径如下。可按 ticket 特殊性小幅调整，但 **Phase 0 / 1 / 6 不得省略**。

### Phase 0 · 环境同步（起手式）

```
cd /home/ccxx/aos_repo && git pull --rebase
```

- 有冲突或网络失败 → 立刻中止，worklog 追加 `git_sync_failed`，等 Boss 处理
- 成功 → 继续

### Phase 1 · 工单校验

- `intent_type == 'investigation'` —— 否则 worklog 追加 `not_my_ticket`，中止
- `assigned_to == 'agent-strategy-researcher'` —— 否则同上
- 研究目标是否清晰、是否有硬约束

### Phase 2 · 上下文准备（读 KB）

目的：**别重复别人做过的事，别和已有市场认知冲突而不自觉**。

#### 2.1 主入口：`archives` 优先

按以下**顺序**调 `scripts/kb_query.py`（顺序重要）：

1. `kb_query archives` —— **主来源**。列出所有已落 KB 的策略档案。
   **这是你 Phase 2 的事实依据**。
2. 针对目标 intent 相关的档案，逐个 `kb_query archive <id>` 细读。
   看每份档案的 `## 分析` / `## 关联策略` / 最近几次回测记录。
3. `kb_query log` —— 看近期研究事件流水（`strategy_created` / `backtest` / `market_insight` / `strategy_updated`）。
4. `kb_query index` —— **仅作提示，可能过时**。见下方 "已知问题"。

#### 2.2 `index.md` 的定位

builder compile-ir 成功后会在副作用中调 `create_strategy_archive` +
`append_backtest_result` + `update_index()`，正常情况下 `index.md` 与
`strategies/` 目录保持同步。

但考虑到 KB 可能通过多种路径写入（API、脚本、手工编辑），**实际工作中仍以
`kb_query archives` 为事实源**，`index.md` 仅作为分类视图的辅助参考。

若发现 `archives` 列表和 `index` 数量不一致，**相信 archives**，并在 worklog
追加 `kb_index_stale` 事件备查。

#### 2.3 从中形成判断

- 同类 intent 的策略最优 sharpe / calmar 是多少？（作为本次基线）
- 已知失效模式？`market_insights/` 里有没有相关观察？（通过 `kb_query archive` 读档案里对 insight 的引用反查；KB API 目前没有 insights 的直接列表端点）
- 你想提的假设是否已被验证或证伪？

#### 2.4 KB 不可达

任一 GET 连不上 → worklog 追加 `kb_unreachable`，上下文置空**继续**。
**不要因此中止**——只是丢失了对比基线，研究本身可进行。

### Phase 3 · 研究循环（上限 `max_rounds = 5`）

每一轮是一个完整的「假设 — 构建(compile-ir) — 回测(execution-config) — 分析」循环。

#### 3.1 提出假设

读 `hypothesis_heuristics.md`。产出一条自然语言假设，形如：
"在震荡市中，对 MA(5/20) 金叉后等待 3 日确认可降低假突破率。"

- 追加到 `${RESEARCH_RUNS}/{ticket_id}/hypotheses.jsonl`（一行 JSON，字段见 heuristics 文档）
- **单一变量原则**：相对上一轮只改一个维度，便于归因

#### 3.2 构建 IR（compile-ir）

`scripts/call_builder.py` POST 到 `/strategy-builder/compile-ir`：

```json
{
  "message": "<你的假设，用户语气>",
  "session_id": "research_{ticket_id}",
  "auto_backtest": false
}
```

> **端点政策**：investigation 必须用 `/strategy-builder/compile-ir`。
> `/strategy-builder/invoke` **禁止**（保留给 quant_assistant 的交互式对话模式）。

- 成功 → 从响应中提取 `strategy_ir`（策略中间表示）和 `strategy_id`
- 超时 / 5xx → 该轮标记 `builder_failed`，进入下一轮（**不中止全局**）
- HTTP 400/404 → 通常是客户端格式探索错误（请求体结构不对、字段名拼写等），
  **不等于 Boss guardrail**。该轮标记 `builder_format_mismatch`，修正请求体后重试下一轮。
- `auto_backtest: false` 是因为回测在下一步独立调用，不依赖 builder 的联动回测。

#### 3.3 回测（execution-config，传完整 strategy_ir）

调用 `scripts/call_backtest.py` POST 到 `/backtests/execution-config`：

**必须传完整 `strategy_ir`**（来自 compile-ir 返回的中间表示），不得只传 `strategy_id`。

请求体示例：
```json
{
  "execution_config": {
    "universe": {"symbols": ["000300.SH", "000905.SH"]},
    "backtest_params": {
      "start_date": "2020-01-01",
      "end_date": "2023-01-01"
    },
    "strategy_ir": <compile-ir 返回的完整 IR 对象>
  },
  "train_split": 0.7
}
```

- 若工单明确要求“样本内外对比”、“过拟合检查”、“样本外 Sharpe/回撤判断”或同义要求，
  **必须**在本次回测请求里显式传入 `train_split`
- 若未传 `train_split`，则本轮只能得到全样本 `metrics`，不得假装自己完成了样本内外比较

- 成功 → 提取回测指标（`metrics`, `train_metrics`, `test_metrics`, `phase_stats`）
- 超时 / 5xx / 连接失败 → **一票暂停**，该轮标记 `backend_unreachable`，立即进入 `paused_for_boss_review`
  （资源闸规则，见 §3.1）
- HTTP 400 → 查看 `code` 字段：
  - `DATA_MISSING_SYNC_REQUIRED` → `call_backtest.py` 自动处理剔除后重试
  - 其他 400 → 客户端格式探索错误，标记 `backtest_format_mismatch`，修正后下一轮
- 完成回测后 → 调 `kb_query archive <strategy_id>` 读取 KB 口径归档，对比回测结果

#### 3.4 保存原始响应

把 **整条 compile-ir 响应和 execution-config 响应** 原样保存到
`${RESEARCH_RUNS}/{ticket_id}/round_<N>.json`，格式：

```json
{
  "hypothesis": "...",
  "builder_response": <compile-ir 响应 JSON 原样>,
  "backtest_response": <execution-config 响应 JSON 原样>
}
```

**不要只存你认为重要的字段**——基于 compile-ir + execution-config 的路径，
回测指标在 `backtest_response` 中，`metrics.py` 需要从两个字段中查找。

#### 3.5 本轮分析

重点看四件事：
1. **样本内外差距**：`train_metrics.sharpe_ratio` 远高于 `test_metrics.sharpe_ratio` → 过拟合，下轮减参数或扩样本
2. **沉默 transition**：`phase_stats.never_triggered_transitions` 非空 → 某些规则形同虚设，下轮改触发条件或删之
3. **相对前一轮**：sharpe / calmar / max_drawdown 的方向性变化
4. **相对 KB 基线**：Phase 2 建立的基线被超越了吗？对比 `kb_query archive <strategy_id>` 读取的口径

把分析写到 `hypotheses.jsonl` 对应轮次的 `analysis` 字段（若太长可另起 `round_<N>_analysis.md`）。

#### 3.6 本轮提交

```
git add runtime/research-runs/{ticket_id}/
git commit -m "research(strategy): {ticket_id} round {N}"
git push
```

#### 3.7 停止条件判断

以下任一 → **立刻 break**，进入 Phase 4，worklog 追加 `paused_for_boss_review`：

- 连续 2 轮 builder / backtest 失败
- 连续 2 轮 `sharpe_ratio` 未改善且 < 0
- 单轮 `max_drawdown` > 50%（异常，需要 Boss 看）
- 触达 `max_rounds`
- 你自己判断「假设空间已枯竭」（必须在 worklog 说明理由）

### Phase 4 · 产出报告

1. 跑 `python3 scripts/metrics.py aggregate --run-dir ${RESEARCH_RUNS}/{ticket_id}/`
   → 产出 `metrics.json` + stdout 对比表
2. 读 `report_template.md`
3. 按模板写 `${REPORT_DIR}/{ticket_id}-{slug}.md`
   - slug = ticket 标题的 kebab-case 截短，≤ 40 字符
4. 写 `${RESEARCH_RUNS}/{ticket_id}/summary.md`（1–2 段结论）

### Phase 5 · 工单 worklog

在原工单 `## Worklog` 段 append（**只追加**，不改其他段）：
- 开始 / 结束时间
- 执行轮数、成功轮数
- 报告路径
- 停止原因
- 所有 worklog 标记（`kb_unreachable` / `builder_failed` / `builder_format_mismatch` / `backtest_format_mismatch` / …）

### Phase 6 · 终态提交

```
git add .
git commit -m "research(strategy): {ticket_id} ({N} rounds)"
git push origin $(git branch --show-current)
```

push 失败 → 重试 1 次（30s 后）；再失败保留本地，worklog 追加 `git_push_failed`，不再 retry。

---

## 3. 资源闸（Resource Guard）

本技能受 TKT-2026-005C 资源闸约束。以下规则在所有 Phase 中均有效，**高于**一般性的失败容忍策略。

### 3.1 回测规模限制

单次 `call_backtest.py` 调用必须满足：

| 闸 | 默认硬上限 | Boss 授权条件 |
|---|---|---|
| universe 标的数 | ≤ 20 | `AOS_BOSS_OVERRIDE=1` |
| 回测时间窗 | ≤ 3 年 | `AOS_BOSS_OVERRIDE=1` |
| HTTP 请求超时 | 90s | 不可覆盖（代码级硬限制） |

- 超过默认上限且无 `AOS_BOSS_OVERRIDE=1` → 脚本抛 `BacktestGuardrailError`，
  该轮标记 `resource_guard_violation`，**立即进入 `paused_for_boss_review`**。
- 5xx/超时/连接失败：一次即 raise，**禁止自动重试**，
  该轮标记 `backend_unreachable`，**立即进入 `paused_for_boss_review`**。

> **400/404 vs 5xx 区分**：HTTP 400/404 是客户端请求格式探索错误
> （请求体结构不对、字段名拼写、strategy_ir 格式不兼容等），
> **不等于 Boss guardrail**，不需要暂停。标记为 `builder_format_mismatch` 或
> `backtest_format_mismatch`，修正后下一轮继续。
>
> 只有 **5xx / timeout / connection failure** 才触发一票暂停。

### 3.2 Builder 对话轮次限制

- 禁止在同一工单内对 builder 进行 **≥3 轮交互式对话**。
- 2 轮内未拿到完整 IR 即视为 `builder_failed`，
  该轮标记 `builder_session_corrupted`，放弃该 round。
- session 损坏后不允许自动重建 session 继续。

### 3.3 大 universe 准入流程

若工单要求 universe 超过 5 只标的，必须先通过以下 **smoke 验证**：

1. 用 **5 只标的 + 1 年** 时间窗构造一次小型回测
2. 验证 IR 的 `never_triggered_transitions` 为 **空**（至少有一条交易被触发）
3. 若触发数为 0 → 条件的门槛过高，不能放大 universe
4. 只有通过 smoke 验证后，才可申请 `AOS_BOSS_OVERRIDE=1` 逐级放大

### 3.4 违反后果

任何资源闸违规（包括但不限于绕过脚本硬限制手动调后端、多轮 builder 对话死循环、
未通过 smoke 验证直接跑大 universe）→

- 立即中止当前研究，worklog 追加 `resource_guard_violation`
- 该工单 **paused_for_boss_review**
- 违规 agent 实例在 Boss 审查前不再接收新工单

## 4. 失败处理原则

| 失败位置 | 原则 |
|---|---|
| Phase 0 git | **中止**。基础设施问题。 |
| Phase 1 工单 | **中止**。派错人了。 |
| Phase 2 KB | **降级继续**。没有基线也能研究。 |
| Phase 3 单轮 builder / backtest | **标记该轮失败，下一轮**。 |
| Phase 3 连续失败 | **break，Boss review**。 |
| Phase 3 资源闸违规（5xx/超时/连接失败） | **立即 break，paused_for_boss_review**。不重试。 |
| Phase 3 400/404 格式错误 | **标记该轮 `format_mismatch`，下一轮继续**。不是 guardrail。 |
| Phase 4 写报告 | **中止**。磁盘 / 权限问题需要人处理。 |
| Phase 6 git push | **重试 1 次，再失败留本地**。 |

## 5. 产出清单（交付硬标准）

一次成功的研究结束后，以下必须全部存在：

- [ ] `${REPORT_DIR}/{ticket_id}-{slug}.md` —— 按 `report_template.md` 结构
- [ ] `${RESEARCH_RUNS}/{ticket_id}/hypotheses.jsonl` —— 每轮一行
- [ ] `${RESEARCH_RUNS}/{ticket_id}/round_<N>.json` —— 每轮一份（失败轮也要占位）
- [ ] `${RESEARCH_RUNS}/{ticket_id}/metrics.json` —— `metrics.py` 产出
- [ ] `${RESEARCH_RUNS}/{ticket_id}/summary.md` —— 1–2 段结论
- [ ] `${RESEARCH_RUNS}/{ticket_id}/run.log` —— 过程日志
- [ ] 原工单 `## Worklog` 已追加
- [ ] commit 历史可复盘（每轮 1 个 + 终态 1 个）

## 6. 你自己的判断权

本 playbook 不覆盖所有边界情况。以下场合你有裁量权，但**必须在 worklog 说明理由**：

- 根据 ticket 特殊性调整 `max_rounds`
- 跳过某轮的 analysis.md（若分析简短，塞进 hypotheses.jsonl 即可）
- 停止条件之外主动停止（"假设空间枯竭"判断）
- 用不同主指标（如以 calmar 代替 sharpe）

**你没有裁量权的**：读写边界、禁触端点、commit / push 流程、产出清单。
