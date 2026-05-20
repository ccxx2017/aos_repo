---
ticket_id: TKT-2026-005C
title: Backtest Safety Guard — 脚本侧硬限制
intent_type: infrastructure_patch
assigned_to: agent-strategy-researcher
priority: P0
blocks: TKT-2026-005B
status: open
created_by: Boss
created_at: 2026-05-19
tags: [backtest, safety, timeout, infra]
---

## A. 背景

Ticket B（TKT-2026-005B VCP 突破策略研究）在 Round 2 失败：
- **Builder 多轮损坏**：`strategy_builder.py` 的多轮对话模式下，builder session 在轮次转换间状态丢失，导致 Round 2 提交进入损坏状态。
- **后端无超时/取消/隔离**：`call_backtest.py` 向 192.168.1.136:8000 提交了包含 231 只标的的回测请求。后端未设单次请求超时，请求持续挂起直至 watchdog 从外部杀死；在此期间 builder 也无法接收后续指令。
- **根因总结**：当前回测调用栈（call_backtest.py → builder → backend）在请求层面**没有任何安全护栏**——无最大标的数限制、无最大回测年份限制、无请求超时、无自动重试防护。

本工单**只修复脚本侧 / agent 侧**的问题。后端侧的异步化改造不在本工单范围内。

## B. 本工单范围

### B-1 `call_backtest.py` 安全护栏

在 `/home/ccxx/aos_repo/scripts/call_backtest.py` 中增加以下硬限制：

| 参数 | 默认硬上限 | 说明 |
|---|---|---|
| `max_symbols` | 20 | 单次回测请求最多 20 只标的 |
| `max_years` | 3 | 回测时间窗口最多 3 年 |
| `per_request_timeout` | 90s | HTTP 请求超时，超时即 raise，无自动重试 |

#### 超阈值授权机制

若 agent 需要超出上述默认值（例如需要 50 只标的或 5 年数据），须按以下步骤：
1. `call_backtest.py` 检测到参数超出默认上限；
2. 检查环境变量 `AOS_BOSS_OVERRIDE=1` 是否存在且值为 `1`；
3. 若存在 → 允许执行（日志记录 `WARN: BOSS_OVERRIDE active for symbols=50,years=5`）；
4. 若不存在 → 拒绝执行，打印 `FATAL: BOSS_OVERRIDE required for symbols=50 > max_symbols=20`，返回非零退出码。

#### 禁止自动重试

- 后端无响应（HTTP 超时、连接拒绝、5xx）→ 立即 raise，**禁止自动重试**。
- 日志必须保留原始错误信息（status_code + response_body 前 200 字符）。

### B-2 `research_workflow.md` 增加 §3.7 资源闸条款

若 `research_workflow.md` 存在，在现有流程的最后追加一节 §3.7。若文件不存在，则创建 `aos/docs/research_workflow.md` 并写入此条款。

条款内容：

```markdown
### 3.7 资源闸（Resource Guard）

调用 `call_backtest.py` 前必须检查以下条件：

1. **标的数** ≤ `max_symbols`（默认 20），超过须 `AOS_BOSS_OVERRIDE=1`
2. **时间跨度** ≤ `max_years`（默认 3 年），超过须 `AOS_BOSS_OVERRIDE=1`
3. **请求超时** 设为 `per_request_timeout`（默认 90s），超时视为后端不可用
4. **禁止自动重试**：后端无响应一次即 raise，agent 必须记录失败原因后中止当前 round
5. **session 单一性**：一个 round 内的多次调用应复用同一 builder session。若 session 损坏，放弃该 round，标记 `builder_session_corrupted`，不允许自动重建 session 继续
```

### B-3 附带要求

- `call_backtest.py` 的 `--help` 输出必须包含上述三个安全参数及其默认值。
- 修改日志：入参日志必须打印实际使用的 `symbols_count`、`years_span`、`timeout` 值。

## C. 验收清单

- [ ] `call_backtest.py` 对 `--symbols` 超过 20 只报错并提示 `AOS_BOSS_OVERRIDE`，返回非零退出码
- [ ] `call_backtest.py` 对 `--years`（或等效参数）超过 3 年执行相同拦截
- [ ] `call_backtest.py` 设置 `requests` 或 `httpx` 的超时为 90s，超时后 raise 且不重试
- [ ] `AOS_BOSS_OVERRIDE=1` 环境变量存在时允许超阈值执行，日志包含 `BOSS_OVERRIDE` 字样的警告
- [ ] `research_workflow.md` §3.7 资源闸条款存在并覆盖上述 5 条规则

## Worklog

_（初始工单，无 worklog）_
