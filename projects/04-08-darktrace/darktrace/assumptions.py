"""Darktrace / Thoma Bravo inputs. Single source of truth for the engine, the Excel build and the tests.

Projects 04 (sell-side fairness view) and 08 (LBO) share this file.
Tags: S = sourced (key into SOURCES), A = assumption, D = derived from sourced figures.
USD millions unless stated. Per-share figures in USD or pence as labelled. Darktrace year end is 30 June.
"""

SOURCES = {
    "R27": ("Rule 2.7 announcement, Recommended Cash Acquisition of Darktrace plc, 26 Apr 2024",
            "https://ir.darktrace.com/regulatory-news/2024/4/26/1813465"),
    "SCH": ("Publication of Scheme Document, 23 May 2024",
            "https://ir.darktrace.com/regulatory-news/2024/5/23/1823676"),
    "VOTE": ("Results of Court Meeting and General Meeting, 18 Jun 2024",
             "https://www.investegate.co.uk/announcement/rns/darktrace--dark/result-of-meeting/8266218"),
    "REG": ("Regulatory approval and timetable update, 16 Sep 2024",
            "https://www.lse.co.uk/rns/DARK/regulatory-approval-timetable-update-r7souzslq618lx3.html"),
    "EFF": ("Scheme Effective, 1 Oct 2024",
            "https://ir.darktrace.com/regulatory-news/2024/10/1/1870431"),
    "FY23": ("Darktrace FY 2023 final results, 6 Sep 2023",
             "https://ir.darktrace.com/regulatory-news/2023/9/6/1713518"),
    "H124": ("Darktrace half-year results to 31 Dec 2023, 7 Mar 2024",
             "https://ir.darktrace.com/regulatory-news/2024/3/7/1796862"),
    "Q424": ("Darktrace Q4 FY 2024 trading update, 18 Jul 2024",
             "https://ir.darktrace.com/regulatory-news/2024/7/18/1843731"),
    "BBG1": ("Bloomberg Law, Thoma Bravo lines up $2 billion financing for Darktrace buyout, 26 Apr 2024",
             "https://news.bloomberglaw.com/private-equity/thoma-bravo-lines-up-2-billion-financing-for-darktrace-buyout"),
    "BBG2": ("Bloomberg Law, Banks kick off $2.1 billion loan package for Darktrace LBO, 13 Jun 2024",
             "https://news.bloomberglaw.com/private-equity/banks-kick-off-2-1-billion-loan-package-for-darktrace-buyout"),
    "PB": ("PitchBook LCD, Darktrace wraps loan package backing Thoma Bravo's buyout, 2024",
           "https://pitchbook.com/news/articles/darktrace-wraps-loan-package-backing-thoma-bravos-buyout"),
    "UST": ("US 10-year Treasury yield, monthly average, via Alpha Vantage TREASURY_YIELD (Federal Reserve H.15)",
            "https://www.federalreserve.gov/releases/h15/"),
    "PX": ("Weekly closing prices, week ending 19 Apr 2024, via Alpha Vantage TIME_SERIES_WEEKLY",
           "https://www.alphavantage.co/documentation/"),
    "UKTAX": ("UK corporation tax main rate 25% from 1 Apr 2023; corporate interest restriction 30% of tax-EBITDA",
              "https://www.gov.uk/government/publications/corporate-interest-restriction-guidance"),
    "CRWD": ("CrowdStrike Q4 FY2024 results (8-K), 5 Mar 2024",
             "https://www.sec.gov/Archives/edgar/data/1535527/000153552724000004/crwd-20240305xex991.htm"),
    "PANW": ("Palo Alto Networks Q2 FY2024 results (8-K), 20 Feb 2024",
             "https://www.sec.gov/Archives/edgar/data/1327567/000132756724000003/ex991q224earningsrelease.htm"),
    "PANW23": ("Palo Alto Networks Q4 FY2023 results (8-K), Aug 2023",
               "https://www.sec.gov/Archives/edgar/data/1327567/000132756723000020/ex991q423earningsrelease.htm"),
    "FTNT": ("Fortinet Q4 2023 results (8-K), 6 Feb 2024",
             "https://www.sec.gov/Archives/edgar/data/1262039/000126203924000006/ftntq4-2023ex991.htm"),
    "ZS": ("Zscaler Q2 FY2024 results (8-K), 29 Feb 2024",
           "https://www.sec.gov/Archives/edgar/data/1713683/000171368324000036/zs-01312024_991.htm"),
    "ZS23": ("Zscaler Q4 FY2023 results, Sep 2023", "https://ir.zscaler.com/node/12446"),
    "S": ("SentinelOne Q4 FY2024 results (8-K), 13 Mar 2024",
          "https://www.sec.gov/Archives/edgar/data/1583708/000158370824000003/sentineloneq424exhibit991.htm"),
    "RPD": ("Rapid7 Q4 2023 results (8-K), 7 Feb 2024",
            "https://www.sec.gov/Archives/edgar/data/1560327/000156032724000008/rapid720238-kex991.htm"),
    "TENB": ("Tenable Q4 2023 results (8-K), 7 Feb 2024",
             "https://www.sec.gov/Archives/edgar/data/1660280/000166028024000007/q42023financialresults-ear.htm"),
    "SOPH": ("Thoma Bravo, Recommended cash offer for Sophos Group plc, 14 Oct 2019",
             "https://www.thomabravo.com/press-releases/thoma-bravo-announces-a-recommended-cash-offer-for-sophos-group-plc"),
    "PFPT": ("Help Net Security, Thoma Bravo to acquire Proofpoint, 27 Apr 2021",
             "https://www.helpnetsecurity.com/2021/04/27/proofpoint-thoma-bravo/"),
    "PFPT20": ("Proofpoint Q4 and FY2020 results, Feb 2021",
               "https://www.stocktitan.net/news/PFPT/proofpoint-announces-fourth-quarter-and-full-year-2020-financial-ctrg7ip5ik4h.html"),
    "MIME": ("Mimecast / Permira transaction press release (8-K), 7 Dec 2021",
             "https://www.sec.gov/Archives/edgar/data/1644675/000119312521349648/d262865dex991.htm"),
    "MIME21": ("Mimecast Q4 and FY2021 results, May 2021",
               "https://www.stocktitan.net/news/MIME/mimecast-announces-fourth-quarter-and-full-year-2021-financial-h24ibjmuzp7j.html"),
    "SAIL": ("SailPoint / Thoma Bravo press release (8-K), 11 Apr 2022",
             "https://www.sec.gov/Archives/edgar/data/1627857/000119312522100936/d248941dex991.htm"),
    "SAIL21": ("SailPoint Q4 and FY2021 results, 28 Feb 2022",
               "https://www.businesswire.com/news/home/20220228005991/en/SailPoint-Announces-Fourth-Quarter-and-Full-Year-2021-Financial-Results"),
    "ICON": ("ICON Corporate Finance, Cybersecurity sector update, Oct 2022 (SailPoint deal EV)",
             "https://www.iconcorpfin.com/wp-content/uploads/2025/06/ICON_Cybersecurity_Sector-Update_October-2022.pdf"),
    "PING": ("Ping Identity / Thoma Bravo press release, 3 Aug 2022",
             "https://press.pingidentity.com/2022-08-03-Ping-Identity-to-be-Acquired-by-Thoma-Bravo-for-2-8-Billion"),
    "PING21": ("Ping Identity Q4 and FY2021 results (8-K), 24 Feb 2022",
               "https://www.sec.gov/Archives/edgar/data/1679826/000155837022001937/ping-20220224xex99d1.htm"),
    "FORG": ("ForgeRock / Thoma Bravo press release (8-K), 11 Oct 2022",
             "https://www.sec.gov/Archives/edgar/data/1543916/000119312522260580/d399542dex991.htm"),
    "FORG21": ("ForgeRock Q4 and FY2021 results, 1 Mar 2022",
               "https://stocktitan.net/news/FORG/forge-rock-announces-strong-fourth-quarter-and-full-year-2021-6x6745nqyk22.html"),
    "KNBE": ("KnowBe4 / Vista press release (8-K), 11 Oct 2022",
             "https://www.sec.gov/Archives/edgar/data/1664998/000119312522261033/d409662dex991.htm"),
    "KNBE21": ("KnowBe4 Q4 and FY2021 results, Feb 2022",
               "https://www.stocktitan.net/news/KNBE/know-be4-announces-fourth-quarter-and-fiscal-year-2021-financial-k4oklarrxaz2.html"),
}

