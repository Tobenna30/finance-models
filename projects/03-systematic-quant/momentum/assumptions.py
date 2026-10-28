"""S=sourced; A=assumed; D=derived. Decimal monthly returns, USD exposure."""
from pathlib import Path
DATA=Path(__file__).parent/'data'
START='1963-01'  # A: modern research sample; earlier published data retained but not used.
TRAIN_END='1999-12'  # A: fixed design/test split, not a Sharpe-optimised break.
TEST_START='2000-01'  # D: next month after design sample.
END='2026-09'  # S: French 202609 CRSP release retrieved 28 October 2026.
LEG_WEIGHT=.5  # A: +50% winners, -50% losers; 100% gross, zero net each month.
COST_BP=10.0  # A: each unit of bought or sold notional, excluding borrow.
ONE_WAY_TURNOVER=.5  # A: replace 50% of each leg per month. NOT measured from holdings.
BORROW_ANNUAL=.02  # A: 2% annual stock borrow charged on 50% short NAV.
# D: traded gross NAV = buys + sells = 4*leg_weight*one_way_turnover.
MONTHS=12  # A: annualisation; Sharpe uses mean/std * sqrt(12), excess over cash.
TURNOVER_GRID=[.25,.5,1.0]  # A: observable-implementation uncertainty.
COST_GRID=[0.,10.,25.,50.]  # A: one-way execution bp stress.
SOURCES={
 'deciles':'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_10_port_form_pr_12_2.html',
 'library':'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html',
 'factor':'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html',
}
