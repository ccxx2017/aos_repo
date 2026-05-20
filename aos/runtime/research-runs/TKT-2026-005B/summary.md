# TKT-2026-005B VCP Breakout Entry — Research Summary

## Status: Round 4 Smoke Completed (Limited Resume)

### Round 1 (original)
- 4-phase VCP IR (watch→pullback→breakout→holding)
- 0 trades — conflicting condition gates prevented any entry
- Conclusion: phase transition logic error (volume>MA20*1.5 AND ATR contraction<0.8 AND drawdown<0.6 mutually exclusive)

### Round 2 (abandoned)
- Builder session corruption; backend hung on 231-symbol backtest

### Round 3 (smoke attempt — old path)
- Builder session corrupted after 5 conversation turns
- No backtest completed

### Round 4 (current — compile-ir + execution-config)
- **Path**: `/api/v1/strategy-builder/compile-ir` + `/api/v1/backtests/execution-config`
- **Hypothesis**: `close > highest(close, 20) AND volume > volume_ma(20)` with 20-day time stop
- **Universe**: 5 stocks (`600519.SH`, `000858.SZ`, `600036.SH`, `601318.SH`, `000333.SZ`)
- **Period**: 2025-01-01 → 2025-12-31
- **Results**:
  - 97 trades, 5/5 symbols traded ✅
  - Win rate: 36.08%
  - Sharpe ratio: 1.1659 (per KB archival data)
  - Cumulative return: -83.84% (KB) / +1.79% (API raw)
  - Max drawdown: 99.86%
- **Key finding**: The simplest VCP breakout baseline (close>20d high + volume>MA20) **triggers frequently** (solved Round 1's 0-trade problem), but **loses money overall** — 64% of trades are losing.
- **Limitation**: This is a limited smoke run, not a full research conclusion.

### Remaining work (for full research resume)
1. Add quality filter: volume threshold > MA20*1.5 (reduce false breakouts)
2. Add volatility-based trailing stop (replace pure time stop)
3. Test sensitivity of "trend" pre-condition (MA slope before breakout)
4. Test wider universe (full intended A-share scope)
5. Train/test split (70/30 time split as per ticket constraint) instead of full window

## Next Steps
Wait for Boss review of Round 4 smoke results. Not authorized for full research resume.