# =====================================================================================
# 1. Deal facts (all S unless tagged otherwise)
# =====================================================================================
DEAL = {
    "acquirer": "Luke Bidco Limited (funds managed or advised by Thoma Bravo, L.P.)",
    "announce_date": "26 Apr 2024",
    "scheme_doc_date": "23 May 2024",
    "meeting_date": "18 Jun 2024",
    "regulatory_cleared": "16 Sep 2024",
    "sanction_date": "24 Sep 2024",
    "effective_date": "1 Oct 2024",
    "long_stop": "27 Jan 2025",
    "offer_usd": 7.75,            # S R27: cash per share
    "offer_p": 620.0,             # S R27: GBP equivalent at the announcement exchange rate
    "equity_value": 5315.0,       # S R27: fully diluted, $m (c.GBP 4,254m)
    "enterprise_value": 4992.0,   # S R27: $m (c.GBP 3,995m)
    "ltm_revenue": 616.0,         # S R27: 12 months to 31 Dec 2023
    "ltm_ebitda": 146.0,          # S R27: Adjusted EBITDA, 12 months to 31 Dec 2023
    "ev_rev_stated": 8.1,         # S R27
    "ev_ebitda_stated": 34.2,     # S R27
    "arr_dec23": 702.1,           # S H124: constant currency ARR 31 Dec 2023
    "rpo_dec23": 1253.7,          # S H124
    "undisturbed_p": 517.0,       # S R27: closing price 25 Apr 2024
    "vwap3m_p": 429.9,            # S R27: 3-month VWAP to 25 Apr 2024
    "high12m_p": 518.6,           # S R27: 12-month high close
    "placing_p": 425.0,           # S R27: 21 Mar 2024 secondary placing
    "ipo_p": 250.0,               # S R27: IPO 30 Apr 2021
    "prem_close": 0.200, "prem_vwap3m": 0.443, "prem_high": 0.196, "prem_placing": 0.460,   # S R27
    "shares_issued": 703.68,      # S R27: m, excluding 3.32m treasury
    "irrevocables_pct": 0.1471,   # S SCH: 103.0m shares at 22 May 2024; binding even if a higher offer is made (R27)
    "court_for_pct": 0.9955,      # S VOTE: % of Scheme Shares voted
    "court_turnout_pct": 0.6529,  # S VOTE: Scheme Shares voted as % of issued share capital
    "interim_1l": 1685.0, "interim_2l": 460.0,   # S R27 / BBG1: interim facilities at announcement
    "rule3_advisers": "Jefferies and Qatalyst Partners", "bidco_adviser": "Goldman Sachs International",
}
FX = DEAL["offer_usd"] / (DEAL["offer_p"] / 100)              # D: implied USD per GBP = 1.25
FD_SHARES = DEAL["equity_value"] / DEAL["offer_usd"]           # D: fully diluted shares, m (685.8)
NET_CASH = DEAL["equity_value"] - DEAL["enterprise_value"]     # D: 323 = cash 383.2 less leases 60.2 at 31 Dec 2023

