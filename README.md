# Blaque Baux Beaming

**The Fleury OPPW TQQQ strategy — a weekly reactive-move premium, or 3× leverage beta plus a backtest-fill mirage?**

The "One Percent Per Week" (OPPW) strategy on TQQQ (3× NDX): **static** — enter after a 1% dip from Monday's open, target
+1%, exit at week's end (Wealth-Lab card: APR 125.69%, Sharpe 2.22, maxDD −35.87%); **adaptive** (TASC Jun-2026) —
Monday-open entry, a dynamic ~7% target, momentum-weakness exit on Tuesday, 1.5% hard stop. Beaming tests the honest
nulls: is this a real edge, or 3× leverage in a bull decade — and does the adaptive layer beat static or just overfit?

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/beaming_1_oppw.py   # needs Alpaca data keys in the environment
```

## The finding (the magic is a fill artifact; the executable version loses to QQQ)

[`research/beaming_1_oppw.py`](research/beaming_1_oppw.py) — TQQQ OHLC, weekly accounting, causal.

| strategy (2016–26) | Sharpe | CAGR | maxDD | total |
|---|---|---|---|---|
| STATIC OPPW | **+6.2** ⚠️ | +50% | −18% | 76× |
| ADAPTIVE OPPW | +0.51 | +10% | −35% | 2.7× |
| TQQQ buy-hold | +0.86 | +39% | −71% | 32× |
| QQQ buy-hold | +1.02 | +19% | −26% | 6.4× |

- **STATIC's +6.2 Sharpe is a fill artifact, not an edge.** It assumes you enter *exactly* at Monday-open−1% and exit
  *exactly* at +1%, with **same-day fills** on a 3× ETF whose daily range easily spans both — daily bars can't say the low
  preceded the high, and it ignores slippage. "Capture +1% almost every week" is fiction. (Per the family's own rule —
  see `brunt` — an extraordinary Sharpe is a red flag, not a prize.)
- **The executable version tells the truth.** Adaptive (clean Monday-open entry, no tiny-target fill game) earns Sharpe
  +0.51 — it **loses to simply holding QQQ** (+1.02) and trails TQQQ risk-adjusted (+0.86). Once you can't game the fill,
  OPPW is just leverage beta.
- **It's 3× NDX in a bull decade** — TQQQ buy-hold already did 32× at +39%/yr (with a −71% crash). The 125% APR / 2.22
  Sharpe brochure is the fill artifact plus a crash-free window.
- **The adaptive machinery doesn't rescue it** — below even plain QQQ; extra complexity, no edge.

## Verdict

**NULL / leverage beta — with a fill-artifact warning.** OPPW's spectacular backtest is manufactured by unrealistic
intraday fills on daily bars; strip the fill game and it's 3× NDX leverage that *underperforms a plain QQQ hold*
risk-adjusted, wrapped in weekly timing that mostly just lowers time-in-market. The adaptive layer is overfit decoration.
If you want 3× NDX, size it honestly — don't dress leverage as a system, and never trust a weekly-target backtest that
daily bars can't actually fill. A `beaming_2` on minute bars would model real fills — and only shrink the edge further.

## Status

**Research.** Honest null — a viral leverage-ETF "system" whose headline Sharpe is shown to be a backtest-fill artifact,
with the only honest benchmark (holding TQQQ/QQQ) applied. Static-vs-adaptive, weekly accounting, favorable-window check,
Alpaca SIP daily OHLC. No live capital.
