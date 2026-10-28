# UK gilts / GBP: hold versus a hiking curve
28 October 2026 | curves 27 October; FX and carry 23 October | Illustrative research

## Conditional 2s10s steepener; reject passive GBP carry
The OIS 12-month instantaneous forward plus an assumed 5bp Bank Rate/SONIA basis implies 4.9843% Bank Rate. This is 123.43bp of hikes against a 3.75% hold scenario. September CPI is 3.5%, above target. Holding rates is a contestable assumption, not a prediction from the data. The thesis needs inflation to subside enough to prevent the priced tightening. Assume 2y falls 50bp and 10y falls 10bp in that scenario; fiscal or inflation pressure that lifts the long end or forces more near-term hikes can break the view.

| Trade log, entered 28 October 2026 | Value |
|---|---:|
| Fitted 10y less 2y entry | 58.4025bp |
| Stop / target, same fitted spread | 43.4025 / 83.4025bp |
| Gross absolute DV01, half per leg | GBP1,000,000/bp |
| Long 1.625% October 2028 nominal | GBP2,706.003m |
| Short 4.875% July 2036 nominal | GBP660.758m |
| Three-month carry / roll | GBP4.1098m / GBP1.3052m |
| Carry plus roll / single-leg DV01 | 10.829944 spread bp |
| 1–27 September 2022 shock replay | GBP-4.7306m |
| 1 September–14 October 2022 replay | GBP21.4780m |

Stop implies roughly GBP7.5m first-order loss before carry and convexity. This risk budget is large. Short proceeds are assumed available and both legs finance at Bank Rate. Borrow availability, margin, repo specialness and bid/ask are excluded. Carry holds each cash-flow zero rate fixed; roll ages cash flows down an unchanged curve. Cash bond proxy yields differ from the fitted zero spread used for the stop. The replay shocks today's bond cash flows by the historical 2y/10y moves; it is not a realised 2022 trading return. Convexity matters: near-parallel moves need not give zero P&L.

!!rates_policy.png

## Policy path method and sources
Published BoE continuously compounded zero rates give discount factors. Adjacent MPC dates bound intervals; differences in log discounts divided by ACT/365 time give average overnight forwards. Daily compounding conversion plus the 5bp basis gives the displayed Bank Rate proxy. Before the first monthly tenor, the zero rate is held flat. This is a smoothed meeting approximation with term premia, not discrete meeting probabilities. A 0/5/10bp basis changes the terminal rate by the same 0/5/10bp. A 25bp parallel scenario change need not translate one-for-one into gilt yields.

Sources: Bank of England yield-curves page, Bank Rate history and upcoming MPC dates; DMO April–June 2026 Quarterly Review, Annex A page 7; ONS September 2026 CPI bulletin, released 21 October. Exact URLs and downloaded-file SHA256 hashes are in policy/data/manifest.json and assumptions.py. Archive curves can be revised; this is not a vintage backtest.

---PAGEBREAK---
# Sterling: policy repricing does not buy a stable FX beta
Daily matched observations, January 2020–23 October 2026. GBP appreciation is positive for both pairs; GBP/EUR is the inverse of the usual EUR/GBP quote. Returns are log percentages. The regressor is the change in the 12-month OIS instantaneous forward, with a constant basis cancelling out. OLS includes an intercept. Reported t statistics use Newey–West, five lags, finite-sample adjustment.

| Pair / sample | GBP move % per +10bp | HAC t | R-squared | N |
|---|---:|---:|---:|---:|
| GBP_USD / full | -0.100740 | -3.0969 | 0.019638 | 1658 |
| GBP_USD / ex2022 | -0.050506 | -2.2224 | 0.004455 | 1417 |
| GBP_USD / LDI | -0.367194 | -6.2293 | 0.464584 | 29 |
| GBP_USD / MPC | -0.053353 | -0.4841 | 0.013622 | 13 |
| GBP_USD / CPI | -0.015455 | -0.1967 | 0.002856 | 9 |
| GBP_EUR / full | 0.005135 | 0.2350 | 0.000105 | 1658 |
| GBP_EUR / ex2022 | 0.052037 | 2.9291 | 0.009148 | 1417 |
| GBP_EUR / LDI | -0.145974 | -3.1758 | 0.208496 | 29 |
| GBP_EUR / MPC | 0.059535 | 1.4361 | 0.066879 | 13 |
| GBP_EUR / CPI | 0.034567 | 0.8598 | 0.025262 | 9 |

The USD full-sample slope is negative: higher UK rate pricing coincides with weaker sterling. Excluding 2022 halves its magnitude. In the LDI window, 1 September–14 October 2022, a +10bp repricing coincides with -0.3672% GBP/USD and -0.1460% GBP/EUR. Fiscal credibility and global dollar demand can dominate the interest-rate channel. The euro slope changes sign after removing 2022. These are associations, not causal policy surprises or a trading signal.

| Carry snapshot, 23 October 2026 | GBP vs USD | GBP vs EUR |
|---|---:|---:|
| Bank Rate minus SOFR / euro short-term rate, pp | -0.1700 | 1.3080 |
| Trailing 252-observation annualised FX vol, % | 6.213516 | 3.626434 |
| Carry / vol | -0.027360 | 0.360685 |

Reject passive GBP carry: it is negative against USD and the positive EUR differential is modest relative to currency risk. Carry/vol is a rate-differential screen, not an expected Sharpe or executable forward return. It omits future spot drift, cross-currency basis, roll and transaction costs. Volatility uses matched observations and 252 annualisation; holiday gaps can span several calendar days.

MPC events cover the published 2025 and 2026 calendars. CPI events are the nine verified February–October 2026 release dates. Event returns run from the previous matched close to the event-day close, not intraday windows. One MPC date lacks a matched US observation. The small CPI sample and sparse-event HAC estimates support no event-trading claim. UK and US close times differ; global rates and risk shocks are omitted.

FRED republishes Federal Reserve H.10 GBP/USD and EUR/USD, New York Fed SOFR and ECB euro short-term rate. Derive EUR/GBP as EUR/USD divided by GBP/USD. No forward-filled spot observations. The rates snapshot intentionally uses the same date as the last available FX observation. Rebuild the Python research after a data update; the workbook labels the regression outputs as fixed historical estimates.
