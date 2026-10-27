# 09: Vitamin Well / Vital Bidco private-credit underwriting

Public-information analysis as at **27 October 2026** of the 2026 refinancing and planned EMPWR combination. This is a credit research model, not a record of an actual loan commitment or access to private borrower reporting.

## Modules built

- Debt capacity at assumed gross leverage and interest-cover limits.
- Five-year cash-flow and debt schedule, with revolver funding, repayment, amortisation and sweep.
- One active forecast with a Downside / Base / Bull selector in `Inputs!C4`.
- Headroom to **underwriting policy assumptions**, not verified loan covenants.
- Default recovery waterfall and EBITDA / multiple sensitivity.
- Forecast monitoring view, Python engine, live Excel workbook, tests and credit memo.

## Results

**Reject an unconditional commitment at the modelled debt size.** Base policy headroom is thin and the downside fails the assumed leverage and coverage tests. Verify pricing, opening cash, debt perimeter, adjusted EBITDA, security and covenants before approval. These outputs do not establish a breach of the actual loan agreement.

| Metric | Result |
|---|---:|
| Reported new term loan | EUR1,900m equivalent, due 2033 |
| Reported revolver commitment | EUR200m equivalent |
| Term loan translated at assumed 11.0 SEK/EUR | SEK20,900m |
| Entry debt capacity under assumed policy | SEK21,422.5m |
| EBITDA fall to entry leverage limit | 2.4% |
| Base 2026 gross leverage / cash interest cover | 5.34x / 2.64x |
| Base / downside peak RCF draw | SEK107.9m / SEK980.1m |
| Downside peak leverage / minimum cover | 7.52x / 1.44x |
| Downside minimum cash plus undrawn RCF | SEK1,519.9m |
| Modelled unfunded cash gap, all cases | Nil |
| Default first-lien recovery | 58.8% |

Recovery assumes a 35% cash EBITDA haircut, 6x stressed multiple, 10% costs, SEK100m prior claims, a fully drawn revolver and pari passu treatment. These assumptions were not calibrated to a recovery target. Liquidity availability does not establish acceptable credit risk or contractual covenant compliance.

## Deliverables

- [Workbook](models/Vitamin_Well_Credit.xlsx)
- [Credit memo PDF](writeup/Vitamin_Well_credit_memo.pdf) and [text](writeup/Vitamin_Well_credit_memo.md)
- [Exact results and case schedules](outputs/results.json)
- [Recorded source facts and assumption register](data/source_register.json)
- [Python assumptions](vitamin/assumptions.py) and [engine](vitamin/engine.py)

## Sources and scope

The September 2026 S&P rating action is the source of the **reported new facilities and agency forecasts**. It is not an audited borrower report or an executed credit agreement. Cinven's July 2026 announcement establishes the planned EMPWR combination, with terms undisclosed. Its 2024 announcement establishes the ownership transaction. A Blue Owl SEC filing documents a **legacy** loan; its spread, maturity and lender holding are not reused as new facility terms or total borrower debt. Exact URLs and sections are in `vitamin/assumptions.py` and the workbook Sources sheet.

The model starts with the midpoint of S&P's 2026 EBITDA range and an assumed margin to infer revenue. All model history is therefore a full-year pro forma proxy. It does not claim audited actuals, completion of EMPWR, or cash flows remaining after the review date. Pricing, FX translation, opening cash, cash taxes, amortisation and policy limits are explicit assumptions.

## How to run

Use Python 3.11+ with repository requirements, plus `matplotlib` and `python-docx` for the write-up. From the repository root:

```sh
PYTHONPATH=projects/09-private-credit python -m vitamin.engine
PYTHONPATH=projects/09-private-credit python -m vitamin.build_excel
SOFFICE=/path/to/soffice PYTHONPATH=projects/09-private-credit python -m vitamin.recalc
python projects/09-private-credit/writeup/make_charts.py
python projects/09-private-credit/writeup/write_memo.py
PATH=/path/to/libreoffice-bin:$PATH python projects/09-private-credit/writeup/build_pdf.py projects/09-private-credit/writeup/Vitamin_Well_credit_memo.md
python -m pytest tests/test_vitamin_credit.py -q
```

`write_memo.py` refreshes memo figures, results JSON and the source register from the inputs and engine. `recalc.py` caches live workbook formulas through LibreOffice. Tests verify all forecast metrics against Python, switch the case selector in temporary workbooks, check cash and debt reconciliation, and test capacity/recovery boundaries. Native case-switch tests skip with an explicit reason if LibreOffice is unavailable; the engine and saved base-case parity tests still run.

## Limitations and next evidence

- No audited group balance sheet, cash-flow bridge or full sources-and-uses schedule. Purchase consideration is undisclosed. Cash/debt rollforwards reconcile; a full balance sheet is not fabricated.
- No final agreement, contractual covenant thresholds, addback definition, RCF access test, security opinion or legal recovery ranking. The monitoring view is a forecast template.
- Only term-loan and revolver funded debt is modelled. Unverified leases, other debt and rating adjustments are excluded.
- Constant illustrative FX and rates; mixed loan currencies are not modelled. The opening-balance interest convention omits current-year interest on new draws.
- The model's 2026 FCF is SEK98.9m negative, versus the agency's approximately SEK700-800m outflow forecast. Public evidence does not reconcile the difference. Do not tune a plug or equate the two measures.
- Recovery depends heavily on assumed enterprise value, priority claims and pari passu status. No executable loan price or verified new spread is available, so this is not a relative pricing recommendation.

Do not cite the policy thresholds as real covenants or describe the prospective model as actual underwriting or borrower monitoring experience.
