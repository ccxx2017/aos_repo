---
ticket_id:        TKT-2026-001
title:            实例化第一位数字员工：值班汇报员
intent_type:      feature
priority:         p1
status:           draft
assigned_to:      boss
created_by:       boss
created_at:       2026-04-23
updated_at:       2026-04-23
closed_at:        null
due:              2026-05-15
links:
  parent:         null
  children:       []
  related:        []
  adr:            []
  divergence:     []
tags:             [agents, bootstrap, first-hire]
---

## Intent

> "我想要一个每天早上自动告诉我系统状态的员工，异常时还能主动提醒我。
> 这也是组织的第一位数字员工，用来验证 Charter + Ticket 闭环是否跑得通。"
> —— Boss, 2026-04-23

## Context

### 为什么现在做
- Wiki 迁移刚完成（历史工单 TKT-020~TKT-034 封板），三级骨架
  `agents/ · tickets/ · boss/` 已立。
- `agents/_charter-template.md` v0.1 与 `tickets/_protocol.md` v0.1 已提交。
- **两份协议需要一次真实实战来反向检验**。与其凭空造验证案例，
  不如直接启动第一个真正有价值的员工。

### 为什么选"值班汇报员"作为第一个
1. **职责极窄**：每日汇报 + 异常告警。一句话说得清。
2. **风险极低**：默认只读、只推送，不改仓库、不调破坏性 API。
   是数字员工里最适合"练手"的形态。
3. **反馈极快**：每天都会跑，好不好用一周就知道。
4. **产出 Boss 每天都看**：天然被高频检验，不会"建了没人用"。

### 依赖
- 已有系统健康 API（路径待 Charter 中确认）
- OpenClaw runtime 可用
- feishu bot 通道可用（历史上已跑通）

## Deliverable Spec

### 必须产出
- [ ] **Charter 文档**：`aos/org/agents/agent-duty-reporter.md`
  - 必须符合 `_charter-template.md v0.1`，八节齐全
  - Front Matter 完整，初始 `status: draft`
- [ ] **Runtime 实现**：`~/.openclaw/workspace/skills/duty-reporter/SKILL.md`
  - 至少覆盖：读取健康 API → 生成日报 → 推送 feishu
- [ ] **花名册登记**：在 `agents/_index.md` 中新增条目
- [ ] **每日产出落地**：`aos/org/boss/daily.md`（每日覆盖）

### 验收标准
- [ ] Charter 经 Boss 审阅通过
- [ ] 连续 **3 个工作日**产出日报，内容合格（不是占位文本，含真实数据）
- [ ] 模拟一次异常场景，验证告警链路通畅
- [ ] 三次试运行后，Charter `status: draft → active`

### 显式排除（本工单不做）
- ❌ 不做多渠道推送（仅 feishu，邮件/钉钉后续另开工单）
- ❌ 不做历史日报归档（本期日报是覆盖写，归档策略后续讨论）
- ❌ 不做异常自动修复（只告警，不动手）

## Worklog

### 2026-04-23 @boss
- 起草本工单（TKT-2026-001）
- 下一步：起草 Charter 初稿（`agent-duty-reporter.md`）

## Resolution

（待填）