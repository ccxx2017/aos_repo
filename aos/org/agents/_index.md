---
doc_type: agent-index
schema_version: 0.1
maintained_by: Boss
last_reviewed: 2026-04-23
---

# Agent Index · 员工花名册

> 组织内所有数字员工的索引。**新员工 Charter 建立后必须在此登记**；
> 员工状态变更（paused / retired）也必须同步此表。
>
> 本表只存索引，真实 Charter 在各自 `agent-<id>.md` 文件中。

---

## 在岗员工（active）

| ID | 姓名 | 职责一句话 | 版本 | 上线日 | 上次 review |
|----|------|-----------|------|--------|-------------|
| —  | —   | （暂无）   | —    | —      | —           |

## 试用期（draft）

| ID | 姓名 | 职责一句话 | 关联工单 | 目标转正日 |
|----|------|-----------|---------|-----------|
| [agent-duty-reporter](./agent-duty-reporter.md) | 值班汇报员 | 每日系统健康汇报 + 异常告警 | [TKT-2026-001](../tickets/open/TKT-2026-001-setup-duty-reporter.md) | 2026-05-15 |
| [agent-strategy-researcher](./agent-strategy-researcher.md) | 策略研究员 | 接受 Boss 下达的研究类工单，驱动多轮"假设→回测→分析→沉淀"循环，
把可复用的策略发现写入 `data/knowledge/`。 | [TKT-2026-002](../tickets\open\TKT-2026-002-charter-strategy-researcher.md) | 2026-05-15 |


## 停职（paused）

| ID | 姓名 | 停职原因 | 停职日 | 预计复职 |
|----|------|---------|--------|---------|
| —  | —   | —        | —      | —       |

## 退休（retired）

| ID | 姓名 | 服役期 | 退休原因 |
|----|------|--------|---------|
| —  | —   | —      | —        |

---

## 登记规则

1. **新建 Charter** → 同时在"试用期"表新增一行
2. **status: draft → active** → 从"试用期"移到"在岗员工"
3. **status → paused / retired** → 移到对应表，原表删除
4. **本索引与 Charter 状态不一致时，以 Charter 为准**，但必须尽快修复索引