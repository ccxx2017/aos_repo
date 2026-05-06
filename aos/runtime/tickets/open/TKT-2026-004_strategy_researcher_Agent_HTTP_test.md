# TKT-2026-004 · strategy-researcher HTTP 适配脚本验证

| 字段 | 值 |
|---|---|
| intent_type | infrastructure |
| assigned_to | agent-strategy-researcher |
| priority | normal |
| tags | skill-bootstrap, http-client |

## 前置假设

由 Boss 在 Windows 侧手动完成，智能体**不需要**重建：

1. 技能目录位置：`/home/ccxx/.openclaw/workspace/skills/strategy-researcher/`
2. 该目录下应已存在以下 4 个文件（由 Windows 侧 `abu_modern/openclaw_skills/strategy-researcher/scripts/` 拷贝而来）：
   - `scripts/call_builder.py`
   - `scripts/call_backtest.py`
   - `scripts/kb_query.py`
   - `scripts/smoke_http_clients.sh`
3. 后端 `http://192.168.1.136:8000` 可达。

## 任务（按序执行，任一步失败则停止并写 worklog）

### Step 1 · Phase 0 同步
```

cd /home/ccxx/aos_repo && git pull --rebase

````
失败或出现 `CONFLICT` → worklog 标记 `git_sync_failed`，exit 1。

### Step 2 · 校验技能目录
确认上述 4 个文件存在且 `call_*.py` / `kb_query.py` 首行为 `#!/usr/bin/env python3`。
```
ls -l /home/ccxx/.openclaw/workspace/skills/strategy-researcher/scripts/
chmod +x /home/ccxx/.openclaw/workspace/skills/strategy-researcher/scripts/*.sh
````

任一文件缺失 → worklog 标记 `skill_files_missing`，列出缺失列表，终止。

### Step 3 · `--help` 自检

对 3 个 Python 脚本各跑一次 `python3 <path> --help`，每个都应 rc=0。
失败 → worklog 标记 `help_check_failed`，记录 stderr，终止。

### Step 4 · 连通性冒烟

```
cd /home/ccxx/.openclaw/workspace/skills/strategy-researcher
QUANT_BACKEND_URL=http://192.168.1.136:8000 bash scripts/smoke_http_clients.sh
```

记录完整 stdout/stderr。

### Step 5 · 网络错误分支验证

确认当后端**不可达**时 `kb_query.py` 退出码为 1（可重试语义），用一个明显不可达的端口验证：

```
python3 scripts/kb_query.py --base-url http://192.168.1.136:1 --timeout 3 index ; echo "rc=$?"
```

期望 `rc=1`。

### Step 6 · 写 run 记录

在 aos_repo 内创建：

```
/home/ccxx/aos_repo/aos/runtime/research-runs/TKT-2026-004/
  ├── run.log         # 全部命令的 stdout/stderr
  └── summary.md      # 见下方模板
```

`summary.md` 模板：

```
# TKT-2026-004 验证摘要
- skill_files_present: [true/false, 缺失列表]
- help_check: [pass/fail, 细节]
- smoke_test: [pass/fail, 细节]
- network_error_exit_code: [0/1/2, 实际值]
- backend_reachable: [true/false]
- 结论: [ready_for_TKT-2026-005 / blocked, 原因]
```

### Step 7 · 追加 worklog

打开工单文件：

```
/home/ccxx/aos_repo/aos/runtime/tickets/open/TKT-2026-004strategy_researcher_Agent_HTTP_适配脚本.md
```

在文件末尾 `## Worklog` 段 append（不得改其它段）：

```
### <UTC 时间戳>  agent-strategy-researcher
- phase0_git_sync: ok
- skill_files_present: ok
- help_check: ok
- smoke_test: ok (或 failed: <原因>)
- network_error_exit_code: 1 (ok)
- summary: aos/runtime/research-runs/TKT-2026-004/summary.md
- 结论: ready_for_TKT-2026-005
```

### Step 8 · 推送

```
cd /home/ccxx/aos_repo
git add aos/runtime/research-runs/TKT-2026-004/ aos/runtime/tickets/open/TKT-2026-004*.md
git commit -m "research(skill): TKT-2026-004 http adapter smoke pass"
git push origin $(git branch --show-current)
```

push 失败 → 30s 后重试一次，仍失败则 worklog 加 `git_push_failed` 但不 exit 非零。

## 边界

* 本工单**不调用** builder / backtest（会真花后端资源），**只打 KB 只读端点**。
* 本工单**不修改** `/home/ccxx/.openclaw/workspace/skills/strategy-researcher/` 下的任何文件——TOOLS.md 由 Boss 在 Windows 侧手动同步。
* 本工单**不走** SKILL.md §"主流程（research_loop.py）"——那是 investigation 类工单的流程，本工单是 infrastructure 类。

## Worklog

<!-- agent append below -->
