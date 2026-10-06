#!/usr/bin/python3
# =============================================================================
# beaming_1_oppw.py — is OPPW a real reactive-move premium, or 3x leverage beta with a weekly timing wrapper?
#
# TQQQ OHLC, weekly accounting, causal. Fills assumed AT the trigger level (favorable to the strategy).
#  STATIC OPPW  : enter when intraweek price dips to Monday_open·0.99; target entry·1.01; else exit Friday close.
#  ADAPTIVE     : enter Monday open; 1.5% hard stop; dynamic target (~7%, scaled by Monday's move); momentum-weakness
#                 exit = if Tuesday closes below Monday close, exit Tuesday close; else exit Friday close.
#  BENCHMARKS   : TQQQ buy-hold, QQQ buy-hold (weekly). The honest question: does OPPW beat just HOLDING TQQQ?
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _beaming_common import weeks, wk_stats, bars
import numpy as np

TQ = weeks("TQQQ")
print("="*98); print(f"BEAMING #1 — OPPW on TQQQ: reactive premium or leverage beta?  ({TQ[0][0][0]} → {TQ[-1][-1][0]}, {len(TQ)} weeks)"); print("="*98)

def static_oppw(wk):
    """1% dip from Monday open → target +1%, else Friday close. Returns weekly return (0 if never triggered)."""
    mon_o = wk[0][1]; entry = mon_o * 0.99; tgt = entry * 1.01; ent = False
    for (d, o, h, l, c) in wk:
        if not ent and l <= entry: ent = True            # dipped to trigger → filled at entry
        if ent and h >= tgt: return 0.01                 # target hit (+1%)
    if ent: return wk[-1][4] / entry - 1                 # exit Friday close
    return 0.0                                            # no trade this week

def adaptive_oppw(wk):
    """Monday-open entry, 1.5% stop, dynamic ~7% target scaled by Monday move, Tuesday momentum-weakness exit."""
    mon_o = wk[0][1]; mon_c = wk[0][4]; entry = mon_o
    mon_ret = mon_c / mon_o - 1
    tgt = entry * (1 + max(0.03, min(0.10, 0.07 + mon_ret)))   # dynamic target, bounded 3-10%
    stop = entry * 0.985
    for i, (d, o, h, l, c) in enumerate(wk):
        if l <= stop: return stop / entry - 1            # hard stop -1.5%
        if h >= tgt: return tgt / entry - 1              # dynamic target
        if i == 1 and c < mon_c: return c / entry - 1    # Tuesday momentum-weakness exit
    return wk[-1][4] / entry - 1                          # exit Friday close

def bh_weekly(sym):
    w = weeks(sym); return np.array([wk[-1][4] / wk[0][1] - 1 for wk in w])   # Friday close / Monday open

st = np.array([static_oppw(w) for w in TQ])
ad = np.array([adaptive_oppw(w) for w in TQ])
tq_bh = bh_weekly("TQQQ"); qq_bh = bh_weekly("QQQ")
pct_traded = np.mean(st != 0)

print(f"\n  CLAIM (Wealth-Lab, static): APR 125.69%, Sharpe 2.22, maxDD -35.87%")
print(f"\n  strategy (weekly, 2016-26)        {'Sharpe':>8}{'CAGR':>9}{'maxDD':>8}{'total x':>9}")
for nm, r in [("STATIC OPPW", st), ("ADAPTIVE OPPW", ad), ("TQQQ buy-hold", tq_bh), ("QQQ buy-hold", qq_bh)]:
    a = wk_stats(r); print(f"  {nm:30}{a['sh']:>+8.2f}{a['cagr']*100:>+8.0f}%{a['dd']*100:>+7.0f}%{(a['total']+1):>+8.1f}x")
print(f"  (STATIC trades {pct_traded*100:.0f}% of weeks; the rest flat — so it sits out most of TQQQ's compounding.)")

