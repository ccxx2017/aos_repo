---
doc_type: ticket-protocol
schema_version: 0.1
maintained_by: Boss
last_reviewed: 2026-04-23
---

# Ticket Protocol

> 工单是**组织中流动的最小工作单元**。Boss 下达的每一个意图、agent 之间
> 的每一次协作、需要追溯的每一次执行，都应该有对应的工单。
>
> 设计原则：
> 1. **一张工单 = 一个可验收的产出**。不可验收的不是工单，是日记。
> 2. **Intent 用自然语言，Spec 用结构**。保留 Boss 的原话，也保留机器可读的要求。
> 3. **状态机单向为主**。避免"复活"工单，需要重开就另立新单并交叉引用。
> 4. **工单即记忆**。closed 的工单是组织最重要的可检索资产。

---

## 1. 工单 ID 规则

格式：`TKT-YYYY-NNN`
- `YYYY`：创建年份
- `NNN`：当年流水号，三位起步，不足补零

**与历史迁移工单（TKT-020 ~ TKT-034）的衔接：**
历史工单保留在 `_archive/` 或 `_tickets/`（迁移脚手架）中，不进入本协议管辖的
`tickets/` 目录。新工单从 `TKT-2026-001` 开始编号。

---

## 2. 工单文件结构

每张工单是一个独立的 Markdown 文件，命名：
```
tickets/<state>/TKT-YYYY-NNN-<slug>.md
```
- `<state>`: `open` 或 `closed`
- `<slug>`: 短标题的 kebab-case，如 `setup-duty-reporter`

---

## 3. Front Matter Schema（必填）

```yaml
---
ticket_id:        TKT-2026-001
title:            一句话标题（不超过 40 字）
intent_type:      feature | bugfix | investigation | report | decision | chore
priority:         p0 | p1 | p2 | p3
status:           draft | assigned | in-progress | review | done | rejected | cancelled
assigned_to:      agent-xxx | boss | unassigned
created_by:       boss | agent-xxx
created_at:       YYYY-MM-DD
updated_at:       YYYY-MM-DD
closed_at:        YYYY-MM-DD | null
due:              YYYY-MM-DD | null
links:
  parent:         TKT-YYYY-NNN | null
  children:       []
  related:        []
  adr:            []            # 关联的 decisions/xxx.md
  divergence:     []            # 关联的 divergences/xxx.md
tags:             []
---
```

---

## 4. 工单正文结构

工单正文**必须**包含以下五节。缺一不可。

### 4.1 Intent（原始意图）
Boss 或上游的**原话**。不要改写、不要润色。这一节是工单的"初心"，
后续若发现执行偏航，第一步就是回看这里。

### 4.2 Context（上下文）
执行前需要知道的背景：
- 为什么现在做这件事
- 相关的系统状态 / 历史决策
- 依赖的前置工单（已完成）

### 4.3 Deliverable Spec（产出要求）
**结构化**地列出验收标准。禁止含糊的"尽量""最好"。

```markdown
- [ ] 必须产出：docs/wiki/agents/agent-duty-reporter.md
- [ ] 必须包含：Front Matter + 第 1~7 节
- [ ] 产出格式：符合 _charter-template.md v0.1
- [ ] 验收方式：Boss 审阅 + status: draft → active 前的试运行 ≥3 次
```

### 4.4 Worklog（执行日志）
执行人（Boss 或 agent）按时间倒序追加。每条 worklog 至少包含：

```markdown
### 2026-04-23 14:30 @agent-xxx
- 做了什么
- 遇到什么
- 下一步
- 产出链接（如有）
```

**worklog 只追加，不修改历史条目。** 如需更正，新增一条说明。

### 4.5 Resolution（结案说明）
仅在 `status: done | rejected | cancelled` 时填写：
- 最终产出的链接
- 验收结果（Boss 一句话）
- 学到的东西（可选，但强烈建议）
- 是否衍生新工单

---

## 5. 状态机

```
        ┌──────────────────────────────────────────┐
        │                                          │
     draft ──► assigned ──► in-progress ──► review ──► done
        │         │              │            │
        │         │              │            └──► rejected ──► (重开需新工单)
        │         │              │
        └─────────┴──────────────┴──► cancelled
```

### 状态定义

