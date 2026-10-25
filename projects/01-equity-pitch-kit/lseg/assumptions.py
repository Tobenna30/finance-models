"""LSEG model inputs (v2: driver-based). Single source of truth for the Python engine and the Excel build.

Tags: S = sourced (citation in SOURCES), A = assumption, D = derived from sourced figures.
GBP millions unless stated; per-share in pence.
"""

YEARS_HIST = [2023, 2024, 2025]
YEARS_FCST = [2026, 2027, 2028, 2029, 2030]

SOURCES = {
    "FY25": "LSEG 2025 Preliminary Results RNS, 26 Feb 2026",
    "FY24": "LSEG 2024 Preliminary Results, 27 Feb 2025 (2023 comparatives)",
    "H126": "LSEG H1 2026 Interim Report, 30 Jul 2026",
    "Q326": "LSEG Q3 2026 Trading Update, Oct 2026",
    "OCT": "Reuters via Euronext, 'LSEG to buy Octus in $3.5 billion deal', Oct 2026",
    "PX": "Alpha Vantage quote LSEG.LON, close 23 Oct 2026",
    "SA": "stockanalysis.com statistics pages, accessed 25 Oct 2026",
}

# ---------- Revenue lines: (key, label, division) ----------
LINES = [
    ("wf", "Workflows", "D&A"), ("df", "Data & Feeds", "D&A"), ("an", "Analytics", "D&A"),
    ("fs", "FTSE Russell Subscription", "FTSE"), ("fa", "FTSE Russell Asset-based", "FTSE"),
    ("ri", "Risk Intelligence", "RI"),
    ("eq", "Equities", "MKT"), ("fido", "Fixed Income, Derivatives & Other", "MKT"), ("fx", "FX", "MKT"),
    ("otc", "OTC Derivatives", "MKT"), ("sr", "Securities & Reporting", "MKT"),
    ("ncc", "Non-Cash Collateral", "MKT"), ("nti", "Net Treasury Income", "MKT"),
    ("oth", "Other", "OTH"),
]
DIVISIONS = [("D&A", "Data & Analytics"), ("FTSE", "FTSE Russell"), ("RI", "Risk Intelligence"),
             ("MKT", "Markets"), ("OTH", "Other")]

# FY sub-line income (S: FY25 RNS; 2024 restated). 2023 sub-lines not disclosed on the current basis.
HIST_LINES = {
    "wf": {2024: 1899, 2025: 1925}, "df": {2024: 1740, 2025: 1822}, "an": {2024: 220, 2025: 231},
    "fs": {2024: 603, 2025: 630}, "fa": {2024: 308, 2025: 324}, "ri": {2024: 531, 2025: 579},
    "eq": {2024: 392, 2025: 412}, "fido": {2024: 1334, 2025: 1539}, "fx": {2024: 260, 2025: 272},
    "otc": {2024: 582, 2025: 641}, "sr": {2024: 235, 2025: 229}, "ncc": {2024: 111, 2025: 117},
    "nti": {2024: 266, 2025: 257}, "oth": {2024: 13, 2025: 8},
}
# Quarterly sub-line income (S: H1 2026 report, Q3 2026 update, FY25 RNS)
QUARTERS = ["Q1 25", "Q2 25", "Q3 25", "Q4 25", "Q1 26", "Q2 26", "Q3 26"]
Q = {
    "wf":   [491, 477, 471, 481, 491, 489, 479],
    "df":   [454, 453, 453, 466, 475, 486, 483],
    "an":   [59, 57, 58, 58, 59, 61, 61],
    "fs":   [155, 159, 157, 159, 160, 165, 169],
    "fa":   [83, 75, 84, 82, 88, 91, 96],
    "ri":   [143, 144, 144, 148, 153, 157, 160],
    "eq":   [102, 103, 102, 105, 114, 116, 112],
    "fido": [394, 383, 375, 387, 452, 412, 428],
    "fx":   [69, 70, 67, 66, 74, 71, 70],
    "otc":  [161, 153, 160, 167, 183, 172, 186],
    "sr":   [56, 59, 55, 59, 61, 63, 61],
    "ncc":  [27, 30, 30, 30, 29, 30, 27],
    "nti":  [65, 63, 61, 68, 74, 69, 73],
    "oth":  [2, 2, 2, 2, 2, 2, 2],
}
# Q4 2026E reported growth vs Q4 2025 (A; anchored on Q3 2026 reported growth)
Q4_GROWTH = {"wf": 0.015, "df": 0.065, "an": 0.050, "fs": 0.070, "fa": 0.120, "ri": 0.090,
             "eq": 0.080, "fido": 0.100, "fx": 0.040, "otc": 0.120, "sr": 0.060, "ncc": 0.000,
             "nti": 0.100, "oth": 0.000}

