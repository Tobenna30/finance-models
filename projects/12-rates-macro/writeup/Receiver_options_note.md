# Separate the policy trade from the gilt-supply trade

28 October 2026. Independent research by Tobenna Agubuche. Curve 27 October; Budget 28 October. No post-Budget curve or executable option quotes.

Pass an unconditional cash 2s10s steepener. The Budget raises planned gilt sales to £250.6bn from £246.2bn in April but reduces the planned long conventional allocation to £15.5bn from £22.4bn. This is a comparison with April, not an announcement surprise: intervening transfers also changed allocations. Less long supply can help long gilts relative to the front end and work against a cash steepener. Face-value issuance is not DV01 supply; QT, maturities and issue-level duration still matter.

If the independent view is a bounded fall in front-end swap rates, compare a receiver spread with the outright receiver. The latest downloaded BoE curve gives a synthetic 3m-forward 2y annual-pay swap rate of 4.95285%. A receiver spread struck ATM/25bp lower isolates the proposed expression from cash-gilt supply basis but still has swap-curve, volatility and implementation risks.

At an assumed flat normal vol of 80bp/sqrt(year), the outright costs 15.96 rate bp and spread 9.48bp before costs. With the workbook's assumed 1bp incremental cost per strategy, spread break-even is a 10.48bp rally. The outright outperforms after a 31.48bp rally on the same-notional, frozen-annuity PV-equivalent basis. These are structural mechanics, not an empirical option-pricing edge or an argument for a rally. The model has no probability-weighted expected return.

The next MPC is 5 November. September CPI rose to 3.5%; the September MPC voted 6-3 to hold 3.75%, with three preferring a hike. These facts do not establish an easing thesis. Obtain and timestamp both strike vols, forward, quote side, settlement and costs before assessing a trade. If no substantiated bounded-rally thesis or pricing edge exists, pass.

The attached `Sterling_Receiver_Options.xlsx` has live pricing, dealer-input controls, costs, curve shocks, scenarios and sensitivities. All default vols/costs are assumptions. Native Excel-compatible results reconcile to Python; missing selected dealer inputs block valuation. Annual synthetic payment dates are not a standard-date execution schedule. Dealer-forward mode retains the curve annuity and requires the same underlying. The linear comparison has uncapped loss and is not equal-risk sizing.

Sources:
- HM Treasury, Budget 2026, section 8.3 and Table A.1: https://www.gov.uk/government/publications/budget-2026-document/budget-2026-html
- BoE OIS data and methodology: https://www.bankofengland.co.uk/statistics/yield-curves
- ONS September CPI, 21 Oct: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2026
- September MPC: https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026
- MPC calendar: https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates

Existing two-page PDF shows before-cost premium sensitivities; the workbook additionally deducts editable costs. Neither is an execution recommendation or Deutsche Bank research.
