# US momentum: the early premium does not survive intact
28 October 2026 | Monthly prior-12–2 deciles | Data through September 2026

## Reject a standalone strategy under the base cost assumptions
Net Sharpe falls from 0.838088 in the design period to 0.050320 after 1999. Evaluation-period geometric excess growth is -0.538% a year. The long-run premium is not enough to justify a standalone allocation on this implementation proxy. Keep it as a research benchmark, not evidence of a deployable stock-selection system.

| Sample | Months | Net Sharpe | Net CAGR | Annual vol |
|---|---:|---:|---:|---:|
| Design 1963–1999 | 444 | 0.838088 | 7.738% | 9.456% |
| Evaluation 2000–Sep 2026 | 321 | 0.050320 | -0.538% | 16.117% |
| Full sample | 765 | 0.388509 | 4.184% | 12.715% |

## Portfolio and costs
At each monthly rebalance, buy 50% NAV in the value-weighted winner decile and short 50% in the loser decile. These published portfolios use historical eligible NYSE, AMEX and NASDAQ names, ranked on months -12 through -2 with NYSE decile breakpoints. This is the standard 12–1 skipped-month convention. Dollar exposure is zero at rebalance; beta need not be zero and weights drift within the month.

Assume replacement of 50% of each leg monthly. Bought plus sold notional is 100% NAV. Charge 10bp on that traded amount and 2% annual borrow on the 50% short. Annual arithmetic drag is 1.2 percentage points execution plus 1.0 point borrow: 2.2 points total. Turnover and borrow are assumptions, not measurements. Collateral cash return is outside the excess-P&L series; no risk-free rate is subtracted again. The compounded excess index is not a fully financed total-return NAV.

!!momentum_drawdown.png

## Historical split and walk-forward discipline
Use 1963–1999 to define the design sample and freeze the canonical signal, deciles, weights and cost model. Evaluate 2000 onward without parameter search. Each January, an expanding training window reports the prior-sample Sharpe and volatility beside the next year's result; no future observations feed these estimates. No risk scaling or beta model is fitted. This is a historical pseudo-out-of-sample split, not a prospective preregistered test or an untouched dataset. The modern split includes widely known crash episodes.

---PAGEBREAK---
# Costs and crash risk determine the decision

## Drawdowns, monthly observations
| Peak | Trough | Recovery | Monthly net drawdown |
|---|---|---|---:|
| 2009-02 | 2021-05 | Unrecovered Sep 2026 | -57.600% |
| 2002-09 | 2007-02 | 2008-11 | -34.825% |
| 2000-12 | 2001-01 | 2001-09 | -21.103% |
| 1980-11 | 1981-08 | 1982-09 | -16.675% |
| 1999-02 | 1999-05 | 1999-11 | -16.344% |

The largest monthly marked drawdown is -57.600%, from February 2009 to May 2021, and is unrecovered by September 2026. This is an extended peak-to-trough episode, not a one-month loss. Daily and intramonth extremes are unavailable from the monthly series.

| Calendar year | Net return |
|---|---:|
| 2009 | -44.979% |
| 2021 | -18.847% |
| 2016 | -15.308% |
| 2003 | -15.272% |
| 2023 | -14.063% |

The strategy returns -44.979% in 2009, including -22.773% in April. A rebound in prior losers can overwhelm the short leg. Published French Mom returns -52.831% in 2009, but it uses different size/return sorts and 200% gross exposure. The correlation of our gross returns with Mom is 0.898923, or 0.890844 after 1999. Shared CRSP inputs mean this is a consistency comparison, not independent validation or alpha evidence.

## Cost sensitivity
At base 50% one-way turnover, evaluation-period historical arithmetic net mean reaches zero at 16.758567bp execution cost per traded notional, after 2% annual short borrow. This is an arithmetic historical break-even, not a quote. The live workbook stresses 0/10/25/50bp and 25/50/100% monthly replacement. A constant cost changes the mean but not the return standard deviation. Short availability, locate fees, market impact and changing turnover could worsen returns beyond these assumptions.

## Data boundary and sources
Kenneth French Data Library, 10 Portfolios Formed Monthly on Momentum, first value-weight monthly table; F-F Momentum Factor, first monthly table. The original ZIP files, 202609 CRSP vintage, hashes, extracted monthly returns and reproducible parser are committed. The library states monthly formation using information through month -2 and prior-month market equity. Original full data start in January 1927; the chosen analysis starts in January 1963.

This uses published historical-universe aggregates, not a list of today's surviving tickers. Raw security-level daily prices, delisted-name histories and holdings are not supplied by the free files. Consequently this module does not reconstruct signals, validate each delisting return, measure turnover or prove a survivorship-bias-free point-in-time stock panel. French's daily momentum deciles are formed daily, so they are not substituted for this monthly strategy. Revised historical research returns and the 2025 FIZ/CIZ methodology change are additional vintage limits.

Sources and method URLs are in momentum/assumptions.py; downloaded-file hashes and dates are in momentum/data/manifest.json. Sharpe is monthly arithmetic mean divided by sample standard deviation, multiplied by square root of 12. Costs are arithmetic percentage-point drags, not differences in CAGR. No assumptions were adjusted to improve the result. Existing projects and CV figures are unchanged.
