---
ticket_id:        TKT-2026-005H
title:            execution-config 打通 train_split 主链路
intent_type:      feature
priority:         p0
status:           draft
assigned_to:      Project Agent
created_by:       boss
created_at:       2026-05-21
updated_at:       2026-05-21
closed_at:        null
due:              null
links:
  parent:         null
  children:       []
  related:        [TKT-2026-005G, TKT-2026-005F, TKT-2026-005B]
  adr:            []
  divergence:     []
tags:             [strategy_researcher, backtest, train_split, execution_config, schema_bridge]
---

## Intent

> execution-config 增加 train_split 透传，并让 call_backtest.py 支持 split 回测。

## Context

### 为什么现在做

- `TKT-2026-005G` 的 schema 覆盖审计已确认：`样本内外对比` 在 `strategy_researcher` 的运行时手册里已经是硬要求，
  但正式主链路 `scripts/call_backtest.py -> /api/v1/backtests/execution-config` 还拿不到
  `train_metrics/test_metrics`，导致该要求目前是“纸面成立、运行时未打通”。
- 当前 `research_workflow.md` 和 `report_template.md` 已要求研究员比较样本内外差异、识别过拟合；
  如果主链路不支持 `train_split`，后续任何围绕过拟合、样本外 Sharpe 的判断都会失真或退化为猜测。
- 本工单属于 `schema.md` 与 `strategy_researcher` 之间最关键的一条 `P0 bridge`：
  先把主链路可达性补齐，再处理字段完整性、`strategy_created` 日志、关联策略候选、market insight 候选等后续缺口。

### 依赖

- 审计报告：`aos/reports/project/schema-audit/TKT-2026-005G-schema-coverage-audit.md`
- 正式技能资产源：
  - `aos/org/skills/strategy_researcher/scripts/call_backtest.py`
  - `aos/org/skills/strategy_researcher/TOOLS.md`
  - `aos/org/skills/strategy_researcher/prompts/research_workflow.md`
  - `aos/org/skills/strategy_researcher/prompts/report_template.md`
- 后端主链路：
  - `backend/app/api/endpoints/backtests/start.py`
  - 如需要，相关回测服务 / schema 定义 / `BacktestResult` 组装逻辑
- 参考工单：
  - `TKT-2026-005F`（compile-ir -> execution-config 主链路已定型）
  - `TKT-2026-005B`（真实 smoke 已验证 compile-ir 路径可跑通，但没有 split 回测能力）

## Deliverable Spec

### 必须产出
- [ ] 后端 `POST /api/v1/backtests/execution-config` 支持接收 `train_split` 参数，并把该参数真正透传到回测执行链路
- [ ] 当请求携带 `train_split` 时，后端响应中可返回 `train_metrics` / `test_metrics`（或与现有响应协议等价、可被 `call_backtest.py` 可靠解析的结构）
- [ ] `aos/org/skills/strategy_researcher/scripts/call_backtest.py` 支持传入 `train_split`，并把 split 回测结果原样保存在输出 JSON 中
- [ ] `aos/org/skills/strategy_researcher/TOOLS.md` 更新 `call_backtest.py` 的参数说明、输入示例和返回语义，明确 split 回测可用
- [ ] `aos/org/skills/strategy_researcher/prompts/research_workflow.md` 明确：
  当工单要求样本内外对比时，研究员必须在回测请求中显式传 `train_split`
- [ ] `aos/org/skills/strategy_researcher/prompts/report_template.md` 明确：
  如果本轮请求使用了 `train_split`，报告中必须展示样本内外差异；如果没用，则必须写明原因
- [ ] 至少新增或更新一条自动化测试，验证 `execution-config + train_split` 主链路不漂移
- [ ] 产出一份简短验证记录：
  `aos/reports/project/schema-audit/TKT-2026-005H-train-split-bridge-validation.md`

### 验收标准
- [ ] `train_split` 只解决一件事：让 `strategy_researcher` 主链路可获得样本内外结果；不得顺手把其他 schema 缺口混入同一工单
- [ ] 未携带 `train_split` 时，现有 `execution-config` 行为保持兼容，不破坏现有 smoke 路径
- [ ] 携带 `train_split` 时，响应中真实出现样本内外结果；不能只是接受参数但静默忽略
- [ ] `call_backtest.py` 对 split 结果的保存是“原样保存”，不擅自裁剪掉 `train_metrics/test_metrics`
- [ ] `research_workflow.md` 与 `report_template.md` 的文案更新后，与后端现实能力一致，不再出现“文档要求比较样本内外、但主链路做不到”的断裂
- [ ] 自动化测试覆盖至少以下一项：
  - 带 `train_split` 的 happy path
  - 无 `train_split` 的兼容路径
- [ ] 验证记录里要明确写出：
  请求示例、返回字段位置、`call_backtest.py` 保存后的 JSON 路径、是否已能支撑 `strategy_researcher` 做样本内外比较

### 执行方法约束
- [ ] 只以 `aos/org/skills/strategy_researcher/` 为正式技能资产源；不再修改或参考 `openclaw_skills/`
- [ ] 以最小修改为原则，优先打通现有 `execution-config` 主链路，不另起一条平行回测接口
- [ ] 不在本工单中修改 `data/knowledge/schema.md`
- [ ] 不在本工单中处理 `strategy_created` 日志、`Universe` 字段占位值、`Notes/净值穿零解释`、`关联策略候选`、`market insight 候选`
- [ ] 若后端现有响应结构已能承载 split 结果，优先复用；不要为了这个工单重写整套 backtest response 契约

### 显式排除
- ❌ 不在本工单中补 `compile-ir` 的 `strategy_created` 日志
- ❌ 不在本工单中补 `Universe=compile_ir` 的字段完整性问题
- ❌ 不在本工单中补 `Notes / 净值穿零说明`
- ❌ 不在本工单中补 `关联策略候选 / market insight 候选` 小节
- ❌ 不在本工单中做异步化、任务队列、取消接口或并发治理

## Worklog

### 2026-05-21 @boss
- 起草工单。
- 依据 `TKT-2026-005G` 审计报告，确定这是当前最高优先级的 `P0 bridge`。
- 任务边界明确收紧：只打通 `train_split` 主链路，不并带修复其他 schema 缺口。

## Resolution

（仅在 done / rejected / cancelled 时填写）
