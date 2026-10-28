from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'policy'))
import engine as E
r=E.results();p=Path(__file__).parent
rows=['| Pair / sample | GBP move % per +10bp | HAC t | R-squared | N |','|---|---:|---:|---:|---:|']
for pair,v in r['fx'].items():
 for sample,a in v['regressions'].items():rows.append(f"| {pair} / {sample} | {a['slope']:.6f} | {a['t']:.4f} | {a['r2']:.6f} | {a['n']} |")
text=f'''# UK gilts / GBP: hold versus a hiking curve
28 October 2026 | curves 27 October; FX and carry 23 October | Illustrative research

## Conditional 2s10s steepener; reject passive GBP carry
The OIS 12-month instantaneous forward plus an assumed 5bp Bank Rate/SONIA basis implies {r['implied_bank_rate_12m_pct']:.4f}% Bank Rate. This is {abs(r['implied_cuts_bp']):.2f}bp of hikes against a 3.75% hold scenario. September CPI is 3.5%, above target. Holding rates is a contestable assumption, not a prediction from the data. The thesis needs inflation to subside enough to prevent the priced tightening. Assume 2y falls 50bp and 10y falls 10bp in that scenario; inflation pressure that forces front-end yields higher relative to the long end can break the view.

| Trade log, entered 28 October 2026 | Value |
|---|---:|
| Fitted 10y less 2y entry | {r['spread_bp']:.4f}bp |
| Stop / target, same fitted spread | {r['stop_bp']:.4f} / {r['target_bp']:.4f}bp |
| Gross absolute DV01, half per leg | GBP1,000,000/bp |
| Long 1.625% October 2028 nominal | GBP{r['bonds'][0]['nominal_gbp']/1e6:,.3f}m |
| Short 4.875% July 2036 nominal | GBP{abs(r['bonds'][1]['nominal_gbp'])/1e6:,.3f}m |
| Three-month carry / roll | GBP{r['carry_gbp']/1e6:.4f}m / GBP{r['roll_gbp']/1e6:.4f}m |
| Carry plus roll / single-leg DV01 | {r['carry_roll_bp']:.6f} spread bp |
| 1–27 September 2022 shock replay | GBP{r['replay']['peak']['pnl_gbp']/1e6:.4f}m |
| 1 September–14 October 2022 replay | GBP{r['replay']['end']['pnl_gbp']/1e6:.4f}m |

Stop implies roughly GBP7.5m first-order loss before carry and convexity. This risk budget is large. Short proceeds are assumed available and both legs finance at Bank Rate. Borrow availability, margin, repo specialness and bid/ask are excluded. Carry holds each cash-flow zero rate fixed; roll ages cash flows down an unchanged curve. Cash bond proxy yields differ from the fitted zero spread used for the stop. The replay shocks today's bond cash flows by the historical 2y/10y moves; it is not a realised 2022 trading return. Convexity matters: near-parallel moves need not give zero P&L.

!!rates_policy.png

## Policy path method and sources
Published BoE continuously compounded zero rates give discount factors. Adjacent MPC dates bound intervals; differences in log discounts divided by ACT/365 time give average overnight forwards. Daily compounding conversion plus the 5bp basis gives the displayed Bank Rate proxy. Before the first monthly tenor, the zero rate is held flat. This is a smoothed meeting approximation with term premia, not discrete meeting probabilities. A 0/5/10bp basis changes the terminal rate by the same 0/5/10bp. A 25bp parallel scenario change need not translate one-for-one into gilt yields.

Sources: Bank of England yield-curves page, Bank Rate history and upcoming MPC dates; DMO April–June 2026 Quarterly Review, Annex A page 7; ONS September 2026 CPI bulletin, released 21 October. Exact URLs and downloaded-file SHA256 hashes are in policy/data/manifest.json and assumptions.py. Archive curves can be revised; this is not a vintage backtest.

---PAGEBREAK---
# Sterling: policy repricing does not buy a stable FX beta
Daily matched observations, January 2020–23 October 2026. GBP appreciation is positive for both pairs; GBP/EUR is the inverse of the usual EUR/GBP quote. Returns are log percentages. The regressor is the change in the 12-month OIS instantaneous forward, with a constant basis cancelling out. OLS includes an intercept. Reported t statistics use Newey–West, five lags, finite-sample adjustment.

{chr(10).join(rows)}

The USD full-sample slope is negative: higher UK rate pricing coincides with weaker sterling. Excluding 2022 halves its magnitude. In the LDI window, 1 September–14 October 2022, a +10bp repricing coincides with {r['fx']['GBP_USD']['regressions']['LDI']['slope']:.4f}% GBP/USD and {r['fx']['GBP_EUR']['regressions']['LDI']['slope']:.4f}% GBP/EUR. Fiscal credibility and global dollar demand can dominate the interest-rate channel. The euro slope changes sign after removing 2022. These are associations, not causal policy surprises or a trading signal.

| Carry snapshot, 23 October 2026 | GBP vs USD | GBP vs EUR |
|---|---:|---:|
| Bank Rate minus SOFR / euro short-term rate, pp | {r['fx']['GBP_USD']['carry_pct']:.4f} | {r['fx']['GBP_EUR']['carry_pct']:.4f} |
| Trailing 252-observation annualised FX vol, % | {r['fx']['GBP_USD']['vol_pct']:.6f} | {r['fx']['GBP_EUR']['vol_pct']:.6f} |
| Carry / vol | {r['fx']['GBP_USD']['carry_to_vol']:.6f} | {r['fx']['GBP_EUR']['carry_to_vol']:.6f} |

Reject passive GBP carry: it is negative against USD and the positive EUR differential is modest relative to currency risk. Carry/vol is a rate-differential screen, not an expected Sharpe or executable forward return. It omits future spot drift, cross-currency basis, roll and transaction costs. Volatility uses matched observations and 252 annualisation; holiday gaps can span several calendar days.

MPC events cover the published 2025 and 2026 calendars. CPI events are the nine verified February–October 2026 release dates. Event returns run from the previous matched close to the event-day close, not intraday windows. One MPC date lacks a matched US observation. The small CPI sample and sparse-event HAC estimates support no event-trading claim. UK and US close times differ; global rates and risk shocks are omitted.

FRED republishes Federal Reserve H.10 GBP/USD and EUR/USD, New York Fed SOFR and ECB euro short-term rate. Derive EUR/GBP as EUR/USD divided by GBP/USD. No forward-filled spot observations. The rates snapshot intentionally uses the same date as the last available FX observation. Rebuild the Python research after a data update; the workbook labels the regression outputs as fixed historical estimates.
'''
(p/'Gilt_GBP_note.md').write_text(text)
(rp:=p.parent/'policy/data/results.json').write_text(json.dumps(r,indent=2))
