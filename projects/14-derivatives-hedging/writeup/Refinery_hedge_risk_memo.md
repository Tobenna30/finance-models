# Refinery margin hedge: 80% cover for 2027

*Illustrative 100,000 bbl/day South African coastal refinery. Teaching case, not a real asset or executable quotes. Market data read 27 Oct 2026.*

## Recommendation
Hedge 80% of budgeted diesel, jet and petrol barrels with monthly zero-cost collars: buy puts 5% below forward and sell calls at equal premium. A 30% crack fall cuts margin 10%, versus 30% unhedged. Six weeks of outage during a 30% spike costs 2.3% of the $875m budget on unbacked calls. At 90%, another 2.5 points of downside protection costs 2.6% in that outage, above the 2.5% appetite.

| Cover | 30% crack fall | Outage cost on unbacked calls | Outage + 30% spike, total |
|---|---|---|---|
| Unhedged | -30.0% | 0.0% | +15.0% |
| 50% | -17.5% | 1.4% | +2.5% |
| 70% | -12.5% | 2.0% | -2.5% |
| **80%** | **-10.0%** | **2.3%** | **-5.0%** |
| 90% | -7.5% | 2.6% | -7.5% |

## Inputs and pricing check
On 20 Oct 2026, NYH diesel traded $105.91/bbl over Brent ($115.22), versus a trailing-year average of $56.89. Goldman expects 2027 diesel and jet cracks above $40, versus about $20 normally. Without a public forward curve, use $40 diesel and trailing-year petrol of $26.41. Annualised month-average crack volatility is $44.71/bbl diesel and $40.56/bbl petrol: crisis-year inputs, not forecasts.

Bachelier allows negative cracks, as in 2020. Its zero-cost call is 5% above forward ($42.00 diesel). Black-76 upside skew moves December's diesel call to $45.68 and lowers outage cost to 1.6%; the crack-fall loss stays 10%. The recommendation holds under both models.

## FX overlay
Sell $189m forward against R3.2bn of rand costs at 16.78 to 17.28 ZAR/USD (spot 16.64; Fed funds 3.88%; SARB repo 7.25%). With 15% rand appreciation, margin after costs is R9.94bn hedged versus R9.45bn unhedged.

## Residual risks and controls
Scores use likelihood x impact on a 5x5 scale. Operations owns outage risk (3x5=15): update run plans weekly and recut hedges on notice. Commercial risk owns NYH basis (3x4=12): reconcile weekly and investigate >10% divergence. Independent risk owns model/volatility risk (3x4=12): obtain dealer curves and implied vols. Treasury/credit owns counterparty and collateral risk (2x5=10): limits, CSA and liquidity stress. Treasury owns FX risk (2x4=8): sell dollars only against approved costs.

## Sources and limits
FRED/EIA series and source links are in assumptions.py and the workbook. SARB 7.25% via eNCA and Goldman's forecast via IBTimes are secondary sources to confirm. NYH proxies replace local pricing; flat forwards replace monthly curves. Refining margin excludes opex and is not profit or cash flow. Crisis-volatility Monte Carlo puts unhedged 5th-percentile margin below zero and the 80% hedge at -35% versus budget: stress only. Payoff and trade-off charts accompany this memo in charts/.
