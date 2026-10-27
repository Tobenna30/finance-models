# 16 — Institutional client coverage and consultant review

Built 27 October 2026 as independent historical research using official 30 June 2026 documents.

# Escalate five open questions before a mandate decision

Independent institutional consultant-review case, 27 October 2026. Catalogue 16: one hypothetical UK pension client. The US Global Bond Fund is a public-information proxy, not a UK-approved mandate or an actual client relationship.

## Review judgement
Escalate. Class I beat the Bloomberg Global Aggregate by 18bp over the quarter to 30 June 2026 but lagged by 51bp over one year. The three-year annualised gap was -13bp and the five-year gap -46bp. Positive quarterly commentary cannot establish persistent net outperformance. These gaps are arithmetic differences between same-horizon quoted returns, not a statistically estimated alpha.

## Process questions
The fund held 31.9% corporates against 18.4% in the index: an active weight of 13.5 percentage points. Treasuries were 13.0 points underweight. These exposures are consistent with an active spread-sector approach; they do not prove sources of return. The commentary identifies credit allocation as a contributor but does not publish a numerical attribution table. Request that table rather than manufacture a bridge.

## Consultant workflow
Eight sample questions are recorded: three supported and five open. Suggested role owners and a five-day deadline are illustrative. The five gaps cover numerical attribution, GBP-hedged mandate terms, pension vehicle access, security-level process evidence and a Class R ticker inconsistency between the factsheet header and table. No requests were sent, no meeting occurred and no responses are claimed.

The quarter and YTD are cumulative returns; longer periods are annualised. All are the same 30 June 2026 endpoint. Net expenses are not deducted again from these published returns. Fund sectors sum to 100%; benchmark weights sum to 99.9% due to source rounding, leaving a 0.1pp residual. dash for benchmark cash is interpreted as zero and documented. Sample statuses can be changed in Excel and dashboard counts update.

## Meeting brief
Ask the investment team why longer-horizon excess returns remain negative despite the quarter's credit contribution. Ask how FX and duration would differ in a GBP-hedged mandate. Request exact share-class and vehicle identifiers before circulating performance. Keep the case unapproved until the missing mandate-specific evidence is obtained.

## Limits
A dated aggregate snapshot cannot establish security selection, turnover decisions, risk-adjusted skill or client suitability. This case uses public data and hypothetical workflow records; it was built with Codex assistance. It is not a record of actual consultant servicing.

Sources: archived factsheet pages 1–2 and commentary pages 1–2; URLs in data/sources.json. Source and assumption tags are described in assumptions.py. Python/Excel parity and period checks are in tests.


## Reproduce
Run `python -m consultant_review.build_excel` from this directory. Recalculate with the bundled LibreOffice, then run the project parity tests. Input assumptions and sourced values are kept separate. Models: `models/Consultant_Review.xlsx`.
