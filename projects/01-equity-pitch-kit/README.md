# 01 — Long/Short Equity Pitch Kit

**Long candidate:** London Stock Exchange Group (LSEG) — does AI erode or entrench financial data moats? Includes analysis of the debt-funded $3.54bn Octus acquisition.
**Short candidate:** Rolls-Royce (RR.) — a crowded long priced for perfection as aftermarket growth slows and jet fuel costs rise.

Final direction is set by the model, not assumed.

## Deliverables
- Three-statement model (historicals + 5-year forecast), driver-based
- DCF (WACC build, terminal value cross-checks) and trading comps
- Bull / base / bear scenarios with probability-weighted target price
- 2-page pitch per name (thesis, variant view, catalysts, risks, what would change our mind)
- Reusable template so the kit can be pointed at a new company quickly

## LSEG model — [`models/LSEG_Model.xlsx`](models/LSEG_Model.xlsx)

| Base case (price 9,510p, 23 Oct 2026) | |
|---|---|
| DCF fair value | **~10,990p (+16%)** |
| Bear / Bull | ~8,320p (−13%) / ~13,570p (+43%) |
| Probability-weighted (25/50/25) | ~10,970p (+15%) |
| 2026E / 2027E adj EPS | 494p / 563p |
| 2027E P/E at current price | 16.9x |
| Net debt / EBITDA 2027E (post-Octus) | 2.1x |

**Structure:** Inputs (every number tagged sourced / assumption / derived) → divisional revenue build (Data & Analytics, FTSE Russell, Risk Intelligence, Markets, Octus) → adjusted P&L with reported bridge → cash flow → share count & buybacks → economic balance sheet (clearing balances excluded) → DCF with live WACC × terminal-growth sensitivity → Bear/Base/Bull scenarios. Change `Inputs!Scenario` to flex the whole model.

**Calibrated to company guidance:** 2026 equity FCF ≥ £2.8bn, EBITDA margin +100–120bp, capex c.9.5% of income, leverage at the upper end of 1.5–2.5x after Octus.

**How it's built:** `lseg/assumptions.py` holds every input; `lseg/engine.py` is a pure-Python version of the model; `lseg/build_excel.py` writes the formula-driven workbook. CI checks that the balance sheet balances, cash ties, scenarios are ordered, and 2026 outputs sit inside guidance.

**Known limitations (next iterations):** trading comps not yet populated; Tradeweb minority valued at a flat P/E rather than market value; Octus margin/close date are assumptions (not disclosed); no 2023 historicals yet.

## Status
- [x] Data collection (FY25 results, H1 2026, Q3 2026 update, Octus deal)
- [x] LSEG model
- [ ] LSEG trading comps
- [ ] LSEG 2-page pitch
- [ ] Rolls-Royce model
- [ ] Rolls-Royce pitch
