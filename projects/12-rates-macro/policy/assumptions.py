"""S=sourced; A=analyst assumption; D=derived. Rates stored as percentages."""
from pathlib import Path
DATA = Path(__file__).parent / 'data'
ASOF = '2026-10-27'  # S: BoE daily curve snapshot, retrieved 28 October 2026.
BANK_RATE = 3.75  # S: https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp
CPI = 3.5  # S: ONS September 2026 CPI, released 21 October.
BASIS_BP = 5.0  # A: Bank Rate less SONIA; constant, not independently observed.
BUDGET = 1_000_000.0  # A: sum of absolute leg DV01s in GBP per bp; 500k each.
HORIZON = .25  # A: three-month carry/roll horizon in years.
SCENARIO_END = 3.75  # A: hold Bank Rate over twelve months; inflation remains above target.
STOP_BP = 15.0  # A: close on adverse 15bp change in fitted 10y-minus-2y spread.
TARGET_BP = 25.0  # A: take profit on favourable 25bp spread move.
HAC_LAGS = 5  # A: one trading week for heteroskedasticity/autocorrelation adjustment.
VOL_DAYS = 252  # A: annualisation convention; latest 252 matched observations.
REPLAY_START, REPLAY_PEAK, REPLAY_END = '2022-09-01','2022-09-27','2022-10-14'  # A: fixed LDI episode windows, no fitted maximum.
# S: DMO Apr-Jun 2026 Quarterly Review, Annex A p7. Near-2y and near-10y proxies.
# These are curve-priced cash bonds, not executable dealer quotes.
BONDS = [('GB00BFX0ZL78',1.625,'2028-10-22'),('GB00BWBR1N39',4.875,'2036-07-31')]
MPC_FUTURE = ['2026-11-05','2026-12-17','2027-02-04','2027-03-18','2027-04-29','2027-06-17','2027-07-29','2027-09-16','2027-11-04']  # S: BoE upcoming MPC calendar; final date bounds last interval.
SOURCES = {
 'curves':'https://www.bankofengland.co.uk/statistics/yield-curves',
 'bank_rate':'https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp',
 'mpc':'https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates',
 'dmo':'https://www.dmo.gov.uk/media/r2ejghpr/apr-jun-2026a.pdf',
 'cpi':'https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/september2026',
 'fx':'https://fred.stlouisfed.org/series/DEXUSUK',
 'eurusd':'https://fred.stlouisfed.org/series/DEXUSEU',
 'sofr':'https://fred.stlouisfed.org/series/SOFR',
 'estr':'https://fred.stlouisfed.org/series/ECBESTRVOLWGTTRMDMNRT',
}
