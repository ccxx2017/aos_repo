# Tools · strategy-researcher

本清单对应 SKILL.md v0.2.1。

## 通用约定

- 后端基地址：默认 `http://192.168.1.136:8000`，可用环境变量 `QUANT_BACKEND_URL` 覆盖。
- 所有 Python 脚本**仅依赖标准库**（`urllib` + `json` + `argparse` + `pathlib` 等），无需 pip install。
- 统一输出 JSON 到 stdout：`{"ok": true, ...}` 或 `{"ok": false, "error": "...", ...}`；
  `metrics.py` 额外打印 markdown 表格，便于人读。
- 统一退出码：`0` 成功 · `1` 可重试（网络/超时） · `2` 不可恢复（业务错误/4xx/输入非法）。
- 超时：GET 默认 30s；builder 默认 300s；backtest 默认 90s（TKT-2026-005C 资源闸）；`--timeout` 可覆盖。
- **脚本不做工作流决策**。研究主循环的判断在智能体（见 `prompts/research_workflow.md`），脚本只是工具。

---

## 已落地 · HTTP 适配层

### scripts/call_builder.py

| 项 | 内容 |
|---|---|
| 用途 | **PRIMARY** POST `/strategy-builder/compile-ir` |
| 入参 | JSON 请求体（stdin 或 `--input-file`），透传给后端 |
| 出参 | `{"ok": true, "status": 200, "data": {...}}` |
| 关键参数 | `--base-url` `--timeout` `--input-file` `--endpoint` |
| 错误码 | `invalid_json_input`(2) · `http_4xx`(2, 客户端格式探索) · `http_5xx`(2, 一票暂停) · `network_error`(1) |
| 端点政策 | **investigation 必须使用 `/strategy-builder/compile-ir`**。`/strategy-builder/invoke` **禁止**（保留给 quant_assistant 交互式对话模式） |
| 示例 | `echo '{"message":"...","session_id":"research_TKT-2026-007","auto_backtest":true}' \| python3 scripts/call_builder.py` |

### scripts/call_backtest.py

| 项 | 内容 |
|---|---|
| 用途 | POST `/backtests/execution-config`，自动处理 `DATA_MISSING_SYNC_REQUIRED` 的单次重试 |
| 入参 | JSON 请求体，至少含 `execution_config.universe.symbols` **且必须传入完整 `strategy_ir`**（不可只传 `strategy_id`）；如需样本内外回测，可在顶层追加 `train_split`（如 `0.7`） |
| 出参 | `{"ok": true, "retried": bool, "run_id": "...", "status": "completed", ...}`；若请求含 `train_split`，会在 `raw.data.train_metrics` / `raw.data.test_metrics` 原样保留后端结果，并镜像到顶层 `train_metrics` / `test_metrics` |
| 关键参数 | `--base-url` `--timeout` `--input-file` `--no-retry-on-missing-data` |
| 重试策略 | 仅 `DATA_MISSING_SYNC_REQUIRED` 且 `missing_symbols` 非空时剔除后重试 1 次；剔后 universe 为空 → `empty_universe_after_prune`(2) |
| 错误码 | `invalid_json_input`(2) · `http_4xx`(2, 客户端格式探索) · `http_5xx`(2, 一票暂停) · `retry_failed`(2) · `empty_universe_after_prune`(2) · `network_error`(1) |
| **回测传参要求** | execution-config 必须传完整 `strategy_ir`（builder compile-ir 返回的中间表示），不得只传 `strategy_id` |
| 示例 | `echo '{"execution_config":{"universe":{"type":"explicit","symbols":["000300.SH","000905.SH"]},"backtest_params":{"start_date":"2020-01-01","end_date":"2023-01-01"},"strategy_ir":{...}},"train_split":0.7}' \| python3 scripts/call_backtest.py` |

### scripts/kb_query.py

