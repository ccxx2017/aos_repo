---

# 工单：TKT-2026-005D-auto-research-builder-api

## 1. Frontmatter (工单元数据)
```yaml
ticket_id: TKT-2026-005D
title: 新增自动研究编译接口与修复回测异常序列化契约
status: closed
assigned_to: project-ai-backend-developer  # 实施主体：项目AI/后端开发者 (非 strategy-researcher)
intent_type: infrastructure_patch
priority: P0
created_at: 2026-05-20
deadline: 2026-05-23
```

---

## 2. 背景与上下文 (Context)
在 `TKT-2026-005B` 的首次受限 Smoke Run 中，系统暴露了两个致命的工具契约缺陷，直接导致了自动研究员（`strategy-researcher`）的执行失败：
1. **Builder 交互式会话僵死**：现有的 `POST /strategy-builder/invoke` 接口是为人类交互和 `quant_assistant` 设计的，包含多轮追问机制（`pending_user_input`）。当自动研究员提交不完美的 IR 时，Builder 试图进行多轮会话，导致 Agent 陷入死循环。
2. **Backtest 500 异常未序列化**：当回测发生内部错误时，后端直接抛出 Python 异常（如 `ValueError`），导致 FastAPI 尝试序列化该 Exception 对象，触发 `TypeError: ValueError is not JSON serializable`，最终向客户端返回了非结构化的 HTTP 500 崩溃响应。

### 核心决策：双通道分流
为了不破坏人类在飞书端交互微调的灵活性，同时给自动研究员提供一个“无状态、单次提交、非交互”的编译环境，我们决定**不修改原有交互接口**，而是**新建一个 Auto Research 专用编译接口**，并彻底重构后端的错误捕获与响应契约。

---

## 3. 实施范围 (In Scope)

### 任务 3.1：新增非交互式编译端点 `POST /strategy-builder/compile-ir`
在后端路由中新增一个专为 `strategy-researcher` 服务的端点，其行为契约必须是**无状态且非交互**的：
* **请求格式**：
  * **Method**: `POST`
  * **Path**: `/strategy-builder/compile-ir`
  * **Payload (JSON)**: 必须包含完整的 `strategy_ir` 对象，以及可选的元数据。
    ```json
    {
      "strategy_ir": {
        "strategy_name": "VCP_Breakout_v1",
        "universe": ["600519.SH", "000001.SZ"],
        "phases": [...],
        "transitions": [...]
      },
      "metadata": {
        "ticket_id": "TKT-2026-005B",
        "round": 3
      }
    }
    ```
* **核心行为规则**：
  1. **禁止多轮追问**：无论 IR 校验是否通过，**绝对禁止**返回 `pending_user_input` 状态，禁止保存或依赖 Session 状态。
  2. **单次判定**：后端接收到请求后，立即调用 `knowledge_base.py` 相关的编译与校验逻辑。
  3. **自动落库（KB 写入桥）**：如果编译成功，后端必须在响应返回前，在侧作用域中自动调用 `create_strategy_archive()` 将策略写入 `data/knowledge/strategies/` 目录，并更新索引。
  4. **暂时关闭自动回测**：在此接口中，即使 `auto_backtest=true`，也应暂时将其硬编码为 `false`，回测必须由 Agent 侧的 `call_backtest.py` 显式触发，以隔离排障。
* **成功响应 (200 OK)**：
  ```json
  {
    "success": true,
    "strategy_id": "stg_20260520_xxxxxx",
    "compiler_status": "compiled",
    "archive_created": true,
    "warnings": []
  }
  ```
* **失败响应 (400 Bad Request)**：
  ```json
  {
    "success": false,
    "error": {
      "code": "IR_COMPILE_FAILED",
      "message": "因子定义或语法校验未通过",
      "field_errors": [
        {"field": "strategy_ir.phases[0].indicators", "reason": "因子不在注册表中"}
      ]
    }
  }
  ```

### 任务 3.2：修复 Backtest 500 异常序列化契约
重构回测接口（`POST /backtests/execution-config`）及全局异常处理器，确保任何后端崩溃都不会向客户端透传非 JSON 序列化的 Python 异常对象：
1. **全局异常捕获**：在 FastAPI 中注册全局异常 Handler，捕获所有的 `Exception`、`ValueError`、`KeyError` 等。
2. **统一 JSON 契约**：当发生未捕获异常时，统一返回 HTTP 400 或 500 状态码，且 Body 必须为标准结构化 JSON，格式如下：
  ```json
  {
    "success": false,
    "error": {
      "code": "BACKTEST_INTERNAL_ERROR",
      "message": "回测执行引擎发生未捕获异常: [异常简短描述]",
      "retryable": false
    }
  }
  ```
