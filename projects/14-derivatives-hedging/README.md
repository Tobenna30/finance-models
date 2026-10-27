# 14: Derivatives, hedging and commodities

## Modules built

- Refinery crack-margin collars, outage stress and USD/ZAR cost overlay for an illustrative 100,000 bbl/day South African refinery.
- Bachelier pricing with Black-76 cross-check, live Excel formulas, scenario grid and Monte Carlo stress.

## Results

Hedge 80% of budgeted 2027 product barrels with monthly zero-cost collars. A 30% crack fall reduces annual refining margin by 10%, versus 30% unhedged. Six weeks of outage during a 30% crack spike creates unbacked call costs of 2.3% of annual budget margin; 90% cover exceeds the assumed 2.5% appetite.

See [risk memo](writeup/Refinery_hedge_risk_memo.md), [PDF](writeup/Refinery_hedge_risk_memo.pdf) and [workbook](models/Refinery_Hedge.xlsx).

## Reproduce

Run `python -m refinery.engine` with this directory on PYTHONPATH. Build with `python -m refinery.build_excel`, then run `refinery/recalc.py`. Tests: `pytest tests/test_refinery_hedge.py` from the repository root.

## Limitations

Teaching case, not executable quotes. NYH proxies replace local prices, a flat forward replaces the monthly curve, and crisis-year volatility drives pricing. Refining margin excludes opex. Outage appetite is an assumption. Monte Carlo is a stylised stress, not a forecast.
