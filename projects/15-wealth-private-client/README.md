# 15 — Family fund selection

Built 27 October 2026 as independent historical research using official 30 June 2026 documents.

# Pass Class I despite its 25bp fee advantage

Independent historical review, 27 October 2026. Catalogue 15: fund selection for a hypothetical family after a liquidity event. This is not a real client or an investment recommendation.

## Decision
Pass institutional Class I for the assumed direct retail family. Meeting the $100,000 minimum does not establish institutional eligibility. Keep retail Class R only for further suitability and platform review. Compare access before comparing cost.

## Analysis
The 30 June 2026 factsheet reports net expense ratios of 0.67% for Class I and 0.92% for Class R. The 25bp difference implies $2,500 annual indicative expense on a $1m balance. These are two share classes of the same manager and fund, not two independent manager choices. There is no invented peer universe.

The workbook models fee sensitivity at assumed pre-expense returns of -2%, 5% and 8%. Returns are hypothetical, constant and not forecasts. Published fund performance is not used in this fee model, so fees are not deducted twice. A separate illustration uses gross expenses of 0.79% and 1.04%; expiry of the waiver on 31 January 2027 does not prove an automatic fee increase.

Duration of 6.87 implies a first-order price loss of 6.87% for a parallel 100bp yield rise. This omits carry, convexity, FX, spread changes and management responses. The fund is not a cash substitute.

## Manager questions
Confirm exact share-class identifiers: the factsheet header and its fund-facts table differ for Class R. Obtain the current prospectus and platform terms before deciding access. Ask about currency hedging and the family's actual spending currency. Assess whether active credit and foreign-currency exposure match the intended bond sleeve.

## Limits
This is a dated fee/access screening exercise, not a full peer-manager recommendation. Public aggregate exposures do not prove security-level process consistency. No household tax, withdrawals or allocation decision is modelled. It is an independent research tool built with Codex assistance; the owner must understand and validate it before presenting it.

Sources: local archived factsheet pages 1–2; URL in data/sources.json. Every numeric input is tagged S or A in assumptions.py. The Python engine and recalculated Excel results are tested for parity.


## Reproduce
Run `python -m fund_selection.build_excel` from this directory. Recalculate with the bundled LibreOffice, then run the project parity tests. Input assumptions and sourced values are kept separate. Models: `models/Fund_Selection.xlsx`.
