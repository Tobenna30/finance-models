# 05: Strategic Merger Model (Accretion/Dilution)

**EQT / Range Resources. Reject as priced on the model assumptions.** Announcement analysis of the 26 October 2026 all-stock transaction. It does not imply experience advising either company.

## Modules built

- Share issuance, ownership, equity consideration and premium at the fixed 0.987 exchange ratio.
- Comparable-period LTM net-income bridge, with GAAP and company-adjusted measures separate.
- Normalised accretion/dilution retaining Range stock compensation, synergy ramp, illustrative purchase accounting and integration costs.
- One active Down / Base / Up case selector on Inputs. Ratio / synergy sensitivity uses simple live formulas.
- EPS break-even synergies, synergy value versus premium, reverse exchange ratio and finite-life cross-check.
- Python engine, recalculated live Excel, exact results, source register, charts, memo and tests.

## Results

| Metric | Base result |
|---|---:|
| Management annual synergy target | USD325m within two years |
| Equity consideration / premium, proxy closing shares | USD12.97bn / USD2.21bn |
| New shares / Range ownership | 233.139m / 27.04% |
| No-synergy recurring EPS effect | -5.6% |
| Year 1 inclusive EPS / EPS effect | USD3.83 / -7.4% |
| Year 2 inclusive EPS effect | -1.3% |
| Year 3 recurring EPS / EPS effect | USD4.19 / +1.3% |
| Company-adjusted year 3, before PPA | +4.4% |
| EPS / value break-even annual pre-tax synergy | USD265.6m / USD343.9m |
| Perpetuity / finite 15-year value surplus | USD-135.3m / USD-718.8m |
| Value break-even exchange ratio | 0.977 |
| Down / base / up year 3 recurring EPS effect | -6.9% / +1.3% / +6.0% |

Full savings cover earnings dilution but do not cover the premium and assumed costs at a 10% discount rate, even with no-growth perpetual savings. The price proxies, closing share count and standalone value proxy make the valuation conclusion provisional. Do not equate accretion with value creation.

## Deliverables

- [Live Excel workbook](models/EQT_Range_Merger.xlsx)
- [Two-page memo](writeup/EQT_Range_merger_memo.pdf) and [markdown](writeup/EQT_Range_merger_memo.md)
- [Exact results and all cases](outputs/results.json)
- [Inputs CSV](data/inputs.csv), [source register](data/source_register.json), [assumptions](eqt_range/assumptions.py), [engine](eqt_range/engine.py)

## How to run

Python 3.11+ with repository requirements. The write-up also uses matplotlib and python-docx. From the repository root:

```sh
PYTHONPATH=projects/05-strategic-merger python -m eqt_range.engine
PYTHONPATH=projects/05-strategic-merger python -m eqt_range.build_excel
SOFFICE=/path/to/soffice PYTHONPATH=projects/05-strategic-merger python -m eqt_range.recalc
python projects/05-strategic-merger/writeup/make_charts.py
python projects/05-strategic-merger/writeup/write_memo.py
SOFFICE=/path/to/soffice python projects/05-strategic-merger/writeup/build_pdf.py projects/05-strategic-merger/writeup/EQT_Range_merger_memo.md
python -m pytest tests/test_strategic_merger.py -q
```

`build_excel` uses openpyxl under AGENTS.md. `recalc` caches formulas using LibreOffice. Native input-change tests use temporary workbooks and skip if LibreOffice is unavailable. Cached parity and engine tests remain mandatory. DOCX is a gitignored build intermediate.

## Method and limits

- Earnings are LTM June 2026: FY2025 minus H1 2025 plus H1 2026. Full post-close years hold earnings constant. No Q3 results, consensus or 2027 earnings forecast.
- Use attributable EQT earnings, excluding noncontrolling interests. Company non-GAAP policies differ. Range's USD47.607m LTM SBC addback is retained at an assumed 25% tax rate. Other adjustments are not fully harmonised. Historical GAAP NI is a separate lens, not SEC pro forma EPS.
- Q2 diluted weighted shares proxy closing counts and awards. They produce USD12.97bn consideration versus Reuters' USD12.83bn. Closing numbers need verification. The combined EV above USD50bn is not consideration.
- EQT USD55.63 and Range USD45.53 are rounded manual proxies inferred from Reuters' USD54.91 offer and 20.6% premium. Primary exchange prices remain unverified. Unaffected Range price proxies standalone value; no standalone intrinsic DCF.
- Analyst assumptions: USD1,500m depreciable fair-value step-up, 15-year life, USD300m integration costs (60/40), USD50m fees, 25% incremental tax, 50% year 1 synergy capture, 10% discount rate. Fees receive no tax shield. Integration and synergy tax shields are assumed usable immediately.
- Perpetual synergies are an optimistic cash proxy with no growth, incremental capex or working capital. A finite 15-year test is shown. DD&A is noncash and excluded from synergy cash value. The >USD600m management pathway is sensitivity only.
- Existing interest remains embedded in earnings. There is no incremental acquisition borrowing, acquisition cash payment or financing-interest deduction. Gross integration/fee cash uses reconcile to USD350m. No opening liquidity, refinancing capacity, full balance sheet or three-statement forecast is claimed.
- Relative earnings cases hold EQT fixed and vary Range earnings and synergy capture. These do not map a Henry Hub move into cash flow, model hedges or forecast gas prices.

## Sources

- [DEAL: EQT, 26 Oct 2026, Transaction Details and Synergy Value](https://ir.eqt.com/newsroom/news-releases/news-release-details/2026/EQT-Announces-Strategic-Acquisition-of-Range-Resources-Creating-Americas-Undisputed-Natural-Gas-Champion/default.aspx)
- [E25: EQT FY2025 release, adjusted net income reconciliation; annual column, USD000](https://ir.eqt.com/newsroom/news-releases/news-release-details/2026/EQT-Reports-Fourth-Quarter-and-Full-Year-2025-Results-and-Provides-2026-Guidance/default.aspx)
- [E26: EQT Q2 2026 release, adjusted net income reconciliation; six-month columns and Q2 shares, USD000](https://ir.eqt.com/investor-relations/news/news-release-details/2026/EQT-Reports-Second-Quarter-2026-Results/default.aspx)
- [R25: Range FY2025 release, pp11-12 net income reconciliation; annual column, USD000](https://ir.rangeresources.com/node/29286/pdf)
- [R26: Range Q2 2026 release, pp7,9,11-12; six-month net income and stock compensation, Q2 diluted shares, USD000](https://ir.rangeresources.com/static-files/efd9ff3a-a355-40d0-9193-b491b2e7de52)
- [PRICE: SECONDARY cross-check: Reuters via Investing.com, 26 Oct 2026, USD54.91 offer and 20.6% premium; EQT proxy 54.91 / 0.987, Range proxy 54.91 / 1.206](https://www.investing.com/news/stock-market-news/eqt-range-resources-tie-up-in-50-billionplus-deal-to-create-us-gas-giant-4972044)