# =====================================================================================
# 2. Darktrace history (FY to 30 June)
# =====================================================================================
HIST = {   # S unless noted
    "Revenue":   {2022: 415.5, 2023: 545.4, 2024: 689.5},   # FY22 D (FY23 less +129.9 growth); FY24 "at least" (Q424, unaudited)
    "ARR (cc)":  {2023: 637.3, 2024: 782.2},
    "Net ARR added": {2023: 143.6, 2024: 144.9},
    "Customers": {2023: 8799, 2024: 9735},
    "Gross churn": {2023: 0.068, 2024: 0.063},
    "Net ARR retention": {2023: 1.047, 2024: 1.066},
    "Gross margin": {2023: 0.898},
}
H1 = {"rev_h1fy24": 330.3, "rev_h1fy23": 259.3, "ebitda_h1fy24": 84.5, "ebitda_h1fy23": 45.2,
      "sbp_h1fy24": 22.7, "capex_h1fy24": 8.0, "da_h1fy24": 43.5, "adj_ebit_h1fy24": 71.0,
      "cash_dec23": 383.2, "leases_dec23": 60.2, "ocf_h1fy24": 65.6, "buyback_h1fy24": 44.4}   # S H124
FY23_EBITDA_NEWDEF = DEAL["ltm_ebitda"] - H1["ebitda_h1fy24"] + H1["ebitda_h1fy23"]          # D: 106.7
GUIDE_FY24 = {"rev_growth": (0.235, 0.250), "ebitda_margin_min": 0.21, "fcf_conv_fy24": (0.50, 0.60),
              "fcf_conv_after": (0.80, 1.20), "adj_ebit_steady_state": "mid-20%s"}             # S H124 / FY23