HIST = {   # group level (S)
    "Recoveries":     {2023: 370, 2024: 364, 2025: 360},
    "Total income":   {2023: 8009, 2024: 8494, 2025: 8986},
    "Adj EBITDA":     {2023: 3777, 2024: 4148, 2025: 4523},
    "Adj D&A":        {2023: 915, 2024: 983, 2025: 1017},
    "Purchased amortisation": {2024: 1499, 2025: 1221},
    "Net finance":    {2024: 195, 2025: 179},
    "NCI":            {2024: 323, 2025: 334},
    "Capex":          {2024: 957, 2025: 919},
    "Equity FCF":     {2023: 1800, 2024: 2184, 2025: 2445},
    "Buybacks":       {2023: 1200, 2024: 1052, 2025: 2152},
    "Adj EPS":        {2023: 323.9, 2024: 363.5, 2025: 420.6},
    "DPS":            {2023: 115.0, 2024: 130.0, 2025: 150.0},
    "WASO":           {2024: 532, 2025: 524},
}
DIV_EBITDA_HIST = {"D&A": {2024: 1569, 2025: 1617}, "FTSE": {2024: 594, 2025: 635},
                   "RI": {2024: 293, 2025: 333}, "MKT": {2024: 1656, 2025: 1929}, "OTH": {2024: 36, 2025: 9}}

# ---------- KPIs (S) ----------
KPI = {
    "ASV growth":        {2024: 0.063, 2025: 0.059},          # H1 26: 6.1%
    "Retention":         {2025: 0.924},                       # H1 25 92.6%, H1 26 92.8%
    "Gross sales":       {2025: 481},                         # rolling 12m, £m; H1 26 £482m
    "ETF AUM end ($bn)": {2024: 1433, 2025: 1827},            # H1 26 end 2,193; H1 26 avg 1,997
    "SwapClear notional ($trn)": {2025: 1941},                # H1 26 1,165 (+29.4%)
    "Avg cash collateral (EURbn)": {2024: 109.0, 2025: 101.3},# H1 26 110.2
    "Tradeweb ADV ($bn)": {2025: 2625},                       # H1 26 3,180 (+24.8%)
}

OPENING_BS = {"Cash": 3949, "Goodwill & intangibles": 31273, "Borrowings incl leases": 11718, "Total equity": 22168}
OPENING_SHARES = 510.0

SHARE_PRICE = 9510.0
GBPUSD = 1.32
EURGBP = 1.17     # EUR per GBP (S, Q326 guidance FX)

