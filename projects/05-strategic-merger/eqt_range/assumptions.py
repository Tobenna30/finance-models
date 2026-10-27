"""USD millions and million shares unless stated. Frozen announcement analysis.

S: sourced; A: analyst assumption; D: calculated in engine/workbook.
Financial cutoff 30 June 2026; announcement 26 October 2026. No Q3 results.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SENS_RATIOS = (.8, .9, .987, 1.05, 1.1)  # A: exchange-ratio range around agreed terms
SENS_SYNERGIES = (0., 162.5, 250., 325., 450., 600.)  # A: USDm stresses, not forecasts
SOURCES = {
    "DEAL": ("EQT, 26 Oct 2026, Transaction Details and Synergy Value", "https://ir.eqt.com/newsroom/news-releases/news-release-details/2026/EQT-Announces-Strategic-Acquisition-of-Range-Resources-Creating-Americas-Undisputed-Natural-Gas-Champion/default.aspx"),
    "E25": ("EQT FY2025 release, adjusted net income reconciliation; annual column, USD000", "https://ir.eqt.com/newsroom/news-releases/news-release-details/2026/EQT-Reports-Fourth-Quarter-and-Full-Year-2025-Results-and-Provides-2026-Guidance/default.aspx"),
    "E26": ("EQT Q2 2026 release, adjusted net income reconciliation; six-month columns and Q2 shares, USD000", "https://ir.eqt.com/investor-relations/news/news-release-details/2026/EQT-Reports-Second-Quarter-2026-Results/default.aspx"),
    "R25": ("Range FY2025 release, pp11-12 net income reconciliation; annual column, USD000", "https://ir.rangeresources.com/node/29286/pdf"),
    "R26": ("Range Q2 2026 release, pp7,9,11-12; six-month net income and stock compensation, Q2 diluted shares, USD000", "https://ir.rangeresources.com/static-files/efd9ff3a-a355-40d0-9193-b491b2e7de52"),
    "PRICE": ("SECONDARY cross-check: Reuters via Investing.com, 26 Oct 2026, USD54.91 offer and 20.6% premium; EQT proxy 54.91 / 0.987, Range proxy 54.91 / 1.206", "https://www.investing.com/news/stock-market-news/eqt-range-resources-tie-up-in-50-billionplus-deal-to-create-us-gas-giant-4972044"),
}
# label, value, tag, units, source locator or assumption rationale
INPUTS = {
    "ratio": ("Exchange ratio", .987, "S", "EQT/RRC", "DEAL: fixed stock exchange, not a cash offer"),
    "synergy": ("Annual base synergy target", 325., "S", "USDm", "DEAL: within two years; >600 long-term pathway excluded"),
    "eqt_shares": ("EQT Q2 diluted weighted shares", 629.049, "S", "m shares", "E26: 629,049 thousand; A: closing share-count proxy"),
    "rrc_shares": ("Range Q2 diluted weighted shares", 236.210, "S", "m shares", "R26 p9: 236,210 thousand; A: shares exchanged proxy, includes dilutive awards"),
    "eqt_price": ("EQT reference price proxy", 55.63, "A", "USD/share", "PRICE: 54.91 / 0.987 rounded; manual proxy, not independently verified exchange close"),
    "rrc_price": ("Range unaffected price proxy", 45.53, "A", "USD/share", "PRICE: 54.91 / 1.206 rounded; manual proxy, value conclusion provisional pending primary prices"),
    "e_adj25": ("EQT adjusted NI FY2025", 1879.156, "S", "USDm", "E25: attributable to EQT; excludes noncontrolling interests"),
    "e_adj126": ("EQT adjusted NI H1 2026", 1708.344, "S", "USDm", "E26: attributable to EQT"),
    "e_adj125": ("EQT adjusted NI H1 2025", 986.283, "S", "USDm", "E26: comparable prior six months"),
    "e_gaap25": ("EQT GAAP NI FY2025", 2039.247, "S", "USDm", "E25: attributable to EQT"),
    "e_gaap126": ("EQT GAAP NI H1 2026", 1698.654, "S", "USDm", "E26: attributable to EQT"),
    "e_gaap125": ("EQT GAAP NI H1 2025", 1026.286, "S", "USDm", "E26: attributable to EQT"),
    "r_adj25": ("Range adjusted NI FY2025", 719.745, "S", "USDm", "R25 p12: excluding certain items"),
    "r_adj126": ("Range adjusted NI H1 2026", 545.732, "S", "USDm", "R26 p12: excluding certain items"),
    "r_adj125": ("Range adjusted NI H1 2025", 389.871, "S", "USDm", "R26 p12: comparable prior six months"),
    "r_gaap25": ("Range GAAP NI FY2025", 658.024, "S", "USDm", "R25 p12: net income as reported"),
    "r_gaap126": ("Range GAAP NI H1 2026", 536.953, "S", "USDm", "R26 p12: net income as reported"),
    "r_gaap125": ("Range GAAP NI H1 2025", 334.630, "S", "USDm", "R26 p12: comparable prior six months"),
    "r_sbc25": ("Range SBC addback FY2025", 45.959, "S", "USDm", "R25 p12: net income reconciliation; not 39.612 from cash-flow table"),
    "r_sbc126": ("Range SBC addback H1 2026", 24.481, "S", "USDm", "R26 p12: stock-based compensation"),
    "r_sbc125": ("Range SBC addback H1 2025", 22.833, "S", "USDm", "R26 p12: stock-based compensation"),
    "tax": ("Tax on incremental earnings / costs", .25, "A", "%", "Blended proxy, also used to retain Range SBC; immediate deductibility assumed except fees"),
    "stepup": ("Illustrative depreciable fair-value step-up", 1500., "A", "USDm", "PPA unavailable; straight-line stress, not a reserve valuation"),
    "life": ("Step-up depreciation life", 15., "A", "years", "Annual incremental DD&A = step-up / life; depletion timing unverified"),
    "integration": ("Total integration cash cost", 300., "A", "USDm", "Analyst reserve; 60% year 1 / 40% year 2, paid and expensed together"),
    "fees": ("Transaction fees at closing", 50., "A", "USDm", "Analyst reserve; expensed in year 1, cash at closing; no tax deduction"),
    "discount": ("Synergy discount rate", .10, "A", "%", "10% nominal, no growth; finite 15-year test beside optimistic perpetuity"),
    "ramp1": ("Year 1 average synergy capture", .50, "A", "%", "Half annual run rate, full year 2; no closing stub"),
    "cost1": ("Year 1 integration cost share", .60, "A", "%", "Remaining 40% in year 2"),
    "case": ("Case selector: 1 Down / 2 Base / 3 Up", 2, "A", "index", "Stress Range relative earnings; EQT held constant, not a calibrated gas-price shock"),
    "r_down": ("Down: Range earnings multiplier", .80, "A", "x", "20% relative earnings haircut"),
    "r_base": ("Base: Range earnings multiplier", 1., "A", "x", "Hold LTM earnings constant; not a 2027 forecast"),
    "r_up": ("Up: Range earnings multiplier", 1.20, "A", "x", "20% relative earnings improvement"),
    "s_down": ("Down: synergy target realised", .50, "A", "%", "Half management base target"),
    "s_base": ("Base: synergy target realised", 1., "A", "%", "Management base target, subject to execution"),
    "s_up": ("Up: synergy target realised", 1., "A", "%", "No speculative long-term synergy uplift"),
}

def values():
    return {key: row[1] for key, row in INPUTS.items()}
