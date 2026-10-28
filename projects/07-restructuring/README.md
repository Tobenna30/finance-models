# 07: Restructuring & Liability Management

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
| Minimum cash with upsize and maturity extension assumed | GBP342.5m |
| First buffer breach, existing capacity only | January 2027 |
| Gap to GBP100m buffer if March extension fails | GBP257.5m |
| Gap if monthly cash use increases to GBP250m | GBP357.5m |
| Illustrative Class A / Class B waterfall recovery | 63.75% / nil |
| Class A recovery, existing capacity only at same EV | 78.75% |
| Illustrative Class A par break-even EV | GBP24.11bn |
| Class B proposed legacy recovery value | GBP59m |
| Class B legacy fraction at GBP6bn equity proxy | 0.98% |
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
- Negotiated plan equity consideration and the illustrative enforcement waterfall are separate cases. The fixed legacy holding would need GBP101.7bn equity value to equal the original GBP1bn debt face; that is a reverse wealth calculation, not restored debt entitlement or a valuation target.

## Sources

- [CONSENT: TWUL, 15 Oct 2026, Sixteenth Consent Requests: facility draw, conditional upsize, pari passu proposal, vote 29 Oct](https://www.thameswater.co.uk/news/2026/oct/twul-sixteenth-consent-requests-results)
- [CLASSB: TWUL, 16 Oct 2026, Class B TSA: proposed full debt write-off, c5.9% recovery, rights to invest; not completed](https://www.thameswater.co.uk/news/2026/oct/class-b-creditors-update)
- [AR26: TWUL Group annual report 2025/26: p39 cash flow; pp139-140 loans/bonds; p124 hedging priority and historical c69% Class A trading level; pp108-109 March 2027 maturity extension](https://www.thameswater.co.uk/media-library/2tad3w44/annual-report-2025-26.pdf)