3. **禁止直接序列化 Exception**：在返回前，必须将 Exception 转换为 `str(e)` 或自定义的错误消息，严禁让 FastAPI 直接序列化异常实例本身。

---

## 4. 排除范围 (Out of Scope)
* **禁止**修改或破坏原有的交互式端点 `POST /strategy-builder/invoke` 的任何行为。
* **禁止**在此工单中实现后端异步队列（`POST /jobs`）——异步化留给 P1 阶段，本次仅修复同步模式下的契约与异常捕获。
* **禁止**修改 `strategy-researcher` 的 `SKILL.md` 或启动实际研究（本工单实施主体为开发 AI，不激活研究员 Agent）。

---

## 5. 严格执行前检查报告 (Pre-execution Checklist)
项目 AI 在开始编写代码前，**必须先读取并显式输出**以下检查报告：
1. **本次你实际读取了哪些 .md 文件**：
2. **你是否调用了任何 scripts/ 下的脚本**：
3. **哪个文件是最高行为手册**：
4. **正式执行时必须遵循哪些 Phase**：
   * **Phase 0**: 确认本地后端代码库处于最新分支。
   * **Phase 1**: 编写单元测试，复现 Backtest 500 序列化失败问题。
   * **Phase 2**: 实现 `POST /strategy-builder/compile-ir` 接口。
   * **Phase 3**: 重构全局异常处理器，修复序列化问题。
   * **Phase 4**: 运行本地测试，确保双接口分流且不互相干扰。
5. **是否已经满足正式执行条件**：(评估环境连通性与代码库只读访问，给出是/否结论)

---

## 6. 验收标准与验证路径 (Acceptance Criteria)

### 6.1 机械化代码审计
* 检查新端点 `/strategy-builder/compile-ir` 源码，确认其中没有任何读取 Session、返回 `pending_user_input` 或支持多轮对话的代码。
* 检查 FastAPI 异常处理器，确认所有 `except Exception as e` 分支中，返回的 JSON Payload 均不包含原始 Exception 对象，而是将其转化为字符串。

### 6.2 接口行为验证 (需提供 curl 运行日志)
1. **验证通道 A (旧接口不受影响)**：
   * 发送不完整请求至 `/strategy-builder/invoke`，验证其依然能返回 `pending_user_input` 并维持 Session。
2. **验证通道 B (新接口严格编译)**：
   * 提交一个合法的 `strategy_ir`，验证返回 `200 OK`，且 `archive_created` 为 `true`，在 `data/knowledge/strategies/` 下成功生成了对应的 markdown 档案。
   * 提交一个包含未知因子的非法 `strategy_ir`，验证其立即返回 `400 Bad Request` 和结构化 JSON 错误，**没有**进入多轮会话。
3. **验证异常序列化修复**：
   * 故意向回测端点发送一个会触发后端 `ValueError` 的极端请求，验证其返回合法的 JSON 格式错误（状态码 500 或 400），且不出现 `TypeError: ValueError is not JSON serializable` 报错。

---

## 7. 交付物清单 (Deliverables)
1. 后端新增端点 `/strategy-builder/compile-ir` 的实现代码。
2. 修复后的后端异常捕获与序列化模块代码。
3. 本地验证测试脚本或 `curl` 测试命令及其实际输出日志。
4. 在工单末尾追加 Worklog，记录修改的文件列表及测试通过证明。

---

## 8. Worklog

### 8.1 执行摘要
- 完成 `POST /strategy-builder/compile-ir` 新增，实现为无状态、非交互、单次判定通道。
- 保持原有 `POST /strategy-builder/invoke` 行为不变，旧接口仍保留 `pending_user_input` 多轮会话能力。
- 修复 `POST /backtests/execution-config` 在内部异常场景下的结构化 JSON 返回，避免直接透传或序列化 Python Exception。
- 扩展全局异常处理器，使 `HTTPException.detail` 与兜底异常都转换为可序列化的标准错误对象。

### 8.2 修改文件列表
- `backend/app/api/endpoints/strategy_builder.py`
- `backend/app/api/endpoints/backtests/start.py`
- `backend/app/core/exception_handlers.py`
- `backend/tests/api/endpoints/test_strategy_skill_endpoints_e1.py`
- `backend/tests/api/endpoints/test_backtests_refactored.py`
- `backend/tests/api/endpoints/test_error_envelope.py`
- `backend/tests/manual/validate_tkt_2026_005d.py`

### 8.3 关键实现说明

