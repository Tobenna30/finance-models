"""S=sourced, A=assumed; returns in percentage points."""
PERIODS=['3 months','YTD','1 year','3 years annualised','5 years annualised','10 years annualised']
FUND=[1.05,-0.26,0.11,3.28,-2.01,0.72]
BENCHMARK=[0.87,-0.21,0.62,3.41,-1.55,0.38]
SECTORS=[('Global Treasuries',40.7,53.7),('Corporates',31.9,18.4),('Securitized',12.8,12.7),('Government Related',10.9,15.1),('Cash & Equivalents',3.7,0.0)]
SOURCE='Factsheet p1 returns and p2 sectors; 30 Jun 2026. Commentary p1 reconciles returns.'
REQUESTS=[
 ('Q1','Performance periods and fee basis','Supported','Factsheet p1 and commentary p1: Class I net returns, identical 30 Jun 2026 end date','Research analyst'),
 ('Q2','Benchmark identity','Supported','Bloomberg Global Aggregate Index, factsheet p1','Research analyst'),
 ('Q3','Share-class costs and waiver','Supported','0.67% net and 0.79% gross, waiver 31 Jan 2027, factsheet p1','Client service'),
 ('Q4','Numerical return attribution','Open','Commentary p2 names contributors but does not quantify contributions','Investment team'),
 ('Q5','GBP-hedged mandate suitability','Open','US mutual fund snapshot does not establish GBP-hedged institutional mandate terms','Investment director'),
 ('Q6','Institutional client access','Open','Hypothetical UK pension eligibility and appropriate vehicle require confirmation','Client service'),
 ('Q7','Holdings and process consistency','Open','Aggregate sectors cannot establish trading decisions or security-level discipline','Investment team'),
 ('Q8','Class R identifier inconsistency','Open','Factsheet header LSGBXR differs from fund-facts table LSGLX','Client service'),
]
ASSUMPTIONS={'client':'Hypothetical UK pension reviewing a global bond mandate, not an actual relationship','due_days':5,'cash_benchmark':0.0}
