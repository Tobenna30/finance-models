"""USD millions and million securities. S sourced; A assumption; D in engine.

Priced terms, 27 Oct 2026. Offerings have not closed as of the analysis date.
Preferred conversion illustration uses initial Class A terms only. The pending
Class C transition makes these reference mechanics, not actual 2029 dilution.
"""
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'PRICING':('Meta, 27 Oct 2026 pricing release: offer sizes, prices, conversion limits, dividends and forward cash timing','https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Announces-Pricing-of-Offering-of-Depositary-Shares-Representing-Series-A-Mandatory-Convertible-Preferred-Stock-and-Offering-of-Class-A-Common-Stock-in-Connection-with-Forward-Sale-Agreements/default.aspx'),
 'LAUNCH':('Meta, 26 Oct 2026 launch: financing plan, conditional ATM and AI investment','https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Announces-Launch-of-Offering-of-Depositary-Shares-Representing-Series-A-Mandatory-Convertible-Preferred-Stock-and-Offering-of-Class-A-Common-Stock-in-Connection-with-Forward-Sale-Agreements/default.aspx'),
 'Q3':('Meta Q3 2026 release, 21 Oct: September balance sheet, nine-month cash flow, FY capex guidance, Class C discussion','https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/default.aspx'),
 'Q2SEC':('Meta June 2026 10-Q, Note 8: May notes coupon range 4.55%-6.45%; historical terms, not current yields','https://www.sec.gov/Archives/edgar/data/1326801/000162828026050705/meta-20260630.htm'),
}
# Label, value, tag, unit, locator or rationale
INPUTS={
 'deposits':('Depositary shares offered',250.,'S','m','PRICING: base offering, excludes option'),
 'deposit_price':('Depositary share public price',50.,'S','USD','PRICING'),
 'deposits_per_pref':('Depositary interests per preferred share',20.,'S','x','PRICING: each represents 1/20th'),
 'liquidation':('Liquidation preference per preferred share',1000.,'S','USD','PRICING'),
 'dividend':('Preferred annual dividend',.065,'S','%','PRICING: when declared, cash or shares permitted'),
 'min_rate':('Minimum initial Class A conversion rate',1.3620,'S','shares/pref','PRICING: subject to adjustments and Class C transition'),
 'max_rate':('Maximum initial Class A conversion rate',1.6000,'S','shares/pref','PRICING: subject to adjustments and Class C transition'),
 'common_shares':('Forward common shares',40.,'S','m','PRICING: base offer, physical settlement assumption below'),
 'offer_price':('Common public offering price',625.,'S','USD','PRICING: priced, not a live market quote'),
 'forward_price':('Initial net forward price',622.92,'S','USD','PRICING: approximate, subject to contractual adjustments'),
 'atm':('Planned future Class C ATM',60000.,'S','USDm','LAUNCH: no signed programme; excluded from funded proceeds'),
 'cash':('Reported cash and cash equivalents',11222.,'S','USDm','Q3: 30 Sep 2026, excludes restricted cash'),
 'securities':('Reported marketable securities',71227.,'S','USDm','Q3: distinct from cash'),
 'assets':('Reported total assets',478836.,'S','USDm','Q3: 30 Sep 2026'),
 'liabilities':('Reported total liabilities',206450.,'S','USDm','Q3: 30 Sep 2026'),
 'equity':('Reported stockholders equity',272386.,'S','USDm','Q3: 30 Sep 2026'),
 'ocf9':('Nine-month operating cash flow',96873.,'S','USDm','Q3 cash flow reconciliation'),
 'ppe9':('Nine-month cash property/equipment purchases',83055.,'S','USDm','Q3 cash flow reconciliation'),
 'lease9':('Nine-month finance-lease principal payments',2769.,'S','USDm','Q3 cash flow reconciliation'),
 'capex_low':('FY2026 capex guidance low',135000.,'S','USDm','Q3: includes finance-lease principal'),
 'capex_high':('FY2026 capex guidance high',145000.,'S','USDm','Q3: guidance, not capital commitment or financing need'),
 'pref_fee':('Preferred issuance cost proxy',.002,'A','%','Unverified 20bp; company rounded net proceeds approximately USD12.5bn'),
 'forward_expense':('Forward additional expense proxy',10.,'A','USDm','After initial forward price discount, unverified fixed expense'),
 'forward_change':('Net forward price adjustment stress',0.,'A','%','Zero base, not a claim that contractual carry/dividend/borrow adjustments are zero'),
 'equity_fee':('Immediate common issuance cost proxy',.003328,'A','%','33.28bp from (625-622.92)/625, applied as a comparison assumption'),
 'bond_fee':('Straight-bond issuance cost proxy',.005,'A','%','50bp; not an underwriting quote'),
 'bond_coupon':('Hypothetical bond coupon',.055,'A','%','Illustrative five-year issue at par; historical own-note range cross-check only'),
 'bond_yield':('Hypothetical bond valuation yield',.055,'A','%','Not current trading yield; vary separately from fixed coupon'),
 'bond_term':('Hypothetical bond term',5,'A','years','Annual coupons, bullet repayment; no refinancing assumption'),
 'tax':('Incremental debt tax shield',.21,'A','%','Illustrative immediately usable 21%; preferred dividends receive no shield'),
 'bridge_rate':('Bridge interest rate',.055,'A','%','Simple ACT/365; available only as an analytical overlay, no facility verified'),
 'bridge_fee':('Bridge fee',.005,'A','%','50bp on funding gap, paid separately from proceeds'),
 'investor_hurdle':('Preferred investor return hurdle',.08,'A','%','Illustrative 8% annual required return, not a market-implied yield'),
 'case':('Case: 1 Down / 2 Base / 3 Up',2,'A','index','Initial Class A conversion mechanics only'),
 'price_down':('Down: final averaging price proxy',400.,'A','USD','Not a target price or forecast'),
 'price_base':('Base: final averaging price proxy',625.,'A','USD','Reference offer price, not a forecast'),
 'price_up':('Up: final averaging price proxy',850.,'A','USD','Not a target price or forecast'),
}
CLOSE=date(2026,10,29)  # S PRICING: expected, not completed
SETTLE=date(2027,11,19)  # S PRICING: latest expected settlement; A single physical settlement on deadline
CONVERT=date(2029,8,15)  # S PRICING: mandatory settlement on or about date
DIVIDEND_DATES=[date(y,m,15) for y in (2027,2028,2029) for m in (2,5,8,11) if date(y,m,15)<=CONVERT]
PRICE_GRID=(300.,400.,500.,625.,700.,800.,900.)  # A: initial-term conversion illustrations
YIELD_GRID=(.035,.045,.055,.065,.075)  # A: yield sensitivity

def values():return {k:v[1] for k,v in INPUTS.items()}
