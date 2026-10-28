"""Monthly published-portfolio replication, not independent security-level signals.
A historical-universe aggregate avoids selecting today's surviving names, but does
not independently audit constituents, delisting treatments or publication vintages.
"""
import json,math
import numpy as np
import pandas as pd
import assumptions as A

def raw():return pd.read_csv(A.DATA/'monthly.csv',index_col='month')

def panel(cost_bp=A.COST_BP,turnover=A.ONE_WAY_TURNOVER,borrow=A.BORROW_ANNUAL):
    d=raw().loc[A.START:A.END].copy()
    d['gross']=A.LEG_WEIGHT*(d.decile10-d.decile1)
    d['execution_cost']=4*A.LEG_WEIGHT*turnover*cost_bp/10000
    d['borrow_cost']=A.LEG_WEIGHT*borrow/12
    d['net']=d.gross-d.execution_cost-d.borrow_cost
    # Report compounded excess-P&L index on fixed monthly NAV. Actual collateral
    # interest is outside this excess-return index; do not subtract Rf again.
    d['wealth']=(1+d.net).cumprod()
    d['high_water']=np.maximum.accumulate(np.r_[1.,d.wealth.to_numpy()])[1:]
    d['drawdown']=d.wealth/d.high_water-1
    return d

def stats(d):
    x=d.net;n=len(d);wealth=(1+x).prod()
    return {'months':n,'start':d.index[0],'end':d.index[-1],'net_sharpe':float(x.mean()/x.std(ddof=1)*math.sqrt(12)),'annual_net_mean':float(x.mean()*12),'annual_net_vol':float(x.std(ddof=1)*math.sqrt(12)),'net_cagr':float(wealth**(12/n)-1),'annual_execution_drag':float(d.execution_cost.mean()*12),'annual_borrow_drag':float(d.borrow_cost.mean()*12),'annual_total_cost_drag':float((d.execution_cost+d.borrow_cost).mean()*12),'factor_correlation':float(d.gross.corr(d.mom))}

def drawdowns(d,limit=5):
    # Non-overlapping peak-to-trough-to-recovery episodes, including unrecovered.
    episodes=[];peak=1.;peak_date='1962-12';trough=0.;trough_date=None;active=False
    for date,row in d.iterrows():
        wealth=float(row.wealth)
        if wealth>=peak:
            if active:episodes.append({'peak':peak_date,'trough':trough_date,'recovery':date,'drawdown':trough})
            peak=wealth;peak_date=date;trough=0.;active=False
        else:
            active=True;dd=wealth/peak-1
            if dd<trough:trough=dd;trough_date=date
    if active:episodes.append({'peak':peak_date,'trough':trough_date,'recovery':None,'drawdown':trough})
    return sorted(episodes,key=lambda x:x['drawdown'])[:limit]

def walk_forward(d):
    rows=[]
    for year in range(2000,2027):
        before=d[d.index<str(year)];test=d[d.index.str.startswith(str(year))]
        if test.empty:continue
        # Expanding training risk estimate uses only previous months. Rules and
        # weights remain frozen; no tuning on the evaluation year's returns.
        rows.append({'year':year,'train_end':before.index[-1],'train_months':len(before),'train_sharpe':stats(before)['net_sharpe'],'train_annual_vol':stats(before)['annual_net_vol'],'test_months':len(test),'test_return':float((1+test.net).prod()-1),'test_annual_vol':stats(test)['annual_net_vol']})
    return rows

def results():
    d=panel();years=d.groupby(d.index.str[:4]).net.apply(lambda x:float((1+x).prod()-1));dd=drawdowns(d)
    costs=[]
    for t in A.TURNOVER_GRID:
        for c in A.COST_GRID:
            s=stats(panel(c,t).loc[A.TEST_START:]);costs.append({'turnover':t,'cost_bp':c,**s})
    s=stats(d.loc[A.TEST_START:]);be=(d.loc[A.TEST_START:].gross.mean()-A.LEG_WEIGHT*A.BORROW_ANNUAL/12)/(4*A.LEG_WEIGHT*A.ONE_WAY_TURNOVER)*10000
    return {'design':stats(d.loc[:A.TRAIN_END]),'evaluation':s,'full':stats(d),'worst_drawdown':dd[0],'drawdown_episodes':dd,'worst_years':[{'year':str(y),'net_return':float(v),'months':int((d.index.str.startswith(y)).sum())} for y,v in years.sort_values().head(5).items()],'crash_2009':{'net_return':float(years.loc['2009']),'april_net':float(d.loc['2009-04'].net),'published_mom_2009':float((1+d.loc['2009-01':'2009-12'].mom).prod()-1)},'correlation_full':float(d.gross.corr(d.mom)),'oos_break_even_execution_bp':float(be),'walk_forward':walk_forward(d),'cost_sensitivity':costs,'verdict':'Reject a standalone momentum strategy under base costs; retain as a published-portfolio research benchmark, without a stock-level implementation claim.'}
if __name__=='__main__':print(json.dumps(results(),indent=2))