# ---------- Driver assumptions, 2027-2030 (index 0 = 2026 is unused for driver lines; 2026 = 9M actual + Q4E) ----------
# Subscription engine: ASV growth = gross sales % + price/other - (1 - retention)
RETENTION = [None, 0.928, 0.928, 0.928, 0.928]            # A (H1 26 actual 92.8%)
GROSS_SALES_PCT = [None, 0.093, 0.093, 0.092, 0.092]      # D: 2025 gross sales £481m / subscription income £5,187m
PRICE_OTHER = [None, 0.040, 0.040, 0.040, 0.040]          # D: 2025 implied 4.2%
SPREAD = {   # line growth minus ASV growth (A; H1 26 organic: wf -3.3, df +1.4, an -0.1, fs +0.1, ri +3.6)
    "wf": [None, -0.030, -0.030, -0.030, -0.030],
    "df": [None, 0.012, 0.012, 0.012, 0.012],
    "an": [None, 0.000, 0.000, 0.000, 0.000],
    "fs": [None, 0.005, 0.005, 0.005, 0.005],
    "ri": [None, 0.030, 0.025, 0.020, 0.015],
}
# FTSE Russell asset-based: revenue = average ETF AUM x yield
ETF_AUM_AVG_2026 = 2100.0                                   # A ($bn; H1 26 avg 1,997, end-H1 2,193)
ETF_AUM_GROWTH = [None, 0.10, 0.10, 0.09, 0.09]             # A: market return + net flows
ETF_YIELD_CHANGE = [None, -0.02, -0.02, -0.02, -0.02]       # A: fee compression
# Markets drivers
TW_ADV_2026 = 3150.0                                         # A ($bn/day; H1 26 3,180)
TW_ADV_GROWTH = [None, 0.00, 0.05, 0.06, 0.06]              # A: 2026 is a peak year (H1 ADV +24.8%), so flat in 2027
FIDO_CAPTURE_CHANGE = [None, -0.02, -0.02, -0.02, -0.02]    # A
SWAPCLEAR_GROWTH = [None, 0.02, 0.05, 0.06, 0.06]           # A (notional cleared; H1 26 +29.4%, so 2027 normalises)
OTC_CAPTURE_CHANGE = [None, -0.01, -0.01, -0.01, -0.01]     # A
COLLATERAL_2026 = 109.0                                      # A (EURbn avg; H1 26 110.2)
COLLATERAL_GROWTH = [None, 0.03, 0.03, 0.03, 0.03]          # A
NTI_SPREAD_CHANGE = [None, -0.05, 0.0, 0.0, 0.0]            # A: rate cuts compress spread in 2027
OTHER_GROWTH = {"eq": [None, 0.00, 0.04, 0.05, 0.05], "fx": [None, 0.02, 0.04, 0.04, 0.04],
                "sr": [None, 0.04, 0.04, 0.04, 0.04], "ncc": [None, 0.03, 0.03, 0.03, 0.03],
                "oth": [None, 0.0, 0.0, 0.0, 0.0]}
RECOVERIES_GROWTH = 0.03

# Divisional EBITDA margins on income excl. recoveries (2025A: 40.7/66.6/57.5/55.6; H1 26: 42.3/68.1/59.4/58.6)
# 2026 set so group margin lands c.51.6% (guide +100-120bp cc; H2 margin below H1's 52.7%)
DIV_MARGIN = {"D&A": [0.415, 0.420, 0.425, 0.430, 0.435], "FTSE": [0.670, 0.674, 0.678, 0.682, 0.686],
              "RI": [0.580, 0.584, 0.588, 0.592, 0.596], "MKT": [0.570, 0.573, 0.576, 0.579, 0.582]}
DIV_DA_2025 = {"D&A": 574, "FTSE": 89, "RI": 48, "MKT": 306}   # D: 2025 adj EBITDA less adj operating profit (S, FY25)
OTHER_EBITDA = 5.0

ADJ_DA_PCT = [0.110, 0.108, 0.106, 0.104, 0.102]
CAPEX_PCT = [0.095, 0.095, 0.093, 0.092, 0.090]
PURCH_AMORT_2026 = 1150.0
PURCH_AMORT_DECLINE = 0.05
TAX_RATE = 0.245
NCI_SHARE = 0.132       # D: 2025 adjusted NCI £334m / adjusted net income £2,529m (S, FY25)
NCI_PAYOUT = 0.60
NET_FIN_RATE = 0.0255
OTHER_CASH_PCT = 0.0285
DIV_PAYOUT = 0.36
BUYBACKS_FIXED = {2026: 3000.0, 2027: 1650.0}
BUYBACK_SHARE_OF_SURPLUS = 0.90
BUYBACK_PRICE_GROWTH = 0.08

OCTUS = {"price_usd_m": 3535.0, "close_year": 2027, "rev_2026_usd_m": 310.0, "growth": 0.12,
         "ebitda_margin": 0.40, "purch_amort": 110.0, "debt_rate": 0.050}

DCF = {"rf": 0.049, "beta": 0.85, "erp": 0.050, "kd_pre": 0.050, "debt_weight": 0.15}
# Beta: observed 5y beta is 0.41 (S, SA); Blume-adjusted 0.60 (D). I use 0.85 (A) as a conservative choice:
# a low raw beta against a FTSE 100 heavy in energy, miners and banks understates LSEG's exposure to
# global financial-market activity. Sensitivity is shown on the DCF sheet.
BETA_OBSERVED = 0.41
BETA_BLUME = round(0.67 * BETA_OBSERVED + 0.33, 2)

