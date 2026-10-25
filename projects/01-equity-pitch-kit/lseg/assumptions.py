"""LSEG model inputs. Single source of truth for both the Python engine and the Excel build.

Every input carries a tag:
  S = sourced (company filing / market data, citation in SOURCES)
  A = assumption (analyst judgement)
  D = derived (calculated from sourced figures)
All money in GBP millions unless stated. Per-share in pence.
"""

YEARS_HIST = [2024, 2025]
YEARS_FCST = [2026, 2027, 2028, 2029, 2030]

SOURCES = {
    "FY25": "LSEG 2025 Preliminary Results RNS, 26 Feb 2026",
    "H126": "LSEG H1 2026 Interim Results, 30 Jul 2026",
    "Q326": "LSEG Q3 2026 Trading Update, Oct 2026",
    "OCT": "Reuters via Euronext, 'LSEG to buy Octus in $3.5 billion deal', Oct 2026",
    "PX": "Alpha Vantage quote LSEG.LON, close 23 Oct 2026",
}

# ---------- Historicals (S, FY25 RNS) ----------
HIST = {
    "Data & Analytics":   {2024: 3859, 2025: 3978},
    "FTSE Russell":       {2024: 911,  2025: 954},
    "Risk Intelligence":  {2024: 531,  2025: 579},
    "Markets":            {2024: 3180, 2025: 3467},
    "Other":              {2024: 13,   2025: 8},
    "Recoveries":         {2024: 364,  2025: 360},
    "Adj EBITDA":         {2024: 4148, 2025: 4523},
    "Adj D&A":            {2024: 983,  2025: 1017},
    "Purchased amortisation": {2024: 1499, 2025: 1221},  # non-underlying D&A & impairment
    "Net finance":        {2024: 195,  2025: 179},
    "Capex":              {2024: 957,  2025: 919},
    "Equity FCF":         {2024: 2184, 2025: 2445},
    "Buybacks":           {2024: 1052, 2025: 2152},
    "Adj EPS":            {2024: 363.5, 2025: 420.6},
    "DPS":                {2024: 130.0, 2025: 150.0},
    "WASO":               {2024: 532,  2025: 524},
}

# Opening economic balance sheet, 31 Dec 2025 (S, FY25 RNS).
# Clearing-member assets/liabilities (c.£757bn, equal and offsetting) are excluded.
OPENING_BS = {
    "Cash": 3949,
    "Goodwill & intangibles": 31273,
    "Borrowings incl leases": 11718,
    "Total equity": 22168,
}
OPENING_SHARES = 510.0          # m, excl treasury, 31 Dec 2025 (S)

# ---------- Market data ----------
SHARE_PRICE = 9510.0            # p (S, PX)
GBPUSD = 1.32                   # (S, Q326 guidance FX assumption)

# ---------- Forecast assumptions (A unless noted). Lists align with YEARS_FCST ----------
GROWTH = {   # reported growth incl FX, base case
    "Data & Analytics":  [0.040, 0.050, 0.055, 0.055, 0.055],
    "FTSE Russell":      [0.085, 0.085, 0.080, 0.080, 0.075],
    "Risk Intelligence": [0.090, 0.095, 0.090, 0.085, 0.080],
    "Markets":           [0.110, 0.070, 0.060, 0.060, 0.055],
    "Other":             [0.000, 0.000, 0.000, 0.000, 0.000],
}
RECOVERIES_GROWTH = 0.03
EBITDA_MARGIN = [0.515, 0.522, 0.528, 0.533, 0.537]   # on income excl recoveries, ex-Octus
ADJ_DA_PCT = [0.110, 0.108, 0.106, 0.104, 0.102]
CAPEX_PCT = [0.095, 0.095, 0.093, 0.092, 0.090]      # 2026 c.9.5% guided (S, Q326)
PURCH_AMORT_2026 = 1150.0
PURCH_AMORT_DECLINE = 0.05
TAX_RATE = 0.245                 # guided 24-25% (S, Q326)
NCI_SHARE = 0.129                # (D) 2025: adj PBT x (1-24%) less adj EPS x WASO, / adj net income
NCI_PAYOUT = 0.60
NET_FIN_RATE = 0.0255            # (D) 2025 net finance / avg net debt
OTHER_CASH_PCT = 0.030           # leases, WC, non-underlying cash, % of EBITDA; calibrated to 2026 EqFCF guide >= £2.8bn
DIV_PAYOUT = 0.36                # (D) 2025 DPS / adj EPS = 35.7%
BUYBACKS_FIXED = {2026: 3000.0, 2027: 1650.0}   # 2026: £2.6bn YTD + Q4 tranche; 2027: £0.4bn remaining + £1.25bn mid of £1.0-1.5bn guide
BUYBACK_SHARE_OF_SURPLUS = 0.90  # 2028+: share of post-dividend equity FCF returned
BUYBACK_PRICE_GROWTH = 0.08

