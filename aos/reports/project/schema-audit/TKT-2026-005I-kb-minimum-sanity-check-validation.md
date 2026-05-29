# TKT-2026-005I KB Minimum Sanity Check Validation

## 范围

- 工单目标：只验证 `compile-ir -> KB archive` 的最小字段完整性与 `universe` 占位值防护
- 不包含：`strategy_created` 日志、关联策略、market insight、Notes、历史档案批量迁移

## 最小字段清单

- `strategy_id`
- `run_id`
- `strategy_name`
- `strategy_ir`
- `universe`
- `time_range`
- `train_split`
- `metrics`
- `train_metrics`
- `test_metrics`
- `phase_stats`

## 本次实现选择

- 对缺字段档案，采用“**允许落库，但明确写入 `sanity_check_failed`**”策略
- 不再允许把 `compile_ir` 这样的占位字符串写成看似真实的 `universe`
- `compile-ir` 初始建档时通常缺少 `run_id / metrics / phase_stats / time_range`，因此档案会显式标记为：
  - `sanity_check_status = sanity_check_failed`
  - `sanity_check_failed = true`
  - `sanity_missing_fields = [...]`
  - `sanity_failure_reasons = [...]`
- 回测结果通过 `append_backtest_result()` 回填后，若字段齐全，档案会升级为：
  - `sanity_check_status = passed`
  - `sanity_check_failed = false`

## 返回与复查位置

- `kb_query archive <strategy_id>` 最终读取的是 `/api/v1/knowledge/archives/{strategy_id}`
- 当前返回内容中的复查位置：
  - Markdown 顶部 `- **Sanity Check**: ...`
  - `## 档案元数据` 下的 JSON code block
- 人工复查时可在该 JSON block 中确认：
  - `universe` 是否仍为占位值
  - `run_id / time_range / metrics / phase_stats` 是否已经回填
  - `train_split` 是否为 `full` 或具体 split 数值
  - `train_metrics / test_metrics` 是否与 split 语义一致

## 自动化验证

- 已更新测试：
  - [test_knowledge_base.py](file:///d:/智能投顾/量化相关/abu_modern/quant_intelligence/tests/test_knowledge_base.py)
  - [test_strategy_skill_endpoints_e1.py](file:///d:/智能投顾/量化相关/abu_modern/backend/tests/api/endpoints/test_strategy_skill_endpoints_e1.py)
- 覆盖点：
  - `create_strategy_archive()` 在占位 `universe` / 缺关键字段时写入 `sanity_check_failed`
  - `append_backtest_result()` 回填 `run_id`、`time_range`、`metrics`、`phase_stats` 后可生成合格档案
  - `compile-ir` 端点不再把 `compile_ir` 占位字符串传入归档函数

## 测试命令

```powershell
.\.venv\Scripts\python.exe -m pytest quant_intelligence/tests/test_knowledge_base.py backend/tests/api/endpoints/test_strategy_skill_endpoints_e1.py -k "knowledge_base or compile_ir" -q
```

## 测试结果

- `14 passed, 5 deselected, 1 warning`

## 结论

- `compile-ir` 主链路已不再把占位 `universe` 伪装成合格档案字段
- KB 档案现在具备最小字段级的 sanity gate：缺字段时显式失败，字段齐全时显式通过
- `kb_query archive` 读取结果已足以复查本工单要求的最小可信门槛
- 这可以作为恢复研究前的最小可信门槛，但不等于已完成 `关联策略`、`market insight`、`Notes` 等后续 `P1` 工作
