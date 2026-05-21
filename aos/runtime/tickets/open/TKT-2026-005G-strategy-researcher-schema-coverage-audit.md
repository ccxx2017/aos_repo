---
ticket_id:        TKT-2026-005G
title:            strategy_researcher schema 覆盖审计
intent_type:      report
priority:         p1
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
  related:        [TKT-2026-005F, TKT-2026-005B]
  adr:            []
  divergence:     []
tags:             [strategy_researcher, schema, audit, knowledge_base, source_of_truth]
---

## Intent

> 现在需要的是一张 “schema 覆盖审计” 工单

## Context

### 为什么现在做

- Boss 已明确决定：弃用 `openclaw_skills/`，以后以 `aos/org/skills/` 作为 `strategy_researcher` 的唯一权威源。
- 现阶段已确认 `data/knowledge/schema.md` 对 `strategy_researcher` 形成了**部分吸收、部分引用、部分缺失**的状态；
  如果不做一次覆盖审计，后续继续补 `SKILL.md` / `TOOLS.md` / `prompts/` 时，容易凭感觉补规则，导致：
  - 同一规则在多个文件里复写且漂移；
  - 关键规则只存在于 `schema.md`，但没有进入运行时手册；
  - 机械性 Lint 规则、字段完整性规则和 KB 更新规则无人真正执行。
- `TKT-2026-005F` 已把 `aos/org/skills/strategy_researcher/` 建立为正式技能资产源；
  在此基础上，应尽快确认：`schema.md` 中哪些内容应该被运行时手册显式吸收，哪些只保留引用即可。

### 依赖

- `data/knowledge/schema.md` 为当前 KB 规则权威源
- `aos/org/skills/strategy_researcher/SKILL.md`
- `aos/org/skills/strategy_researcher/TOOLS.md`
- `aos/org/skills/strategy_researcher/prompts/README.md`
- `aos/org/skills/strategy_researcher/prompts/research_workflow.md`
- `aos/org/skills/strategy_researcher/prompts/hypothesis_heuristics.md`
- `aos/org/skills/strategy_researcher/prompts/report_template.md`
- 参考工单：`TKT-2026-005F`（正式技能资产源建立），`TKT-2026-005B`（真实研究执行暴露的契约问题）

## Deliverable Spec

### 必须产出
- [ ] 产出一份审计报告：`aos/reports/project/schema-audit/TKT-2026-005G-schema-coverage-audit.md`
- [ ] 产出一份覆盖矩阵：逐条枚举 `data/knowledge/schema.md` 中对 `strategy_researcher` 有意义的规则，并为每条规则标注以下四种状态之一：
  `已由后端保证` / `已被 skill 显式吸收` / `仅被引用未吸收` / `尚未覆盖`
- [ ] 在覆盖矩阵中，为每条规则给出证据路径，证据必须落到具体文件，例如：
  `aos/org/skills/strategy_researcher/SKILL.md`、`TOOLS.md`、`prompts/research_workflow.md`
- [ ] 审计报告必须把 `schema.md` 中的规则至少分成以下五类：
  `KB 读写边界`、`策略档案字段与结构`、`回测结果追加规则`、`分析/关联策略更新规则`、`Lint / 格式规范`
- [ ] 审计报告必须明确给出“哪些规则不应复制进入 skill 文件，只保留交叉引用”的判断，并说明理由
- [ ] 审计报告必须输出一个缺口清单（gap list），按优先级分为 `P0 / P1 / P2`
- [ ] 若存在需要后续落地的缺口，报告末尾必须给出后续工单建议清单；建议粒度要小，禁止把所有缺口塞进一张大而全工单

### 验收标准
- [ ] 不复述 `schema.md` 全文，而是做“规则提取 + 覆盖归类 + 缺口判定”
- [ ] 每个“已吸收”判断都有明确证据；不能写“看起来已经覆盖”
- [ ] 每个“尚未覆盖”判断都要给出建议落点：应落在 `SKILL.md`、`TOOLS.md`、`prompts/`、后端，还是保持为 schema 侧权威源
- [ ] 明确区分“引用 schema”与“真正进入运行时约束”这两种状态，不能混为一谈
- [ ] 明确排查以下高风险项是否已进入运行时手册：
  `4 位小数`、`run_id / strategy_id 可追溯`、`never_triggered_transitions`、`样本内外对比`、
  `关联策略更新`、`市场认知文档触发时机`、`只追加不删除`、`字段完整性自检`
- [ ] 结论能直接支撑后续补丁工单，不停留在泛泛分析

### 执行方法约束
- [ ] 以 `aos/org/skills/strategy_researcher/` 为唯一技能资产源进行审计，**不再**把 `openclaw_skills/` 作为判断依据
- [ ] 若发现历史文档、旧工单或旧运行时目录与当前权威源冲突，允许记录为“历史残留/已弃用”，但不得因此否定当前权威源
- [ ] 先做静态审计，不执行 builder/backtest，不产生新的研究运行数据
- [ ] 本工单的核心产出是“覆盖结论”和“缺口清单”，不是立即修改 skill 文件

### 显式排除
- ❌ 不在本工单中直接修改 `aos/org/skills/strategy_researcher/` 的任何文件
- ❌ 不在本工单中修改 `data/knowledge/schema.md`
- ❌ 不在本工单中恢复或兼容 `openclaw_skills/`
- ❌ 不在本工单中发起新的策略研究、回测或 KB 写入
- ❌ 不把“后端已保证”的规则再机械复制一份到 skill 文档

## Worklog

### 2026-05-21 @boss
- 起草工单。
- 背景判断：当前最需要的不是继续补技能，而是先把 `schema.md` 对 `strategy_researcher` 的覆盖关系审清楚。
- 下一步：指派执行人完成静态审计报告与覆盖矩阵。

### 2026-05-21 @Project Agent
- 已完成静态审计，不执行 builder/backtest，不产生新的研究运行数据。
- 已产出审计报告与覆盖矩阵：`aos/reports/project/schema-audit/TKT-2026-005G-schema-coverage-audit.md`
- 结论摘要：
  - `strategy_researcher` 已吸收研究流程类规则（KB 读取顺序、可追溯性、`never_triggered_transitions`、报告 `4 位小数`）。
  - KB 归档的机械动作已主要由后端保证（`create_strategy_archive()`、`append_backtest_result()`、`update_index()`、`### Run {run_id}`、append-only）。
  - 主要缺口集中在 `train_split` 主链路未接通、`strategy_created` 日志未在 `compile-ir` 主链路补齐、`关联策略/market insight` 触发规则未进入运行时手册、字段完整性缺少 sanity check。
- 已在报告中给出五类规则的覆盖矩阵、证据路径、P0/P1/P2 gap list，以及拆分后的后续工单建议。

## Resolution

（仅在 done / rejected / cancelled 时填写）
