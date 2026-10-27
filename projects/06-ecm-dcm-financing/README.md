# 06: ECM / DCM Financing Case

**Meta AI infrastructure financing. Accept the equity-led package for staged investment.** Priced terms as at 27 October 2026, before the expected 29 October close. Match capex to cash arrival or arrange bridge funding. This is an issuer funding case, not a Meta stock recommendation or claim of advisory experience.

## Modules built

- Actual base offering sizes and issuer cash timing: preferred plus deferred common forwards.
- Immediate common equity and five-year straight-debt alternatives sized to the same eventual net proceeds.
- Issuance fees, recurring cash charges, bridge overlay, effective-interest schedule and bond yield sensitivity.
- Preferred initial Class A conversion and return illustration, dividend stub and reverse terminal-price hurdle.
- Static issue-only financial positions with assets, liabilities, equity capital and cash reconciliation.
- S/A/D input register, pure Python engine, live recalculated workbook, tests, charts and two-page memo.

## Results

| Metric | Base result |
|---|---:|
| Gross priced package | USD37.50bn |
| Expected net cash at close, with fee proxy | USD12.475bn |
| Deferred net proceeds, with expense proxy | USD24.907bn |
| Total eventual net proceeds | USD37.382bn |
| Net funding deferred | 66.6% |
| Annual preferred dividends, if paid in cash | USD812.5m |
| Bridge after-tax cost to latest settlement | USD1.243bn |
| Debt alternative face / effective yield | USD37.570bn / 5.62% |
| Debt annual after-tax coupon | USD1.632bn |
| Immediate common alternative new shares | 60.011m |
| Preferred initial-terms share range | 17.025m-20.000m |
| Initial-terms price hurdle at assumed 8% return | USD763.24 |
| Planned conditional ATM included in funded proceeds | Nil |

The pricing release supersedes the USD22.5bn common launch size with USD25bn. These figures exclude all over-allotments. Company rounded preferred net proceeds are approximately USD12.5bn; this model uses an unverified 20bp cost proxy to estimate USD12.475bn. The common initial net forward price is sourced, but later adjustments and expenses are not final.

## Deliverables

- [Live workbook](models/Meta_ECM_DCM.xlsx)
- [Financing memo PDF](writeup/Meta_financing_memo.pdf) and [markdown](writeup/Meta_financing_memo.md)
- [Exact results](outputs/results.json), [inputs CSV](data/inputs.csv) and [source register](data/source_register.json)
- [Assumptions](meta/assumptions.py), [engine](meta/engine.py), [workbook builder](meta/build_excel.py)

## How to run

Python 3.11+, repository requirements, matplotlib and python-docx. From repository root:

```sh
PYTHONPATH=projects/06-ecm-dcm-financing python -m meta.engine
PYTHONPATH=projects/06-ecm-dcm-financing python -m meta.build_excel
SOFFICE=/path/to/soffice PYTHONPATH=projects/06-ecm-dcm-financing python -m meta.recalc
python projects/06-ecm-dcm-financing/writeup/make_charts.py
python projects/06-ecm-dcm-financing/writeup/write_memo.py
SOFFICE=/path/to/soffice python projects/06-ecm-dcm-financing/writeup/build_pdf.py projects/06-ecm-dcm-financing/writeup/Meta_financing_memo.md
python -m pytest tests/test_meta_financing.py -q
```

The case selector changes the initial Class A averaging-price illustration, not historical figures. Workbook formulas tie to Python. Native case/input-change tests run when LibreOffice is available, otherwise skip explicitly. The debt schedule is fixed at five years and validates that maturity. Rebuild after changing structure. DOCX is a gitignored intermediate.

## Method and limits

- **Initial conversion illustration only.** Class C transition, stock dividend, adjusted conversion limits and voting rights are not modelled. Do not quote initial reference shares as actual 2029 dilution. Standard piecewise conversion and four-decimal rounding require final prospectus confirmation.
- All preferred dividends are assumed declared and paid in cash. 30/360 is an analyst approximation pending final prospectus review. Share-paid dividends, arrears, early/fundamental-change conversion and the floor price for share-paid dividends are excluded. There is no principal protection.
- Forward proceeds assume physical settlement on 19 November 2027, with zero base adjustment to the approximate initial USD622.92 price and USD10m additional expenses. Actual rate, dividend, stock-borrow and settlement provisions may change timing, cash and dilution.
- Debt coupon/yield 5.5%, debt fees 50bp, bridge rate 5.5%, bridge fee 50bp and tax shield 21% are analyst assumptions. Historical own-note coupons provide context only; there are no live comparable yields or financing commitments. Common issuance costs are assumed at 33.28bp.
- Annual financing cash charges exclude ordinary common dividends and equity opportunity cost. Preferred, forward equity and five-year debt have different risks and horizons. This is not a WACC optimisation or a ranking of all-in economic cost.
- The bridge assumes all eventual net proceeds are needed at closing. This is a timing stress, not a sourced Meta funding requirement. Interest and fees are additional operating cash requirements, not included in matched net issuance proceeds or the static position snapshots.
- Position snapshots retain net issuance proceeds in cash on the September balance sheet. They exclude subsequent capex, operating cash, bridge financing, dividends and any other changes. Preferred is assumed equity capital; final accounting classification is unverified. They are not future-date balance-sheet forecasts.
- Q3 liquid resources include cash and marketable securities. Nine-month free cash flow subtracts property/equipment purchases and finance-lease principal from operating cash. Neither historical cash flow nor liquid resources is added to new proceeds. The ATM is conditional, unsigned and excluded.
- The 8% investor hurdle is an assumption. Its terminal price is a deterministic reverse calculation under initial terms, not a risk-neutral preferred valuation, market-implied expected share price or actual Class C target.

## Sources

- [PRICING: Meta, 27 Oct 2026 pricing release: offer sizes, prices, conversion limits, dividends and forward cash timing](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Announces-Pricing-of-Offering-of-Depositary-Shares-Representing-Series-A-Mandatory-Convertible-Preferred-Stock-and-Offering-of-Class-A-Common-Stock-in-Connection-with-Forward-Sale-Agreements/default.aspx)
- [LAUNCH: Meta, 26 Oct 2026 launch: financing plan, conditional ATM and AI investment](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Announces-Launch-of-Offering-of-Depositary-Shares-Representing-Series-A-Mandatory-Convertible-Preferred-Stock-and-Offering-of-Class-A-Common-Stock-in-Connection-with-Forward-Sale-Agreements/default.aspx)
- [Q3: Meta Q3 2026 release, 21 Oct: September balance sheet, nine-month cash flow, FY capex guidance, Class C discussion](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/default.aspx)
- [Q2SEC: Meta June 2026 10-Q, Note 8: May notes coupon range 4.55%-6.45%; historical terms, not current yields](https://www.sec.gov/Archives/edgar/data/1326801/000162828026050705/meta-20260630.htm)
