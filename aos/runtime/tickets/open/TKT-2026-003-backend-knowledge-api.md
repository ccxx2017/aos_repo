---
id: TKT-2026-003
title: 后端：知识库只读 HTTP API + 写侧自动落库
status: open
priority: high
assigned_to: boss
created_at: 2026-05-06
created_by: boss
blocks: [TKT-2026-004]
blocked_by: []
tags: [backend, knowledge-base, api]
---

## Intent

strategy-researcher 数字员工需要读取 `data/knowledge/` 下的策略档案和索引，
但 Agent 与后端是**网络隔离**关系（Agent 只能 HTTP 调用后端，不能 import
Python 模块）。因此需要：

1. 为 `knowledge_base.py` 的 4 个读函数在后端加 4 个只读 GET 接口；
2. 将 `create_strategy_archive()` 和 `append_backtest_result()` 这两个
   写函数**内嵌到已有业务端点的成功路径**里，让知识库随 strategy-builder
   和 backtest 的执行自动增长，Agent 永远不直接调用写侧。

## Deliverable Spec

### 只读 GET 接口（4 个）

- [ ] `GET /api/v1/knowledge/index` → 200 / `text/plain`，返回 `read_index()` 内容
- [ ] `GET /api/v1/knowledge/strategies` → 200 / `application/json`，
      返回 `list_strategy_archives()` 的结果，每项含
      `{id, intent, ir_summary, backtest_count, created_at}`
- [ ] `GET /api/v1/knowledge/strategies/{strategy_id}` → 200 / `application/json`，
      返回 `read_strategy_archive(strategy_id)` 的完整 markdown 内容；
      不存在时 404
- [ ] `GET /api/v1/knowledge/log` → 200 / `text/plain`，返回 `read_log()` 内容

### 写侧自动化 hook（2 处）

- [ ] 在 `POST /strategy-builder/invoke` 成功生成新策略 IR 的路径尾部，
      调用 `create_strategy_archive(ir, intent)`；失败则仅记日志、
      **不影响**该端点的 200 响应（归档失败不阻塞业务）
- [ ] 在 `POST /backtests/execution-config` 返回 200 的路径尾部，
      调用 `append_backtest_result(strategy_id, backtest_result)`；失败处理同上
- [ ] 以上两处写完后，调用 `update_index()` 刷新 `index.md`

### 容错要求

- [ ] `data/knowledge/` 目录不存在时，4 个 GET 接口返回 200 + 空内容
      （`index` 返回占位文本，`strategies` 返回 `[]`，`log` 返回空串），**不得 500**
- [ ] 所有写侧 hook 失败时只记 WARNING 日志，不抛异常污染业务响应

## 显式排除

- ❌ 不开放 POST / PUT / DELETE 到 `/knowledge/*`（写侧永不对 Agent 暴露）
- ❌ 不修改 `knowledge_base.py` 现有 9 个函数的签名
- ❌ 不引入鉴权（与其他 API 保持一致的内网信任模型）
- ❌ 不做缓存（知识库规模小，每次读盘即可）

## 验收方式

- [ ] curl 4 个 GET 接口，各自返回预期结构
- [ ] 跑一次完整链路：调用 `strategy-builder/invoke` → 查 `/knowledge/strategies`
      能看到新策略 → 调用 `backtests/execution-config` → 再查该策略
      的 backtest_count 增加
- [ ] 故意把 `data/knowledge/` 重命名，4 个 GET 仍 200 不 500

## Worklog

_待开工后 append_