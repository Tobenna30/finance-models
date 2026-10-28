"""GBPm; 27 Oct 2026. S sourced, A assumption, D calculated.

No live cash balance, agreed RP2 plan, legal claims register or executable bond
prices obtained. New funding remains conditional. Waterfall is illustrative.
"""
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MONTHS=[date(2026+(10+i)//12,(10+i)%12+1,1) for i in range(12)]
SOURCES={
 'CONSENT':('TWUL, 15 Oct 2026, Sixteenth Consent Requests: facility draw, conditional upsize, pari passu proposal, vote 29 Oct','https://www.thameswater.co.uk/news/2026/oct/twul-sixteenth-consent-requests-results'),
 'CLASSB':('TWUL, 16 Oct 2026, Class B TSA: proposed full debt write-off, c5.9% recovery, rights to invest; not completed','https://www.thameswater.co.uk/news/2026/oct/class-b-creditors-update'),
 'AR26':('TWUL Group annual report 2025/26: p39 cash flow; pp139-140 loans/bonds; p124 hedging priority and historical c69% Class A trading level; pp108-109 March 2027 maturity extension','https://www.thameswater.co.uk/media-library/2tad3w44/annual-report-2025-26.pdf'),
}
INPUTS={
 'drawn':('Super senior drawn, 15 Oct',2650.,'S','GBPm','CONSENT: issuer-to-TWUL chain, not additional separate loans'),
 'facility':('Existing super senior facility capacity',3000.,'S','GBPm','CONSENT: conditional capacity; undrawn is not free cash'),
 'upsize':('Proposed incremental capacity',2400.,'S','GBPm','CONSENT: commitments to be sought in tranches, not fully committed'),
 'ss_rate':('Existing super senior historical coupon',.0975,'S','%','AR26 pp139-140; A: also applied to illustrative new draws'),
 'b_claim':('Approximate Class B debt',1000.,'S','GBPm','CLASSB: cGBP1bn, not an exact reconciled legal claim'),
 'b_recovery':('Proposed Class B legacy recovery',.059,'S','%','CLASSB: recovery rate, NOT 5.9% ownership of the whole equity'),
 'b_rights':('Class B right to invest new equity',150.,'S','GBPm','CLASSB: additional investment right, not a free GBP150m recovery'),
 'a_quote':('Historical Class A trading reference',.69,'S','price/par','AR26 p124: c69% at March 2026, not current or executable'),
 'historic_burn':('FY26 cash outflow before other financing',1130.2,'S','GBPm/year','AR26 p39: excludes subsequent borrowings, leases and derivative settlements'),
 'cash':('Opening accessible cash proxy, 31 Oct',200.,'A','GBPm','Current accessible balance unavailable; not rolled forward from March cash'),
 'burn':('Monthly cash use before new-draw interest',200.,'A','GBPm/month','Illustrative stress above FY26 GBP94.2m monthly outflow; includes all opening-debt interest and capex, no automatic financing plug'),
 'buffer':('Minimum cash buffer',100.,'A','GBPm','Analyst liquidity buffer, not a covenant or regulatory requirement'),
 'fee':('Incremental upsize draw fee',.02,'A','%','2% fee on new GBP2.4bn only; no fee assumed on existing undrawn GBP350m'),
 'funding_case':('Funding case: 0 blocked / 1 existing / 2 upsize',2,'A','index','2 assumes approvals and commitments for illustration; not current funded position'),
 'maturity_case':('March extension: 0 no / 1 yes',1,'A','index','Separate from liquidity approvals; base assumes extension, not an agreed outcome'),
 'march_claim':('March 2027 senior principal stress',500.,'A','GBPm','Illustrative payable if extension fails; exact instrument amounts unavailable'),
 'equity':('Post-money plan equity value proxy',6000.,'A','GBPm','Unverified plan equity value; used only to translate legacy recovery into ownership'),
 'equity_stress':('Equity value multiplier',1.,'A','x','Hold allocated shares fixed, vary realised equity value'),
 'ev':('Illustrative distributable enterprise value',18000.,'A','GBPm','Not RCV or agreed plan value; independent recovery scenario'),
 'cost':('Value leakage / enforcement costs',.05,'A','%','5% illustrative cost before creditor distributions'),
 'hedges':('Priority hedge / other claim reserve',1500.,'A','GBPm','Termination claims unverified; assume ahead of super senior, relation requires legal review'),
 'class_a':('Class A claim proxy',16000.,'A','GBPm','Unverified round claim amount, not a reconciliation of statutory or covenant net debt'),
}
# A: six equal potential draws, November to September. No commitment asserted.
UPSIZE_MONTHS=(0,2,4,6,8,10)
EV_GRID=(12000.,15000.,18000.,21000.,24000.,27000.)
EQUITY_GRID=(.5,1.,1.5)
def values():return {k:v[1] for k,v in INPUTS.items()}
