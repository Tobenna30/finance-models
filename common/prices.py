"""Weekly closing prices for the LSEG pair/stub tracker. Tries Stooq first, then Yahoo's public chart endpoint.

Run: python -m common.prices  -> writes data/prices_weekly.csv (date, symbol, close)
"""
import csv, io, json, sys, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
UA = "Mozilla/5.0 (research project; contact agubuchetobe@gmail.com)"
SYMBOLS = {"LSEG": ("lseg.uk", "LSEG.L"), "TW": ("tw.us", "TW"), "FDS": ("fds.us", "FDS"), "GBPUSD": ("gbpusd", "GBPUSD=X")}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def stooq(sym):
    txt = get(f"https://stooq.com/q/d/l/?s={sym}&i=w")
    rows = list(csv.DictReader(io.StringIO(txt)))
    if not rows or "Close" not in rows[0]: raise ValueError(txt[:80])
    return [(r["Date"], float(r["Close"])) for r in rows if r["Close"] not in ("", "N/D")]


def yahoo(sym):
    from datetime import datetime, timezone
    j = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5y&interval=1wk"))
    res = j["chart"]["result"][0]
    ts, cl = res["timestamp"], res["indicators"]["quote"][0]["close"]
    return [(datetime.fromtimestamp(t, timezone.utc).date().isoformat(), c) for t, c in zip(ts, cl) if c is not None]


def main():
    DATA.mkdir(exist_ok=True)
    out = []
    for name, (sq, yh) in SYMBOLS.items():
        for src, fn, s in (("stooq", stooq, sq), ("yahoo", yahoo, yh)):
            try:
                rows = fn(s); out += [(d, name, c, src) for d, c in rows]; print(name, src, len(rows), file=sys.stderr); break
            except Exception as e:
                print(name, src, "failed:", e, file=sys.stderr)
    with (DATA / "prices_weekly.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["date", "symbol", "close", "source"]); w.writerows(out)


if __name__ == "__main__":
    main()
