# AOS — 数字员工组织工作区

## 目录结构

| 目录 | 用途 |
|------|------|
| org/ | 组织定义（角色 Chater、架构、Boss 手册） |
| 
runtime/tickets/ | 正式工单系统（open → doing → blocked → done） |
| 	asks/ | Boss 随手记 backlog（不成形想法 / 待办） |
| 
reports/org/ | 组织自身报告（绩效、工单统计） |
| 
reports/project/ | 项目状态报告（duty_reporter 日报等） |
| decisions/ | 组织运行决策（ORD），区别于 docs/decisions/ |

## tasks/ 与 runtime/tickets/ 的分工

- **tasks/** 是你的个人灵感和临时清单，不需要状态机，一句话也行
- **runtime/tickets/** 是正式工单，指派给数字员工，遵循 open → doing → done 状态机
- 一个想法成熟后，从 	asks/backlog.md 提升为正式 TKT-xxx 工单
