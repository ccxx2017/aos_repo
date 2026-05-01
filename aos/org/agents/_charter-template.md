---
doc_type: agent-charter-template
schema_version: 0.1
maintained_by: Boss
last_reviewed: 2026-04-23
---

# Agent Charter Template

> 本文件是**数字员工的雇佣合同模板**。每实例化一个新员工，在 `agents/` 下
> 创建 `<agent-id>.md`，按本模板填写。模板本身不代表任何员工。
>
> 设计原则：
> 1. **一份 Charter = 一份职责**。不要造"全能员工"，职责越窄越稳。
> 2. **输入输出必须可机读**。Boss 能用自然语言，agent 之间必须用结构。
> 3. **权限最小化**。默认只读，需要写权限必须明列路径。
> 4. **可停职、可退休**。status 字段是组织生命力的开关。

---

## Front Matter（必填）

每个 Charter 必须以如下 YAML 开头：

```yaml
---
agent_id:        agent-<短名>          # 如 agent-duty-reporter
name:            中文名                 # 如 "值班汇报员"
version:         0.1
status:          draft | active | paused | retired
owner:           Boss
created:         YYYY-MM-DD
last_reviewed:   YYYY-MM-DD
runtime:         openclaw | mcp-tool | direct-api | hybrid
runtime_ref:     ~/.openclaw/workspace/skills/<skill-name>/SKILL.md
channels:        [telegram, wiki-commit, cron]   # 触发/输出渠道
tags:            [reporting, monitoring]
---
```

---

## 1. 职责（Responsibility）

**一句话**说清这个员工存在的理由。禁止超过两句。

> 示例：每日汇报系统健康状况，并在异常时主动告警。

如果你写不出一句话，说明职责不够收敛，**先回去拆**，不要建这个员工。

---

## 2. 输入（Inputs）

### 2.1 工单输入
- 接受的 ticket 类型（对应 `tickets/_protocol.md` 中的 `intent_type`）
- 不接受的类型（显式排除，避免越权）

### 2.2 信息源（Context Sources）
列出 agent 运行时会读取的所有来源，含路径/端点：

| 来源 | 类型 | 访问方式 | 频率 |
|------|------|----------|------|
| 系统健康 API | REST | GET /api/health | 按需 |
| Wiki | Git | 本地 clone | 按需 |

### 2.3 触发方式（Triggers）
- [ ] 定时：`cron: 0 8 * * *`
- [ ] 事件：`webhook: /hooks/xxx`
- [ ] 对话：由 Boss 在 <channel> 呼出
- [ ] 工单派发：status 变为 `assigned` 且 `assigned_to == agent_id`

---

## 3. 产出（Deliverables）

### 3.1 产出形式
明确列出 agent 能生成的每种产出，以及落地位置：

| 产出类型 | 格式 | 落地位置 | 命名规则 |
|---------|------|----------|----------|
| 日报 | Markdown | `boss/daily.md`（覆盖） | — |
| 异常工单 | Ticket | `tickets/open/` | `TKT-YYYY-NNN.md` |
| 消息推送 | 文本 | Telegram | — |

### 3.2 产出质量标准
- 必须包含的字段 / 段落
- 长度上下限
- 异常情况下的降级输出

### 3.3 归档规则
产出完成后，**谁**在**什么条件下**把它从 open 移到 closed，是否写入 log.md。

---

## 4. 权限（Permissions）

### 4.1 读权限
明确路径清单。默认仓库只读。

```
- docs/wiki/**                      ✅ 全读
- src/**                            ✅ 全读
- .env, secrets/**                  ❌ 禁止
```

### 4.2 写权限
**必须逐条列出可写路径**。默认禁止写。

```
- docs/wiki/boss/daily.md           ✅ 覆盖写
- docs/wiki/tickets/open/**         ✅ 创建新文件
- docs/wiki/tickets/closed/**       ❌ 只有 Boss 或指定 agent 可移动
- docs/wiki/decisions/**            ❌ ADR 必须 Boss 审批
```

### 4.3 执行权限
- 可调用的外部 API / 工具
- 禁止调用的（如部署、删除、转账类操作**默认禁止**）
- 需要 Boss 二次确认的（列入 Human-in-the-loop 清单）

### 4.4 Human-in-the-loop 清单
哪些动作必须 Boss 批准后才能执行？这是**红线**。

---

## 5. 协作关系（Collaborations）

### 5.1 上游
谁给它派活？（Boss / 其他 agent / cron / 事件源）

### 5.2 下游
它的产出给谁消费？（Boss / 其他 agent / 外部系统）

### 5.3 汇报对象
- **每日汇报：** 去向 + 形式
- **异常上报：** 触发条件 + 去向
- **静默策略：** 什么情况下不打扰 Boss

---

## 6. 验收标准（Acceptance & KPI）

### 6.1 "在认真工作"的信号
可量化的心跳指标。例如：
- 每日 08:00±5min 内必须产出日报
- 连续 3 日无产出 → 自动 status 变为 `paused` 并告警

### 6.2 "产出合格"的判定
- Boss 抽检频率
- 打回（reject）的标准动作
- 连续被打回 N 次 → 触发 Charter 复审

### 6.3 复审周期
- 默认每 **30 天**一次 Charter review
- review 结果：续聘 / 调整 Charter / 停职 / 退休

---

## 7. 运行时绑定（Runtime Binding）

### 7.1 技术栈
- Runtime: OpenClaw / MCP / 直接 API
- Skill 路径或代码仓路径
- 依赖的外部服务

### 7.2 部署与启停
- 如何启动
- 如何停用（status → paused 之后的实际下线动作）
- 如何退休（status → retired 之后数据/日志的归宿）

### 7.3 可观测性
- 日志位置
- 关键指标（调用次数、失败率、延迟）
- 问题排查入口

---

## 8. 变更历史（Changelog）

```
| 版本 | 日期 | 变更 | 操作人 |
|------|------|------|--------|
| 0.1  | YYYY-MM-DD | 初始创建 | Boss |
```

**变更规则：**
- 职责/权限/KPI 任一修改，`version` minor +1
- 大幅重构或换 runtime，`version` major +1
- 所有变更必须写 changelog，不得覆盖历史

---

## 附：创建一个新员工的 checklist

1. [ ] 从本模板复制为 `agents/agent-<id>.md`
2. [ ] 填满 Front Matter，`status: draft`
3. [ ] 写完职责、输入、产出、权限四节
4. [ ] 起草 Charter 后**先让 Boss 审阅一遍**再开发
5. [ ] 实现 runtime（OpenClaw skill / 代码）
6. [ ] 本地试运行至少 3 次，贴结果到 Charter 末尾
7. [ ] Boss 批准后 `status: active`，并在 `agents/_index.md` 登记
8. [ ] 计入下一次组织盘点（`boss/agenda.md`）
