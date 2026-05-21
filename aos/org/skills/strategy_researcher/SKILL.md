---
name: strategy-researcher
version: 0.2.1
status: trial
description: 策略研究员——接受 ticket，驱动"假设→构建→回测→分析"多轮循环，产出研究报告。
charter_ref: /home/ccxx/aos_repo/aos/org/agents/agent-strategy-researcher.md
charter_ver: v0.1.0
owner: Boss
host: ubuntu-dev
runtime: python>=3.10
---

# Skill: strategy-researcher (v0.2.1 · trial)

> **v0.2.1 变更要点**（相对 v0.2.0）：
> - **端点切换**：`call_builder.py` 默认端点从 `/strategy-builder/invoke` 改为 `/strategy-builder/compile-ir`。
>   investigation 必须使用 compile-ir，invoke 端点禁止。
> - **回测传参固化**：`execution-config` 必须传完整 `strategy_ir`，不得只传 `strategy_id`。
> - **research_workflow 更新**：新流程 compile-ir → archive_created → execution-config → kb_query 读 KB 口径。
> - **metrics.py 兼容**：新增 `_extract_backtest()` 函数，自动检测新路径（backtest_response）和旧路径（builder_response.backtest），不再误判 compile-ir + execution-config 结果为 no_backtest。
> - **错误语义明确**：HTTP 400/404 是客户端格式探索错误，不等于 Boss guardrail；5xx/timeout/connection failure 仍然一票暂停。
>
> **v0.2.0 变更要点**（相对 v0.1.0）：
> - **撤销** `research_loop.py` 硬编码脚本。研究主流程改由**自然语言 playbook**承载
>   （见 `prompts/research_workflow.md`），由智能体自主执行——
>   研究是判断密集型工作，不应写成状态机。
> - **撤销** `report_render.py`。报告是叙事性产物，按 `prompts/report_template.md` 写即可。
> - **新增** `scripts/metrics.py`（纯标准库指标聚合工具）。
> - **新增** `prompts/` 目录（README / research_workflow / hypothesis_heuristics / report_template）。
> - 状态 `draft → trial`：HTTP 适配与行动手册齐备，可执行首个真实研究工单。
> - `llm_client.py` **延后**，等首次真实使用暴露需求后再评估（见 Ticket A 决策）。

## 身份绑定
- agent_id:    agent-strategy-researcher
- charter_ref: /home/ccxx/aos_repo/aos/org/agents/agent-strategy-researcher.md
- charter_ver: v0.1.0
- status:      trial

## 运行时
- host:        ubuntu-dev (192.168.1.136 同网段)
- runtime_dir: /home/ccxx/.openclaw/workspace/skills/strategy_researcher/
- python:      /usr/bin/python3 (>=3.10)
- schedule:    on-demand · ticket-driven (无 cron)

## 路径常量
```
REPO_ROOT      = /home/ccxx/aos_repo
AOS_ROOT       = ${REPO_ROOT}/aos
TICKETS_DIR    = ${AOS_ROOT}/runtime/tickets
RESEARCH_RUNS  = ${AOS_ROOT}/runtime/research-runs
REPORT_DIR     = ${AOS_ROOT}/reports/project/research
BACKEND        = http://192.168.1.136:8000/api/v1
KB_API         = ${BACKEND}/knowledge
BUILDER_API    = ${BACKEND}/strategy-builder/compile-ir
BACKTEST_API   = ${BACKEND}/backtests/execution-config
```

## 读写边界（硬约束）

**读**：
- `${AOS_ROOT}/org/**`
- `${AOS_ROOT}/runtime/tickets/open/{assigned_ticket}.md`
- `${AOS_ROOT}/runtime/research-runs/**`
- `${AOS_ROOT}/reports/project/research/**`
- `runtime_dir/prompts/**`（自己的行动手册）
- `${KB_API}/index` (GET)
- `${KB_API}/archives` (GET, list)
- `${KB_API}/archives/{strategy_id}` (GET, detail)
- `${KB_API}/log` (GET)

**调用**（POST，有副作用但不直接落本地文件）：
- `${BUILDER_API}` (POST) — investigation 使用 compile-ir；invoke 端点禁止
- `${BACKTEST_API}` (POST)

**写**（独占）：
- `${REPORT_DIR}/{ticket_id}-{slug}.md`
- `${RESEARCH_RUNS}/{ticket_id}/{hypotheses.jsonl, round_<N>.json, metrics.json, summary.md, run.log}`
- 承接工单的 `## Worklog` 段（append-only）

**出站**：仅 `${BACKEND}` 下的白名单端点。

**禁止**：
- 任何 `${BACKEND}/strategy-deploy/*` 调用
- 任何 `${BACKEND}/order/*` 调用
- 直接读写 Windows 端 `D:\智能投顾\量化相关\abu_modern\data\knowledge\`
- 直接 import `quant_intelligence.*`（Ubuntu 侧无此包）
- **直接写 KB**（KB 写入由后端在 builder/backtest 成功后的副作用中完成）
- 修改 charter / `_protocol.md` / 其他 agent 产出

## 主流程

**本 SKILL.md 不再内嵌流程伪代码**。

**约束声明**：本技能所有操作受 TKT-2026-005C 资源闸约束。
详细条款见 `prompts/research_workflow.md §3`。

- `intent_type == 'investigation'` 的研究工单：
  行动手册见 `prompts/research_workflow.md`（每次任务开始必读）
- `intent_type ∈ {'infrastructure', 'skill-bootstrap'}` 的工单：
  走"技能自检流程"，由工单正文给出步骤清单，不套用上述手册

## 失败处理矩阵（总则）

更细粒度见 `prompts/research_workflow.md §3`。

| 阶段          | 失败现象          | 处理                                       |
|---------------|-------------------|--------------------------------------------|
| git pull      | 冲突/网络         | 中止，worklog 标记 `git_sync_failed`       |
| ticket 校验   | intent 不匹配     | 中止，worklog 标记 `not_my_ticket`         |
| KB read       | 任一 GET 失败     | 上下文置空，worklog 标记 `kb_unreachable`  |
| builder POST  | 超时/5xx          | 该轮标记 `builder_failed`，下一轮继续      |
| backtest      | 引擎超时/业务失败 | 该轮 metrics 为 null，下一轮继续           |
| 资源闸违规    | 超限/无授权       | **立即 break，paused_for_boss_review**，不重试 |
| 停止条件触发  | 连续失败/阈值异常 | break，worklog 写 `paused_for_boss_review` |
| 写报告        | 磁盘满/权限       | 中止，worklog 标记 `report_write_failed`   |
| git push      | 网络/认证         | 重试 1 次（30s），仍失败保留本地并标记     |

## 自检（trial 合格标准）

- 完成 1 个真实研究工单，报告按 `prompts/report_template.md` 所有必需章节齐全
- `hypotheses.jsonl` / `round_*.json` / `metrics.json` / `summary.md` / `run.log` 齐备
- worklog 有完整轮次记录，commit 历史可追溯
- 未触发任何 §读写边界 禁止项（grep 检查 `deploy` / `order` 关键字）
- 报告引用的 `strategy_id` 在 `${KB_API}/archives/{id}` 真实可读
- Boss 评审通过 1 张工单 → 进入 Trial 2

## 工具索引

- 脚本清单见 `TOOLS.md`
- 行动手册见 `prompts/`（入口 `prompts/research_workflow.md`）
```

---