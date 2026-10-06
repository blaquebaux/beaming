#!/usr/bin/python3
# =============================================================================
# _beaming_common.py — shared helpers for Blaque Baux BEAMING (Fleury OPPW TQQQ: static vs adaptive).
# Alpaca SIP daily OHLC bars (adjustment=all → total return); env keys. Read-only.
#
# The "One Percent Per Week" (OPPW) strategy on TQQQ (3x NDX): STATIC — enter after a 1% dip from Monday's open,
# target +1%, exit at week's end; its Wealth-Lab card shows APR 125.69% / Sharpe 2.22 / maxDD -35.87%. ADAPTIVE
# (TASC Jun-2026) — Monday-open entry, a dynamic ~7% target, momentum-weakness exit on Tuesday, 1.5% hard stop.
# BEAMING tests the honest nulls: (1) is OPPW a real reactive-move premium, or just 3x LEVERAGE BETA in a bull
# decade with a weekly timing wrapper (so the only honest benchmark is TQQQ — and QQQ — BUY-AND-HOLD)? and (2) does
# the adaptive layer actually beat the static one, or is the extra machinery overfit? The Wealth-Lab headline is
# almost certainly a favorable window; the full 2016-26 sample includes TQQQ's ~-80% 2022 crash, which any honest
# test must carry. Weekly-return accounting (one trade per week), entry fills assumed AT the trigger level (favorable).
# =============================================================================
import os, json, urllib.request, math, datetime
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    """{date: (open, high, low, close)} daily, total-return adjusted."""
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: (b["o"], b["h"], b["l"], b["c"]) for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def weeks(sym):
    """Group a symbol's OHLC into ISO weeks. Returns list of weeks, each a list of (date, o,h,l,c) in order."""
    b = bars(sym); dates = sorted(b)
    wk = {}
    for d in dates:
        y, w, _ = datetime.date.fromisoformat(d).isocalendar()
        wk.setdefault((y, w), []).append((d,) + b[d])
    return [wk[k] for k in sorted(wk)]

def wk_stats(r, ppy=52):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 10 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    yrs = len(r) / ppy
    return dict(sh=r.mean()/r.std()*math.sqrt(ppy), cagr=cum[-1]**(1/yrs) - 1,
                dd=float((cum/np.maximum.accumulate(cum)-1).min()), vol=r.std()*math.sqrt(ppy),
                total=cum[-1]-1)
