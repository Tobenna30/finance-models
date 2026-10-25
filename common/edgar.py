"""Pull audited fundamentals for US-listed peers from SEC EDGAR (XBRL company facts API).

Run: python -m common.edgar  -> writes data/edgar_us_peers.csv
SEC requires a descriptive User-Agent with contact details. No API key needed.
"""
import csv, json, sys, time, urllib.request
from pathlib import Path

UA = "Tobenna Agubuche agubuchetobe@gmail.com"
PEERS = {  # ticker: CIK
    "SPGI": 64040, "MCO": 1059556, "MSCI": 1408198, "FDS": 1013237,
    "ICE": 1571949, "NDAQ": 1120193, "CME": 1156375, "TW": 1758730,
}
CONCEPTS = {  # first tag found wins
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "operating_income": ["OperatingIncomeLoss"],
    "d_and_a": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet"],
    "net_income": ["NetIncomeLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "debt_long": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "debt_current": ["LongTermDebtCurrent", "DebtCurrent", "ShortTermBorrowings"],
}
OUT = Path(__file__).resolve().parents[1] / "data" / "edgar_us_peers.csv"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def latest_annual(facts, tags, unit="USD", instant=False):
    for tag in tags:
        node = facts.get("us-gaap", {}).get(tag)
        if not node or unit not in node["units"]:
            continue
        rows = [x for x in node["units"][unit] if x.get("form") == "10-K" and x.get("fp") == "FY"]
        if not instant:
            rows = [x for x in rows if "start" in x and 350 <= (_days(x["start"], x["end"])) <= 380]
        if rows:
            best = max(rows, key=lambda x: (x["end"], x.get("filed", "")))
            return best["val"], best["end"], tag
    return None, None, None


def _days(a, b):
    from datetime import date
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def shares_out(facts):
    node = facts.get("dei", {}).get("EntityCommonStockSharesOutstanding")
    if not node: return None, None
    rows = node["units"]["shares"]
    latest_end = max(x["end"] for x in rows)
    return sum(x["val"] for x in rows if x["end"] == latest_end), latest_end   # sums share classes


def main():
    out = []
    for tick, cik in PEERS.items():
        f = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
        row = {"ticker": tick, "cik": cik, "entity": f.get("entityName")}
        for k, tags in CONCEPTS.items():
            unit = "USD/shares" if k == "eps_diluted" else "USD"
            v, end, tag = latest_annual(f["facts"], tags, unit, instant=k in ("cash", "debt_long", "debt_current"))
            row[k], row[k + "_period_end"], row[k + "_tag"] = v, end, tag
        row["shares_out"], row["shares_date"] = shares_out(f["facts"])
        out.append(row); print(tick, row["entity"], row["revenue"], row["operating_income"], file=sys.stderr)
        time.sleep(0.2)   # SEC fair-access: <10 requests/second
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