# Octus (debt-funded, $3.535bn; S, Q326/OCT). Close timing, margin and amortisation are A.
OCTUS = {
    "price_usd_m": 3535.0,
    "close_year": 2027,
    "rev_2026_usd_m": 310.0,     # (S, OCT) $300-320m expected this year, midpoint
    "growth": 0.12,              # (A) "double-digit revenue growth" (S, LSEG RNS)
    "ebitda_margin": 0.40,       # (A)
    "purch_amort": 110.0,        # (A)
    "debt_rate": 0.050,          # (A) incremental cost of new debt
}

# ---------- Valuation ----------
DCF = {
    "rf": 0.049, "beta": 0.85, "erp": 0.050,
    "kd_pre": 0.050, "debt_weight": 0.15,
    "tv_growth": 0.030,
    "nci_multiple": 25.0,        # P/E applied to Tradeweb minority share of earnings
}

# ---------- Scenarios: 1 = Bear, 2 = Base, 3 = Bull ----------
SCENARIO = 2
SCEN = {
    "growth_adj":  {1: -0.025, 2: 0.0, 3: 0.015},   # added to every division's growth, every year
    "margin_adj":  {1: -0.010, 2: 0.0, 3: 0.006},   # added to EBITDA margin from 2027
    "tv_growth":   {1: 0.025,  2: 0.030, 3: 0.035},
}
SCEN_NAMES = {1: "Bear", 2: "Base", 3: "Bull"}

# ---------- Trading comps (S: stockanalysis.com statistics pages, accessed 25 Oct 2026; prices 20–23 Oct 2026) ----------
# Forward P/E = consensus next-year EPS basis; EV/EBITDA is trailing and on the data provider's own EBITDA
# definition (not always adjusted) -> use forward P/E as the primary metric.
COMPS_DATE = "Prices 20–23 Oct 2026; stockanalysis.com, accessed 25 Oct 2026"
COMPS = [
    # name, ticker, group, ccy, mkt cap (bn, local), EV (bn), fwd P/E, EV/EBITDA TTM, EBITDA margin
    ("S&P Global", "SPGI", "Data & analytics", "USD", 130.54, 142.16, 23.99, 17.46, 0.5051),
    ("Moody's", "MCO", "Data & analytics", "USD", 83.36, 89.36, 26.83, 22.07, 0.4952),
    ("MSCI", "MSCI", "Data & analytics", "USD", 44.02, 50.65, 28.41, 25.09, 0.5881),
    ("FactSet", "FDS", "Data & analytics", "USD", 11.68, 12.96, 16.89, 14.39, 0.3636),
    ("RELX", "REL.L", "Data & analytics", "GBP", 52.87, 61.57, 20.33, 18.26, 0.3387),
    ("Experian", "EXPN.L", "Data & analytics", "GBP", 26.78, 30.79, 20.48, 15.84, 0.3008),
    ("Intercontinental Exchange", "ICE", "Exchanges & infrastructure", "USD", 91.36, 110.82, 19.58, 16.51, 0.6359),
    ("Nasdaq", "NDAQ", "Exchanges & infrastructure", "USD", 57.33, 66.03, 22.45, 18.92, 0.6036),
    ("CME Group", "CME", "Exchanges & infrastructure", "USD", 109.42, 110.95, 23.62, 22.46, 0.7103),
    ("Deutsche Börse", "DB1.DE", "Exchanges & infrastructure", "EUR", 55.60, 60.39, 23.49, 17.50, 0.4319),
    ("Euronext", "ENX.PA", "Exchanges & infrastructure", "EUR", 17.71, 19.55, 18.93, 15.59, 0.5906),
]
LSEG_SAME_SOURCE = {"price": 9490.0, "mkt_cap": 45.57, "ev": 57.25, "fwd_pe": 18.39, "ev_ebitda": 17.40}

# ---------- Company-compiled analyst consensus (S: LSEG IR consensus page, compiled 13 Oct 2026, 12 analysts;
# pre-dates the Octus announcement and the Q3 guidance upgrade) ----------
CONSENSUS = {
    "Data & Analytics": {2026: 4143, 2027: 4394, 2028: 4649},
    "FTSE Russell": {2026: 1035, 2027: 1130, 2028: 1226},
    "Risk Intelligence": {2026: 632, 2027: 701, 2028: 775},
    "Markets": {2026: 3804, 2027: 4091, 2028: 4380},
    "Total income excl. recoveries": {2026: 9622, 2027: 10324, 2028: 11038},
    "Adjusted EBITDA": {2026: 4972, 2027: 5388, 2028: 5821},
    "Adjusted EPS (p)": {2026: 480.6, 2027: 550.9, 2028: 615.5},
    "DPS (p)": {2026: 167.3, 2027: 189.4, 2028: 209.9},
}
