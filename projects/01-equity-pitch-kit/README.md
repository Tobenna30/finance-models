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

| Price 9,510p (23 Oct 2026) | Value | vs price |
|---|---:|---:|
| DCF base / bear / bull (Octus purchase now deducted) | 9,343p / 6,724p / 11,643p | −2% / −29% / +22% |
| SOTP (peer forward P/E by division) | 11,480p | +21% |
| LSEG ex-Tradeweb forward P/E | 16.6x | vs FactSet 16.9x |
| Trailing P/E vs 5-year average | 19.8x | vs 25.3x |
| Retention implied by the share price | 93.4% | vs 92.8% reported |

> **Pitch under revision.** A DCF fix (the Octus purchase price was not deducted) moved the DCF from 9,880p to 9,343p. The two-page pitch still shows the old figures; do not send it until it is updated.

**Modules built:** initiate coverage ✅ · react to results (Q3 2026 update, [note](writeup/LSEG_Q3_2026_update.pdf)) ✅

**What makes it a professional build**
- **Quarterly anchor:** 14 income lines, Q1 2025 to Q3 2026 actuals; 2026E = 9M actual + Q4E.
- **Driver-based forecasts:** subscription income from ASV growth = gross sales + price − churn (retention); FTSE Russell asset-based = ETF AUM × yield; FIDO = Tradeweb ADV × capture; OTC = SwapClear notional × capture; NTI = cash collateral × spread.
- **Divisional EBITDA** from LSEG's segment disclosure → group P&L, cash flow, buybacks, economic balance sheet (balances every year).
- **Valuation:** DCF with live WACC × g grid; Tradeweb minority deducted at market P/E; SOTP on peer forward P/E; reverse DCF (retention, volumes, margins, terminal growth implied by the price); Bear/Base/Bull switch that flexes every driver.
- **PM-proofing:** Tradeweb stub valuation (listed sub at market value); beta box (observed 0.41, Blume 0.60, used 0.85, with value sensitivity); 5-year trailing P/E history with chart; peak-volume normalisation in 2027; SEC EDGAR audited fundamentals for US peers, refreshed weekly by GitHub Actions.
- **Evidence & trackers:** third-party industry studies on AI and data demand (Burton-Taylor, Expand/BCG, Coalition Greenwich & SIX, Substantive Research, FactSet filings); weekly hiring tracker (LSEG vs FactSet open roles by function, from Workday career sites); weekly Tradeweb-stake and LSEG-vs-FactSet tracker. All refreshed every Monday by GitHub Actions.
- **Checks:** model vs company-compiled consensus; pair trade against FactSet considered and rejected (reasoning in the workbook).
- **Engine parity:** `lseg/engine.py` reproduces every Excel number to the penny (tested after LibreOffice recalculation, including the scenario switch). CI tests: balance sheet, cash tie-out, history ties to reported totals, 2026 inside guidance, consensus proximity, formulas-only forecasts.

**Limitations:** 2023 history at group level only (sub-lines not disclosed on today's basis); peer multiples from a third-party site; Octus margin and close date are assumptions.

## Status
- [x] Data collection (FY25 results, H1 2026, Q3 2026 update, Octus deal)
- [x] LSEG model (v2: driver-based, quarterly, SOTP, reverse DCF)
- [x] LSEG trading comps + consensus check
- [x] LSEG 2-page pitch ([PDF](writeup/LSEG_pitch.pdf), [text](writeup/LSEG_pitch.md))
- [ ] Rolls-Royce model
- [ ] Rolls-Royce pitch
