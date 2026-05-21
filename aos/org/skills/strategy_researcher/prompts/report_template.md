# report_template.md — 研究报告模板

> 产出位置：`${REPORT_DIR}/{ticket_id}-{slug}.md`
> 读者：Boss（决定是否立项 / 部署） + 未来的你（复盘）

## 文件名

`{ticket_id}-{slug}.md`，例如 `TKT-2026-007-ma-trend-5d-confirmation.md`。
- slug 用 kebab-case，≤ 40 字符
- 不含空格 / 中文 / 标点（便于 shell 引用）

## 章节骨架（不可缺项）

```markdown
# {研究主题标题}

- **Ticket**: {ticket_id}
- **Agent**: agent-strategy-researcher
- **Rounds executed**: {N}
- **Stopped reason**: {completed | max_rounds | builder_failed_x2 | drawdown_extreme | hypothesis_space_exhausted | paused_for_boss_review}
- **Date range**: {start_date} ~ {end_date}

## 1. 背景与目标

{2–3 段说明工单要研究什么、为什么值得研究。引用 ticket 正文关键句。}

## 2. 先验上下文

{Phase 2 读 KB 得到的图景。KB 不可达时写明 "basis=agent_prior"。}

### 2.1 已有同类策略

| strategy_id | Intent | 最佳 Sharpe | 主要特征 |
|---|---|---|---|
| ... | ... | ... | ... |

### 2.2 引用的市场认知

- `volume_shrink_rebound` (confidence=high) —— 本研究 Round X 复用
- ...

## 3. 研究轮次

每一轮（按 round_idx 递增）：

### Round {N}

- **假设**：{一句话}
- **机制假说**：{为什么应该成立}
- **相对上一轮的改动**：{单一变量}
- **IR 摘要**：{phases + transitions 一句话}
- **回测**：
  - Run ID: `{run_id}`
  - 区间: {start} ~ {end}
  - Sharpe: {x.xxxx}（train {x.xxxx} / test {x.xxxx}）
  - 年化收益: {x.xxxx}
  - 最大回撤: {x.xxxx}
  - Calmar: {x.xxxx}
- **观察**：{2–4 条 bullet。样本内外差距？沉默 transition？相对基线变化？}

（失败轮也要有条目，标 `status: builder_failed` / `no_backtest`，写失败原因）

## 4. 跨轮对比

直接嵌入 `metrics.py aggregate` 产出的 markdown 表。然后 1–2 段**分析性**文字：

- 哪一轮最好？为什么？是假设的胜利还是参数过拟合？
- 哪些改动无效（sharpe 没动）？
- 最好轮 vs 最差轮差距？说明稳健性如何？

## 5. 结论与建议

### 5.1 本次研究回答了什么
{工单问题的直接答案。一句话能说清就一句话。}

### 5.2 最佳产出
{推荐哪个 strategy_id 进入下一步？给出 run_id。说明为什么是它。}

### 5.3 下一步
{1–3 个后续方向，可作为新工单种子：
- "建议开 ticket：验证 Round 3 策略在 2022 熊市的表现"
- "建议开 ticket：扩展 Round 5 参数网格"
- "本方向暂时到顶，建议转向 X"}

## 6. 附录

### 6.1 Run ID 一览

| Round | run_id | 数据位置 |
|---|---|---|
| ... | ... | `runtime/research-runs/{ticket_id}/round_N.json` |

### 6.2 引用的档案

- `${KB}/archives/{strategy_id}` —— 被引用的方式

### 6.3 执行元数据

- Git commit 范围: `{first_sha}..{last_sha}`
- 主机: ubuntu-dev
- Python: 3.x
- 开始 / 结束时间
```

## 写作要求

- **所有数值保留 4 位小数**（与 `data/knowledge/schema.md` 约定一致）
- **不凑数**。失败轮如实写，别粉饰
- **能溯源**。每个论断引 `run_id` / `strategy_id` / insight topic 之一
- **分析 > 陈述**。读者看得见 metrics 表，不需要你复述数字；他们需要的是你对数字的解读
- **长度控制**：典型 800–2000 字。超 2000 字说明你在复述数据，压回去