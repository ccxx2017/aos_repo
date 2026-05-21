目标不是研究，而是把这次 smoke 中临时发现/修改的东西固化：

call_builder.py --endpoint 不能只停留在 Ubuntu skill 目录的本地修改里，要同步到正式技能资产源。
TOOLS.md 明确写：
investigation 必须用 /strategy-builder/compile-ir
禁止 /strategy-builder/invoke
execution-config 回测必须传完整 strategy_ir，不是只传 strategy_id
research_workflow.md 补充新流程：
compile-ir → archive_created → call_backtest execution-config → kb_query 读取 KB 口径
metrics.py 要兼容新路径，不能再把 compile-ir + execution-config 的结果误判为 no_backtest。
明确 400/404 的客户端格式探索错误不等于 Boss guardrail；但 5xx/timeout/connection failure 仍然一票暂停。

## Worklog

**2026-05-21 08:01** — 开始执行工具契约同步（v0.2.0 → v0.2.1）

### 已修改文件

| 文件 | 变更 |
|---|---|
| `scripts/call_builder.py` | 默认端点从 `/strategy-builder/invoke` 改为 `/strategy-builder/compile-ir`；更新 docstring 说明端点政策 |
| `SKILL.md` | BUILDER_API 路径更新；v0.2.1 changelog 添加；版本号 0.2.0 → 0.2.1 |
| `TOOLS.md` | call_builder 用途改为 compile-ir；call_backtest 增加 strategy_ir 传参要求；新增 4xx vs 5xx 错误语义表 |
| `prompts/research_workflow.md` | Phase 3 重构为 compile-ir → execution-config → KB read 流程；§3.1 更新 400/404 错误语义说明 |
| `scripts/metrics.py` | 新增 `_extract_backtest()` 函数，兼容新路径（backtest_response）和旧路径（builder_response.backtest）；更新 docstring |
| `aos/org/skills/strategy_researcher/` | **新建** — 作为正式技能资产源，同步包含全部脚本和 prompts |

### 文件变更统计
- 修改 5 个文件（workspace skill 目录）
- 新增 12 个文件（aos_repo org/skills/ 目录）
- commit: `224eb6b`
- git push: ✅ 成功

**2026-05-21 08:01** — 所有变更已落地。工单完成。