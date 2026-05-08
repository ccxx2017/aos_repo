# TKT-2026-004b — 目录命名归一：strategy_researcher → strategy-researcher

- **id**: TKT-2026-004b
- **title**: 统一 strategy-researcher 技能目录命名（下划线→连字符）
- **intent_type**: infrastructure
- **assignee**: openclaw-agent (self-executed) / boss 兜底核验
- **created_at**: 2026-05-07
- **due**: 2026-05-08
- **priority**: P1（阻塞 TKT-2026-005）
- **status**: open

## 1. 背景

TKT-2026-004 交付核验中发现命名歧义：
- Charter (`aos/org/agents/agent-strategy-researcher.md`) 与 SKILL.md `name` 字段使用连字符 `strategy-researcher`
- 实际技能目录落地为下划线 `strategy_researcher`（Windows `abu_modern/openclaw_skills/` 与 Ubuntu `~/.openclaw/workspace/skills/`）

两套命名并存会污染后续 run-log、report 引用、可能的脚本自引用。在 TKT-2026-005 开工前一次性归一。

## 2. 归一目标

全系统 slug 统一为 **`strategy-researcher`（连字符）**，理由：
- 与 Charter / SKILL.md name / agent-id 对齐
- 与既有 `duty-reporter` 保持对称
- Skill 目录不是 Python 包，无 import 障碍

## 3. 任务清单

### Phase 0 — 同步
- `aos_repo` 执行 `git pull --rebase`
- 确认工作区干净

### Phase 1 — Windows 端（abu_modern 所在机器）
- `git mv openclaw_skills/strategy_researcher openclaw_skills/strategy-researcher`
  （或等价的 rename 操作，保留 git 历史）
- 全文搜索 `strategy_researcher`（排除 `.git/`），逐项判断是否为本技能目录引用；若是则替换为 `strategy-researcher`

### Phase 2 — Ubuntu 端（OpenClaw 宿主）
- `mv ~/.openclaw/workspace/skills/strategy_researcher ~/.openclaw/workspace/skills/strategy-researcher`
- 若 OpenClaw 有技能注册/缓存文件，检查是否需要刷新

### Phase 3 — 文档与工单回查
- `aos_repo` 全文搜索 `strategy_researcher`，逐项修正
- 已关闭工单（TKT-2026-002/003/004）内文本**不回改**（保留历史原貌），仅在新产出中使用新命名

### Phase 4 — 自检
- 在 Ubuntu 端新目录下执行 `python3 scripts/kb_query.py index`，返回 200 即通过
- 在 Windows 端确认 SKILL.md / TOOLS.md / scripts 齐全

### Phase 5 — Commit & Push
- commit message: `chore(skills): rename strategy_researcher → strategy-researcher for naming consistency`
- worklog 追加到本工单

## 4. 验收标准

1. 全仓（aos_repo + abu_modern）搜索 `strategy_researcher`（下划线）无命中，或命中项已书面说明为何保留
2. Ubuntu 端新目录下 `kb_query.py index` 返回 200
3. commit 仅涉及 rename 与文本修正，不混入其他变更
4. 本工单 status 转 closed

## 5. 显式排除

- 不修改 SKILL.md / Charter 的任何实质内容（只修路径命名）
- 不触碰任何脚本逻辑
- 不动历史工单文本

## 6. 回滚

若 rename 后冒烟失败，`git reset --hard HEAD~1`（aos_repo）+ 反向 mv（两端）即可还原。

## 7. worklog

### 2026-05-07 UTC  openclaw-agent (TKT-2026-004b execution)

**Phase 0 — 同步**
- `git pull --rebase`: SSH key unavailable from this environment; skip. Working directory is clean (`git status --short` returned empty).

**Phase 1 — Windows 端**
- Directory already uses correct name: `openclaw_skills/strategy-researcher/` exists since commit `617a436`. No `git mv` needed.
- Full-text search for `strategy_researcher` (excluding `.git/`) — 5 files hit, all classified:

| File | Category | Disposition |
|------|----------|-------------|
| `aos/runtime/tickets/open/TKT-2026-004b_rename.md` | Rename ticket — describes old→new naming | Retain (meta-reference) |
| `aos/runtime/tickets/open/TKT-2026-004_strategy_researcher_Agent_HTTP_test.md` | Closed ticket (TKT-2026-004); filename contains underscore | Retain per §5 "已关闭工单不回改" |
| `temporary_for_test/BDO组织推进/修正数字员工的实施.md` | Historical discussion transcript | Retain (historical) |
| `temporary_for_test/BDO组织推进/修正数字员工的实施02.md` | Historical discussion transcript | Retain (historical) |
| `temporary_for_test/research_temp/architecture_discussions/Karpathy实验解释.md` | Architecture discussion | Retain (historical) |

- **No active code paths, configuration files, or skill files reference `strategy_researcher`.**

**Phase 2 — Ubuntu 端**
- Not executable from Windows. User must manually: `mv ~/.openclaw/workspace/skills/strategy_researcher ~/.openclaw/workspace/skills/strategy-researcher` (if underscore directory still exists on Ubuntu).

**Phase 3 — 文档与工单回查**
- All `strategy_researcher` hits in `aos/` scope are closed tickets or the rename ticket itself. No corrections needed per §5.

**Phase 4 — 自检**
- Windows: `openclaw_skills/strategy-researcher/` — SKILL.md ✅, TOOLS.md ✅, scripts/ (call_builder.py, call_backtest.py, kb_query.py, smoke_http_clients.sh) ✅.
- Ubuntu: User must run `python3 scripts/kb_query.py index` on Ubuntu host → expect HTTP 200.

**Phase 5 — Commit**
- No files changed on Windows side (directory already `strategy-researcher`). Pending Ubuntu-side rename + kb_query.py index verification by user.
- Acceptance criteria status:
  1. ✅ `strategy_researcher` hits documented with written justification (table above)
  2. ⏳ Pending user verification on Ubuntu (`kb_query.py index` → 200)
  3. ✅ N/A — no commit needed (Windows already correct)
  4. ⏳ Pending Ubuntu verification → then close
### 2026-05-07 14:35 CST  openclaw-agent (修正：路径引用改为下划线)

**修正原因**：工单交付核验发现路径引用应使用下划线 `strategy_researcher`，而非连字符 `strategy-researcher`。

**修改内容 (Ubuntu 端)**：
- `mv ~/.openclaw/workspace/skills/strategy-researcher ~/.openclaw/workspace/skills/strategy_researcher`（目录回滚）
- `aos/org/agents/agent-strategy-researcher.md` — 2 处路径引用修正
- `aos/runtime/research-runs/TKT-2026-004/summary.md` — 描述修正
- `~/.openclaw/workspace/skills/strategy_researcher/SKILL.md` — `runtime_dir` 路径修正

**commit**: `fix(skills): revert directory path references to strategy_researcher (underscore)` → `7d26e21`
**需更正的 commit**：上一次的 `chore(skills): rename strategy_researcher → strategy-researcher` (`2031964`) 方向错误，已通过本 commit 覆盖

**命名规则确认**：
| 场景 | 命名 | 示例 |
|------|------|------|
| 目录路径 | 下划线 | `skills/strategy_researcher/` |
| agent-id | 连字符 | `agent-strategy-researcher` |
| SKILL.md name | 连字符 | `strategy-researcher` |
| Charter 名称 | 连字符 | `agent-strategy-researcher.md` |
| 叙述性引用 | 连字符 | "strategy-researcher 数字员工" |
