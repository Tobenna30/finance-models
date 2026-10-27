"""Refresh the memo, README results, source register and exact engine output."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from eqt_range.engine import calculate, main
from eqt_range.assumptions import ROOT, SOURCES, INPUTS

main()
b=calculate();down=calculate({'case':1});up=calculate({'case':3});ys=b['years']
p=lambda v:f'{v:+.1%}'
memo=f'''# EQT and Range merger analysis
*Tobenna Agubuche | 27 October 2026 | Announcement terms, LTM June 2026 earnings*

**Reject as priced on this model.** The USD325m annual synergy target produces {p(ys[2]['recurring_accretion'])} recurring EPS accretion after retaining stock compensation and an illustrative purchase-accounting charge. It falls short of the USD{b['value_breakeven_synergy']:.0f}m needed to cover the equity premium and costs. The shortfall is USD{-b['value_surplus']:.0f}m even with perpetual synergies. Verify closing shares, primary prices and purchase accounting before treating this as an executable recommendation.

## Why this deal matters
EQT announced the all-stock acquisition on 26 October. The combination connects Appalachian gas supply and infrastructure to demand from LNG, power and industry. Range shareholders receive 0.987 EQT shares each. The companies target USD325m of annual synergies within two years. The longer-term pathway above USD600m is excluded from the base case. The announced enterprise value above USD50bn refers to the combined company, not the purchase price. [1]

## What EQT shareholders receive
| Measure | Model result |
|---|---:|
| Equity consideration / premium, closing share proxies | USD{b['equity_consideration']/1000:.2f}bn / USD{b['premium']/1000:.2f}bn |
| New EQT shares / Range ownership | {b['new_shares']:.1f}m / {b['target_ownership']:.1%} |
| EQT standalone normalised EPS | USD{b['eqt_eps']:.2f} |
| Year 1 EPS including integration and fees | USD{ys[0]['inclusive_eps']:.2f} ({p(ys[0]['inclusive_accretion'])}) |
| Year 3 recurring EPS | USD{ys[2]['recurring_eps']:.2f} ({p(ys[2]['recurring_accretion'])}) |
| Company-adjusted year 3 EPS before PPA | USD{ys[2]['company_eps']:.2f} ({p(ys[2]['company_accretion'])}) |
| No-synergy recurring EPS effect | {p(b['no_synergy_accretion'])} |

!!eps_bridge.png

## Earnings quality and integration
LTM earnings equal FY2025 less H1 2025 plus H1 2026. EQT adjusted attributable net income is USD{b['ltm']['e_adj']:,.1f}m. Range adjusted net income is USD{b['ltm']['r_adj']:,.1f}m, including a USD{b['ltm']['r_sbc']:.1f}m pre-tax stock-compensation addback. Retaining that expense at an assumed 25% tax rate reduces Range earnings to USD{b['r_normal']:,.1f}m. [2-5]

The model assumes USD1,500m of depreciable fair-value uplift over 15 years, USD300m integration costs split 60/40 across years 1 and 2, and USD50m fees. These are analyst assumptions. Year 1 earns half the synergy run rate. Stock consideration requires no acquisition cash payment, but issuing shares still transfers value. Integration and fees consume USD350m gross cash. The model does not establish liquidity capacity.

---PAGEBREAK---
## Accretion is not the same as value creation
Recurring EPS needs USD{b['eps_breakeven_synergy']:.0f}m of annual pre-tax synergies to break even. The value test needs USD{b['value_breakeven_synergy']:.0f}m. It discounts assumed after-tax cash savings at 10%, allows half the run rate in year 1, then holds savings flat forever. Costs reduce that value. This optimistic perpetuity yields USD{b['net_synergy_pv']/1000:.2f}bn net savings against the USD{b['premium']/1000:.2f}bn premium. Limiting savings to 15 years increases the shortfall to USD{-b['finite_surplus']:.0f}m.

The value break-even exchange ratio is {b['max_value_ratio']:.3f}, versus the agreed 0.987. This is a ceiling under the stated price proxies and savings assumptions, not a target price. No standalone intrinsic valuation was performed.

!!synergy_value.png

## What changes the decision
| Relative earnings and synergy case | Year 3 recurring EPS effect |
|---|---:|
| Down: Range earnings -20%, half synergy target | {p(down['years'][2]['recurring_accretion'])} |
| Base: constant earnings, full USD325m target | {p(ys[2]['recurring_accretion'])} |
| Up: Range earnings +20%, full USD325m target | {p(up['years'][2]['recurring_accretion'])} |

EQT earnings stay constant in these cases. The stress isolates Range's relative earnings contribution. It is not a calibrated Henry Hub price sensitivity. The workbook also varies the exchange ratio and annual synergies. Approval would require evidence supporting savings above the value break-even level, lower costs or a lower effective premium. The USD600m pathway needs a separate execution case.

## Evidence to review
- Confirm actual closing shares and award conversion. The model uses Q2 diluted weighted shares of 629.049m for EQT and 236.210m for Range. This produces USD12.97bn equity consideration, versus Reuters' USD12.83bn based on a different share count. [3,5,6]
- Verify primary exchange prices. USD55.63 for EQT and USD45.53 for Range are rounded proxies inferred from Reuters' USD54.91 offer and 20.6% premium. They are not independently verified closing prices. [6]
- Obtain final purchase accounting, reserve depletion, debt fair values, tax attributes and the integration plan. The historical GAAP lens in Excel is not SEC pro forma EPS.
- Refresh earnings separately when Q3 results are available. This freezes the announcement analysis at LTM June 2026 and uses full post-close years, not calendar 2027 forecasts. Close is expected Q1 2027, subject to approvals. [1]

## Sources
[1] EQT merger announcement, 26 Oct 2026, transaction details and synergy target. [2] EQT FY2025 results, attributable and adjusted NI reconciliation. [3] EQT Q2 2026 results, six-month NI and diluted shares. [4] Range FY2025 results, pp11-12 net income reconciliation. [5] Range Q2 2026 results, pp9,11-12. [6] Reuters via Investing.com, 26 Oct 2026, offer value and premium, secondary cross-check. Full links and locators are in the workbook Sources tab and project README.
'''
(ROOT/'writeup'/'EQT_Range_merger_memo.md').write_text(memo)
(ROOT/'data'/'source_register.json').write_text(json.dumps({'announcement_date':'2026-10-26','financial_cutoff':'2026-06-30','sources':{k:{'locator':v[0],'url':v[1]} for k,v in SOURCES.items()},'inputs':{k:dict(label=v[0],value=v[1],tag=v[2],unit=v[3],source_or_reason=v[4]) for k,v in INPUTS.items()}},indent=2)+'\n')
readme=f'''# 05: Strategic Merger Model (Accretion/Dilution)

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
| Equity consideration / premium, proxy closing shares | USD{b['equity_consideration']/1000:.2f}bn / USD{b['premium']/1000:.2f}bn |
| New shares / Range ownership | {b['new_shares']:.3f}m / {b['target_ownership']:.2%} |
| No-synergy recurring EPS effect | {p(b['no_synergy_accretion'])} |
| Year 1 inclusive EPS / EPS effect | USD{ys[0]['inclusive_eps']:.2f} / {p(ys[0]['inclusive_accretion'])} |
| Year 2 inclusive EPS effect | {p(ys[1]['inclusive_accretion'])} |
| Year 3 recurring EPS / EPS effect | USD{ys[2]['recurring_eps']:.2f} / {p(ys[2]['recurring_accretion'])} |
| Company-adjusted year 3, before PPA | {p(ys[2]['company_accretion'])} |
| EPS / value break-even annual pre-tax synergy | USD{b['eps_breakeven_synergy']:.1f}m / USD{b['value_breakeven_synergy']:.1f}m |
| Perpetuity / finite 15-year value surplus | USD{b['value_surplus']:.1f}m / USD{b['finite_surplus']:.1f}m |
| Value break-even exchange ratio | {b['max_value_ratio']:.3f} |
| Down / base / up year 3 recurring EPS effect | {p(down['years'][2]['recurring_accretion'])} / {p(ys[2]['recurring_accretion'])} / {p(up['years'][2]['recurring_accretion'])} |

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

'''
readme+='\n'.join(f'- [{key}: {label}]({url})' for key,(label,url) in SOURCES.items())+'\n'
(ROOT/'README.md').write_text(readme)
