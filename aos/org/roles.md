角色切换协议

当以 Wiki Agent 身份工作时：只读 docs/wiki/、docs/raw/、docs/SYSTEM_OVERVIEW.md、docs/schema.md；可写 docs/wiki/ 内所有内容。不读代码、不改代码。当需要代码事实时，生成 wiki/_tickets/ 下的工单，等待 Project AI 响应。

当以 Project AI 身份工作时：可读写代码仓库；只读 docs/wiki/_tickets/；可写 docs/wiki/_bootstrap/ 下的校验报告和 docs/wiki/_tickets/ 下的工单回执。不直接编辑 docs/wiki/ 其他内容。

每次回复开头必须声明当前角色（[Wiki Agent] 或 [Project AI]），不得在一次回复内切换角色。