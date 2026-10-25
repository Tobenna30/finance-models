"""Turns the weekly data pulls (repo /data) into LSEG tracking series: hiring mix, Tradeweb stake share, pair performance."""
import csv
from collections import Counter, defaultdict
from pathlib import Path
from . import assumptions as A

DATA = Path(__file__).resolve().parents[3] / "data"


def _rows(name):
    p = DATA / name
    return list(csv.DictReader(p.open())) if p.exists() else []


def hiring():
    """Latest snapshot by company and category (re-classified with the current rules) plus history totals."""
    import sys; sys.path.insert(0, str(DATA.parent))
    from common.jobs import classify, CATEGORIES
    cats = [c for c, _ in CATEGORIES] + ["Other"]
    snap = defaultdict(Counter); date = None
    for r in _rows("jobs_latest.csv"):
        snap[r["company"]][classify(r["title"])] += 1; date = r["date"]
    hist = [(r["date"], r["company"], int(r["total"])) for r in _rows("jobs_history.csv") if r["total"]]
    return dict(date=date, cats=cats, snap={k: dict(v) for k, v in snap.items()}, history=hist)


def _lseg_shares(d: str) -> float:
    """LSEG shares in issue (m), interpolated between disclosed points (S: FY24/FY25 WASO, YE25, Oct 2026)."""
    pts = [("2024-01-01", 535.0), ("2024-12-31", 531.0), ("2025-12-31", 510.0), ("2026-10-23", A.LSEG_MKT_SHARES)]
    from datetime import date as D
    t = D.fromisoformat(d)
    if t <= D.fromisoformat(pts[0][0]): return pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        da, db = D.fromisoformat(a), D.fromisoformat(b)
        if da <= t <= db: return va + (vb - va) * (t - da).days / (db - da).days
    return pts[-1][1]


def weekly():
    """Weekly series from 2024: Tradeweb stake as % of LSEG market cap; LSEG vs FactSet relative price in GBP (rebased)."""
    from datetime import date as D
    px = defaultdict(dict); wk_date = {}
    for r in _rows("prices_weekly.csv"):
        iso = D.fromisoformat(r["date"]).isocalendar()[:2]              # align markets by ISO week
        px[r["symbol"]][iso] = float(r["close"])
        if r["symbol"] == "LSEG": wk_date[iso] = r["date"]
    weeks = sorted(set(px["LSEG"]) & set(px["TW"]) & set(px["FDS"]) & set(px["GBPUSD"]))
    out = []
    base = None
    for wk in weeks:
        d = wk_date[wk]
        px_ = {k: px[k][wk] for k in ("LSEG", "TW", "FDS", "GBPUSD")}
        fx = px_["GBPUSD"]
        lseg_mcap = px_["LSEG"] / 100 * _lseg_shares(d)                  # £m
        stake = px_["TW"] * A.TW_SHARES_M * A.LSEG_TW_ECON / fx           # £m (share count held at latest 10-Q)
        rel = px_["LSEG"] / 100 / (px_["FDS"] / fx)                     # LSEG £ per FactSet £
        if d >= "2024-01-01":
            base = base or rel
            out.append(dict(date=d, lseg=px_["LSEG"], tw=px_["TW"], fds=px_["FDS"], gbpusd=fx,
                            stake_pct=stake / lseg_mcap, rel=rel / base * 100))
    return out
