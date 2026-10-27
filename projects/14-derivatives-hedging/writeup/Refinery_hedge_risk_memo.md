# Refinery margin hedge: hedge 80% of 2027 cracks with zero-cost collars

*Illustrative 100,000 bbl/day South African coastal refinery. Teaching case, not a real asset or executable quotes. Market data read 27 Oct 2026.*

## Recommendation
Hedge 80% of budgeted 2027 diesel, jet and petrol barrels with monthly zero-cost collars. Buy puts 5% below the forward crack and sell calls at the strike that makes the premiums net to zero. Sell dollars forward against the rand cost budget.

At 80% cover, a 30% fall in 2027 cracks cuts refining margin by **10%** against **30%** unhedged. If a six-week outage hits while cracks rise 30%, the sold calls on the missing barrels cost **2.3%** of the **$875m** annual budget margin. 90% cover saves another 2.5 points in a fall, but its outage cost of 2.6% breaches the 2.5% appetite. 80% is the most protection inside that limit.

| Cover | 30% crack fall | Outage cost on unbacked calls | Outage + 30% spike, total |
|---|---|---|---|
| Unhedged | -30.0% | 0.0% | +15.0% |
| 50% | -17.5% | 1.4% | +2.5% |
| 70% | -12.5% | 2.0% | -2.5% |
| **80%** | **-10.0%** | **2.3%** | **-5.0%** |
| 90% | -7.5% | 2.6% | -7.5% |

!! charts/payoff.png | charts/tradeoff.png

## Market inputs
Spot cracks are extreme. On 20 Oct 2026 NYH diesel traded $105.91/bbl over Brent ($115.22), against a trailing-year average of $56.89. Goldman Sachs expects 2027 diesel and jet cracks above $40, against about $20 in a normal year. The model uses $40 for diesel and the trailing-year average of $26.41 for petrol, because no public crack forward curve was available. The brief is a refiner locking in unusually high 2027 margins before they fall back.

Volatility is the annualised change in month-average cracks over the past year: $44.71/bbl for diesel and $40.56/bbl for petrol. That is a crisis-year figure. It sets premium size, not the headline percentages.

## Model check: Bachelier against Black-76
Bachelier prices the collar because cracks can go negative, as they did in 2020. Its zero-cost call sits exactly 5% above the forward ($42.00 for diesel), so the results hold at any crack level. Black-76 assumes a lognormal crack with upside skew, which pushes the December diesel call out to $45.68. Under Black-76 strikes the outage cost falls to 1.6%, while the 30% fall result is unchanged at 10%. The Bachelier figure is the cautious one, and the recommendation holds under either model.

## FX overlay
The refinery earns dollars and pays about R3.2bn of rand costs. Selling $189m forward at 16.78 to 17.28 ZAR per dollar (spot 16.64, Fed funds 3.88%, SARB repo 7.25%) locks those costs. If the rand strengthens 15%, rand margin after costs falls to R9.94bn hedged against R9.45bn unhedged.

## Residual risk register (5x5, after controls)
| Risk | L | I | Score | Owner | Control and trigger |
|---|---|---|---|---|---|
| Unplanned outage leaves sold calls unbacked | 3 | 5 | 15 | Refinery operations manager | Weekly run-plan update. Recut hedge volumes on any outage notice |
| Basis: refinery slate and pricing differ from NYH cracks | 3 | 4 | 12 | Commercial risk manager | Weekly product-level reconciliation. Investigate >10% divergence |
| Model and volatility: inputs from one crisis year | 3 | 4 | 12 | Independent market risk analyst | Replace with dealer quotes and monthly implied vols before trading |
| OTC counterparty or collateral call on sold calls | 2 | 5 | 10 | Treasury and credit managers | Approved limits, CSA terms and a liquidity stress before execution |
| Rand strength against the dollar margin | 2 | 4 | 8 | Treasury manager | Sell dollars only against the approved rand cost budget |

## Limits
Refining margin is crack times barrels, with opex excluded, so it is not profit or cash flow. NYH cracks stand in for South African product prices. One forward per product replaces a monthly curve. The SARB rate and the Goldman forecast come from secondary reports. A Monte Carlo at crisis-year volatility puts the unhedged 5th percentile below zero margin and the 80% hedged case at -35%, so treat it as a stress picture, not a forecast.
