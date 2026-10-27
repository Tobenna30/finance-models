"""Vitamin Well / Vital Bidco: public-information underwriting, 27 Oct 2026.

SEK millions. S = source fact or explicitly identified rating-agency forecast;
A = analyst assumption, not a loan term; D = calculation from named inputs.
No borrower audited financial statements or executed loan agreement obtained.
"""

SOURCES = {
    "SP26": ("S&P rating action, 7 Sep 2026, Vital Holdco assigned B+; opening bullets and financial outlook. Agency forecasts, not audited actuals.",
             "https://www.spglobal.com/ratings/en/regulatory/article/-/view/type/HTML/id/3623391"),
    "CIN26": ("Cinven, 2 Jul 2026, Vitamin Well Group to combine with EMPWR. Financial terms undisclosed; subject to approvals.",
              "https://www.cinven.com/news-insights/vitamin-well-group-empwr/"),
    "CIN24": ("Cinven, 6 Aug 2024, agreement to become lead investor; Bridgepoint retains minority; financial terms undisclosed.",
              "https://www.cinven.com/news-insights/cinven-to-become-lead-investor-in-vitamin-well/"),
    "OBDC25": ("Blue Owl 10-Q, 30 Sep 2025, Vital Bidco investment rows: legacy first lien S+450bp, Oct 2031. Lender holding, not total borrower debt.",
               "https://www.sec.gov/Archives/edgar/data/1655888/000165588825000024/obdc-20250930.htm"),
}

AS_OF = "2026-10-27"
YEARS = list(range(2026, 2031))  # A: full-year pro forma horizon, not closing stub
# label, value, tag, unit, source / reasoning; these feed the workbook Inputs sheet.
INPUTS = {
    "tlb_eur": ("New term loan, EURm equivalent", 1900.0, "S", "EURm", "SP26: agency reports issuance; final agreement unverified"),
    "rcf_eur": ("Revolver commitment, EURm equivalent", 200.0, "S", "EURm", "SP26: reported undrawn commitment"),
    "maturity": ("Term loan maturity year", 2033, "S", "year", "SP26; exact date unverified"),
    "fx": ("SEK per EUR, constant translation proxy", 11.0, "A", "SEK/EUR", "Round common currency proxy; not an observed spot or FX hedge"),
    "ebitda_low": ("2026 agency EBITDA forecast low", 4000.0, "S", "SEKm", "SP26: adjusted pro forma forecast"),
    "ebitda_high": ("2026 agency EBITDA forecast high", 4200.0, "S", "SEKm", "SP26: adjusted pro forma forecast"),
    "margin": ("Starting EBITDA margin proxy", .26, "A", "%", "Middle of agency's 25-27% outlook; not reported margin"),
    "cash_haircut": ("Adjusted EBITDA to cash EBITDA haircut", .05, "A", "%", "5% reserve for noncash/addback leakage; requires reconciliation"),
    "opening_cash": ("Opening cash proxy", 500.0, "A", "SEKm", "Unverified opening liquidity; sensitise before any approval"),
    "minimum_cash": ("Minimum operating cash", 300.0, "A", "SEKm", "Analyst buffer, not a covenant"),
    "base_rate": ("Reference rate proxy", .03, "A", "%", "Constant illustrative blended funding rate; not current EURIBOR/SOFR"),
    "spread": ("New term-loan spread proxy", .04, "A", "%", "Illustrative 400bp; not carried from the legacy loan or verified pricing"),
    "rcf_spread": ("Revolver spread proxy", .045, "A", "%", "Illustrative 450bp; not verified pricing"),
    "commit_fee": ("Undrawn revolver fee", .005, "A", "%", "50bp annual assumed commitment fee"),
    "amort": ("Annual term-loan amortisation", .01, "A", "%", "1% of original principal; loan documentation required"),
    "sweep": ("Excess cash sweep", .50, "A", "%", "Repay RCF first; sweep half residual above cash buffer to TLB"),
    "tax": ("Illustrative blended cash tax rate", .22, "A", "%", "Simplified 22% cash tax; not legal tax advice or group effective tax rate"),
    "da": ("D&A as percentage of revenue", .025, "A", "%", "Proxy for acquired manufacturing assets"),
    "capex_low": ("2026 agency capex forecast low", 1200.0, "S", "SEKm", "SP26: capacity expansion forecast"),
    "capex_high": ("2026 agency capex forecast high", 1300.0, "S", "SEKm", "SP26: capacity expansion forecast"),
    "capex_normal": ("Capex after expansion, revenue share", .035, "A", "%", "Normalised maintenance and growth investment"),
    "transaction_cost": ("2026 agency transaction-cost forecast", 824.0, "S", "SEKm", "SP26: one-off costs; deducted once in 2026"),
    "nwc": ("Working capital investment / revenue change", .15, "A", "%", "Inventory/receivable funding; release allowed on falling sales"),
    "max_leverage": ("Underwriting gross leverage ceiling", 5.5, "A", "x", "Credit policy proxy, not a contractual covenant"),
    "min_cover": ("Underwriting cash interest cover floor", 2.0, "A", "x", "Cash EBITDA / interest plus commitment fee"),
    "recovery_haircut": ("Default EBITDA haircut", .35, "A", "%", "35% stress to starting cash EBITDA, independent of sponsor forecasts"),
    "recovery_multiple": ("Default enterprise-value multiple", 6.0, "A", "x", "6x stressed cash EBITDA; no clean trading comp set obtained"),
    "recovery_cost": ("Enforcement costs / stressed EV", .10, "A", "%", "10% cost reserve, not a legal priority opinion"),
    "priority_claims": ("Other priority claims", 100.0, "A", "SEKm", "Illustrative reserve; actual claims unverified"),
    "recovery_rcf_draw": ("Revolver drawn at default", 1.0, "A", "%", "Full draw; assume pari passu with term loan"),
}

def value(key):
    return INPUTS[key][1]

TLB = value("tlb_eur") * value("fx")  # D
RCF = value("rcf_eur") * value("fx")  # D
EBITDA = (value("ebitda_low") + value("ebitda_high")) / 2  # D: midpoint of forecast
REVENUE = EBITDA / value("margin")  # D: inferred, NOT disclosed revenue
CASES = {
    # A: forward scenarios, not company guidance. Base 2027 sales growth follows SP26's forecast;
    # later taper and downside/bull paths are analyst assumptions. First period is a pro forma proxy.
    "Downside": {"growth": [0, -.10, .02, .04, .05], "margin": [.24, .21, .22, .23, .24],
                 "rate_shock": .02, "capex_multiplier": 1.25},
    "Base": {"growth": [0, .15, .12, .10, .08], "margin": [.26, .27, .27, .27, .27],
             "rate_shock": 0.0, "capex_multiplier": 1.0},
    "Bull": {"growth": [0, .20, .15, .12, .10], "margin": [.27, .28, .285, .285, .285],
             "rate_shock": -.005, "capex_multiplier": .90},
}
