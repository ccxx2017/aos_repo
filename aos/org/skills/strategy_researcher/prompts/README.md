# prompts/ — strategy-researcher 行动手册

本目录存放 strategy-researcher 数字员工执行研究工单时使用的**自然语言 playbook**。
这些不是被脚本消费的 prompt 模板，而是给智能体自己读的工作手册。

## 文件清单

| 文件 | 用途 | 读取时机 |
|---|---|---|
| `research_workflow.md` | 主 playbook：从接单到交付的端到端流程 | **每个 investigation 工单开始必读** |
| `hypothesis_heuristics.md` | 如何提出有归因价值的假设 | 每轮循环提假设前参考 |
| `report_template.md` | 研究报告的章节骨架与写作规范 | 写报告前参考 |

## 硬约束（所有 playbook 的公共前提）

1. **只读 KB**。知识库写入由后端在 builder/backtest 成功时作为副作用完成。
   你通过 `scripts/kb_query.py` 读 index / archives / log，**绝不**直接写 KB。
   KB 字段含义、Intent 分类、小数位约定见仓库侧 `data/knowledge/schema.md`
   （权威源，本目录不复制其内容）。

2. **只调白名单端点**：builder / backtest / kb_query。
   禁触 `strategy-deploy/*`、`order/*`。

3. **写入边界**（详见 `SKILL.md §读写边界`）：
   - `${REPORT_DIR}/{ticket_id}-{slug}.md`
   - `${RESEARCH_RUNS}/{ticket_id}/{hypotheses.jsonl, round_<N>.json, metrics.json, summary.md, run.log}`
   - 承接工单的 `## Worklog` 段（append-only）

4. **可追溯**：每个结论能溯源到一个 `run_id` 或 `strategy_id` 或 `insight topic`。

5. **轮次有限**：默认每个工单 ≤ 5 轮；触发停止条件立刻停，原因写 worklog。

## 寻址约定

这些文件部署在 Ubuntu 侧 `~/.openclaw/workspace/skills/strategy_researcher/prompts/`。
你通过**相对技能目录**访问，不要用 CWD 相对路径。

## 与 backend 侧 `data/knowledge/schema.md` 的分工

| 关注点 | 文档 |
|---|---|
| 研究员如何研究（流程、判断、产出） | 本目录（openclaw 侧） |
| KB 的数据结构与写入规则 | `data/knowledge/schema.md`（backend 侧） |

跨引用时，本目录的文档**只做指针**，不复述 schema.md 的内容。