| 状态 | 含义 | 谁可以转入 |
|------|------|-----------|
| `draft` | 起草中，尚未正式下发 | Boss / agent |
| `assigned` | 已指派负责人，等待开工 | Boss |
| `in-progress` | 执行中，worklog 有更新 | assigned_to |
| `review` | 待 Boss 或指定评审人验收 | assigned_to |
| `done` | 验收通过，归档 | Boss（或 Boss 授权的评审 agent） |
| `rejected` | 验收不通过，终止（不回滚） | Boss |
| `cancelled` | 因外部原因终止 | Boss |

### 状态转换规则

1. **只有 Boss 能 `assign`**（早期阶段。后续可授权调度类 agent）。
2. `in-progress → review` 必须附带产出链接。
3. `review → done` 必须有 Boss 或指定评审人的明确签字（worklog 里写一句"approved by @boss"）。
4. **`done` 和 `rejected` 是终态**。需要重做 → 新开工单，`links.parent` 指向原单。
5. **30 天无更新的 `in-progress` 工单**自动告警（由"工单管家" agent 巡检，初期可由 Boss 手动扫）。

---

## 6. 目录规则

```
tickets/
├── _protocol.md              # 本文件
├── _template.md              # 空白工单模板（从本协议派生）
├── open/                     # draft / assigned / in-progress / review
│   └── TKT-2026-001-xxx.md
└── closed/                   # done / rejected / cancelled
    └── 2026/
        └── TKT-2026-001-xxx.md
```

### 流转动作
- 创建：直接写入 `open/`
- 结案：从 `open/` 移动到 `closed/<year>/`，并更新 Front Matter 的 `closed_at`
- **移动即归档**。Git history 保留全部痕迹，无需在工单里再复述。

---

## 7. 工单与其他 Wiki 对象的关系

| 关联对象 | 关系 | 约定 |
|---------|------|------|
| **ADR (`decisions/`)** | 工单执行过程中做出重大决策 → 生成 ADR，在 `links.adr` 登记 |
| **Divergence (`divergences/`)** | 执行偏离 Spec → 写偏差记录，在 `links.divergence` 登记 |
| **Agent Charter (`agents/`)** | 工单产出新员工或修改 Charter → 在工单 Resolution 中附链接 |
| **Component/Architecture 页** | 工单修改了系统结构 → 同步更新对应 Wiki 页，在 worklog 里写明 |
| **log.md** | 重大工单（p0/p1）结案时追加一行迁移日志风格的记录 |

**核心原则：工单是动作，Wiki 其他部分是状态。动作完成必须更新状态，否则组织记忆就断层。**

---

## 8. Boss 视图与工单的关系

- `boss/inbox.md`：自动聚合 `status: review` 的工单链接
- `boss/agenda.md`：Boss 手动维护的当前优先级工单清单
- `boss/daily.md`：值班汇报员每日汇总 open 工单的当前分布

**这三个页面不存储工单本体，只是索引。工单唯一真实源是 `tickets/` 下的文件。**

---

## 9. 最小工单示例

```markdown
---
ticket_id:        TKT-2026-001
title:            实例化值班汇报员（agent-duty-reporter）
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
tags:             [agents, bootstrap]
---

## Intent
"我想要一个每天早上自动告诉我系统状态的员工，异常时还能主动提醒我。"

## Context
- Wiki 迁移刚完成，Agents/Tickets/Boss 三个目录骨架已立。
- 这是组织的第一个数字员工，验证 Charter + Ticket 闭环是否跑得通。
- 依赖：已有系统健康 API、OpenClaw runtime。

## Deliverable Spec
- [ ] 产出 `agents/agent-duty-reporter.md`，符合 _charter-template.md v0.1
- [ ] 实现 OpenClaw skill：`~/.openclaw/workspace/skills/duty-reporter/SKILL.md`
- [ ] 接通 Telegram 推送
- [ ] 连续 3 天产出合格日报，Boss 批准后转 status: active
- [ ] 在 `agents/_index.md` 登记

## Worklog
### 2026-04-23 15:00 @boss
- 起草工单。下一步：起草 Charter 初稿。

## Resolution
（待填）
```

---

## 10. 变更历史

```
| 版本 | 日期 | 变更 | 操作人 |
|------|------|------|--------|
| 0.1  | 2026-04-23 | 初始协议 | Boss |
```

**本协议自身的修订规则：**
- 任何字段的新增/删除/语义变化都要 minor +1
- 状态机的变更必须 major +1，并配套一份 ADR（放入 `decisions/`）
