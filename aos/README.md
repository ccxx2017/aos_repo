# AOS

AOS 表示 **Agentic Organization System**。

它是 AI 数字组织的操作知识与运行工作区。
AOS = Boss + Agents + Memory + Projects + Runtime + Archive

它不是普通 wiki。

## Domains

| 领域 | 路径 | 含义 |
|---|---|---|
| Organization | `org/` | Boss、agents、roles、policies、registry |
| Projects | `projects/` | 被管理项目的知识与项目级归档 |
| Runtime | `runtime/` | 当前 tickets、reports、runs、logs、status |
| Archive | `archive/` | 跨领域或未分类历史材料 |

## Archive Rule

```text
项目相关归档   -> projects/<project_id>/archive/
组织相关归档   -> org/archive/
运行相关归档   -> runtime/archive/
跨域/未分类归档 -> archive/

Naming Note
本目录原名为 wiki/。

由于它现在不仅包含静态知识页面，还包含组织定义、项目状态、运行工单、报告与历史记忆，因此重命名为 aos/。