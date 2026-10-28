# US equities: momentum and factor research

## Modules built

**momentum-factor-backtest**: monthly dollar-neutral replication from Kenneth French's published value-weight prior-12–2 return deciles; fixed design/evaluation split, expanding annual training reviews, assumed trading/borrow costs, crash analysis and comparison with published Mom.

This is a published-portfolio research backtest. It does not reconstruct security-level signals from daily prices, audit each delisted name or measure realised turnover. It must not be presented as an independently built point-in-time stock database.

## Results

**Reject a standalone strategy under the base cost assumptions.** The premium weakens sharply after 1999, and costs leave little arithmetic return.

| Output | Result |
|---|---:|
| Design, Jan 1963–Dec 1999, net Sharpe | 0.8380878370893319 |
| Evaluation, Jan 2000–Sep 2026, net Sharpe | 0.05032017544564235 |
| Evaluation net geometric excess growth | -0.5382077649849881% a year |
| Annual execution / borrow / total arithmetic drag | 1.2 / 1.0 / 2.2 percentage points |
| Largest monthly marked drawdown | -57.5999438823279% |
| Peak / trough / recovery | Feb 2009 / May 2021 / unrecovered Sep 2026 |
| 2009 net return | -44.9786637698919% |
| Gross decile spread correlation with published Mom | 0.8989229091365992 |
| Evaluation correlation | 0.8908437008534287 |

All exact engine outputs, annual walk-forward rows, worst years, cost grid and drawdown episodes are in `momentum/data/results.json`. The recalculated workbook is [Momentum_Factor_Backtest.xlsx](models/Momentum_Factor_Backtest.xlsx); the two-page note is [Momentum_factor_note.pdf](writeup/Momentum_factor_note.pdf).

## Method

Monthly formation uses return from months -12 through -2, skipping the latest month, with NYSE decile breakpoints and historical eligible NYSE/AMEX/NASDAQ names. Long 50% NAV in winners and short 50% in losers gives 100% gross exposure and zero dollars net at monthly rebalance, not zero beta. The first value-weighted monthly table is used; the equal-weighted and annual tables are excluded by the parser.

Base costs assume 50% one-way replacement of each leg each month and 10bp per bought or sold notional. Total traded notional is 100% NAV monthly. Add 2% annual borrow on the 50% short. These are assumptions, not estimates from holdings. Gross spread is an excess return over collateral cash; do not subtract a risk-free rate again. The compounded excess-P&L index is not a fully financed total-return NAV.

Rules and cost assumptions remain fixed. The early sample is 1963–1999 and the later sample starts in 2000. Annual walk-forward tables use expanding past-only training samples to report Sharpe and risk beside the next year, without re-optimising weights or fitting a beta/risk scaler. This is historical pseudo-out-of-sample analysis, not a prospective preregistered result. Known crash years were not hidden from the researcher.

Sharpe uses monthly arithmetic mean/sample standard deviation times sqrt(12). Annual cost drag is arithmetic, not a difference in CAGR. Drawdowns are measured monthly from a starting index of one; no daily maximum-drawdown claim is made. Sensitivities stress execution cost and assumed turnover, with borrow separate. Correlation is gross spread versus French Mom; both use related CRSP data and this is not independent validation.

## Run

Python 3.11+ with repository requirements and LibreOffice:

```sh
python projects/03-systematic-quant/momentum/fetch_data.py
python projects/03-systematic-quant/momentum/engine.py
python projects/03-systematic-quant/momentum/build_excel.py
SOFFICE=/path/to/soffice python projects/03-systematic-quant/momentum/recalc.py
python projects/03-systematic-quant/writeup/make_charts.py
python projects/03-systematic-quant/writeup/build_note.py
SOFFICE=/path/to/soffice python projects/03-systematic-quant/writeup/build_pdf.py projects/03-systematic-quant/writeup/Momentum_factor_note.md
python -m pytest tests/test_momentum_factor.py
```

Frozen ZIPs permit an offline rebuild. `fetch_data.py --download` checks hashes and refuses changed releases; review and date a new vintage before replacing the committed source. Monthly workbook return/cost/index/performance/sensitivity formulas recalculate from Inputs and Data. Drawdown episode labels are fixed Python research outputs; rerun the engine after changing costs. The live full-history drawdown minimum remains linked to the monthly return calculation.

## Sources and limits

- [French monthly momentum deciles](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_10_port_form_pr_12_2.html): historical-universe, monthly formation, value-weight returns.
- [French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html): methodology/vintage changes and published Mom factor.
- Raw ZIP hashes, retrieval date 28 October 2026 and 202609 CRSP release are retained in `momentum/data/manifest.json`.

The historical constituent universe avoids simply selecting current survivors. Free aggregate files do not expose individual prices, holdings, delisting-return adjustments or turnover, so these cannot be independently checked. Revised history is not a point-in-time publication vintage. The daily French momentum files form portfolios daily and are not used as a substitute for a monthly implementation. FIZ/CIZ methodology changed from the 2025 release. No claim of an independently survivorship-bias-free stock panel is made.

Transaction costs, borrow availability, market impact, short proceeds and collateral funding may differ materially from the assumptions. Dollar neutrality does not remove market beta or rebound/crash risk. No execution recommendation. Existing models and CVs are unchanged.
