"""Exact figures refresh from the financing engine; no CVs are edited."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from meta.engine import calculate,main
from meta.assumptions import ROOT,INPUTS,SOURCES,CLOSE,SETTLE,CONVERT
main();b=calculate();cases=[calculate({'case':i}) for i in (1,2,3)]
memo=f'''# Meta ECM and DCM financing case
*Tobenna Agubuche | 27 October 2026 | Priced terms, before expected closing*

**Accept the equity-led package for staged investment.** The USD{b['gross_package']/1000:.1f}bn priced package provides about USD{b['initial_cash']/1000:.2f}bn at expected closing in this model. About USD{b['forward_net']/1000:.2f}bn arrives later, at physical settlement of the common-share forwards. Match spending to cash receipts or arrange bridge funding. The planned USD60bn Class C ATM is excluded from available funding. This is a financing recommendation, not a view on Meta's shares. [1,2]

## AI infrastructure funding
Meta is funding a large AI infrastructure programme while changing its equity capital structure. Its Q3 release guides to USD135-145bn of 2026 capex, including finance-lease principal. Nine-month free cash flow was USD{b['historical_fcf']/1000:.2f}bn, after USD85.82bn capex. [2,3]

## Cash raised and cash available
| Financing item | Base model |
|---|---:|
| Preferred gross / assumed net proceeds | USD12.50bn / USD{b['pref_net']/1000:.3f}bn |
| Common gross / deferred net proceeds | USD25.00bn / USD{b['forward_net']/1000:.3f}bn |
| Share of eventual net proceeds deferred | {b['deferred_share']:.1%} |
| Preferred annual cash dividends, if paid | USD{b['annual_dividend']:.1f}m |
| Bridge cost to 19 Nov 2027, after assumed tax | USD{b['bridge_after_tax_cost']/1000:.2f}bn |

!!funding_timing.png

The common offering was upsized from USD22.5bn to USD25bn. Its 40m shares are sold at USD625 through forward sellers. Meta initially receives no proceeds from that sale. The initial forward price is approximately USD622.92, before further contractual adjustments and expenses. The model assumes one physical settlement on 19 November 2027, the latest expected settlement date. [1]

Preferred proceeds use a 20bp fee proxy. Forward expenses are assumed at USD10m, with zero base forward-price adjustment. These are not verified underwriting terms. A 5.5% bridge on the deferred amount costs USD{b['bridge_interest']/1000:.2f}bn interest plus USD{b['bridge_fee']:.0f}m fees before tax. No bridge is claimed to exist. The overlay assumes all eventual proceeds are needed immediately.

---PAGEBREAK---
## Compare the funding alternatives
| Same USD{b['net_total']/1000:.2f}bn eventual net funding | Equity-led package | Immediate common | Straight debt |
|---|---:|---:|---:|
| Cash at expected close, USDbn | {b['initial_cash']/1000:.2f} | {b['net_total']/1000:.2f} | {b['net_total']/1000:.2f} |
| Annual assumed financing cash charge, USDm | {b['annual_dividend']:.1f} | 0 | {b['bond_after_tax_coupon']:.1f} |
| Debt principal repayable in year 5, USDbn | 0 | 0 | {b['bond_face']/1000:.2f} |

The hypothetical debt has a 5.5% coupon, 50bp issuance costs and a 21% usable tax shield. It requires USD{b['bond_face']/1000:.2f}bn face value and has a {b['bond_effective_yield']:.2%} effective yield including fees. Coupon and valuation yield are assumptions, not trading quotes. Preferred dividends have no assumed tax deduction. Immediate common needs {b['equity_shares']:.2f}m shares at USD625 after assumed fees. [4]

Annual cash charges exclude common dividends and the opportunity cost of equity. The package and bond have different horizons and terminal obligations. This comparison does not establish the lowest total cost of capital. Static issue-only balance sheets reconcile proceeds retained as cash; they do not forecast capex deployment or Meta's future liquidity.

## Preferred equity carries downside risk
The 250m depositary shares represent 12.5m preferred shares. On initial Class A terms, conversion rates of 1.3620-1.6000 imply 17.025m-20.000m common shares. The model illustrates the standard fixed-value middle band between USD625 and USD734.21, rounding rates to four decimals. Final prospectus confirmation remains required. [1]

!!preferred_payoff.png

At illustrative averaging prices of USD400 / USD625 / USD850, nominal investor returns including assumed cash dividends are {cases[0]['pref_total_return']:+.1%} / {cases[1]['pref_total_return']:+.1%} / {cases[2]['pref_total_return']:+.1%}. The initial-terms price required to meet an assumed 8% annual return is USD{b['investor_hurdle_price']:.2f}. This deterministic hurdle is not an option valuation or a market forecast.

## Evidence required before execution
- Model the Class C transition, stock dividend and anti-dilution adjustments before quoting actual 2029 dilution or voting effects. The initial Class A schedule is a mechanism illustration only.
- Confirm final underwriting fees, dividend day count, forward carry, stock-borrow adjustments, settlement alternatives and accounting classification. All dividends are assumed declared and paid in cash on an approximate 30/360 schedule.
- Verify spending dates, liquidity restrictions and financing capacity. Reported liquid resources of USD{b['liquid_resources']/1000:.2f}bn include securities and are not added to issuance proceeds. Options and the conditional ATM are excluded. [1-3]

*Sources: [1] Meta pricing release, IR page dated 27 Oct 2026 (release dateline 26 Oct). [2] Meta launch release, 26 Oct 2026. [3] Meta Q3 results, 21 Oct 2026, September balance sheet and cash-flow reconciliation. [4] Meta June 2026 10-Q Note 8: historical own-note coupons only, not live comparables. Full links and locators are in the workbook and README.*
'''
(ROOT/'writeup/Meta_financing_memo.md').write_text(memo)
(ROOT/'data/source_register.json').write_text(json.dumps({'as_of':'2026-10-27','expected_close':CLOSE.isoformat(),'assumed_forward_settlement':SETTLE.isoformat(),'initial_preferred_conversion':CONVERT.isoformat(),'sources':{k:{'locator':v[0],'url':v[1]} for k,v in SOURCES.items()},'inputs':{k:dict(label=v[0],value=v[1],tag=v[2],unit=v[3],source_or_reason=v[4]) for k,v in INPUTS.items()},'method_assumptions':['Initial Class A piecewise conversion with four-decimal rounding; final prospectus confirmation required','30/360 dividend approximation; all declared and paid in cash','Physical forward settlement at deadline; zero base price adjustment, not a claim of zero contractual adjustments','Issue-only balance sheets: preferred treated as equity capital, fees netted against capital or debt carrying value']},indent=2)+'\n')
readme=f'''# 06: ECM / DCM Financing Case

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
| Gross priced package | USD{b['gross_package']/1000:.2f}bn |
| Expected net cash at close, with fee proxy | USD{b['initial_cash']/1000:.3f}bn |
| Deferred net proceeds, with expense proxy | USD{b['forward_net']/1000:.3f}bn |
| Total eventual net proceeds | USD{b['net_total']/1000:.3f}bn |
| Net funding deferred | {b['deferred_share']:.1%} |
| Annual preferred dividends, if paid in cash | USD{b['annual_dividend']:.1f}m |
| Bridge after-tax cost to latest settlement | USD{b['bridge_after_tax_cost']/1000:.3f}bn |
| Debt alternative face / effective yield | USD{b['bond_face']/1000:.3f}bn / {b['bond_effective_yield']:.2%} |
| Debt annual after-tax coupon | USD{b['bond_after_tax_coupon']/1000:.3f}bn |
| Immediate common alternative new shares | {b['equity_shares']:.3f}m |
| Preferred initial-terms share range | 17.025m-20.000m |
| Initial-terms price hurdle at assumed 8% return | USD{b['investor_hurdle_price']:.2f} |
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

'''
readme+='\n'.join(f'- [{k}: {desc}]({url})' for k,(desc,url) in SOURCES.items())+'\n'
(ROOT/'README.md').write_text(readme)
