# hypothesis_heuristics.md — 假设生成启发式

> 参考材料。`research_workflow.md §3.1` 每轮调用你时读它。
> 目标：让每一轮假设都有**归因价值**，而不是随机试错。

## 一个好假设的四个特征

1. **可证伪**。"加入 3 日确认可降低假突破率" 可验；"市场会变好" 不可验。
2. **单一变量**。相对上一轮只改一个维度。多维度同改 → 回测变好时你说不清是哪个的功劳。
3. **可转 IR**。能用 phases + transitions 表达。"应该看情绪" 不可转；"VIX>25 时降仓至 30%" 可转。
4. **有机制**。说得出"为什么应该成立"的理由，哪怕简陋。无机制假设即使数据支持也是过拟合候选。

## 生成假设的五个切入点（按价值从高到低）

### A. 修正上一轮的失效点（最高价值）
- 上轮 `phase_stats.never_triggered_transitions` 非空 → 直接删 / 重写那条 transition
- 上轮样本外崩了 → 这轮减参数或加稳健性过滤
- 上轮回撤集中在某段时间 → 加对应状态的保护条件

### B. 引入 KB 已验证的市场认知
读 `market_insights/` 目录（通过 `kb_query`）。`confidence=high` 的观察直接复用。
例："缩量回调后反弹" 高置信 → 加 "volume < MA20 × 0.7 时买入"。

### C. 参数网格的定向探索
**不是**随便换参数，是有方向的：
- 上轮 MA(5/20) 过拟合 → MA(10/40)（更慢更稳）
- 不要横跳 MA(7/23)（无方向，纯随机）

### D. 跨 Intent 组合
同 universe 在不同市场状态下用不同 intent：趋势市 trend_following，震荡市 mean_reversion。
**前提**：需要一个市场状态判别器作为切换条件。

### E. 标的重组
同策略换 universe（如大盘股 → 小盘股），看策略容量 / 风格暴露。

## 什么样的假设别提

- "增大 max_tokens / 延长历史窗口" —— 不是策略假设，是超参
- "加更多指标" —— 无机制的堆砌
- 上一轮已试过的（读一下 `hypotheses.jsonl` 历史再提）
- 超出 ticket 范围的（ticket 问 A 股 T+1，你提加密永续）

## hypotheses.jsonl 每行的字段

```json
{
  "round": 3,
  "hypothesis": "<一句话自然语言>",
  "rationale": "<机制解释：为什么应该成立>",
  "changed_from_prior": "<相对上一轮改了哪一个维度>",
  "based_on_archives": ["trend_002", "mean_rev_001"],
  "based_on_insights": ["volume_shrink_rebound"],
  "analysis": "<回测后填；本轮观察 2-4 条>"
}

`based_on_*` 是你**可追溯性的证据**。两者都空 = 拍脑袋提的——偶尔可以，但 `rationale` 要写清机制。