FY24_EBITDA_MARGIN = 0.230   # A: above the "at least 21%" guide; H1 was 25.6%, H2 carries commission timing
CAPEX_PCT = H1["capex_h1fy24"] / H1["rev_h1fy24"]            # D: 2.4% of revenue
DA_PCT = (H1["ebitda_h1fy24"] - H1["adj_ebit_h1fy24"]) / H1["rev_h1fy24"]   # D: 4.1% (D&A below adjusted EBITDA)
TAX = 0.25                   # S UKTAX
CIR_CAP = 0.30               # S UKTAX: net interest deductible up to 30% of tax-EBITDA

# =====================================================================================
# 3. Project 04: standalone DCF (public-company view at the undisturbed date)
# =====================================================================================
YEARS_DCF = [2025, 2026, 2027, 2028, 2029, 2030, 2031]
DCF = {
    "rev_growth": [0.21, 0.19, 0.17, 0.15, 0.13, 0.11, 0.09],     # A: FY24 26%, ARR +22.7%, net ARR added flat y/y
    "ebitda_margin": [0.240, 0.255, 0.270, 0.285, 0.295, 0.305, 0.310],  # A: steady-state adj EBIT mid-20s + D&A c.4%
    "sbp_pct": [0.065, 0.060, 0.055, 0.050, 0.045, 0.040, 0.040], # A: H1 FY24 SBP 6.9% of revenue, treated as a cost
    "nwc_pct_drev": 0.10,     # A: deferred revenue grows with billings -> inflow of 10% of revenue increase
    "rf": 0.0454,             # S UST: Apr 2024 average
    "beta": 1.25,             # A: listed cyber peers trade above market beta; Darktrace has no debt
    "erp": 0.050,             # A
    "tv_growth": 0.035,       # A
}
DCF_GRID_WACC = [-0.01, -0.005, 0.0, 0.005, 0.01]
DCF_GRID_G = [-0.01, -0.005, 0.0, 0.005, 0.01]

# =====================================================================================
# 4. Trading comps at the undisturbed date (S: company releases; prices week ending 19 Apr 2024)
# name, ticker, price $, diluted shares m, cash+investments $m, debt $m, next-FY revenue guide midpoint $m,
# last FY revenue $m, guide year, source key
# =====================================================================================
COMPS = [
    ("CrowdStrike", "CRWD", 282.64, 247.94, 3474.7, 742.5, (3924.9 + 3989.0) / 2, 3055.6, "FY Jan-25", "CRWD"),
    ("Palo Alto Networks", "PANW", 277.71, 344.5, 6990.6, 1821.8, (7950 + 8000) / 2, 6892.7, "FY Jul-24", "PANW"),
    ("Fortinet", "FTNT", 63.40, 772.3, 2419.4, 992.3, (5715 + 5815) / 2, 5304.8, "FY Dec-24", "FTNT"),
    ("Zscaler", "ZS", 169.21, 148.95, 2459.8, 1141.0, (2118 + 2122) / 2, 1617.0, "FY Jul-24", "ZS"),
    ("SentinelOne", "S", 20.05, 301.36, 1130.8, 0.0, (812 + 818) / 2, 621.2, "FY Jan-25", "S"),
    ("Rapid7", "RPD", 44.31, 61.50, 439.3, 930.0, (848 + 856) / 2, 777.7, "FY Dec-24", "RPD"),
    ("Tenable", "TENB", 44.83, 116.72, 474.0, 359.3, (895 + 905) / 2, 798.7, "FY Dec-24", "TENB"),
]
# Notes: PANW shares are the non-GAAP diluted count (convertible dilution excluded because the notes are in debt);
# RPD shares are basic for the same reason. PANW and ZS last-FY revenue from their FY2023 releases (PANW23, ZS23).
NTM_WEIGHT_FY24 = 2 / 12     # D: at 25 Apr 2024, NTM = May-Jun 2024 (FY24) + Jul 2024-Apr 2025 (FY25)