| 项 | 内容 |
|---|---|
| 用途 | **只读**访问 KB：`index` / `log` / `archives`(list) / `archive <id>`(detail) |
| 子命令 | `index` / `log` / `archives` / `archive <strategy_id>` |
| 出参 | `index/log/archive` → `{"ok": true, "content": "..."}`；`archives` → `{"ok": true, "archives": [...]}` |
| 错误码 | `http_404`(2) · `network_error`(1) |
| 示例 | `python3 scripts/kb_query.py index \| jq -r .content \| head` |

### scripts/smoke_http_clients.sh

Happy-path 连通性自检（同 v0.1.0）。按序跑 `kb_query index → archives → archive <不存在 id>(预期 rc=2) → log`，任一步失败整体退出非 0。

---

## 已落地 · 计算工具（v0.2.0 新增）

### scripts/metrics.py

| 项 | 内容 |
|---|---|
| 用途 | 把 `${RESEARCH_RUNS}/{ticket_id}/round_<N>.json` 聚合为 `metrics.json`，并打印跨轮对比 markdown 表 |
| 依赖 | 纯标准库（`argparse` / `json` / `pathlib` / `re`） |
| 子命令 | `aggregate --run-dir <研究任务目录>` |
| 输入 | `round_<N>.json`，每份含回测指标，兼容两条路径：**路径 A** `builder_response.backtest.metrics` · **路径 B** `backtest_response.raw.data.metrics`（compile-ir + execution-config 分离模式）。自动检测，不再误判新路径为 `no_backtest` |
| 产出 | 写 `<run-dir>/metrics.json`；stdout 打印对比表 |
| 对比维度 | `sharpe_ratio`, `annualized_return`, `max_drawdown`, `calmar_ratio`, `win_rate`（4 位小数，与 `data/knowledge/schema.md` 对齐） |
| 错误码 | `run_dir_not_found`(2) · `unhandled`(2) |
| 边界 | **不调 HTTP、不调 LLM、不做研究决策**。仅确定性数学 + 格式化 |
| 示例 | `python3 scripts/metrics.py aggregate --run-dir /home/ccxx/aos_repo/aos/runtime/research-runs/TKT-2026-007/` |

---

## 4xx vs 5xx 错误语义（全脚本通用）

| HTTP 状态码 | 分类 | 处理策略 |
|---|---|---|
| 400/404 | 客户端格式探索错误（请求体结构、字段名拼写、strategy_ir 格式不兼容等） | 标记 `format_mismatch`，修正后**下一轮继续**。不是 guardrail，不触发暂停。 |
| 5xx | 服务端内部错误 | 标记 `backend_error_5xx`，**一票暂停**，进入 `paused_for_boss_review`。 |
| timeout / connection failure | 网络级不可达（`network_error`） | 标记 `backend_unreachable`，**一票暂停**，进入 `paused_for_boss_review`。 |

---
## 行动手册（非脚本，但同等重要）

`prompts/` 目录下的自然语言 playbook 是 strategy-researcher 的**核心产物**之一，
承载了工具调用之外"何时调、如何解读、何时停"的全部判断逻辑：

| 文件 | 用途 |
|---|---|
| `prompts/research_workflow.md` | 主 playbook；每个 investigation 工单开始必读 |
| `prompts/hypothesis_heuristics.md` | 假设生成启发式（每轮参考） |
| `prompts/report_template.md` | 研究报告结构与写作规范 |
| `prompts/README.md` | 目录说明与硬约束 |

---

## 已撤销 / 延后

| 原计划 | 状态 | 原因 |
|---|---|---|
| `scripts/research_loop.py` | **撤销** | 研究主流程是智能体判断密集的工作，不应写成脚本状态机。改由 `prompts/research_workflow.md` 承载。 |
| `scripts/report_render.py`（原 TKT-2026-006） | **撤销** | 报告是叙事性产物，按 `prompts/report_template.md` 写即可，无需模板引擎。 |
| `scripts/llm_client.py` | **延后** | 智能体本身即 LLM。卸载到外部 LLM 的需求待首次真实使用暴露后再评估（Ticket A 决策 C 方案）。 |
