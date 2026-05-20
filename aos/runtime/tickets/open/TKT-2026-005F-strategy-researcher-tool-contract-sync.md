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