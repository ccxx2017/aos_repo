---
ticket_id:        TKT-2026-002
title:            起草策略研究员 Charter 与 SKILL 骨架
intent_type:      feature
priority:         p1
status:           draft
assigned_to:      boss
created_by:       boss
created_at:       2026-05-05
updated_at:       2026-05-05
closed_at:        null
due:              2026-05-12
links:
  parent:         null
  children:       [TKT-2026-003, TKT-2026-004]
  related:        [TKT-2026-001]
  adr:            []
  divergence:     []
tags:             [agents, bootstrap, research]
---

## Intent

> "我想要组织的第二位数字员工：一个能接到研究工单后，自己驱动'假设→
> 回测→分析→沉淀'多轮循环、把发现写入知识库的策略研究员。它不要
> 碰部署和下单，那两块由别的工具或人来。"

## Context

### 为什么现在做
- agent-duty-reporter（TKT-2026-001）已经验证 Charter + Ticket + OpenClaw skill 三件套能闭环。
- 量化平台已具备 `/strategy-builder/invoke`、`/backtests/execution-config`、`knowledge_base.py` 等基础设施；schema.md 已经为 LLM agent 编写好了"典型工作流"，但缺一个真正会执行该工作流的 Agent。
- `data/knowledge/strategies/` 已有 5 份历史策略档案，是有生命的知识资产；新研究必须能引用并增量沉淀。

### 依赖
- 已完成：TKT-2026-001（duty-reporter 试运行中，证明 Charter 模板可用）
- 后端能力：`strategy-builder`、`backtests/execution-config`、`knowledge_base.py` 已就绪
- **本工单不依赖 TKT-2026-003/004**——本工单只产出文档骨架

## Deliverable Spec

### 必须产出
- [ ] `aos/org/agents/agent-strategy-researcher.md`，符合 `_charter-template.md v0.1`
- [ ] `openclaw_skills/strategy-researcher/SKILL.md`（骨架版，状态 draft）
- [ ] `openclaw_skills/strategy-researcher/TOOLS.md`（占位，实际工具到 TKT-2026-004 填充）
- [ ] `openclaw_skills/strategy-researcher/scripts/.gitkeep`（占位目录）
- [ ] 本工单 Resolution 段附三个文件的最终路径

### 验收标准
- [ ] Charter §1 职责一句话表述清晰，与 duty-reporter 职责无重叠
- [ ] Charter §4 权限明确禁止 deploy / order 两类调用
- [ ] Charter §4.4 包含 LLM/回测/无改进三个 HITL 阈值
- [ ] SKILL.md 路径常量与读写边界完全对齐 Charter §4
- [ ] SKILL.md 主流程伪代码引用了 schema.md 第 7 节的"典型工作流"
- [ ] Boss 审阅签字（worklog 中明示 `approved by @boss`）

### 显式排除
- ❌ **不**在本工单内实现 `research_loop.py`（拆给 TKT-2026-004）
- ❌ **不**在本工单内实现后端 KB 只读 API（拆给 TKT-2026-003）
- ❌ **不**修改既有的 quant_assistant skill（互不影响）
- ❌ **不**触碰 `data/knowledge/` 任何现有文件（仅消费侧设计，写侧由后端负责）

## Worklog

### 2026-05-05 @boss
- 起草工单。
- 关联决策：是否采用"后端自动落库 + Agent 只读 KB API"方案 → 倾向是，留待 TKT-2026-003 时形成 ADR。
- 下一步：评审本工单内附三份草案（Charter / SKILL.md / TOOLS.md）。
approved by @boss on 2026-05-06

## Resolution

（待填）