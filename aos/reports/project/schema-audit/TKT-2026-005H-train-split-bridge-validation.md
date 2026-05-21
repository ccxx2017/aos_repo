# TKT-2026-005H Train Split Bridge Validation

## 范围

- 工单目标：仅验证 `POST /api/v1/backtests/execution-config` 已打通 `train_split` 主链路
- 不包含：`strategy_created` 日志、`Universe` 字段完整性、`Notes`、关联策略候选、market insight 候选

## 请求示例

```json
{
  "execution_config": {
    "strategy_ir": {
      "strategy_id": "m3_test",
      "version": "2.0",
      "intent": "trend_following",
      "initial_phase": "watch",
      "phases": []
    },
    "universe": {
      "type": "explicit",
      "symbols": ["000001.SZ"]
    },
    "backtest_params": {
      "start_date": "2023-01-01",
      "end_date": "2023-06-30",
      "initial_capital": 1000000,
      "benchmark_symbol": "000300.SH",
      "data_source": "local"
    }
  },
  "train_split": 0.7
}
```

## 返回字段位置

- 接口响应路径：
  - `data.metrics`
  - `data.train_metrics`
  - `data.test_metrics`
  - `data.phase_stats`
  - `data.train_split`
- `call_backtest.py` 成功输出路径：
  - 顶层镜像字段：`train_metrics` / `test_metrics`
  - 原始后端响应：`raw.data.train_metrics` / `raw.data.test_metrics`

## 保存后的 JSON 路径

- `strategy_researcher` 研究回合原样保存 `backtest_response`
- 在 `round_<N>.json` 中可通过以下路径读取：
  - `backtest_response.train_metrics`
  - `backtest_response.test_metrics`
  - `backtest_response.raw.data.train_metrics`
  - `backtest_response.raw.data.test_metrics`

## 自动化验证

- 已更新测试：[test_backtests_refactored.py](file:///d:/智能投顾/量化相关/abu_modern/backend/tests/api/endpoints/test_backtests_refactored.py)
- 覆盖点：
  - `execution-config` 默认兼容路径仍返回 `metrics`
  - `execution-config + train_split` 会调用底层 `run_backtest(..., train_split=...)`
  - 响应中真实返回 `train_metrics` / `test_metrics`

## 结论

- `strategy_researcher` 现已可在正式主链路中显式传入 `train_split`
- 后端已能返回样本内外结果，`call_backtest.py` 也会原样保留 split 回测结果
- 这已能支撑研究流程和报告模板执行样本内外比较，并据此识别潜在过拟合