#### A. 新增 `/strategy-builder/compile-ir`
- 输入仅接受 `strategy_ir` 与可选 `metadata`。
- 不读取 Session，不写入会话状态，不返回 `pending_user_input`。
- 先执行 `StrategyIR.model_validate(...)` 做结构校验。
- 再递归提取 IR 中的 `indicator`，用 `IMPLEMENTED_INDICATORS` 做编译期注册表校验。
- 再调用 `compile_execution_config(...)` 做编译探测。
- 编译成功后在响应前调用 `create_strategy_archive(...)` 和 `update_index()`，自动写入 `data/knowledge/strategies/`。
- 在该接口中将 `auto_backtest` 视为禁用，仅作为 warning 回传，不触发自动回测。

#### B. 修复回测异常序列化契约
- `POST /backtests/execution-config` 新增统一 `_backtest_internal_error(...)` 包装。
- 对非 `HTTPException` 的内部异常统一转换为：
  ```json
  {
    "code": "BACKTEST_INTERNAL_ERROR",
    "message": "回测执行引擎发生未捕获异常: ...",
    "retryable": false
  }
  ```
- 全局异常处理器中对 `detail` / `data` 做字符串化，禁止原始 `Exception` 实例进入 JSON Payload。
- 全局错误响应额外补充 `error` 对象，便于 Agent 或前端直接读取标准错误结构。

### 8.4 自动化测试结果

#### Pytest
执行命令：

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/api/endpoints/test_strategy_skill_endpoints_e1.py backend/tests/api/endpoints/test_backtests_refactored.py backend/tests/api/endpoints/test_error_envelope.py -q
```

实际输出：

```text
...............                                                          [100%]
15 passed, 3 deselected in 2.62s
```

### 8.5 本地接口验证日志

#### 验证脚本
执行命令：

```powershell
.\.venv\Scripts\python.exe backend\tests\manual\validate_tkt_2026_005d.py
```

#### 通道 A：旧接口不受影响
等价命令：

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/strategy-builder/invoke -H "Content-Type: application/json" -d "{...}"
```

关键输出：

```text
HTTP 200
"pending_user_input": "策略已生成：均线上穿且缩量时触发。这样可以吗？..."
"session_id": "sb_10bb9ae34596"
```

结论：
- 旧接口仍返回 `pending_user_input`
- 旧接口仍维持 Session 语义

#### 通道 B-1：新接口合法 IR
等价命令：

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/strategy-builder/compile-ir -H "Content-Type: application/json" -d "{...}"
```

关键输出：

```text
HTTP 200
{
  "success": true,
  "strategy_id": "tkt_2026_005d_demo",
  "compiler_status": "compiled",
  "archive_created": true,
  "warnings": []
}
archive_exists=True path=data\knowledge\strategies\tkt_2026_005d_demo.md
```

结论：
- 新接口成功编译
- 成功自动落库到知识库档案目录
- 响应中未出现 `session_id` 或 `pending_user_input`

#### 通道 B-2：新接口非法 IR
等价命令：

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/strategy-builder/compile-ir -H "Content-Type: application/json" -d "{...invalid...}"
```

关键输出：

```text
HTTP 400
{
  "success": false,
  "error": {
    "code": "IR_COMPILE_FAILED",
    "message": "因子定义或语法校验未通过",
    "field_errors": [
      {
        "field": "strategy_ir.phases",
        "reason": "因子不在注册表中: unknown_factor"
      }
    ]
  }
}
```

结论：
- 非法 IR 立即失败
- 返回结构化错误
- 未进入多轮会话

#### 异常序列化修复验证
等价命令：

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/backtests/execution-config -H "Content-Type: application/json" -d "{...}"
```

关键输出：

```text
HTTP 500
{
  "success": false,
  "code": 500,
  "message": "回测执行引擎发生未捕获异常: compiler exploded",
  "data": {
    "code": "BACKTEST_INTERNAL_ERROR",
    "message": "回测执行引擎发生未捕获异常: compiler exploded",
    "retryable": false
  },
  "errorCode": "BACKTEST_INTERNAL_ERROR",
  "error_code": "BACKTEST_INTERNAL_ERROR",
  "error": {
    "code": "BACKTEST_INTERNAL_ERROR",
    "message": "回测执行引擎发生未捕获异常: compiler exploded",
    "retryable": false
  }
}
```

结论：
- 已返回合法 JSON 错误对象
- 未出现 `TypeError: ValueError is not JSON serializable`

### 8.6 约束遵循记录
- 未调用任何 `scripts/` 目录下脚本。
- 未修改 `POST /strategy-builder/invoke` 的既有会话语义。
- 未实现异步队列 `POST /jobs`。
