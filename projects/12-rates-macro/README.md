# UK gilts / GBP

## Modules built

1. **gilt-curve-policy-path**: BoE fitted nominal/OIS curves, approximate meeting path, a DV01-neutral cash-gilt steepener, carry/roll, stop and 2022 shock replay.
2. **gbp-policy-repricing**: daily policy/FX regressions, ex-2022 and release-day samples, sterling carry versus USD and EUR.

Illustrative desk research dated 28 October 2026. No execution recommendation or actual portfolio.

## Results

| Output | Result |
|---|---:|
| Twelve-month implied Bank Rate, 27 October | 4.984332727626% |
| Implied cuts / hold-scenario cuts | -123.433272762594bp / 0bp |
| Conditional trade | 2s10s steepener |
| Three-month carry plus roll | 10.829943851455 spread bp |
| Entry / stop / target fitted zero spread | 58.402509036363 / 43.402509036363 / 83.402509036363bp |
| September 1–27 2022 shocks on current bonds | -GBP4,730,617.420705 |
| September 1–October 14 2022 shocks | +GBP21,478,027.725699 |
| GBP/USD move per +10bp, full / ex-2022 | -0.100740372307% / -0.050506357751% |
| Corresponding HAC t statistics | -3.096934766317 / -2.222396212656 |
| GBP/EUR move per +10bp, full / ex-2022 | +0.005135270188% / +0.052037121334% |
| Corresponding HAC t statistics | 0.234969786887 / 2.929073556624 |
| GBP carry / annualised FX vol, USD / EUR | -0.027359708721 / 0.360684882659 |

Conditional steepener versus a hold-policy assumption; reject passive GBP carry. The LDI episode reverses the simple positive rate/FX narrative. `policy/data/results.json` contains unrounded machine outputs, all regression samples, meeting intervals and cash flows. `writeup/Gilt_GBP_note.pdf` contains the dated trade log and limitations.

## Run

From the repository root with Python 3.11+ and requirements.txt:

```sh
python projects/12-rates-macro/policy/engine.py
python projects/12-rates-macro/policy/build_excel.py
SOFFICE=/path/to/soffice python projects/12-rates-macro/policy/recalc.py
python projects/12-rates-macro/writeup/make_charts.py
python projects/12-rates-macro/writeup/build_note.py
SOFFICE=/path/to/soffice python projects/12-rates-macro/writeup/build_pdf.py projects/12-rates-macro/writeup/Gilt_GBP_note.md
python -m pytest tests/test_rates_policy.py
```

Committed extracts allow an offline rebuild. `fetch_data.py /tmp/rates-cache` checks downloaded source hashes against the frozen manifest; changing source archives require explicit review of a new vintage. `extract_data.py --cache-dir /tmp/rates-cache` reconstructs the BoE CSV extracts. Original FRED CSVs, processed FX/rates, event dates with source URLs and hashes are committed. Do not silently replace dates with the latest data.

## Sources and limits

Primary: [BoE curves](https://www.bankofengland.co.uk/statistics/yield-curves), [Bank Rate](https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp), [MPC calendar](https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates), [DMO Annex A p7](https://www.dmo.gov.uk/media/r2ejghpr/apr-jun-2026a.pdf), [ONS CPI](https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2026). FRED republishes Federal Reserve FX, New York Fed SOFR and ECB short-term rate series. URLs and extraction audit are in `policy/data/manifest.json`.

Rates are continuous, in percent. Meeting averages are smoothed forwards plus an assumed 5bp basis, not meeting probabilities or pure expectations. The 3.75% hold scenario is assumed. Curve-priced proxies are 1.625% October 2028 and 4.875% July 2036; ACT/365 cash-flow times approximate gilt ACT/ACT. Stop and target refer to fitted zeros, not cash-bond yield spreads. The gross £1m/bp budget means £500k per leg and large notionals. Funding is symmetric at Bank Rate, excluding specialness, haircuts and trading costs. Replay applies historical tenor shocks to today's cash flows, without time passage, and is not an investable 2022 backtest. Carry/roll interpolation is fixed to a three-month horizon; rerun the builder if changing it.

Regression estimates are fixed historical Python research outputs in Excel; carry/risk/policy scenarios are live formulas. MPC events cover 2025–26; CPI dates cover nine releases in February–October 2026. Small event samples, non-synchronous FX/UK closes, holiday gaps and omitted global factors prevent causal interpretation. FX/carry data end 23 October, curves end 27 October. Historical curves are revised, not vintage snapshots. GBP/EUR reports GBP appreciation; EUR/GBP is its inverse. Carry/vol omits FX drift and cross-currency basis and is not an expected Sharpe.