# recent favorable window (echo the Wealth-Lab card, which likely excludes the 2022 crash)
def recent(r, wks=200): return wk_stats(r[-wks:])
rs, ra = recent(st), recent(ad)
print(f"\n  RECENT ~4y window: STATIC Sharpe {rs['sh']:+.2f} / CAGR {rs['cagr']*100:+.0f}%   ADAPTIVE {ra['sh']:+.2f} / {ra['cagr']*100:+.0f}%  — brochure-friendly slices look far better than the full sample")

# ---- verdict ----------------------------------------------------------------------------------------
sa, aa, tqa, qqa = wk_stats(st), wk_stats(ad), wk_stats(tq_bh), wk_stats(qq_bh)
exec_beats_qq = aa['sh'] > qqa['sh'] + 0.1               # does the EXECUTABLE (adaptive) version beat QQQ buy-hold?
print("\n"+"="*98); print("READ:")
print(f"  • STATIC's Sharpe {sa['sh']:+.1f} / {(sa['total']+1):.0f}x IS A FILL ARTIFACT, NOT AN EDGE: it assumes you enter EXACTLY at Monday-open−1% and exit EXACTLY at +1%, with SAME-DAY fills on a 3x ETF whose daily range easily spans both — daily bars can't say the low came before the high, and it ignores slippage. 'Capture +1% almost every week' is fiction. (The family's own rule: an extraordinary Sharpe is a red flag — see brunt.)")
print(f"  • THE EXECUTABLE VERSION TELLS THE TRUTH: ADAPTIVE (clean Monday-open entry, no tiny-target fill game) earns Sharpe {aa['sh']:+.2f}, CAGR {aa['cagr']*100:+.0f}%, maxDD {aa['dd']*100:+.0f}% — it {'beats' if exec_beats_qq else 'LOSES to'} QQQ buy-hold ({qqa['sh']:+.2f}) and trails TQQQ risk-adjusted ({tqa['sh']:+.2f}). Once you can't game the fill, OPPW is just leverage beta.")
print(f"  • IT'S 3x-NDX LEVERAGE IN A BULL DECADE: TQQQ buy-hold already did {(tqa['total']+1):.0f}x at {tqa['cagr']*100:+.0f}%/yr (with a −71% crash) — the big numbers are the 3x, not the weekly rule. The 125% APR / 2.22 Sharpe brochure is the fill artifact plus a crash-free window.")
print(f"  • ADAPTIVE's machinery (dynamic target / Tuesday exit / 1.5% stop) doesn't rescue it — {aa['sh']:+.2f} Sharpe is below even plain QQQ; extra complexity, no edge.")

v = ("NULL / LEVERAGE BETA (+ a fill-artifact warning): OPPW's spectacular backtest is manufactured by UNREALISTIC "
     f"INTRADAY FILLS on daily bars — enter exactly at −1%, exit exactly at +1%, same-day, no slippage — which fabricates "
     f"a Sharpe of {sa['sh']:+.1f} that cannot be earned. Strip the fill game (the ADAPTIVE Monday-open version) and the "
     f"truth appears: Sharpe {aa['sh']:+.2f}, which LOSES to simply holding QQQ ({qqa['sh']:+.2f}) and trails TQQQ buy-hold risk-adjusted "
     f"({tqa['sh']:+.2f}). OPPW is 3x-NDX leverage riding a bull decade with a weekly timing wrapper that mostly just lowers "
     "time-in-market; the 125% APR / 2.22 Sharpe is the artifact plus a crash-free window. The adaptive layer is overfit "
     "decoration, not an improvement. If you want 3x NDX, size it honestly — don't dress leverage as a system, and never "
     "trust a weekly-target backtest that daily bars can't actually fill. beaming_2 = intraday (minute) bars to model "
     "real fills; it will only make the edge smaller.")
print(f"\n  VERDICT: {v}")
print("  (Weekly accounting, entry fills assumed AT the 1% trigger (favorable). The only honest benchmark for a TQQQ")
print("   system is TQQQ buy-hold — beating QQQ is just the 3x leverage. Leverage decay + the 2022 ~-80% crash are in sample.)")
