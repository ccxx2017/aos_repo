---
ticket_id:        TKT-2026-005I
title:            修 KB 最小字段完整性
intent_type:      feature
priority:         p0
status:           accepted
assigned_to:      Project Agent
created_by:       boss
created_at:       2026-05-21
updated_at:       2026-05-28
closed_at:        2026-05-28
due:              null
links:
  parent:         null
  children:       []
  related:        [TKT-2026-005G, TKT-2026-005H, TKT-2026-005F]
  adr:            []
  divergence:     []
tags:             [strategy_researcher, knowledge_base, archive, sanity_check, field_integrity]
---

## Intent

> compile-ir 生成档案时 Universe 退化为占位值，且无最小字段完整性检查。这个必须在恢复研究前修。否则后续研究报告虽然有指标，但 KB 档案的基础元数据不可信。

## Context

### 为什么现在做

- `TKT-2026-005G` 的审计已经把这项缺口列为另一个 `P0`：`compile-ir` 主链路虽然能生成策略档案，
  但归档时 `Universe` 可能退化成占位值，且没有最小字段完整性检查。
- 这类问题比“字段少一点”更严重：研究报告可能已经有 `metrics`，但如果 KB 档案中的基础元数据不可信，
  后续任何基于档案的复盘、检索、引用、交叉比较都会建立在脏数据之上。
- `TKT-2026-005H` 已补上 `train_split` 主链路，让研究过程可以拿到样本内外结果；但如果 KB 在落库时仍允许
  写入占位 `universe` 或缺关键字段，就会形成“运行时能力恢复了，档案口径仍不可信”的断裂。
- 因此，这张工单的目标不是新增功能，而是给 KB 归档链路补一个最小 sanity gate：
  要么生成合格档案，要么显式失败；不能再伪装成合格归档。

### 依赖

- 审计报告：`aos/reports/project/schema-audit/TKT-2026-005G-schema-coverage-audit.md`
- 相关主链路：
  - `backend/app/api/endpoints/strategy_builder.py`
  - `quant_intelligence/strategy_builder/knowledge_base.py`
  - 如需要，相关 strategy archive / backtest append 组装逻辑
- 参考工单：
  - `TKT-2026-005F`（正式技能资产源与主链路契约已定型）
  - `TKT-2026-005H`（`train_split` 主链路已补通，现需保证 KB 档案字段可信）

## Deliverable Spec

### 必须产出
- [ ] 修复 `compile-ir` 生成策略档案时 `universe` 退化为占位值的问题；正式归档不得写入伪造或占位 `universe`
- [ ] 为 KB 归档增加“最小字段完整性检查”，档案至少可复查以下字段：
  - `strategy_id`
  - `run_id`
  - `strategy_name`
  - `strategy_ir`
  - `universe`
  - `time_range`
  - `train_split`
  - `metrics`
  - `train_metrics`
  - `test_metrics`
  - `phase_stats`
- [ ] 当关键字段缺失时，后端行为必须二选一且语义明确：
  - 拒绝落库；或
  - 明确写入 `sanity_check_failed`
- [ ] 不允许把关键字段缺失的档案伪装成正常、合格的 strategy archive
- [ ] `kb_query archive <strategy_id>` 读出的档案必须能够复查上述字段，或明确看到 `sanity_check_failed`
- [ ] 至少新增或更新一条自动化测试，验证：
  - 合格档案可落库并可读回
  - 关键字段缺失时不会伪装成合格档案
- [ ] 产出一份简短验证记录：
  `aos/reports/project/schema-audit/TKT-2026-005I-kb-minimum-sanity-check-validation.md`

### 验收标准
- [ ] 本工单只解决 KB 最小字段完整性与归档 sanity check，不顺手混入其他 schema 缺口
- [ ] `compile-ir` 主链路生成档案时，不再出现占位 `universe` 冒充真实字段的情况
- [ ] 对最小字段集合的检查真实生效；不能只是定义字段列表但运行时静默忽略
- [ ] 对缺字段档案的处理结果可被调用方和排障流程可靠识别：要么拒绝落库，要么带 `sanity_check_failed`
- [ ] `kb_query archive` 返回内容与后端现实能力一致，能支持人工复查最小字段集合
- [ ] 自动化测试至少覆盖以下一项：
  - happy path：字段齐全时正常归档
  - failure path：关键字段缺失时拒绝或显式失败
- [ ] 验证记录里要明确写出：
  - 最小字段清单
  - 失败时的表现形式
  - `kb_query archive` 的复查路径
  - 是否已能作为恢复研究前的最小可信门槛

### 执行方法约束
- [ ] 以最小修改为原则，优先修补现有 `compile-ir -> KB archive` 链路，不另起一套平行归档机制
- [ ] 若现有 archive 结构已能承载 `sanity_check_failed`，优先复用；不要为本工单重写整套 KB 契约
- [ ] 不在本工单中修改 `data/knowledge/schema.md`
- [ ] 不在本工单中处理 `关联策略更新`、`market insight`、`Notes`、`strategy_created` 日志等其他 gap
- [ ] 不把 `train_split` 主链路本身再次重做；只要求其结果在归档时具备最小可信度

### 显式排除
- ❌ 不在本工单中补 `关联策略更新`
- ❌ 不在本工单中补 `market insight` 触发规则
- ❌ 不在本工单中补 `Notes / 净值穿零解释`
- ❌ 不在本工单中补 `strategy_created` 日志链路
- ❌ 不在本工单中做大规模 KB 结构重构或历史档案批量迁移

## Worklog

### 2026-05-21 @boss
- 起草工单。
- 依据 `TKT-2026-005G` 审计结论，确认这是恢复研究前必须完成的另一个 `P0`。
- 任务边界明确收紧：只修 KB 最小字段完整性与 sanity check，不并带处理其他 `P1` 缺口。

### 2026-05-21 @Project Agent
- 已修复 `compile-ir` 归档写入占位 `universe="compile_ir"` 的问题，改为传递真实结构化 `universe` 或保持缺失并显式标记失败。
- 已为策略档案增加 `## 档案元数据` JSON 区块与最小字段级 sanity gate；缺关键字段时写入 `sanity_check_failed`，不再伪装成合格 archive。
- 已更新 `append_backtest_result()`，在回测完成后回填 `run_id`、`time_range`、`train_split`、`metrics`、`train_metrics`、`test_metrics`、`phase_stats`，字段齐全时将档案升级为 `passed`。
- 已补充自动化测试与验证记录：`aos/reports/project/schema-audit/TKT-2026-005I-kb-minimum-sanity-check-validation.md`

### 2026-05-28 @Project Agent
- 已完成 live path verification，结论为 `live_verified_passed`。
- 已确认 `compile-ir -> KB archive` live 主链路输出包含 `## 档案元数据` JSON 区块以及 `sanity_check_failed` / `sanity_missing_fields` / `sanity_failure_reasons`。
- 本工单当前标记：`accepted / live_verified_passed`。

## Resolution

- Acceptance: `accepted`
- Verification: `live_verified_passed`
- Verified Archive: `ir_86a1843218b0`
- Validation Report: `aos/runtime/tickets/done/TKT-2026-005I-kb-minimum-sanity-check-validation.md`
