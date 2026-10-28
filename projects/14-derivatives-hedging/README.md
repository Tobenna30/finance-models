# 14: Derivatives, hedging and commodities

## Modules built

- Refinery crack-margin collars, outage stress and USD/ZAR cost overlay for an illustrative 100,000 bbl/day South African refinery. This is not a real asset or an executable trade recommendation.
- Bachelier pricing with Black-76 cross-check, live Excel formulas, scenario grid and Monte Carlo stress.

- [C++17 pricer](cpp-pricer/README.md): Black-76/Bachelier prices and Greeks, full monthly parity and common-shock Monte Carlo benchmark.

## Results

Hedge 80% of budgeted 2027 product barrels with monthly zero-cost collars. A 30% crack fall reduces annual refining margin by 10%, versus 30% unhedged. Six weeks of outage during a 30% crack spike creates unbacked call costs of 2.3% of annual budget margin; 90% cover exceeds the assumed 2.5% appetite.

| Cover | 30% crack fall | Outage cost on unbacked calls | Outage + 30% spike, total |
|---|---|---|---|
| Unhedged | -30.0% | 0.0% | +15.0% |
| 50% | -17.5% | 1.4% | +2.5% |
| 70% | -12.5% | 2.0% | -2.5% |
| **80%** | **-10.0%** | **2.3%** | **-5.0%** |
| 90% | -7.5% | 2.6% | -7.5% |

Black-76 strikes lower the 80% outage cost to **1.6%**, with the crack-fall loss unchanged at **10%**. Annual budget refining margin is **$875m**.

See [risk memo](writeup/Refinery_hedge_risk_memo.md), [PDF](writeup/Refinery_hedge_risk_memo.pdf) and [workbook](models/Refinery_Hedge.xlsx).

C++ module: maximum pricing/strike difference 2.1316282072803006e-14; 19.39289626276462x stress-kernel speed-up at 20,000 common paths on the stated machine. 57 pytest cases and one CTest case. Timings exclude RNG/I/O; original model outputs are unchanged.

## How to run

From the repository root, inspect the existing model and run its checks:

```sh
PYTHONPATH=projects/14-derivatives-hedging .venv/bin/python -m refinery.engine
.venv/bin/python -m pytest tests/test_refinery_hedge.py tests/test_darktrace.py tests/test_smoke.py
```

The local Python 3.9 environment cannot collect test_lseg.py; CI uses Python 3.11. To rebuild only when inputs intentionally change:

```sh
cd projects/14-derivatives-hedging
../../.venv/bin/python -m refinery.build_excel
SOFFICE=~/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice ../../.venv/bin/python -m refinery.recalc
SOFFICE=~/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice ../../.venv/bin/python writeup/build_pdf.py writeup/Refinery_hedge_risk_memo.md
```

## Sources

Sourced, assumed and derived inputs are tagged in [assumptions.py](refinery/assumptions.py); the workbook includes a Sources sheet. CSV observations are dated 20 to 26 October 2026, read on 27 October.

- FRED/EIA: Brent (DCOILBRENTEU), NYH heating oil (DDFUELNYH), petrol (DGASNYH), oil volatility (OVXCLS) and Fed funds (DFF), retained in data/.
- Alpha Vantage: USD/ZAR. CME: crack-spread methodology.
- **Secondary, confirm before execution:** SARB repo **7.25%** via [eNCA](https://www.enca.com/business-top-stories/reserve-bank-hikes-interest-rates-25-basis-points), against the SARB MPC statement.
- **Secondary, confirm before execution:** Goldman 2027 diesel/jet crack forecast above **$40/bbl**, versus about **$20** normally, via [IBTimes](https://www.ibtimes.com/oil-flows-are-recovering-diesel-likely-continue-being-expensive-while-heres-why-3808277), citing CNBC.

## Limitations

Teaching case, not executable quotes. NYH proxies replace local prices, a flat forward replaces the monthly curve, and crisis-year volatility drives pricing. Refining margin excludes opex. Outage appetite is an assumption. Monte Carlo is a stylised stress, not a forecast.
