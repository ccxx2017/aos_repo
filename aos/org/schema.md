# Wiki Schema

## 原则
- `docs/raw/` 是只读的。LLM 绝不修改这些文件。
- `docs/wiki/` 是 LLM 的工作区。LLM 拥有这个目录的所有文件。
- 用户极少直接编辑 wiki 文件。如果需要修正，告诉 LLM 来做。
- 每次对 wiki 的修改都要更新 `index.md` 和 `log.md`。

## 页面格式
每个 wiki 页面以 YAML frontmatter 开头：
---
title: 页面标题
created: 2026-04-16
updated: 2026-04-16
sources: [raw/design-decisions/xxx.md, raw/reference/yyy.md]
tags: [architecture, backend, websocket]
status: current | outdated | draft
---

## 交叉引用
- 使用 [[wiki-link]] 格式链接其他 wiki 页面
- 每个页面底部有 "Related Pages" 部分
- 引用原始资料时用 `[source](../raw/path/to/file.md)` 格式

## Ingest 流程
当用户提供新的原始资料时：
1. 将原始文件放入 `docs/raw/` 对应子目录
2. 阅读全文，提取关键信息
3. 更新或创建相关 wiki 页面
4. 更新 index.md
5. 在 log.md 追加记录

## Lint 检查项
定期对 wiki 进行健康检查：
- 信息一致性：wiki 页面之间是否有矛盾
- 与代码的一致性：wiki 描述的架构是否与实际代码匹配
- 覆盖度：是否有重要组件/流程没有对应的 wiki 页面
- 时效性：是否有页面的 status 应该标记为 outdated
- 孤岛页面：是否有页面没有任何入链

## 从运行时日志学习
当用户提供系统运行日志时：
1. 分析日志中的服务交互模式
2. 更新对应组件页面的"运行时行为"部分
3. 如果发现异常或错误，更新 troubleshooting.md
4. 如果发现新的性能指标，记录到对应页面