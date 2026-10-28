# Receiver options: Project 12 extension

Built 28 October 2026. This is an auditable comparison of a synthetic SONIA receiver, receiver spread and linear swap. It is not an executable quote or a claim of option cheapness.

## Deliverable

`../models/Sterling_Receiver_Options.xlsx`: Summary, Inputs, Curve, Pricing, Scenarios, Sensitivity and Sources. All valuations and scenario outputs are live formulas. Curve data are frozen to 27 October 2026. Blue cells are editable; green formulas link across sheets. The model permits a dealer forward override, separate strike vols, costs, notional, expiry, integer tenor, width and curve shock. Missing dealer source/timestamp/inputs block dealer mode; inconsistent skew is flagged by vertical price bounds. No mode implies investment approval.

## Scope and units

Annual fixed payments at T+1,...,T+tenor; synthetic year fractions, not a business-day-adjusted contract. Discount annuity A = sum D(T+i); F = [D(T)-D(T+tenor)]/A. BoE zeros are percent continuously compounded; no extrapolation. Normal vol is bp per square-root year. The dealer forward must reference the same underlying schedule; the model retains the curve annuity. Actual cash settlement, payment delay, business-day calendars, CSA, smile dynamics and early-exit valuation require extension before execution.

All payoff comparisons use same notional, not matched delta or risk. Outputs at expiry are PV-equivalent with initial annuity frozen. Do not interpret them as terminal cash without financing/discount conversion. Costs are all-in incremental rate-bp assumptions per strategy, not spread-specific market estimates. Linear swap has uncapped loss. Receiver spread loss is bounded by debit only for a valid vertical price. Half-delta at zero-vol ATM is a convention at a kink. Invalid inputs or missing selected quotes generate explicit errors, not zero prices.

## Data and quote search

BoE official archive was downloaded 28 October with a SHA256 hash in data/curves.json. Public web research on 28 October found swap-rate pages and no executable OTC 3m2y SONIA option surface for both strikes. SwapRates explicitly describes BoE zeros, not dealer par quotes; these were not substituted. Futures-option quotes are not interchangeable with swaption quotes. The workbook's dealer vols, forward, timestamp and source are intentionally blank. Update those only with actual authorised data, using the same contract and quote-side conventions. They have not been fabricated or inferred from realised vol.

## Reproduce

Python engine: `python projects/12-rates-macro/options/engine.py`.

Workbook: `python projects/12-rates-macro/options/build_excel.py`. Uses the documented `@oai/artifact-tool` runtime; resolve it through a temporary node_modules link to the bundled runtime, or install a supported package in your own environment. Set NODE to the selected Node executable. No dependency is vendored. The house-standard Python engine and Excel formulas reconcile; artifact-tool replaces openpyxl authoring in this environment. Openpyxl is used only to inspect and test outputs.

Recalculate the exported workbook in LibreOffice headless to a separate folder, then replace the exported file with the recalculated one. Run `python -m pytest tests/test_receiver_options.py`; set SOFFICE to the LibreOffice executable to include native input-change tests. Other repository checks remain required. PDF research remains conditional and uses a vol grid; no real price advantage is established.

This extension adds a module to project 12, not a new CV project. Existing gilt/GBP modules are unchanged. It does not substantiate the missing EM or bank AT1 models described in an older CV.
