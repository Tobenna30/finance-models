"""Refinery margin hedge inputs. Single source of truth for the engine, the Excel build and the tests.

Project 14 (derivatives, hedging and commodities), module: hedge structures and FX forwards.
An illustrative South African coastal refinery hedges its 2027 diesel and petrol cracks with zero-cost collars.
It is a teaching case. It does not model or name a real asset.
Tags: S = sourced (key into SOURCES), A = assumption, D = derived from sourced figures.
USD per barrel for cracks, USD millions for totals, rand (ZAR) as labelled. Build date 27 Oct 2026.
"""
import csv
import math
import statistics as st
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
VALUATION_DATE = date(2026, 10, 27)
HEDGE_YEAR = 2027
BBL_PER_GAL = 42

SOURCES = {
    "BRENT": ("EIA Europe Brent spot price FOB, via FRED series DCOILBRENTEU, daily, last obs 20 Oct 2026",
              "https://fred.stlouisfed.org/series/DCOILBRENTEU"),
    "ULSD": ("EIA New York Harbor ultra-low sulfur No. 2 diesel spot, via FRED series DDFUELNYH, $/gal, last obs 20 Oct 2026",
             "https://fred.stlouisfed.org/series/DDFUELNYH"),
    "GASO": ("EIA New York Harbor conventional gasoline regular spot, via FRED series DGASNYH, $/gal, last obs 20 Oct 2026",
             "https://fred.stlouisfed.org/series/DGASNYH"),
    "OVX": ("Cboe Crude Oil ETF Volatility Index, via FRED series OVXCLS, close 26 Oct 2026",
            "https://fred.stlouisfed.org/series/OVXCLS"),
    "DFF": ("Federal Reserve effective federal funds rate, via FRED series DFF, 23 Oct 2026",
            "https://fred.stlouisfed.org/series/DFF"),
    "ZAR": ("Alpha Vantage FX_DAILY USD/ZAR close, 26 Oct 2026",
            "https://www.alphavantage.co/documentation/#fx-daily"),
    "SARB": ("eNCA, 'Reserve Bank hikes interest rates by 25 basis points', 23 Sep 2026 (secondary; confirm against the SARB MPC statement)",
             "https://www.enca.com/business-top-stories/reserve-bank-hikes-interest-rates-25-basis-points"),
    "GS": ("IBTimes citing CNBC, Goldman Sachs expects 2027 diesel and jet cracks above $40/bbl vs about $20 normal, 6 Oct 2026 (secondary)",
           "https://www.ibtimes.com/oil-flows-are-recovering-diesel-likely-continue-being-expensive-while-heres-why-3808277"),
    "CURVE": ("Commodity Board, Brent Dec-26 settled $109.94 on 21 Oct 2026, 2027 strip in the mid to high $80s (secondary, context only)",
              "https://commodity-board.com/crude-oil-futures-ease-from-highs-as-curve-flattens-but-backwardation-persists"),
    "CME": ("CME Group, Understanding Crack Spreads (method reference)",
            "https://www.cmegroup.com/education/whitepapers/understanding-crack-spreads"),
}


def _series(name):
    out = {}
    with open(DATA / f"{name}.csv") as f:
        for d, v in csv.reader(f):
            if d == "observation_date" or v in ("", "."):
                continue
            out[d] = float(v)
    return out


def _cracks():
    """Daily NYH product cracks against Brent, $/bbl (D: ULSD or gasoline $/gal x 42 less Brent)."""
    b, u, g = _series("DCOILBRENTEU"), _series("DDFUELNYH"), _series("DGASNYH")
    days = sorted(set(b) & set(u) & set(g))
    return days, {"diesel": [u[d] * BBL_PER_GAL - b[d] for d in days],
                  "petrol": [g[d] * BBL_PER_GAL - b[d] for d in days]}


