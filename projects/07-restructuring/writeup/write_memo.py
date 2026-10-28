"""Refresh exact figures and source record. No CV edits."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from thames.engine import calculate,main
from thames.assumptions import ROOT,INPUTS,SOURCES
main();b=calculate();old=calculate({'funding_case':1});fail=calculate({'maturity_case':0});down=calculate({'burn':250});marked=calculate({'equity_stress':.5})
memo=f'''# Thames Water restructuring case
*Tobenna Agubuche | 27 October 2026 | Conditional liquidity and Class B terms*

**Reject an unconditional new-money commitment.** The proposed GBP2.4bn liquidity upsize may buy time, but it does not complete RP2 or remove the March 2027 maturity problem. Under the stated cash and draw assumptions, approval of both funding and the maturity extension leaves GBP{b['ending_cash']:.1f}m in October 2027. A failed extension creates a GBP{fail['peak_buffer_gap']:.1f}m gap to the model's cash buffer. Accessible cash, tranche commitments and final creditor claims need verification.

## Proposed funding and maturity extension
On 15 October, Thames Water said GBP2.65bn of its GBP3bn super senior facility had been drawn and proposed another GBP2.4bn of capacity. Commitments would be sought in tranches and draws remain conditional. The consent vote is scheduled for 29 October. On 16 October, the company said RP2 might not be implemented before certain senior maturities and the stable platform period expire in March 2027. It intends a further interim extension. [1,2]

## Test liquidity and maturities separately
| Model scenario, Nov 2026 to Oct 2027 | Minimum cash position | Gap to GBP100m buffer |
|---|---:|---:|
| Existing GBP350m undrawn capacity only | GBP{old['minimum_cash']:,.1f}m | GBP{old['peak_buffer_gap']:,.1f}m |
| Upsize and maturity extension assumed | GBP{b['minimum_cash']:,.1f}m | Nil |
| Upsize assumed, GBP500m maturity not extended | GBP{fail['minimum_cash']:,.1f}m | GBP{fail['peak_buffer_gap']:,.1f}m |
| Upsize assumed, monthly use rises to GBP250m | GBP{down['minimum_cash']:,.1f}m | GBP{down['peak_buffer_gap']:,.1f}m |

!!liquidity_cases.png

Opening accessible cash of GBP200m and monthly cash use of GBP200m are analyst assumptions, not reported current balances or company guidance. Six GBP400m upsize tranches are assumed every other month, starting in November. The model charges 2% fees on new upsize draws and 9.75% interest on all incremental borrowing, using a half-month draw convention. The existing facility's 9.75% coupon is a historical source fact, applied to new funding as an assumption. [3]

Monthly cash use includes capex and interest on opening debt, so only new-draw interest is added. The remaining GBP350m capacity is counted once across the issuer-to-TWUL funding chain. Negative positions are unfunded needs, not actual overdrafts. Historical FY26 cash outflow before other financing was GBP1,130.2m, or GBP94.2m per month; the model does not claim that is today's burn rate. [3]

---PAGEBREAK---
## Class B equity and new investment
The proposed treatment writes off approximately GBP1bn of Class B debt. Holders receive an equity allocation intended to give approximately 5.9% recovery, a right to participate in GBP150m of new equity and 5.9% participation rights in certain other new tiers. The overall recapitalisation remains unagreed. [2]

| Class B economics | Model result |
|---|---:|
| Implied value of legacy equity recovery | GBP{b['b_legacy_value']:.1f}m |
| Legacy ownership at assumed GBP6bn post-money equity | {b['b_legacy_fraction']:.2%} |
| Cash paid if GBP150m new equity right exercised | GBP150.0m |
| Net legacy plus new investment value at issue | GBP{b['b_net_package']:.1f}m |
| Legacy recovery if equity value halves | {marked['b_marked_recovery']:.2%} |
| Net package value after new cash paid if equity halves | GBP{marked['b_net_package']:.1f}m |

The GBP150m investment is assumed made at fair value. It creates a GBP150m asset and requires GBP150m cash. It is not free additional recovery. The participation right itself, other new-tier rights and fees are not valued. A negative net package value in the stress reflects losses on voluntary new money; it is not a negative insolvency distribution.

## Recovery depends on claims and value
An independent illustrative waterfall assumes GBP18bn enterprise value, 5% costs, GBP1.5bn priority hedge and other claims, GBP5.4bn super senior debt after all assumed draws and GBP16bn Class A claims. It gives Class A {b['waterfall']['a_recovery']:.2%} recovery and Class B nil. The hypothetical Class A par break-even enterprise value is GBP{b['a_break_even_ev']/1000:.2f}bn. These are scenario outputs, not an assessment of actual legal recoveries.

!!recovery_sensitivity.png

The report cites a c69% Class A trading reference for March 2026. Applied to the scenario claims, it corresponds to GBP{b['historical_quote_implied_ev']/1000:.2f}bn EV. This is a reverse sensitivity, not a current quote or a valuation inferred for March. The negotiated Class B equity consideration and this hypothetical enforcement waterfall are separate analyses. [3]

At the same GBP18bn EV, the existing-capacity-only case gives Class A {old['waterfall']['a_recovery']:.2%}, versus {b['waterfall']['a_recovery']:.2%} after the GBP2.4bn upsize. New super senior claims reduce recovery by 15 percentage points in this fixed-value test. It excludes any value created by deploying the new funding.

## Evidence required before commitment
- Verify current accessible cash, burn, draw conditions and tranche commitments. Cash held at a financing issuer may require consent for downstream use.
- Obtain the maturity-by-instrument schedule, supported extension terms, complete Class A and hedge claims, and legal ranking. The GBP500m March principal stress is assumed.
- Confirm RP2 valuation, equity allocation, new-money terms, regulatory approvals, costs and special-administration alternatives. Neither RCV nor accounting net debt is used as a substitute for recoverable value or legal claims.

*Sources: [1] TWUL, 15 Oct 2026, Sixteenth Consent Requests. [2] TWUL, 16 Oct 2026, Class B TSA update. [3] TWUL Group annual report 2025/26, p39 cash flow, pp108-109 maturities, p124 hedging priority and historic trading reference, pp139-140 debt. Full links and locators are in the workbook and README.*
'''
(ROOT/'writeup/Thames_restructuring_memo.md').write_text(memo)
(ROOT/'data/source_register.json').write_text(json.dumps({'as_of':'2026-10-27','sources':{k:{'locator':v[0],'url':v[1]} for k,v in SOURCES.items()},'inputs':{k:dict(label=v[0],value=v[1],tag=v[2],unit=v[3],source_or_reason=v[4]) for k,v in INPUTS.items()},'scope':['TWUL funding chain counted once','No verified current accessible cash or complete legal claims','Waterfall, equity valuation and March principal amount are explicit assumptions','Class B 5.9% is recovery, not ownership; new investment is a cash outflow']},indent=2)+'\n')
readme=f'''# 07: Restructuring & Liability Management

**Thames Water. Reject an unconditional new-money commitment.** Current public-information analysis as at 27 October 2026, ahead of the scheduled 29 October consent vote. Conditional funding is separated from committed cash, maturity extension and final RP2 implementation.

## Modules built

- Twelve-month cash-use and super senior borrowing schedule with blocked / existing-only / upsize-assumed funding selector.
- Separate March 2027 maturity-extension stress, draw fees, incremental interest and cash-buffer shortfalls.
- Illustrative priority recovery waterfall and EV / costs sensitivity, with all unverified claims tagged as assumptions.
- Proposed Class B legacy recovery, implied equity ownership and separate cash cost of new investment rights.
- Reverse Class A EV sensitivity at the historical c69% reference; legacy Class B holding value equivalent to old par.
- Live recalculated Excel, pure Python engine, input/source registers, charts, two-page memo and tests.

## Results

| Metric | Model result |
|---|---:|
| Existing drawn / capacity, 15 Oct source | GBP2.65bn / GBP3.00bn |
| Conditional existing undrawn capacity, counted once | GBP350m |
| Proposed incremental capacity, not fully committed | GBP2.40bn |
| Super senior debt after all assumed draws | GBP5.40bn |
| Minimum cash with upsize and maturity extension assumed | GBP{b['minimum_cash']:.1f}m |
| First buffer breach, existing capacity only | January 2027 |
| Gap to GBP100m buffer if March extension fails | GBP{fail['peak_buffer_gap']:.1f}m |
| Gap if monthly cash use increases to GBP250m | GBP{down['peak_buffer_gap']:.1f}m |
| Illustrative Class A / Class B waterfall recovery | {b['waterfall']['a_recovery']:.2%} / nil |
| Class A recovery, existing capacity only at same EV | {old['waterfall']['a_recovery']:.2%} |
| Illustrative Class A par break-even EV | GBP{b['a_break_even_ev']/1000:.2f}bn |
| Class B proposed legacy recovery value | GBP59m |
| Class B legacy fraction at GBP6bn equity proxy | {b['b_legacy_fraction']:.2%} |
| Class B new investment paid / net package at issue | GBP150m / GBP59m |

The cash scenario requires an assumed GBP200m accessible opening cash balance, GBP200m monthly use, full consent to the remaining GBP350m, six bimonthly GBP400m upsize draws, 2% upsize fees, 9.75% new-draw interest and extension of an assumed GBP500m March maturity. It is not a forecast of actual current liquidity or proof that funding is sufficient.

## Deliverables

- [Workbook](models/Thames_Restructuring.xlsx)
- [Memo PDF](writeup/Thames_restructuring_memo.pdf) and [markdown](writeup/Thames_restructuring_memo.md)
- [Exact schedules and cases](outputs/results.json), [inputs CSV](data/inputs.csv), [source register](data/source_register.json)
- [Assumptions](thames/assumptions.py), [engine](thames/engine.py), [workbook builder](thames/build_excel.py)

## How to run

Python 3.11+, repository requirements, matplotlib and python-docx. From repository root:

```sh
PYTHONPATH=projects/07-restructuring python -m thames.engine
PYTHONPATH=projects/07-restructuring python -m thames.build_excel
SOFFICE=/path/to/soffice PYTHONPATH=projects/07-restructuring python -m thames.recalc
python projects/07-restructuring/writeup/make_charts.py
python projects/07-restructuring/writeup/write_memo.py
SOFFICE=/path/to/soffice python projects/07-restructuring/writeup/build_pdf.py projects/07-restructuring/writeup/Thames_restructuring_memo.md
python -m pytest tests/test_thames_restructuring.py -q
```

Native input-change tests use temporary workbooks when LibreOffice is available; they skip explicitly otherwise. Engine and saved workbook parity remain mandatory. DOCX is a gitignored intermediate.

## Method and limits

- Source facts cover the 15-16 October announcements and historical annual report. No current cash, complete legal claims register, executed RP2, new-tranche commitments or current bond quotes were obtained. The October vote is prospective at the cutoff.
- The 15 October drawn balance is held flat at the model start as an assumption; it is not a verified 31 October debt balance. Actual intervening cash and draws require a fresh funding bridge.
- Existing capacity less drawn is GBP350m, counted once across upstream issuer and TWUL. Do not add GBP350m at each entity or count GBP2.4bn of proposed capacity as committed cash. Upsize tranches are not actual loan draw dates.
- Cash use includes capex and interest on the opening debt. Only incremental-draw interest is added. FY26 historical outflow of GBP1,130.2m is before other financing and excludes subsequent borrowings/lease repayments and derivative settlements. It is a cross-check, not current burn.
- Negative projected cash shows unfinanced need, with no fictitious borrowing plug. The GBP100m buffer is an analyst assumption. No full balance sheet, regulatory covenant test or contractual liquidity forecast is claimed.
- March GBP500m principal is an assumed cash requirement if extension fails, not proof of funded redemption. It reduces the unfunded cash position but leaves the independent Class A claim proxy unchanged. The extension is separate from funding consent.
- Waterfall EV GBP18bn, 5% costs, GBP1.5bn priority reserve and GBP16bn Class A claims are assumptions. The report confirms some derivatives rank above Class A; hedge-versus-super-senior ranking and termination amounts remain unverified. No precise legal recovery or Special Administration outcome is claimed. EV is not RCV.
- The annual report's c69% Class A reference is historical March 2026. Applying it to scenario claims gives a reverse sensitivity only, not an executable trade or current/then-implied market EV.
- The Class B TSA is binding on its parties but the overall recapitalisation and implementation are conditional. Approximately 5.9% is legacy recovery, not ownership. GBP59m divided by the GBP6bn equity proxy gives the model's 0.98% holding, not a disclosed allocation.
- Exercising GBP150m new equity rights costs GBP150m cash. It is assumed invested at fair value; new and legacy marks are stressed separately in the schedule. The right itself, other 5.9% tier participation rights, consent/work fees and interim Class B coupon receipts are not valued.
- Negotiated plan equity consideration and the illustrative enforcement waterfall are separate cases. The fixed legacy holding would need GBP{b['b_full_par_equity']/1000:.1f}bn equity value to equal the original GBP1bn debt face; that is a reverse wealth calculation, not restored debt entitlement or a valuation target.

## Sources

'''
readme+='\n'.join(f'- [{k}: {desc}]({url})' for k,(desc,url) in SOURCES.items())+'\n'
(ROOT/'README.md').write_text(readme)