# ---------- Tradeweb (listed subsidiary) ----------
TW_PRICE_USD = 121.89          # S: close 22 Oct 2026 (SA)
TW_SHARES_M = 234.03           # S: Class A+B+C+D shares, Tradeweb 10-Q filed 30 Jul 2026
TW_FWD_PE = 28.06              # S: SA
LSEG_TW_ECON = 0.512           # S: LSEG economic interest in Tradeweb, Tradeweb 10-Q, 30 Jun 2026
LSEG_MKT_SHARES = 480.22       # S: LSEG shares outstanding (SA); model end-2026E 479.6m

# ---------- Valuation history (S: Alpha Vantage monthly closes; LSEG adjusted EPS from annual results) ----------
ADJ_EPS_FY = {2021: 272.4, 2022: 317.8, 2023: 323.9, 2024: 363.5, 2025: 420.6}
H1_EPS = {2025: 208.9, 2026: 244.9}
MONTHLY_CLOSE = {  # month-end close, pence
    "2022-01": 7220, "2022-02": 6574, "2022-03": 7966, "2022-04": 7916, "2022-05": 7402, "2022-06": 7632,
    "2022-07": 7998, "2022-08": 8102, "2022-09": 7628, "2022-10": 7566, "2022-11": 8248, "2022-12": 7136,
    "2023-01": 7406, "2023-02": 7432, "2023-03": 7868, "2023-04": 8346, "2023-05": 8550, "2023-06": 8366,
    "2023-07": 8462, "2023-08": 8178, "2023-09": 8234, "2023-10": 8280, "2023-11": 8906, "2023-12": 9274,
    "2024-01": 8942, "2024-02": 8876, "2024-03": 9490, "2024-04": 8846, "2024-05": 9162, "2024-06": 9400,
    "2024-07": 9470, "2024-08": 10250, "2024-09": 10220, "2024-10": 10515, "2024-11": 11270, "2024-12": 11285,
    "2025-01": 12035, "2025-02": 11845, "2025-03": 11460, "2025-04": 11625, "2025-05": 11275, "2025-06": 10635,
    "2025-07": 9260, "2025-08": 9168, "2025-09": 8516, "2025-10": 9486, "2025-11": 8908, "2025-12": 8952,
    "2026-01": 8122, "2026-02": 8860, "2026-03": 8864, "2026-04": 9550, "2026-05": 9022, "2026-06": 8162,
    "2026-07": 8398, "2026-08": 9000, "2026-09": 8160, "2026-10": 9510,
}
RETENTION_HISTORY = {"H1 2025": 0.926, "FY 2025": 0.924, "H1 2026": 0.928}

# ---------- Scenarios: 1 = Bear, 2 = Base, 3 = Bull. Deltas applied to 2027-2030 ----------
SCENARIO = 2
SCEN = {
    "retention_adj": {1: -0.018, 2: 0.0, 3: 0.007},    # AI churn vs stickier data
    "wf_spread_adj": {1: -0.020, 2: 0.0, 3: 0.010},    # extra Workflows (terminal) pressure
    "mkt_vol_adj":   {1: -0.030, 2: 0.0, 3: 0.020},    # ADV, notional, equities, FX growth
    "aum_adj":       {1: -0.060, 2: 0.0, 3: 0.040},    # ETF AUM growth
    "nti_adj":       {1: -0.200, 2: 0.0, 3: 0.0},      # one-off spread cut in 2027
    "margin_adj":    {1: -0.004, 2: 0.0, 3: 0.002},    # per-year change in divisional margin expansion
    "tv_growth":     {1: 0.025, 2: 0.030, 3: 0.035},
}
SCEN_NAMES = {1: "Bear", 2: "Base", 3: "Bull"}
SCEN_PROBS = {1: 0.25, 2: 0.50, 3: 0.25}

# ---------- SOTP on forward P/E (same basis as comps). Each division's share of shareholder earnings x its peer
# median forward P/E. Group D&A allocated by 2025 divisional D&A; interest pro rata; Tradeweb NCI charged to Markets. ----------
SOTP_PEERS = {"D&A": ["FDS", "SPGI", "REL.L", "EXPN.L"], "FTSE": ["MSCI", "SPGI"],
              "RI": ["EXPN.L", "REL.L", "MCO"], "MKT": ["ICE", "CME", "NDAQ", "DB1.DE", "ENX.PA"]}

# ---------- Pair trade inputs (S, SA) ----------
PAIR = {"lseg_beta": 0.41, "fds_beta": 0.77, "fds_short_interest": 0.0905, "fds_fwd_pe": 16.89, "lseg_fwd_pe": 18.39}

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