# =====================================================================================
# 5. Precedent cyber take-privates (S). EV $m, last reported FY revenue $m, premium, premium basis
# =====================================================================================
PRECEDENTS = [
    ("Sophos", "Thoma Bravo", "Oct 2019", 3948.0, 711.0, 0.371, "to close 11 Oct 2019", "SOPH", "SOPH"),
    ("Proofpoint", "Thoma Bravo", "Apr 2021", 12300.0, 1050.0, 0.34, "to close 23 Apr 2021", "PFPT", "PFPT20"),
    ("Mimecast", "Permira", "Dec 2021", 5800.0, 501.4, 0.16, "to unaffected close 27 Oct 2021", "MIME", "MIME21"),
    ("SailPoint", "Thoma Bravo", "Apr 2022", 7051.2, 439.0, 0.48, "to 90-day VWAP", "ICON", "SAIL21"),
    ("Ping Identity", "Thoma Bravo", "Aug 2022", 2800.0, 299.4, 0.63, "to close 2 Aug 2022", "PING", "PING21"),
    ("ForgeRock", "Thoma Bravo", "Oct 2022", 2300.0, 176.9, 0.53, "to close 10 Oct 2022", "FORG", "FORG21"),
    ("KnowBe4", "Vista", "Oct 2022", 4600.0, 246.3, 0.44, "to unaffected close 16 Sep 2022", "KNBE", "KNBE21"),
]
# Headline values for Proofpoint, Mimecast, ForgeRock and KnowBe4 are as announced ("valued at"); KnowBe4's $4.6bn is
# equity value, so its EV/revenue is overstated by its net cash. Revenue is the last full fiscal year before announcement.

# =====================================================================================
# 6. Rival bidder screen (A)
# =====================================================================================
RIVAL = {
    "synergy_pct_rev": 0.10,      # A: strategic cost synergies as % of FY25E revenue (sales and G&A overlap)
    "synergy_multiple": 10.0,     # A: capitalised after-tax synergies (x)
    "integration_cost_x": 1.0,    # A: one-off cost = 1x run-rate synergies
    "strategic_share_kept": 0.5,  # A: share of synergy value a bidder would pay away to win
    "competing_pe_irr": 0.20,     # A: hurdle for a rival sponsor using the same leverage and plan
}

# =====================================================================================
# 7. Project 08: LBO
# =====================================================================================
YEARS_LBO = [2025, 2026, 2027, 2028, 2029]
CLOSE_STUB = 0.75             # D: close 1 Oct 2024 -> 9 of FY25's 12 months under sponsor ownership
HOLD_YEARS = 4.75             # D: 1 Oct 2024 to 30 Jun 2029
DEBT = {   # S PB unless tagged
    "tlb": 1735.0, "tlb_margin": 0.0325, "tlb_oid": 0.995, "tlb_tenor": 7, "tlb_amort": 0.01,   # amort A (market norm)
    "sl": 410.0, "sl_margin": 0.0525, "sl_oid": 0.995, "sl_tenor": 8,
    "floor": 0.0,
}
SOFR = [0.046, 0.039, 0.036, 0.035, 0.035]   # A: forward path from c.4.85% at close
FEES = {"financing_pct": 0.025, "advisory_pct_ev": 0.010}   # A
CASH_AT_CLOSE = H1["cash_dec23"]   # A: last published balance (31 Dec 2023) used as the closing cash proxy
MIN_CASH = 100.0                   # A
SWEEP = 0.75                       # A: share of excess cash applied to the first-lien term loan
LEASE_CASH = 20.0                  # A: annual lease payments (leases $60m at Dec 2023)
MIP = 0.08                         # A: management incentive plan share of exit equity
LEASES_EXIT = H1["leases_dec23"]   # A: lease liabilities held flat; deducted at exit as they are in the entry EV bridge
CASES = {   # A
    "Base": {"rev_growth": [0.19, 0.17, 0.15, 0.13, 0.12], "ebitda_margin": [0.27, 0.31, 0.35, 0.38, 0.40],
             "exit_multiple": 18.0},
    "Downside": {"rev_growth": [0.12, 0.09, 0.07, 0.06, 0.05], "ebitda_margin": [0.24, 0.25, 0.26, 0.27, 0.28],
                 "exit_multiple": 14.0},
}
NWC_PCT_DREV = 0.10   # A: same as the DCF
GRID_EXIT = [14.0, 16.0, 18.0, 20.0, 22.0]
GRID_DEBT = [1500.0, 1800.0, 2145.0, 2400.0, 2700.0]   # total debt at close, $m (2,145 = actual)
IRR_HURDLES = [0.20, 0.25]
