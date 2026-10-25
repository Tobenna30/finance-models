# 04 + 08: Darktrace / Thoma Bravo take-private

Thoma Bravo bought Darktrace plc for $7.75 a share in cash (620p at announcement), an equity value of $5.3bn and an enterprise value of $5.0bn. The offer was announced on 26 Apr 2024 and became effective on 1 Oct 2024. One model covers both sides of the deal:

- **04 Sell-side:** was 620p fair? DCF, listed peers, precedent take-privates, bid premiums, football field, board defence case and a rival-bid screen.
- **08 LBO:** the sponsor's case on the actual price and debt. Sources and uses, first and second-lien term loans, five-year operating case, cash sweep, IRR/MOIC, exit multiple x leverage grid, downside case and a value bridge.

## Deliverables
- Model: [`models/Darktrace_04_08.xlsx`](models/Darktrace_04_08.xlsx) (14 sheets, every forecast and valuation cell a live formula, Sources sheet with links)
- 04 write-up: [`writeup/Darktrace_fairness_note.pdf`](writeup/Darktrace_fairness_note.pdf) (2 pages)
- 08 write-up: [`writeup/Darktrace_LBO_IC_memo.pdf`](writeup/Darktrace_LBO_IC_memo.pdf) (3-page IC memo)

## Results
| Offer 620p ($7.75) | Value | vs offer |
|---|---:|---:|
| Premium to undisturbed close (517p) / 3-month VWAP (429.9p) | 20% / 44% | |
| Offer EV / LTM revenue / NTM revenue / LTM adj. EBITDA | 8.1x / 6.2x / 34.2x | |
| Standalone DCF (SBP as a cost; 551p with SBP added back) | 455p | -27% |
| Listed peers, median EV / NTM revenue (8.2x) | 817p | +32% |
| Precedent cyber take-privates, median EV / LTM revenue (11.7x) | 879p | +42% |
| Precedent median premium (44%) on 517p | 744p | +20% |
| LBO ability to pay at 25% / 20% IRR | 593p / 661p | |
| Strategic buyer with 50% of synergies paid away | 487p | -21% |

| LBO (actual financing) | Base | Downside |
|---|---:|---:|
| Debt at close: $1,735m first lien S+325, $410m second lien S+525 | 14.7x LTM EBITDA | |
| Sponsor equity | $3,001m (55%) | |
| FY29 revenue / EBITDA margin | $1,397m / 40% | $1,002m / 28% |
| Exit multiple | 18x | 14x |
| IRR / MOIC (exit 30 Jun 2029) | 23% / 2.7x | -11% / 0.58x |
| FY29 margin needed for a 20% IRR | 36.9% | |

**Verdict (04):** fair but not full. 620p sits above intrinsic value and inside a sponsor's 20 to 25% IRR range, but well below peer and precedent multiples. No rival had room to pay more, and 14.7% of the shares were under irrevocables that stayed binding against a higher offer.
**Verdict (08):** approve. The return is an operating return: Thoma Bravo paid 34x trailing EBITDA and exits at 18x, so EBITDA has to nearly quadruple. Debt is serviced in the downside; the equity is not protected.

## How it is built
Same standard as the LSEG model in project 01.

- `darktrace/assumptions.py`: single source of inputs. Every value tagged S (sourced, with a key into `SOURCES` and a URL), A (assumption) or D (derived).
- `darktrace/engine.py`: pure Python. DCF, comps (quartiles and a growth regression), precedents, LBO with two tranches, mandatory amortisation, 75% cash sweep, UK 30% interest cap, closed-form ability to pay, value bridge.
- `darktrace/build_excel.py`: openpyxl workbook. Inputs in blue, formulas in black, cross-sheet links in green. The IRR grid is five full re-runs of the debt schedule, not a data table, so every cell is live.
- `darktrace/recalc.py`: recalculates the workbook in LibreOffice headless so the committed file carries values.
- `tests/test_darktrace.py`: the Excel values tie to the engine (cover, football field, every grid cell, value bridge); offer maths ties to the announcement; sources equal uses; debt schedule identities; IRR monotonic in leverage and exit multiple; the closed-form price returns exactly the target IRR; forecast cells are formulas.

```
cd projects/04-08-darktrace
python -m darktrace.build_excel && python -m darktrace.recalc
python3 writeup/make_charts.py
cd writeup && python3 build_pdf.py Darktrace_fairness_note.md && python3 build_pdf.py Darktrace_LBO_IC_memo.md
```

## Sources
Rule 2.7 announcement (26 Apr 2024), scheme document publication (23 May 2024), meeting results (18 Jun 2024), regulatory and timetable update (16 Sep 2024), scheme effective (1 Oct 2024); Darktrace FY23 results, H1 FY24 results and Q4 FY24 trading update; Bloomberg Law and PitchBook LCD on the debt; peer 8-K releases and prices for the week ending 19 Apr 2024; precedent deal releases. Full list in the workbook's Sources sheet.

**Limitations:** FY24 adjusted EBITDA margin (23%) is assumed because Darktrace stopped giving margin guidance after the offer. Closing cash uses the December 2023 balance. The revolver, if any, is not modelled. SOFR path and the operating cases are assumptions. Some precedent values are headline deal values, not computed EVs (KnowBe4's $4.6bn is equity value).
