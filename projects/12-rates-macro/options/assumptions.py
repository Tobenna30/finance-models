"""Single source of inputs. Rates are decimal; normal volatility is bp/sqrt(year)."""
from pathlib import Path
import json
DATA=Path(__file__).parent/'data'
CURVES=json.loads((DATA/'curves.json').read_text())
ASOF=max(CURVES['curves'])
INPUTS={
 'notional':(100_000_000,'A','Illustrative sizing, not a proposed allocation'),
 'expiry':(.25,'A','Synthetic quarter-year option expiry'),
 'tenor':(2,'A','Annual fixed payments; whole years, 1 to 10'),
 'width_bp':(25,'A','Sold receiver strike 25bp below ATM'),
 'long_vol_bp':(80,'A','Sensitivity assumption, not an observed option quote'),
 'short_vol_bp':(80,'A','Separate input permits skew sensitivity'),
 'cost_bp':(1,'A','All-in incremental cost per strategy, rate bp; replace with quote-based costs'),
 'forward_mode':(0,'A','0 curve-derived; 1 dealer forward'),
 'dealer_forward':(None,'S','Enter decimal forward for the same underlying schedule'),
 'vol_mode':(0,'A','0 assumed; 1 dealer strike-specific normal vols'),
 'dealer_long_vol_bp':(None,'S','Missing; no public executable quote found'),
 'dealer_short_vol_bp':(None,'S','Missing; no public executable quote found'),
 'quote_time':('', 'S','Missing; timestamp and timezone required for dealer mode'),
 'quote_source':('', 'S','Missing; source and quote side required for dealer mode'),
 'curve_shock_bp':(0,'A','Parallel shock to all OIS zero rates'),
 'scenario_shift_bp':(-25,'A','Expiry shift relative to selected forward, not a forecast'),
}
DEFAULTS={k:v[0] for k,v in INPUTS.items()}
SOURCES=[
 ('S','BoE OIS continuous zero curve',ASOF,CURVES['url'],'Downloaded 28 Oct 2026. Fitted and revisable; not dealer quotes.'),
 ('S','BoE curve methodology','2026-10-28','https://www.bankofengland.co.uk/statistics/yield-curves','Rates percent continuous; publication normally following business day.'),
 ('S','Budget 2026, section 8.3/Table A.1','2026-10-28','https://www.gov.uk/government/publications/budget-2026-document/budget-2026-html','April-to-Budget allocation comparison is not an announcement surprise.'),
 ('S','ONS September CPI','2026-10-21','https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2026','CPI 3.5%; does not establish an easing forecast.'),
 ('S','September MPC','2026-09-17','https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026','Bank Rate 3.75%; 6-3 hold; three preferred a hike.'),
 ('S','Dealer option surface','Unavailable','', 'No executable OTC 3m2y SONIA strike vols obtained. Do not substitute futures-option or realised vol.'),
]