def _monthly_normal_vol(days, xs):
    """Annualised normal vol of month-average cracks, $/bbl (D). Collars settle on monthly averages,
    so month-average changes are the right basis. Daily spot changes would overstate it."""
    by_m = {}
    for d, x in zip(days, xs):
        by_m.setdefault(d[:7], []).append(x)
    avg = [st.mean(by_m[k]) for k in sorted(by_m)]
    return st.stdev([b - a for a, b in zip(avg, avg[1:])]) * math.sqrt(12)


CRACK_DAYS, CRACKS = _cracks()
SPOT = {"brent": _series("DCOILBRENTEU")[CRACK_DAYS[-1]],                   # S: BRENT, 20 Oct 2026
        "diesel_crack": CRACKS["diesel"][-1], "petrol_crack": CRACKS["petrol"][-1]}  # D
TRAILING_MEAN = {k: st.mean(v) for k, v in CRACKS.items()}                  # D: Oct 2025 to Oct 2026

PRODUCTS = ["diesel", "petrol"]
PRODUCT_LABEL = {"diesel": "Diesel and jet", "petrol": "Petrol"}

# 2027 forward cracks, $/bbl. No public crack forward curve is available on the build date.
FORWARD = {
    "diesel": 40.0,                       # S: GS, 2027 average forecast above $40 (spot is $106, so the curve is backwardated)
    "petrol": round(TRAILING_MEAN["petrol"], 2),  # D: trailing 12-month NYH gasoline crack. No published 2027 forecast found
}
NORMAL_VOL = {k: round(_monthly_normal_vol(CRACK_DAYS, v), 2) for k, v in CRACKS.items()}  # D, $/bbl a year
OVX = _series("OVXCLS")["2026-10-26"] / 100                                # S: OVX, context for the Black-76 check

# Refinery (all A: illustrative coastal South African refinery)
CAPACITY_BPD = 100_000        # A: crude throughput, barrels a day
AVAILABILITY = 0.88           # A: expected on-stream factor after planned maintenance
YIELD = {"diesel": 0.45, "petrol": 0.35}  # A: product yields. The other 20% (LPG, fuel oil) is taken at zero crack
OPEX_ZAR_PER_BBL = 100.0      # A: cash operating cost, about $6/bbl at the spot rate

# Collar design
PUT_DISTANCE = 0.05           # A: buy a put 5% below the forward crack
COVERS = [0.5, 0.7, 0.8, 0.9]  # A: hedge ratios tested, as a share of budget barrels
OUTAGE_APPETITE = 0.025       # A: risk appetite. Unbacked sold calls in one plausible outage should cost under 2.5% of annual margin
SHOCKS = [-0.30, -0.15, 0.0, 0.15, 0.30]   # A: parallel crack moves for the whole year

# Outage test: six weeks, settled month by month, with a crack spike while the plant is down
OUTAGE_START = date(2027, 7, 1)   # A
OUTAGE_DAYS = 42                  # A: six weeks
OUTAGE_SPIKE = 0.30               # A: cracks often rise when a large refinery trips

# Rates and FX
USD_RATE = _series("DFF")["2026-10-23"] / 100   # S: DFF
ZAR_RATE = 0.0725                                # S: SARB (secondary)
USDZAR_SPOT = 16.6408                            # S: ZAR, close 26 Oct 2026
FX_SHOCKS = [-0.15, 0.0, 0.15]                   # A: USD/ZAR moves (negative = rand strengthens)

# Monte Carlo
MC_DRAWS = 20_000
MC_SEED = 20261027
MC_CORR = 0.6                 # A: diesel and petrol crack correlation. Trailing-year daily data gives a positive link

TAGS = {
    "Forward diesel crack": "S", "Forward petrol crack": "D", "Normal vol diesel": "D", "Normal vol petrol": "D",
    "Capacity": "A", "Availability": "A", "Yields": "A", "Opex": "A", "Put distance": "A", "Covers": "A",
    "Outage appetite": "A", "Outage": "A", "USD rate": "S", "ZAR rate": "S", "USD/ZAR spot": "S", "MC correlation": "A",
}
